# -*- coding: utf-8 -*-
"""Reranker com três costas: PyTorch FP32, ONNX INT8 e MiniLM.

A pontuação devolve sempre um número em [0, 1]. A escala é lida uma vez:
se o grafo solta logit, entra uma sigmoide; se já solta probabilidade,
não entra outra. Os pares podem ser ordenados por comprimento para o
padding de cada lote não seguir o texto mais longo.
"""

import math
import os
import sys
from pathlib import Path
from typing import Any, Callable

import numpy as np
import torch
from sentence_transformers import CrossEncoder

_RAIZ = Path(__file__).resolve().parents[2]
_PASTA_ONNX = _RAIZ / "modelos" / "bge_reranker_v2_m3_onnx_int8"
_NOME_BGE = "BAAI/bge-reranker-v2-m3"
_NOME_MINILM = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
_NUCLEOS: int | None = None


def nucleos_fisicos() -> int:
    """Núcleos físicos, para o ONNX não disputar os lógicos do hyperthreading."""
    global _NUCLEOS
    if _NUCLEOS is not None:
        return _NUCLEOS
    n = 0
    if sys.platform == "win32":
        try:
            import subprocess

            saida = subprocess.check_output(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "(Get-CimInstance Win32_Processor | Measure-Object NumberOfCores -Sum).Sum",
                ],
                text=True,
                timeout=30,
            ).strip()
            if saida.isdigit():
                n = int(saida)
        except (OSError, subprocess.SubprocessError):
            n = 0
    if n < 1:
        n = max(1, (os.cpu_count() or 4) // 2)
    _NUCLEOS = n
    return n


def sessao_cpu():
    """Sessão ONNX com um fio entre operadores e os núcleos físicos dentro de cada um."""
    import onnxruntime as ort

    opcoes = ort.SessionOptions()
    opcoes.intra_op_num_threads = nucleos_fisicos()
    opcoes.inter_op_num_threads = 1
    opcoes.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    return opcoes


def _sigmoid(valor: float) -> float:
    if valor >= 0:
        return 1.0 / (1.0 + math.exp(-valor))
    expoente = math.exp(valor)
    return expoente / (1.0 + expoente)


def arquivo_onnx_int8() -> Path:
    """Caminho do ONNX quantizado. Falha se o script offline ainda não rodou."""
    if not _PASTA_ONNX.is_dir():
        raise FileNotFoundError(
            "ONNX INT8 ausente em {}. Rode: python -m src.rag.otimizar_reranker_onnx".format(_PASTA_ONNX)
        )
    candidatos = [
        caminho
        for caminho in _PASTA_ONNX.rglob("*.onnx")
        if "fp32" not in caminho.name.lower()
        and any(marca in caminho.name.lower() for marca in ("qint8", "int8", "quant", "avx2"))
    ]
    if not candidatos:
        raise FileNotFoundError("Não há ONNX INT8 em {}.".format(_PASTA_ONNX))
    return sorted(candidatos)[0]


class SessaoOnnx:
    """Cross-encoder em ONNX Runtime. predict() devolve o logit cru.

    O grafo não inclui sigmoide. escala_fixa avisa o pontuador para aplicar
    uma, e só uma.
    """

    escala_fixa = "logit_sigmoide_python"

    def __init__(self, sessao, tokenizador, max_length: int) -> None:
        self.sessao = sessao
        self.tokenizador = tokenizador
        self.max_length = max_length
        self.entradas = [item.name for item in sessao.get_inputs()]

    def predict(
        self,
        pares,
        batch_size: int = 4,
        activation_fn: Callable | None = None,
        show_progress_bar: bool = False,
        **kwargs,
    ):
        del show_progress_bar, kwargs
        if not pares:
            return np.zeros((0,), dtype=np.float32)
        blocos = []
        for inicio in range(0, len(pares), batch_size):
            fatia = pares[inicio : inicio + batch_size]
            lote = self.tokenizador(
                [par[0] for par in fatia],
                [par[1] for par in fatia],
                padding=True,
                truncation=True,
                max_length=self.max_length,
                return_tensors="np",
            )
            alimentacao = {nome: lote[nome] for nome in self.entradas if nome in lote}
            logits = np.asarray(self.sessao.run(None, alimentacao)[0], dtype=np.float32)
            blocos.append(logits.reshape(len(fatia), -1)[:, 0])
        valores = np.concatenate(blocos)
        if activation_fn is not None and not isinstance(activation_fn, torch.nn.Identity):
            valores = np.asarray([float(activation_fn(torch.tensor(float(item)))) for item in valores], dtype=np.float32)
        return valores


def carregar_pytorch_fp32(max_length: int = 512) -> CrossEncoder:
    """Referência actual: BGE reranker em FP32, janela larga."""
    return CrossEncoder(_NOME_BGE, max_length=max_length, backend="torch")


def carregar_onnx_int8(max_length: int = 320):
    """INT8 lido do disco. A sessão ONNX devolve logits; a sigmoide entra uma vez."""
    import onnxruntime as ort
    from transformers import AutoTokenizer

    arquivo = arquivo_onnx_int8()
    tokenizador = AutoTokenizer.from_pretrained(str(_PASTA_ONNX), local_files_only=True)
    sessao = ort.InferenceSession(
        str(arquivo),
        sess_options=sessao_cpu(),
        providers=["CPUExecutionProvider"],
    )
    return SessaoOnnx(sessao, tokenizador, max_length)


def _eixo_sequencia_estatico(sessao) -> int | None:
    """Menor eixo de sequência fixo. None quando o eixo é dinâmico."""
    menor = None
    for entrada in sessao.get_inputs():
        forma = list(entrada.shape)
        if len(forma) < 2:
            continue
        eixo = forma[1]
        if isinstance(eixo, str) or eixo is None:
            return None
        if isinstance(eixo, int):
            menor = eixo if menor is None else min(menor, eixo)
    return menor


def carregar_onnx_para_producao():
    """Sobe o INT8 em 512 se o eixo dinâmico aceitar um par desse tamanho.

    O export usou dynamic_axes na sequência. Se o grafo estiver estático
    abaixo de 512, ou se o par dummy falhar, a janela fica em 320.
    """
    modelo = carregar_onnx_int8(320)
    formas = ["{} {}".format(entrada.name, list(entrada.shape)) for entrada in modelo.sessao.get_inputs()]
    print("[reranker] entradas: {}".format("; ".join(formas)), flush=True)
    estatico = _eixo_sequencia_estatico(modelo.sessao)
    if estatico is not None and estatico < 512:
        modelo.max_length = min(320, estatico)
        print("[reranker] max_length efetivo: {} (eixo estático)".format(modelo.max_length), flush=True)
        return modelo
    modelo.max_length = 512
    try:
        modelo.predict(
            [("A Constituição admite a pena de morte?", "dispositivo " * 80)],
            batch_size=1,
            activation_fn=torch.nn.Identity(),
            show_progress_bar=False,
        )
    except Exception as exc:
        modelo.max_length = 320
        print("[reranker] max_length efetivo: 320 (fallback: {})".format(type(exc).__name__), flush=True)
        return modelo
    print("[reranker] max_length efetivo: 512", flush=True)
    return modelo


def carregar_minilm(max_length: int = 320) -> CrossEncoder:
    """Cross-encoder pequeno, treinado em pares de busca."""
    return CrossEncoder(_NOME_MINILM, max_length=max_length, backend="torch")


def _valor_unico(saida: Any) -> float:
    return float(np.atleast_1d(np.asarray(saida, dtype=np.float64)).reshape(-1)[0])


def detectar_escala(modelo) -> str:
    """Diz se a saída crua é logit ou probabilidade.

    Identity desliga a activação do CrossEncoder. Se esse número e o
    predict() normal coincidem e cabem em [0, 1], o grafo já devolve
    probabilidade. Se o cru sai do intervalo, ou se o predict normal o
    comprime para [0, 1], há um logit e cabe uma sigmoide — a do
    CrossEncoder, não uma segunda por cima.
    """
    fixa = getattr(modelo, "escala_fixa", None)
    if fixa:
        return fixa
    par = [("pergunta de prova", "trecho de prova")]
    cru = _valor_unico(
        modelo.predict(par, batch_size=1, activation_fn=torch.nn.Identity(), show_progress_bar=False)
    )
    normal = _valor_unico(modelo.predict(par, batch_size=1, show_progress_bar=False))
    if abs(cru - normal) < 1e-4:
        if cru < 0.0 or cru > 1.0:
            return "logit_sigmoide_python"
        return "probabilidade"
    return "logit_sigmoide_crossencoder"


def descrever_escala(modo: str) -> str:
    if modo == "probabilidade":
        return "o modelo já devolve probabilidade em [0, 1]; sigmoide não aplicada"
    if modo == "logit_sigmoide_crossencoder":
        return "o grafo devolve logit; o CrossEncoder aplica uma sigmoide"
    return "o grafo devolve logit; uma sigmoide é aplicada em Python"


def pontuar_pares(
    modelo,
    pergunta: str,
    textos: list[str],
    batch_size: int,
    modo_escala: str,
    ordenar_por_tamanho: bool,
) -> list[float]:
    """Pontua os textos na ordem recebida. O lote pode ser reordenado por tamanho."""
    if not textos:
        return []
    ordem = list(range(len(textos)))
    if ordenar_por_tamanho:
        ordem.sort(key=lambda indice: len(textos[indice]))
    pares = [(pergunta, textos[indice]) for indice in ordem]
    if modo_escala == "logit_sigmoide_python":
        bruto = modelo.predict(
            pares,
            batch_size=batch_size,
            activation_fn=torch.nn.Identity(),
            show_progress_bar=False,
        )
        valores = [_sigmoid(float(item)) for item in np.atleast_1d(np.asarray(bruto)).reshape(-1)]
    elif modo_escala == "probabilidade":
        bruto = modelo.predict(
            pares,
            batch_size=batch_size,
            activation_fn=torch.nn.Identity(),
            show_progress_bar=False,
        )
        valores = [float(item) for item in np.atleast_1d(np.asarray(bruto)).reshape(-1)]
    else:
        bruto = modelo.predict(pares, batch_size=batch_size, show_progress_bar=False)
        valores = [float(item) for item in np.atleast_1d(np.asarray(bruto)).reshape(-1)]
        if any(valor < 0.0 or valor > 1.0 for valor in valores):
            valores = [_sigmoid(valor) for valor in valores]
    saida = [0.0] * len(textos)
    for posicao, indice in enumerate(ordem):
        saida[indice] = valores[posicao]
    return saida


def libertar() -> None:
    """Força a recolha depois de o chamador ter apagado o modelo."""
    import gc

    gc.collect()


def fabrica(nome: str) -> Callable[[], CrossEncoder]:
    if nome == "pytorch":
        return lambda: carregar_pytorch_fp32(512)
    if nome == "onnx":
        return lambda: carregar_onnx_int8(320)
    if nome == "minilm":
        return lambda: carregar_minilm(320)
    raise ValueError("Cenário desconhecido: {}".format(nome))
