# -*- coding: utf-8 -*-
"""Bateria ponta a ponta do RAG constitucional.

Mede o tempo de executar_rag, mostra o roteamento, um excerto dos
artigos e a resposta do LLM. Se o servidor local estiver desligado,
o gerador devolve um aviso e a bateria segue.
"""

import sys
import time
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(1, str(_RAIZ))

from src.rag.pipeline import executar_rag

CASOS_DE_TESTE = [
    {
        "cenario": "Cenário 1 — Rota Direta (Direitos Fundamentais)",
        "pergunta": "A Constituição garante a liberdade de manifestação do pensamento e proíbe o anonimato?",
    },
    {
        "cenario": "Cenário 2 — Benchmark de Fallback (Ordem Econômica)",
        "pergunta": "O Estado pode intervir na economia para criar um monopólio de mineração?",
    },
    {
        "cenario": "Cenário 3 — Pergunta Curta/Ambígua (Estresse do Roteador)",
        "pergunta": "Quem pode propor emenda à Constituição?",
    },
    {
        "cenario": "Cenário 4 — Pegadinha Fora de Escopo (Teste Anti-Alucinação)",
        "pergunta": "Qual é a pena prevista no Código Penal para o crime de furto qualificado?",
    },
]


def _excerto(texto, limite=200):
    """Primeiros caracteres do artigo, numa linha só, para o terminal caber."""
    limpo = " ".join(str(texto).split())
    if len(limpo) <= limite:
        return limpo
    return limpo[:limite] + "..."


def _imprimir_caso(caso, trace, segundos):
    roteamento = trace.get("roteamento") or {}
    confianca_alta = roteamento.get("confianca_alta")
    confianca = "confiança alta" if confianca_alta else "fallback ativado"
    margem = roteamento.get("margem")
    limiar = roteamento.get("limiar")

    print("=" * 72)
    print(caso["cenario"])
    print("Pergunta: {}".format(caso["pergunta"]))
    print("-" * 72)
    print("Roteamento: {} | {}".format(roteamento.get("intencao", "(ausente)"), confianca))
    if margem is not None:
        if limiar is not None:
            print("Margem: {:.4f} | limiar: {:.2f}".format(margem, limiar))
        else:
            print("Margem: {:.4f}".format(margem))
    print("Modo de busca: {}".format(trace.get("modo_busca", "(ausente)")))

    print("Retriever (Top Artigos):")
    artigos = trace.get("artigos_recuperados") or []
    if not artigos:
        print("  (nenhum artigo acima do corte do reranker)")
    for indice, artigo in enumerate(artigos, start=1):
        if isinstance(artigo, dict):
            print(
                "  {}. {} | cosseno {:.3f} | reranker {:.3f} | {}".format(
                    indice,
                    artigo.get("artigo_id", "?"),
                    float(artigo.get("score_cosseno", 0.0)),
                    float(artigo.get("score_reranker", 0.0)),
                    _excerto(artigo.get("texto", "")),
                )
            )
        else:
            print("  {}. {}".format(indice, _excerto(artigo)))

    print("Gerador (LLM):")
    if trace.get("erro_llm"):
        print("Erro: {}".format(trace["erro_llm"]))
    print(trace.get("resposta_llm") or "")
    from auditoria_ponta_a_ponta import auditar_citacoes

    auditoria = auditar_citacoes(trace.get("resposta_llm") or "", artigos)
    estado = "alucinada" if auditoria["citacao_alucinada"] else "fiel"
    print("Checagem de citação: {}".format(estado))
    if auditoria["inventadas"]:
        print("Artigos inventados: {}".format(", ".join(auditoria["inventadas"])))
    if trace.get("modelo_usado"):
        print(
            "Modelo: {} | tokens prompt {} | tokens resposta {}".format(
                trace.get("modelo_usado"),
                trace.get("tokens_prompt"),
                trace.get("tokens_resposta"),
            )
        )
    tempos = trace.get("tempos_s") or {}
    if tempos:
        print(
            "Tempos (s): roteador {:.2f} | retriever {:.2f} | gerador {:.2f} | total {:.2f}".format(
                tempos.get("roteador", 0.0),
                tempos.get("retriever", 0.0),
                tempos.get("gerador", 0.0),
                tempos.get("total", segundos),
            )
        )
    print("Performance da consulta: {:.2f} s".format(segundos))
    print()


def main():
    from src.rag.servidor_llm import garantir_servidor

    estado = garantir_servidor()
    print("LLM: {} | modelo {}".format(estado.get("origem"), estado.get("model") or "(nenhum)"))
    if estado.get("url"):
        print("LLM_URL: {}".format(estado["url"]))
    elif estado.get("comando"):
        print("Servidor ausente. Para subir um modelo à mão:")
        print(estado["comando"])

    duracoes = []
    for caso in CASOS_DE_TESTE:
        inicio = time.perf_counter()
        trace = executar_rag(caso["pergunta"])
        segundos = time.perf_counter() - inicio
        duracoes.append(segundos)
        _imprimir_caso(caso, trace, segundos)

    total = sum(duracoes)
    media = total / len(duracoes) if duracoes else 0.0
    print("=" * 72)
    print("Resumo da bateria")
    print("-" * 72)
    print("Consultas: {}".format(len(duracoes)))
    print("Tempo total: {:.2f} s".format(total))
    print("Tempo médio por consulta: {:.2f} s".format(media))


if __name__ == "__main__":
    main()
