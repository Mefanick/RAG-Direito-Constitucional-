# -*- coding: utf-8 -*-
"""Avaliação cega das 300 perguntas com BGE-M3, BM25 e reranker. Sem LLM."""

import re
import sys
import time
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(1, str(_RAIZ))

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, classification_report, f1_score

from src.rag.encoder import gerar_embedding
from src.rag.retriever import diagnosticar_busca
from src.roteador.servico_classificacao import avaliar_intencao

_CSV = Path(r"c:\Users\nicol\Downloads\dataset_teste_300_perguntas.csv")
_LIMIARES_MARGEM = (0.10, 0.15, 0.20, 0.25, 0.30, 0.40)
_LIMIARES_RERANKER = (0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50)

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


def _recall(hits: list[bool]) -> float:
    return float(np.mean(hits)) if hits else 0.0


def _percentis(valores: np.ndarray) -> str:
    p10, p25, p50, p75, p90 = np.percentile(valores, [10, 25, 50, 75, 90])
    return "média {:.3f} | mediana {:.3f} | P10 {:.3f} | P25 {:.3f} | P50 {:.3f} | P75 {:.3f} | P90 {:.3f}".format(
        float(valores.mean()), float(np.median(valores)), p10, p25, p50, p75, p90
    )


def main() -> None:
    tabela = pd.read_csv(_CSV, encoding="utf-8")
    textos = tabela["texto"].astype(str).tolist()
    esperadas = tabela["intencao_esperada"].astype(str).tolist()
    referencias = tabela["artigo_referencia"].astype(str).tolist()
    constitucional = [i for i, rotulo in enumerate(esperadas) if rotulo != "Fora de Escopo"]
    fora = [i for i, rotulo in enumerate(esperadas) if rotulo == "Fora de Escopo"]

    registros = []
    encode_s = []
    hibrido_s = []
    rerank_s = []
    for numero, texto in enumerate(textos, start=1):
        if numero == 1 or numero % 25 == 0:
            print("Pergunta {}/{}".format(numero, len(textos)), flush=True)
        inicio_encode = time.perf_counter()
        vetor = gerar_embedding(texto)
        encode_s.append(time.perf_counter() - inicio_encode)
        avaliacao = avaliar_intencao(texto, embedding=vetor)
        diagnostico = diagnosticar_busca(texto, avaliacao, embedding=vetor)
        hibrido_s.append(diagnostico["tempo_hibrido_s"])
        rerank_s.append(diagnostico["tempo_reranker_s"])
        registros.append(avaliacao | diagnostico)

    y_true = [esperadas[i] for i in constitucional]
    y_pred = [registros[i]["intencao"] for i in constitucional]
    margens = [registros[i]["margem"] for i in constitucional]

    print()
    print("=" * 72)
    print("Bloco A — Roteador ({} perguntas constitucionais)".format(len(constitucional)))
    print("-" * 72)
    print("Acurácia: {:.3f}".format(accuracy_score(y_true, y_pred)))
    print("F1 macro: {:.3f}".format(f1_score(y_true, y_pred, average="macro", zero_division=0)))
    print(classification_report(y_true, y_pred, zero_division=0))
    print("Limiar   filtradas   acurácia no filtro")
    for limiar in _LIMIARES_MARGEM:
        mask = np.asarray(margens) >= limiar
        n_filtro = int(mask.sum())
        if n_filtro:
            acerto = accuracy_score(np.asarray(y_true)[mask], np.asarray(y_pred)[mask])
            texto_acerto = "{:.3f}".format(acerto)
        else:
            texto_acerto = "—"
        print("{:.2f}     {:4d}        {}".format(limiar, n_filtro, texto_acerto))

    def recalls(chave: str) -> tuple[float, float, float]:
        hits = {1: [], 3: [], 5: []}
        for indice in constitucional:
            alvos = _alvos(referencias[indice])
            if not alvos:
                continue
            ids = registros[indice][chave]
            for k in (1, 3, 5):
                hits[k].append(_bateu(alvos, ids[:k]))
        return _recall(hits[1]), _recall(hits[3]), _recall(hits[5])

    print()
    print("=" * 72)
    print("Bloco B — Ablação do retriever")
    print("-" * 72)
    for nome, chave in (
        ("1. Denso BGE-M3 global", "denso"),
        ("2. Híbrido BM25 + RRF + soft boost", "hibrido"),
        ("3. Pipeline com reranker", "reranker"),
    ):
        r1, r3, r5 = recalls(chave)
        print("{}".format(nome))
        print("  Recall@1 {:.3f} | Recall@3 {:.3f} | Recall@5 {:.3f}".format(r1, r3, r5))

    top_const = np.asarray([registros[i]["top1_reranker"] for i in constitucional])
    top_fora = np.asarray([registros[i]["top1_reranker"] for i in fora])
    print()
    print("=" * 72)
    print("Bloco C — Freio do reranker ({} constitucionais, {} fora)".format(len(constitucional), len(fora)))
    print("-" * 72)
    print("Top-1 constitucional: {}".format(_percentis(top_const)))
    print("Top-1 fora de escopo: {}".format(_percentis(top_fora)))
    print("Limiar   bloqueia fora   descarta constitucional")
    for corte in _LIMIARES_RERANKER:
        bloqueio = float(np.mean(top_fora < corte))
        descarte = float(np.mean(top_const < corte))
        print("{:.2f}      {:.1%}            {:.1%}".format(corte, bloqueio, descarte))

    criticos = [
        ("Anonimato", "A Constituição garante a liberdade de manifestação do pensamento e proíbe o anonimato?", "Art. 5º, IV"),
        ("Mineração", "O Estado pode intervir na economia para criar um monopólio de mineração?", "Art. 173"),
        ("Templos", "A União, os Estados e os Municípios podem instituir impostos sobre templos de qualquer culto?", "Art. 150, VI"),
        ("Furto qualificado", "Qual é a pena prevista no Código Penal para o crime de furto qualificado?", None),
    ]
    print()
    print("=" * 72)
    print("Bloco D — Casos de controle")
    print("-" * 72)
    for nome, pergunta, alvo in criticos:
        vetor = gerar_embedding(pergunta)
        avaliacao = avaliar_intencao(pergunta, embedding=vetor)
        diagnostico = diagnosticar_busca(pergunta, avaliacao, embedding=vetor)
        ids = diagnostico["reranker"]
        acertou = "fora de escopo" if alvo is None else ("sim" if _bateu([alvo], ids) else "não")
        print("{} | {} | margem {:.3f} | {}".format(nome, avaliacao["intencao"], avaliacao["margem"], diagnostico["modo"]))
        print("  alvo no top reranker: {} | top-1 reranker {:.3f}".format(acertou, diagnostico["top1_reranker"]))
        print("  top 5: {}".format(", ".join(ids) if ids else "(vazio)"))

    print()
    print(
        "Latência média: encode {:.1f} ms | híbrido {:.1f} ms | reranker {:.1f} ms | soma {:.1f} ms".format(
            float(np.mean(encode_s)) * 1000,
            float(np.mean(hibrido_s)) * 1000,
            float(np.mean(rerank_s)) * 1000,
            (float(np.mean(encode_s)) + float(np.mean(hibrido_s)) + float(np.mean(rerank_s))) * 1000,
        )
    )


if __name__ == "__main__":
    main()
