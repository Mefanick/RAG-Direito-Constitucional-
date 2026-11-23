# -*- coding: utf-8 -*-
"""Sanidade do índice constitucional: cobertura e o inciso do anonimato."""

import sys
from pathlib import Path

import torch
from sentence_transformers import SentenceTransformer, util

_RAIZ = Path(__file__).resolve().parents[1]
CAMINHO = _RAIZ / "modelos" / "constituicao_vetorizada.pkl"
MODELO = "paraphrase-multilingual-MiniLM-L12-v2"
ANTES = 217

PERGUNTAS = [
    (
        "A Constituição garante a liberdade de manifestação do pensamento e proíbe o anonimato?",
        "Art. 5º, IV",
    ),
    (
        "A União, os Estados e os Municípios podem instituir impostos sobre templos de qualquer culto?",
        "Art. 150",
    ),
]


def _top3(pontuacoes, artigo_ids, textos):
    ordem = sorted(
        ((int(i), float(pontuacoes[i])) for i in range(int(pontuacoes.shape[0]))),
        key=lambda par: par[1],
        reverse=True,
    )[:3]
    linhas = []
    for posicao, score in ordem:
        trecho = " ".join(textos[posicao].split())
        if len(trecho) > 150:
            trecho = trecho[:150] + "..."
        linhas.append((artigo_ids[posicao], score, trecho))
    return linhas


def main():
    cache = torch.load(CAMINHO, weights_only=False)
    artigo_ids = list(cache["artigo_ids"])
    textos = list(cache["textos"])
    intencoes = list(cache["intencoes"])
    embeddings = cache["embeddings"]
    if not isinstance(embeddings, torch.Tensor):
        embeddings = torch.as_tensor(embeddings)

    print("Chunks agora: {}".format(len(textos)))
    print("Chunks antes: {}".format(ANTES))
    print("Forma dos embeddings: {}".format(tuple(embeddings.shape)))
    print("Intenções: {}".format(", ".join(sorted(set(intencoes)))))
    print("Art. 5º, IV no índice: {}".format("Art. 5º, IV" in artigo_ids))
    print("Art. 150 no índice: {}".format(any(i.startswith("Art. 150") for i in artigo_ids)))
    print()

    modelo = SentenceTransformer(MODELO)
    for pergunta, alvo in PERGUNTAS:
        vetor = modelo.encode(pergunta, convert_to_tensor=True, show_progress_bar=False)
        pontuacoes = util.cos_sim(vetor, embeddings)[0]
        topo = _top3(pontuacoes, artigo_ids, textos)
        acertou = any(alvo in ident for ident, _, _ in topo)
        print("=" * 72)
        print(pergunta)
        print("Alvo: {} | no top 3: {}".format(alvo, "sim" if acertou else "não"))
        print("-" * 72)
        for ident, score, trecho in topo:
            print("{:.3f}  {}".format(score, ident))
            print("       {}".format(trecho))
        print()


if __name__ == "__main__":
    main()
