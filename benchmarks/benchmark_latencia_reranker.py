# -*- coding: utf-8 -*-
"""A/B do reranker na mesma amostra de 45 perguntas, com uma consulta de aquecimento.

A cronometra PyTorch FP32, top 12, janela 512, lote 16.
B cronometra o ONNX INT8, top 8, janela 320, lote 4 ordenado por tamanho.
C cronometra o MiniLM mmarco, top 8, janela 320.
O relógio de cada consulta inclui embedding, roteador, cosseno e reranker.
"""

import json
import sys
import time
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(1, str(_RAIZ))

import pandas as pd

from src.rag.encoder import gerar_embedding
from src.rag.reranker import descrever_escala, detectar_escala, libertar, pontuar_pares
from src.rag.retriever import _ARTIGO_IDS, _TEXTOS, _ranking_denso
from src.roteador.servico_classificacao import avaliar_intencao

_CSV = Path(r"c:\Users\nicol\Downloads\dataset_teste_300_perguntas.csv")
_SAIDA = Path(__file__).resolve().parent / "resultados_ab_reranker.json"
_CORTES = (0.20, 0.25, 0.30)
_WARMUP = "Quem pode propor emenda à Constituição?"
_CONTROLES = (
    ("Anonimato", "A Constituição garante a liberdade de manifestação do pensamento e proíbe o anonimato?"),
    ("Mineração", "O Estado pode intervir na economia para criar um monopólio de mineração?"),
    ("Templos", "A União, os Estados e os Municípios podem instituir impostos sobre templos de qualquer culto?"),
    ("Furto qualificado", "Qual é a pena prevista no Código Penal para o crime de furto qualificado?"),
)

import re

_RE_ARTIGO = re.compile(r"Art\.\s*\d+[ºo]?(?:-[A-Za-z])?")


def _norm(valor: str) -> str:
    return re.sub(r"\s+", " ", str(valor)).strip()


def _alvos(referencia: str) -> list[str]:
    return [_norm(item) for item in _RE_ARTIGO.findall(str(referencia))]


def _casa(alvo: str, artigo_id: str) -> bool:
    ident = _norm(artigo_id)
    if ident.startswith("ADCT") and not alvo.startswith("ADCT"):
        return False
    return ident == alvo or ident.startswith(alvo + ",") or ident.startswith(alvo + " ")


def _bateu(alvos: list[str], ids: list[str]) -> bool:
    return any(_casa(alvo, ident) for alvo in alvos for ident in ids)


def _percentil(valores: list[float], p: float) -> float:
    ordenados = sorted(valores)
    if len(ordenados) == 1:
        return ordenados[0]
    posicao = (len(ordenados) - 1) * (p / 100.0)
    baixo = int(posicao)
    alto = min(baixo + 1, len(ordenados) - 1)
    peso = posicao - baixo
    return ordenados[baixo] * (1.0 - peso) + ordenados[alto] * peso


def _amostra() -> tuple[list[str], list[tuple[str, str]]]:
    tabela = pd.read_csv(_CSV, encoding="utf-8")
    fora = tabela.loc[tabela["intencao_esperada"].astype(str) == "Fora de Escopo"]
    constitucional = tabela.loc[tabela["intencao_esperada"].astype(str) != "Fora de Escopo"]
    obrigatorias = ("anonimato", "monopólio de mineração", "culto")
    escolhidas: list[tuple[str, str]] = []
    textos = constitucional["texto"].astype(str).tolist()
    refs = constitucional["artigo_referencia"].astype(str).tolist()
    for marca in obrigatorias:
        for texto, ref in zip(textos, refs):
            if marca in texto.lower() or marca in texto:
                escolhidas.append((texto, ref))
                break
    for texto, ref in zip(textos, refs):
        if len(escolhidas) >= 15:
            break
        if all(texto != item[0] for item in escolhidas):
            escolhidas.append((texto, ref))
    return fora["texto"].astype(str).tolist(), escolhidas[:15]


def _consultar(pergunta: str, pontuar, top_n: int) -> tuple[list[tuple[int, float]], float]:
    inicio = time.perf_counter()
    vetor = gerar_embedding(pergunta)
    avaliacao = avaliar_intencao(pergunta, embedding=vetor)
    pacote = _ranking_denso(pergunta, avaliacao, vetor, 0.05)
    indices = pacote["ordem"][:top_n]
    notas = pontuar(pergunta, [_TEXTOS[indice] for indice in indices])
    pares = sorted(zip(indices, notas), key=lambda par: par[1], reverse=True)
    return pares, time.perf_counter() - inicio


def _recall(escolhidas, resultados: dict[str, list[tuple[int, float]]], corte: float | None) -> tuple[float, float]:
    hits1 = []
    hits5 = []
    for texto, ref in escolhidas:
        pares = resultados[texto]
        if corte is not None:
            pares = [par for par in pares if par[1] >= corte]
        ids = [_ARTIGO_IDS[indice] for indice, _ in pares]
        alvos = _alvos(ref)
        if not alvos:
            continue
        hits1.append(_bateu(alvos, ids[:1]))
        hits5.append(_bateu(alvos, ids[:5]))
    return sum(hits1) / len(hits1), sum(hits5) / len(hits5)


def _bloqueio(fora: list[str], resultados: dict[str, list[tuple[int, float]]], corte: float) -> float:
    bloqueados = 0
    for texto in fora:
        topo = resultados[texto][0][1] if resultados[texto] else 0.0
        if topo < corte:
            bloqueados += 1
    return bloqueados / len(fora)


def _melhor_corte(fora, escolhidas, resultados) -> tuple[float, float, float]:
    """Corte com bloqueio >= 96,7% e o maior Recall@5. Senão, o maior bloqueio com Recall@5 >= 93%."""
    grelha = [indice / 100 for indice in range(5, 96, 5)]
    candidatos = []
    for corte in grelha:
        bloqueio = _bloqueio(fora, resultados, corte)
        _, recall5 = _recall(escolhidas, resultados, corte)
        candidatos.append((corte, bloqueio, recall5))
    suficientes = [item for item in candidatos if item[1] >= 0.967]
    if suficientes:
        return max(suficientes, key=lambda item: (item[2], item[1], -item[0]))
    precisos = [item for item in candidatos if item[2] >= 0.93]
    if precisos:
        return max(precisos, key=lambda item: (item[1], item[2]))
    return max(candidatos, key=lambda item: (item[1], item[2]))


def _rodar(nome: str, fabrica, top_n: int, batch_size: int, ordenar: bool, fora, escolhidas) -> dict:
    print("\n=== {} ===".format(nome), flush=True)
    modelo = fabrica()
    modo = detectar_escala(modelo)
    print("Escala: {}".format(descrever_escala(modo)), flush=True)

    def pontuar(pergunta: str, textos: list[str]) -> list[float]:
        return pontuar_pares(modelo, pergunta, textos, batch_size, modo, ordenar)

    _consultar(_WARMUP, pontuar, top_n)
    print("Aquecimento feito.", flush=True)

    tempos = []
    resultados: dict[str, list[tuple[int, float]]] = {}
    total = len(fora) + len(escolhidas)
    for indice, texto in enumerate(fora + [item[0] for item in escolhidas], start=1):
        pares, gasto = _consultar(texto, pontuar, top_n)
        tempos.append(gasto)
        resultados[texto] = pares
        if indice % 5 == 0 or indice == total:
            print("  {}/{}  {:.2f} s".format(indice, total, gasto), flush=True)

    controles = []
    for rotulo, pergunta in _CONTROLES:
        if pergunta in resultados:
            pares = resultados[pergunta]
            gasto = None
        else:
            pares, gasto = _consultar(pergunta, pontuar, top_n)
        topo = pares[0] if pares else None
        controles.append(
            {
                "nome": rotulo,
                "score": None if topo is None else round(topo[1], 4),
                "artigo": None if topo is None else _ARTIGO_IDS[topo[0]],
                "segundos": None if gasto is None else round(gasto, 2),
            }
        )
        if topo is None:
            print("  {} sem score".format(rotulo), flush=True)
        else:
            extra = "" if gasto is None else "  {:.2f} s".format(gasto)
            print("  {}  {:.3f}  {}{}".format(rotulo, topo[1], _ARTIGO_IDS[topo[0]], extra), flush=True)

    recall1, recall5 = _recall(escolhidas, resultados, None)
    recall1_op, recall5_op = _recall(escolhidas, resultados, 0.25)
    bloqueios = {("{:.2f}".format(corte)): round(_bloqueio(fora, resultados, corte), 4) for corte in _CORTES}
    melhor = _melhor_corte(fora, escolhidas, resultados)
    resumo = {
        "cenario": nome,
        "escala": descrever_escala(modo),
        "media_s": round(sum(tempos) / len(tempos), 3),
        "p50_s": round(_percentil(tempos, 50), 3),
        "p90_s": round(_percentil(tempos, 90), 3),
        "recall_1": round(recall1, 4),
        "recall_5": round(recall5, 4),
        "recall_1_corte_0_25": round(recall1_op, 4),
        "recall_5_corte_0_25": round(recall5_op, 4),
        "bloqueio": bloqueios,
        "melhor_corte": {"corte": melhor[0], "bloqueio": round(melhor[1], 4), "recall_5": round(melhor[2], 4)},
        "controles": controles,
    }
    print(
        "Média {:.2f} s | P50 {:.2f} s | P90 {:.2f} s | R@1 {:.3f} | R@5 {:.3f}".format(
            resumo["media_s"], resumo["p50_s"], resumo["p90_s"], resumo["recall_1"], resumo["recall_5"]
        ),
        flush=True,
    )
    print("Bloqueio {}".format(bloqueios), flush=True)
    print(
        "Melhor corte {:.2f}: bloqueio {:.1%} | Recall@5 {:.3f}".format(melhor[0], melhor[1], melhor[2]),
        flush=True,
    )
    del pontuar
    del modelo
    libertar()
    return resumo


def main() -> None:
    from src.rag.reranker import carregar_minilm, carregar_onnx_int8, carregar_pytorch_fp32

    fora, escolhidas = _amostra()
    print("Fora de escopo: {} | constitucionais: {}".format(len(fora), len(escolhidas)), flush=True)
    gerar_embedding(_WARMUP)
    cenarios = [
        ("A PyTorch FP32 top12", lambda: carregar_pytorch_fp32(512), 12, 16, False),
        ("B ONNX INT8 top8", lambda: carregar_onnx_int8(320), 8, 4, True),
        ("C MiniLM top8", lambda: carregar_minilm(320), 8, 8, False),
    ]
    relatorios = []
    for nome, fabrica, top_n, batch_size, ordenar in cenarios:
        relatorios.append(_rodar(nome, fabrica, top_n, batch_size, ordenar, fora, escolhidas))
        _SAIDA.write_text(json.dumps(relatorios, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nTabela", flush=True)
    print("{:<24} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8}".format(
        "Cenário", "média", "P50", "P90", "R@1", "R@5", "blk.20", "blk.25", "blk.30"
    ), flush=True)
    for item in relatorios:
        print(
            "{:<24} {:>8.2f} {:>8.2f} {:>8.2f} {:>8.3f} {:>8.3f} {:>8.1%} {:>8.1%} {:>8.1%}".format(
                item["cenario"],
                item["media_s"],
                item["p50_s"],
                item["p90_s"],
                item["recall_1"],
                item["recall_5"],
                item["bloqueio"]["0.20"],
                item["bloqueio"]["0.25"],
                item["bloqueio"]["0.30"],
            ),
            flush=True,
        )


if __name__ == "__main__":
    main()
