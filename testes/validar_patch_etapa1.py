# -*- coding: utf-8 -*-
"""Confere o patch: escala do reranker, bloqueio do fora de escopo e três alvos."""

import re
import sys
import time
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(1, str(_RAIZ))

import pandas as pd

from src.rag.encoder import gerar_embedding
from src.rag.retriever import buscar_contexto
from src.roteador.servico_classificacao import avaliar_intencao

_CSV = Path(r"c:\Users\nicol\Downloads\dataset_teste_300_perguntas.csv")
_CORTES = (0.15, 0.20, 0.25, 0.30)
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


def main() -> None:
    tabela = pd.read_csv(_CSV, encoding="utf-8")
    fora = tabela.loc[tabela["intencao_esperada"].astype(str) == "Fora de Escopo"]
    constitucional = tabela.loc[tabela["intencao_esperada"].astype(str) != "Fora de Escopo"]
    obrigatorias = (
        "anonimato",
        "monopólio de mineração",
        "culto",
    )
    escolhidas = []
    textos_const = constitucional["texto"].astype(str).tolist()
    refs = constitucional["artigo_referencia"].astype(str).tolist()
    for marca in obrigatorias:
        for texto, ref in zip(textos_const, refs):
            if marca in texto.lower() or marca in texto:
                escolhidas.append((texto, ref))
                break
    for texto, ref in zip(textos_const, refs):
        if len(escolhidas) >= 15:
            break
        if all(texto != item[0] for item in escolhidas):
            escolhidas.append((texto, ref))
    escolhidas = escolhidas[:15]

    top1_fora = []
    duracoes = []
    for indice, texto in enumerate(fora["texto"].astype(str).tolist(), start=1):
        inicio = time.perf_counter()
        vetor = gerar_embedding(texto)
        avaliacao = avaliar_intencao(texto, embedding=vetor)
        busca = buscar_contexto(texto, avaliacao, embedding=vetor, limiar_reranker=0.0, top_k=1)
        duracoes.append(time.perf_counter() - inicio)
        nota = busca["resultados"][0]["score_reranker"] if busca["resultados"] else 0.0
        top1_fora.append(nota)
        print("fora {:02d}/{}  {:.3f}".format(indice, len(fora), nota), flush=True)

    print("Fora de escopo: {}".format(len(top1_fora)))
    print("Corte    bloqueio")
    for corte in _CORTES:
        bloqueio = sum(score < corte for score in top1_fora) / len(top1_fora)
        print("{:.2f}     {:.1%}".format(corte, bloqueio))

    hits1 = []
    hits5 = []
    for texto, ref in escolhidas:
        inicio = time.perf_counter()
        vetor = gerar_embedding(texto)
        avaliacao = avaliar_intencao(texto, embedding=vetor)
        busca = buscar_contexto(texto, avaliacao, embedding=vetor)
        duracoes.append(time.perf_counter() - inicio)
        ids = [item["artigo_id"] for item in busca["resultados"]]
        alvos = _alvos(ref)
        if not alvos:
            continue
        hits1.append(_bateu(alvos, ids[:1]))
        hits5.append(_bateu(alvos, ids[:5]))
    print()
    print("Constitucionais na amostra: {}".format(len(escolhidas)))
    print("Recall@1: {:.3f}".format(sum(hits1) / len(hits1)))
    print("Recall@5: {:.3f}".format(sum(hits5) / len(hits5)))

    controles = [
        ("Anonimato", "A Constituição garante a liberdade de manifestação do pensamento e proíbe o anonimato?", "Art. 5º, IV"),
        ("Mineração", "O Estado pode intervir na economia para criar um monopólio de mineração?", "Art. 173"),
        ("Templos", "A União, os Estados e os Municípios podem instituir impostos sobre templos de qualquer culto?", "Art. 150, VI"),
        ("Furto qualificado", "Qual é a pena prevista no Código Penal para o crime de furto qualificado?", None),
    ]
    print()
    for nome, pergunta, alvo in controles:
        inicio = time.perf_counter()
        vetor = gerar_embedding(pergunta)
        avaliacao = avaliar_intencao(pergunta, embedding=vetor)
        busca = buscar_contexto(pergunta, avaliacao, embedding=vetor, limiar_reranker=0.0, top_k=5)
        gasto = time.perf_counter() - inicio
        duracoes.append(gasto)
        passou = [item for item in busca["resultados"] if item["score_reranker"] >= 0.20]
        if alvo is None:
            acertou = "bloqueado" if not passou else "passou o corte"
        else:
            acertou = "sim" if _bateu([alvo], [item["artigo_id"] for item in passou]) else "não"
        print("{} | {} | {:.2f} s | {}".format(nome, busca["modo_busca"], gasto, acertou))
        if not busca["resultados"]:
            print("  sem score")
        else:
            print("  top-1 reranker {:.3f}  {}".format(busca["resultados"][0]["score_reranker"], busca["resultados"][0]["artigo_id"]))
            for item in busca["resultados"]:
                print("  {:.3f}  {}".format(item["score_reranker"], item["artigo_id"]))
    print()
    print("Tempo médio por consulta: {:.2f} s".format(sum(duracoes) / len(duracoes)))


if __name__ == "__main__":
    main()
