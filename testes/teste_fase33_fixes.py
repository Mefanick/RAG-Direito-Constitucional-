# -*- coding: utf-8 -*-
"""Checagens locais da Fase 3.3, sem Ollama."""

import hashlib
import sys
from pathlib import Path

import torch

_RAIZ = Path(__file__).resolve().parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(1, str(_RAIZ))

from avaliar_bateria_cega_fase33 import _recuperou
from src.rag.gerador import NUM_PREDICT_LIVRE
from src.rag.tradutor_consulta import FORA, detectar_pergunta_composta, deve_reforcar_apos_fora


def _sha(caminho: Path) -> str:
    resumo = hashlib.sha256()
    with caminho.open("rb") as ficheiro:
        for bloco in iter(lambda: ficheiro.read(1 << 20), b""):
            resumo.update(bloco)
    return resumo.hexdigest()


def testar_rollback() -> None:
    ativo = _RAIZ / "modelos" / "constituicao_vetorizada.pkl"
    bak = _RAIZ / "modelos" / "constituicao_vetorizada.pkl.bak_pre_33"
    arquivo = _RAIZ / "modelos" / "constituicao_vetorizada.pkl.ab_com_ponte"
    doc = _RAIZ / "relatorios" / "ablacao_ponte_leiga_fase33.md"
    if not doc.is_file():
        raise SystemExit("falta a documentação da ablação")
    if _sha(ativo) != _sha(bak):
        raise SystemExit("o pkl ativo não é igual ao backup")
    limpo = torch.load(ativo, weights_only=False)
    if "textos_busca" in limpo or len(limpo["textos"]) != 1772:
        raise SystemExit("o pkl ativo não voltou ao índice limpo")
    enriquecido = torch.load(arquivo, weights_only=False)
    busca = enriquecido.get("textos_busca")
    if not isinstance(busca, list) or len(busca) != 1772:
        raise SystemExit("o arquivo da ablação não tem 1772 textos de busca")
    diferentes = sum(1 for oficial, ampliado in zip(enriquecido["textos"], busca) if oficial != ampliado)
    if diferentes != 448:
        raise SystemExit("o arquivo da ablação não tem 448 chunks enriquecidos: {}".format(diferentes))
    for nome in (
        "modelos/ponte_leiga_cache.jsonl",
        "modelos/ponte_leiga_run.log",
        "benchmarks/resultados_bateria_cega_baseline_sem_ponte.jsonl",
        "relatorios/relatorio_bateria_cega_baseline_sem_ponte.md",
        "benchmarks/resultados_bateria_cega_com_ponte.jsonl",
        "relatorios/relatorio_bateria_cega_com_ponte.md",
    ):
        if not (_RAIZ / nome).is_file():
            raise SystemExit("arquivo da ablação ausente: {}".format(nome))


def testar_detector() -> None:
    frases = [
        ("O cidadão pode recorrer da decisão, e qual é o prazo?", True),
        ("A assembleia aprova o texto, e como se conta o quórum?", True),
        ("Quem propõe a norma? Quem a vota?", True),
        ("A norma vale para todos? Além disso, qual é a exceção?", True),
        ("A regra existe, porém quando ela se aplica?", True),
        ("O governo pode criar e cobrar imposto?", False),
        ("O que é habeas corpus e mandado de segurança?", False),
        ("Quem nomeia o ministro?", False),
    ]
    for frase, esperada in frases:
        obtida = detectar_pergunta_composta(frase)
        if obtida != esperada:
            raise SystemExit("detector: {!r} deu {} e o esperado era {}".format(frase, obtida, esperada))


def testar_fora() -> None:
    if not deve_reforcar_apos_fora(0.15, FORA):
        raise SystemExit("margem 0,15 com FORA_CF88 deveria reforçar")
    if not deve_reforcar_apos_fora(0.2, " fora_cf88 "):
        raise SystemExit("FORA_CF88 com margem alta deveria reforçar")
    if deve_reforcar_apos_fora(0.149, FORA):
        raise SystemExit("margem abaixo de 0,15 não deveria reforçar")
    if deve_reforcar_apos_fora(0.4, "imunidade tributária anterioridade"):
        raise SystemExit("frase constitucional não deveria reforçar")


def testar_artigo_id() -> None:
    caso = {"artigos": ["Art. 155"], "adct": False}
    registro = {
        "artigos_recuperados": [
            {
                "artigo_id": "Art. 156",
                "texto": "não compreendidos no art. 155, II, definidos em lei complementar",
                "child_ids": [],
            }
        ]
    }
    if _recuperou(caso, registro):
        raise SystemExit("menção de art. 155 dentro do Art. 156 não pode contar como recuperação")
    registro["artigos_recuperados"][0]["artigo_id"] = "Art. 155, I"
    if not _recuperou(caso, registro):
        raise SystemExit("o artigo_id Art. 155, I deveria contar")
    if NUM_PREDICT_LIVRE != 360:
        raise SystemExit("conversa livre deveria prever 360 tokens")


def main() -> None:
    testar_rollback()
    testar_detector()
    testar_fora()
    testar_artigo_id()
    print("ok rollback, detector, fora e artigo_id")


if __name__ == "__main__":
    main()
