# -*- coding: utf-8 -*-
"""Confere que o sufixo cotidiano sobrevive na janela de 512 do reranker."""

import sys
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(1, str(_RAIZ))

from transformers import AutoTokenizer

from src.rag.retriever import encaixar_ponte_na_janela
from src.rag.reranker import _PASTA_ONNX


def testar() -> None:
    tokenizador = AutoTokenizer.from_pretrained(str(_PASTA_ONNX), local_files_only=True)
    pergunta = "qual é a regra deste dispositivo longo"
    oficial = "O caput oficial repete uma fórmula jurídica sem equivalente curto. " * 80
    termos = "busca popular, situação do dia a dia, nome consagrado"
    texto = oficial + "\nTermos cotidianos: " + termos
    bruto = tokenizador(pergunta, texto, truncation=False, add_special_tokens=True)["input_ids"]
    if bruto and isinstance(bruto[0], list):
        bruto = bruto[0]
    if len(bruto) <= 512:
        raise SystemExit("O par sintético não passou de 512 tokens.")
    ajustado = encaixar_ponte_na_janela(pergunta, texto, tokenizador, 512)
    if not ajustado.endswith(termos):
        raise SystemExit("O sufixo cotidiano foi alterado.")
    janela = tokenizador(pergunta, ajustado, truncation=True, max_length=512, add_special_tokens=True)["input_ids"]
    if janela and isinstance(janela[0], list):
        janela = janela[0]
    if len(janela) > 512:
        raise SystemExit("A janela passou de 512: {}".format(len(janela)))
    visivel = tokenizador.decode(janela, skip_special_tokens=True)
    if "Termos cotidianos:" not in visivel or termos not in visivel:
        raise SystemExit("O sufixo não chegou intacto aos tokens da janela 512.")
    inteiro = tokenizador(pergunta, ajustado, truncation=False, add_special_tokens=True)["input_ids"]
    if inteiro and isinstance(inteiro[0], list):
        inteiro = inteiro[0]
    if len(inteiro) > 512:
        raise SystemExit("O par ajustado ainda excede 512: {}".format(len(inteiro)))
    print("ok janela 512; bruto {} tokens; ajustado {} tokens.".format(len(bruto), len(inteiro)))


if __name__ == "__main__":
    testar()
