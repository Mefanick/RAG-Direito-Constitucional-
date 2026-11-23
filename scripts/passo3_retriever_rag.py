# -*- coding: utf-8 -*-
"""Demonstração fina do RAG já modularizado.

A classificação vive em src.roteador. A busca vive em src.rag. Este
ficheiro só faz a pergunta e imprime o prompt. Não carrega SVM nem
recalcula os embeddings da Constituição.
"""

import sys
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(1, str(_RAIZ))

from src.rag.encoder import gerar_embedding
from src.rag.retriever import buscar_contexto
from src.roteador.servico_classificacao import avaliar_intencao

duvida = "O Estado pode intervir na economia para criar um monopólio de mineração?"
vetor = gerar_embedding(duvida)
avaliacao = avaliar_intencao(duvida, embedding=vetor)
contexto = buscar_contexto(duvida, avaliacao, embedding=vetor)

print("Intenção: {}".format(avaliacao["intencao"]))
print("Confiança alta: {} | margem {:.4f}".format(avaliacao["confianca_alta"], avaliacao["margem"]))
print("Modo de busca: {}".format(contexto["modo_busca"]))
print()
print(
    "Instrução: Responda à dúvida do utilizador utilizando ESTRITAMENTE "
    "o contexto jurídico abaixo. Não invente leis."
)
print("Contexto Recuperado:")
for posicao, item in enumerate(contexto["resultados"], start=1):
    print("[Artigo {}] {} ({:.3f})".format(posicao, item["artigo_id"], item["score_cosseno"]))
    print(item["texto"])
    print()
print("Pergunta do Utilizador: {}".format(duvida))
