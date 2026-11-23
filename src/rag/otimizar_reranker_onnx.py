# -*- coding: utf-8 -*-
"""Exporta o BGE reranker para ONNX e quantiza os pesos em INT8 (AVX2).

O optimum.onnxruntime desta máquina não importa com transformers 5
(faltam is_offline_mode e get_parameter_dtype). A exportação usa
torch.onnx e a quantização dinâmica do onnxruntime, com pesos QInt8
simétricos por canal — a receita de CPU x86_64 com AVX2.

Corre uma vez. O artefacto fica em modelos/bge_reranker_v2_m3_onnx_int8/.
As consultas seguintes lêem esse disco e não voltam a exportar.
"""

import inspect
import sys
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

_RAIZ = Path(__file__).resolve().parents[2]
if str(_RAIZ) not in sys.path:
    sys.path.insert(0, str(_RAIZ))

from src.rag.reranker import _PASTA_ONNX, arquivo_onnx_int8, nucleos_fisicos

_NOME = "BAAI/bge-reranker-v2-m3"


def _ja_existe() -> bool:
    try:
        return arquivo_onnx_int8().is_file()
    except FileNotFoundError:
        return False


class _Embrulho(torch.nn.Module):
    """Devolve só o logit. O dataclass do transformers não entra no grafo."""

    def __init__(self, base: torch.nn.Module) -> None:
        super().__init__()
        self.base = base

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        return self.base(input_ids=input_ids, attention_mask=attention_mask).logits


def _exportar(modulo: torch.nn.Module, exemplo: dict, destino: Path) -> None:
    argumentos = (exemplo["input_ids"], exemplo["attention_mask"])
    opcoes = {
        "input_names": ["input_ids", "attention_mask"],
        "output_names": ["logits"],
        "dynamic_axes": {
            "input_ids": {0: "batch", 1: "sequence"},
            "attention_mask": {0: "batch", 1: "sequence"},
            "logits": {0: "batch"},
        },
        "opset_version": 17,
        "do_constant_folding": True,
    }
    assinatura = inspect.signature(torch.onnx.export)
    if "dynamo" in assinatura.parameters:
        opcoes["dynamo"] = False
    if "external_data" in assinatura.parameters:
        opcoes["external_data"] = True
    torch.onnx.export(modulo, argumentos, str(destino), **opcoes)


def main() -> None:
    if _ja_existe():
        print("ONNX INT8 já presente em {}".format(arquivo_onnx_int8()), flush=True)
        return
    from onnxruntime.quantization import QuantType, quantize_dynamic

    _PASTA_ONNX.mkdir(parents=True, exist_ok=True)
    print("Núcleos físicos: {}".format(nucleos_fisicos()), flush=True)
    print("A carregar {}.".format(_NOME), flush=True)
    tokenizador = AutoTokenizer.from_pretrained(_NOME)
    modelo = AutoModelForSequenceClassification.from_pretrained(_NOME)
    modelo.eval()
    tokenizador.save_pretrained(str(_PASTA_ONNX))
    modelo.config.save_pretrained(str(_PASTA_ONNX))

    exemplo = tokenizador(
        ["A Constituição proíbe o anonimato?"],
        ["é livre a manifestação do pensamento, sendo vedado o anonimato"],
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=64,
    )
    print("Entradas do tokenizador: {}".format(sorted(exemplo.keys())), flush=True)
    embrulho = _Embrulho(modelo).eval()
    fp32 = _PASTA_ONNX / "model_fp32.onnx"
    print("A exportar o grafo FP32.", flush=True)
    with torch.inference_mode():
        _exportar(embrulho, exemplo, fp32)
    del modelo, embrulho

    destino = _PASTA_ONNX / "model_qint8_avx2.onnx"
    print("A quantizar pesos em INT8, por canal, simétricos (AVX2).", flush=True)
    quantize_dynamic(
        str(fp32),
        str(destino),
        weight_type=QuantType.QInt8,
        per_channel=True,
        reduce_range=False,
        extra_options={"WeightSymmetric": True},
    )
    fp32.unlink(missing_ok=True)
    for resto in _PASTA_ONNX.glob("model_fp32*"):
        if resto.is_file():
            resto.unlink()
    print("Gravado: {} ({:.1f} MB)".format(destino, destino.stat().st_size / (1024 * 1024)), flush=True)

    from src.rag.reranker import carregar_onnx_int8, descrever_escala, detectar_escala

    carregado = carregar_onnx_int8(320)
    modo = detectar_escala(carregado)
    print("Escala do INT8: {}".format(descrever_escala(modo)), flush=True)
    pares = [
        ("A Constituição proíbe o anonimato?", "é livre a manifestação do pensamento, sendo vedado o anonimato"),
        ("Qual a pena de furto qualificado no Código Penal?", "a lei regulará a individualização da pena"),
    ]
    crus = carregado.predict(pares, batch_size=2, activation_fn=torch.nn.Identity())
    for par, cru in zip(pares, crus):
        probabilidade = 1.0 / (1.0 + torch.exp(torch.tensor(-float(cru)))).item()
        print("logit {:.3f} -> probabilidade {:.3f} | {}".format(float(cru), probabilidade, par[0]), flush=True)


if __name__ == "__main__":
    main()
