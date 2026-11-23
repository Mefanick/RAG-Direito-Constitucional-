# -*- coding: utf-8 -*-
"""Orquestrador. Pergunta simples faz uma busca. Pergunta composta parte o enunciado.

A segunda passagem só entra se a primeira ficou abaixo de 0,25 ou se a
fala é uma continuação curta. O gerador é sempre chamado.
"""

import os
import sys
import time

import torch
from pathlib import Path
from typing import Callable

_RAIZ = Path(__file__).resolve().parents[2]
if str(_RAIZ) not in sys.path:
    sys.path.insert(0, str(_RAIZ))

from src.rag.atalho_conversacional import detectar_atalho_trivial
from src.rag.catalogo_modelos import modelo_suporta_think, preparar_modelo, validar_modelo
from src.rag.auditor_citacoes import auditar_citacoes
from src.rag.checkpoints import registrar
from src.rag.encoder import gerar_embedding, max_length_reranker, reordenar_pares
from src.rag.gerador import (
    configuracao_servidor,
    gerar_resposta,
    montar_prompt,
    plano_geracao,
    prefixar_aviso_livre,
)
from src.rag.retriever import buscar_contexto, deduplicar_chunks, fundir_subconsultas
from src.rag.tradutor_consulta import (
    decompor_consulta,
    detectar_pergunta_composta,
    rejeitar_hyde_por_drift,
    traduzir_para_juridico,
)
from src.roteador.servico_classificacao import avaliar_intencao

_MARCAS_CONTINUACAO = (
    "e se",
    "mas",
    "isso",
    "ela",
    "ele",
    "nesse",
    "nessa",
    "então",
    "entao",
    "esse",
    "essa",
    "aquele",
    "aquela",
)


def _continuacao_curta(pergunta: str, historico: list[dict] | None) -> bool:
    if not historico:
        return False
    if len(pergunta.split()) > 8:
        return False
    baixo = pergunta.lower()
    return any(marca in baixo for marca in _MARCAS_CONTINUACAO)


def modo_pelo_topo(score: float) -> str:
    if score < 0.12:
        return "MODO_CONVERSA_LIVRE"
    if score < 0.25:
        return "MODO_RAG_ZONA_CINZENTA"
    return "MODO_RAG_ALTA_CONFIANCA"


def _ids_artigo(item: dict) -> set[str]:
    ids = {str(item.get("artigo_id") or "").strip()}
    for filho in item.get("child_ids") or []:
        ids.add(str(filho).strip())
    ids.discard("")
    return ids


def fundir_top1_p1(
    artigos_p2: list,
    chunk_p1: dict | None,
    top1_p1: float,
    top1_p2: float,
) -> tuple[list, bool]:
    """Mantém o top-1 literal da zona cinzenta quando a 2ª passagem vence.

    Só quando a 2ª passagem vence e ainda está na zona cinzenta.
    Alta confiança não recebe o top-1 fraco da 1ª. Abaixo de 0,12 nada entra.
    O chunk preservado não é
    expandido em documento pai, então continua dentro do teto já usado
    na montagem de cada dispositivo.
    """
    artigos = [item for item in (artigos_p2 or []) if isinstance(item, dict)]
    if (
        float(top1_p2) >= 0.25
        or float(top1_p2) < 0.12
        or float(top1_p1) < 0.12
        or float(top1_p2) < float(top1_p1)
    ):
        return artigos, False
    if not isinstance(chunk_p1, dict):
        return artigos, False
    alvo = str(chunk_p1.get("artigo_id") or "").strip()
    texto = str(chunk_p1.get("texto") or "").strip()
    if not alvo or not texto or len(texto) > 2200:
        return artigos, False
    presentes: set[str] = set()
    for item in artigos:
        presentes.update(_ids_artigo(item))
    if alvo in presentes:
        return artigos, False
    preservado = dict(chunk_p1)
    preservado["artigo_id"] = alvo
    preservado["texto"] = texto
    preservado["origem"] = "fusao_p1"
    return artigos + [preservado], True


def _tabela(candidatos: list[dict]) -> list[str]:
    if not candidatos:
        return ["(sem candidatos)"]
    linhas = []
    for item in candidatos[:5]:
        sub = str(item.get("subconsulta") or "-")
        idx = item.get("chunk_idx")
        linhas.append(
            "idx {:>5}  {:<22} cosseno {:5.3f}  reranker {:5.3f}  sub {:<16} {}".format(
                "-" if idx is None else idx,
                str(item.get("artigo_id"))[:22],
                float(item.get("score_cosseno") or 0.0),
                float(item.get("score_reranker") or 0.0),
                sub[:16],
                item.get("status", ""),
            )
        )
    return linhas


def _sem_vetor(busca: dict) -> dict:
    copia = dict(busca)
    copia.pop("cossenos", None)
    return copia


def _medir_drift_hyde(pergunta: str, hyde: str, embedding_pergunta: torch.Tensor) -> tuple[float, float]:
    """Cosseno BGE-M3 e sigmoide do reranker entre a pergunta e a reescrita."""
    vetor_hyde = gerar_embedding(hyde, convert_to_tensor=True).float().view(-1)
    vetor_pergunta = embedding_pergunta.float().view(-1)
    cosseno = float(torch.dot(vetor_pergunta, vetor_hyde) / (vetor_pergunta.norm() * vetor_hyde.norm()))
    return cosseno, float(reordenar_pares(pergunta, [hyde])[0])


def _responder_llm_puro(
    pergunta: str,
    modelo: str,
    usar_think: bool,
    inicio: float,
    stream: bool,
    on_token,
    etapa,
    gerar: bool,
    cache_status: str,
) -> dict:
    """Uma chamada ao modelo, sem busca, sem auditoria e sem turnos anteriores."""
    registrar(
        "1/6",
        "ENTRADA",
        [
            pergunta,
            "histórico: ignorado (stateless)",
            "modelo: {}".format(modelo),
            "usar_rag: False",
            "usar_think: {}".format(bool(usar_think)),
            "cache: {}".format(cache_status),
        ],
    )
    etapa("Consultando o modelo, sem busca na Constituição...")
    if not gerar:
        geracao = {
            "resposta": "",
            "raciocinio": None,
            "modelo_usado": modelo,
            "tokens_prompt": None,
            "tokens_resposta": None,
            "erro": None,
            "ttft_s": None,
            "think_s": 0.0,
            "think_chars": 0,
            "prefill_s": None,
            "eval_s": None,
            "tok_s": None,
        }
        tempo_gerador = 0.0
    else:
        t0 = time.perf_counter()
        geracao = gerar_resposta(
            pergunta,
            [],
            stream=stream,
            on_token=on_token,
            historico=[],
            modo="MODO_LLM_PURO",
            on_etapa=etapa,
            usar_think=usar_think,
            modelo=modelo,
        )
        tempo_gerador = time.perf_counter() - t0
    total = time.perf_counter() - inicio
    return {
        "pergunta": pergunta,
        "roteamento": {},
        "modo_busca": "llm_puro",
        "classe_consulta": "SIMPLES",
        "subconsultas": [],
        "modo_resposta": "MODO_LLM_PURO",
        "modo_rag": "MODO_LLM_PURO",
        "consulta_traduzida": None,
        "query_traduzida": None,
        "tradutor": None,
        "passagem": 0,
        "top1_score_bruto_p1": None,
        "top1_score_bruto_p2": None,
        "hyde_cosseno": None,
        "hyde_reranker": None,
        "hyde_rejeitado_por_drift": False,
        "hyde_copiou_exemplo": False,
        "fusao_p1_p2_aplicada": False,
        "usar_think": bool(geracao.get("usar_think", usar_think)),
        "think_chars": geracao.get("think_chars") or 0,
        "think_s": geracao.get("think_s") if geracao.get("think_s") is not None else 0.0,
        "artigos_recuperados": [],
        "top_candidatos_brutos": [],
        "top1_score": None,
        "resposta_llm": geracao.get("resposta") or "",
        "raciocinio_llm": geracao.get("raciocinio"),
        "modelo_usado": geracao.get("modelo_usado") or modelo,
        "tokens_prompt": geracao.get("tokens_prompt"),
        "tokens_resposta": geracao.get("tokens_resposta"),
        "erro_llm": geracao.get("erro"),
        "ttft_s": geracao.get("ttft_s"),
        "tok_s": geracao.get("tok_s"),
        "prefill_s": geracao.get("prefill_s"),
        "eval_s": geracao.get("eval_s"),
        "auditoria": None,
        "temperature": 0.1,
        "num_ctx": 2048,
        "num_predict": 1200 if usar_think else 450,
        "think": bool(usar_think),
        "estourou_no_think": bool(geracao.get("estourou_no_think")),
        "tempo_thinking_s": geracao.get("think_s") if geracao.get("think_s") is not None else 0.0,
        "cache": False,
        "duplicatas_removidas": 0,
        "prompt_chars": None,
        "tempos_s": {
            "roteador": 0.0,
            "retriever": 0.0,
            "tradutor": 0.0,
            "gerador": tempo_gerador,
            "total": total,
        },
    }


def executar_rag(
    pergunta: str,
    historico: list[dict] | None = None,
    stream: bool = False,
    on_token: Callable | None = None,
    on_etapa: Callable | None = None,
    cache_status: str = "DESLIGADO",
    simular_offline: bool = False,
    modo_raciocinio: str = "desligado",
    gerar: bool = True,
    usar_think: bool = False,
    modelo: str | None = None,
    usar_rag: bool = True,
) -> dict:
    """Classifica, busca e traduz se precisar. gerar=False para antes do qwen3:8b."""
    if pergunta is None or not str(pergunta).strip():
        raise ValueError("A pergunta do RAG está vazia.")

    def etapa(rotulo: str) -> None:
        if on_etapa is not None:
            on_etapa(rotulo)

    pergunta_limpa = str(pergunta).strip()
    # Cada pergunta é stateless. O campo historico fica na assinatura e é descartado.
    del historico
    historico = []
    modelo_escolhido = validar_modelo(modelo)
    if usar_think and not modelo_suporta_think(modelo_escolhido):
        usar_think = False
    preparar_modelo(modelo_escolhido)
    inicio = time.perf_counter()
    if not usar_rag:
        return _responder_llm_puro(
            pergunta_limpa,
            modelo_escolhido,
            usar_think,
            inicio,
            stream,
            on_token,
            etapa,
            gerar,
            cache_status,
        )
    registrar(
        "1/6",
        "ENTRADA",
        [
            pergunta_limpa,
            "histórico: ignorado (stateless)",
            "modelo: {}".format(modelo_escolhido),
            "usar_rag: {}".format(bool(usar_rag)),
            "usar_think: {}".format(bool(usar_think)),
            "cache: {}".format(cache_status),
        ],
    )
    atalho = detectar_atalho_trivial(pergunta_limpa, historico)
    if atalho:
        decorrido = time.perf_counter() - inicio
        registrar(
            "1B",
            "ATALHO SOCIAL",
            ["tipo: {}".format(atalho["tipo"]), "Pipeline RAG e LLM pulados", "0.00 s"],
            decorrido,
        )
        return {
            "pergunta": pergunta_limpa,
            "roteamento": {},
            "modo_busca": "atalho_social",
            "classe_consulta": "SIMPLES",
            "subconsultas": [],
            "modo_resposta": "MODO_ATALHO_SOCIAL",
            "modo_rag": "MODO_ATALHO_SOCIAL",
            "consulta_traduzida": None,
            "query_traduzida": None,
            "tradutor": None,
            "passagem": 0,
            "top1_score_bruto_p1": 0.0,
            "top1_score_bruto_p2": None,
            "hyde_cosseno": None,
            "hyde_reranker": None,
            "hyde_rejeitado_por_drift": False,
            "hyde_copiou_exemplo": False,
            "fusao_p1_p2_aplicada": False,
            "usar_think": False,
            "think_chars": 0,
            "think_s": 0.0,
            "artigos_recuperados": [],
            "top_candidatos_brutos": [],
            "top1_score": 0.0,
            "resposta_llm": atalho["resposta"],
            "raciocinio_llm": None,
            "modelo_usado": None,
            "tokens_prompt": 0,
            "tokens_resposta": 0,
            "erro_llm": None,
            "ttft_s": 0.0,
            "tok_s": None,
            "prefill_s": 0.0,
            "eval_s": 0.0,
            "auditoria": {
                "status": "SEM_CITACAO",
                "artigos_citados": [],
                "subdispositivos_citados": [],
                "artigos_inventados": [],
                "subdispositivos_nao_confirmados": [],
                "citacao_alucinada": False,
                "citacoes": [],
                "inventadas": [],
                "recuperados": [],
            },
            "temperature": None,
            "num_ctx": None,
            "num_predict": 0,
            "think": False,
            "tempo_thinking_s": 0.0,
            "duplicatas_removidas": 0,
            "prompt_chars": 0,
            "cache": False,
            "tempos_s": {
                "roteador": 0.0,
                "retriever": 0.0,
                "tradutor": 0.0,
                "gerador": 0.0,
                "total": decorrido,
            },
        }

    classe = "COMPOSTA" if detectar_pergunta_composta(pergunta_limpa) else "SIMPLES"
    etapa("Classificando intenção...")
    t0 = time.perf_counter()
    embedding = gerar_embedding(pergunta_limpa, convert_to_tensor=True)
    roteamento = avaliar_intencao(pergunta_limpa, embedding=embedding)
    tempo_roteador = time.perf_counter() - t0
    modo_busca = "densa_com_boost" if roteamento.get("confianca_alta") else "densa_global"
    registrar(
        "2/6",
        "ANALISE + ROTEADOR",
        [
            "classe: {}".format(classe),
            "intenção: {}".format(roteamento.get("intencao")),
            "prob_top1: {:.3f}  margem: {:.3f}".format(
                float(roteamento.get("prob_top1") or 0.0),
                float(roteamento.get("margem") or 0.0),
            ),
            "modo_busca: {}".format(modo_busca),
        ],
        tempo_roteador,
    )

    etapa("Buscando artigos na CF/88...")
    t1 = time.perf_counter()

    def ao_reranquear() -> None:
        etapa("Reordenando relevância...")

    subconsultas: list[str] = []
    if classe == "COMPOSTA":
        etapa("Partindo a pergunta composta...")
        subconsultas = decompor_consulta(pergunta_limpa, historico, modelo_escolhido)

    if len(subconsultas) >= 2:
        buscas = []
        for sub in subconsultas:
            vetor = gerar_embedding(sub, convert_to_tensor=True)
            rota = avaliar_intencao(sub, embedding=vetor)
            buscas.append(
                buscar_contexto(
                    sub,
                    rota,
                    embedding=vetor,
                    ao_reranquear=ao_reranquear,
                    subconsulta=sub,
                    anexar_irmaos=False,
                )
            )
        busca = fundir_subconsultas(buscas, subconsultas)
        for item in buscas:
            item.pop("cossenos", None)
    else:
        subconsultas = []
        busca = _sem_vetor(
            buscar_contexto(
                pergunta_limpa,
                roteamento,
                embedding=embedding,
                ao_reranquear=ao_reranquear,
                composta=classe == "COMPOSTA",
            )
        )
    tempo_busca_1 = time.perf_counter() - t1
    top1 = float(busca.get("top1_score") or 0.0)
    top1_passagem_1 = top1
    brutos_p1 = busca.get("top_candidatos_brutos") or []
    chunk_top1_p1 = brutos_p1[0] if brutos_p1 else None
    linhas_busca = [
        "reranker max_length: {}".format(max_length_reranker()),
        "multi-query: {}".format("sim" if busca.get("modo_busca") == "multi_query" else "não"),
    ]
    if busca.get("modo_busca") == "multi_query":
        for indice, sub in enumerate(subconsultas, start=1):
            linhas_busca.append("sub {}: {}".format(indice, sub))
        linhas_busca.extend("melhor: {}".format(linha) for linha in busca.get("melhores_sub") or [])
    elif classe == "COMPOSTA":
        linhas_busca.append("decomposição insuficiente; busca única com teto 8")
    linhas_busca.extend(_tabela(busca.get("top_candidatos_brutos") or []))
    registrar("3/6", "BUSCA PASSAGEM 1", linhas_busca, tempo_busca_1)

    continuacao = _continuacao_curta(pergunta_limpa, historico)
    consulta_traduzida = None
    tempo_tradutor = 0.0
    tempo_busca_2 = 0.0
    passagem = 1
    top1_bruto_p2 = None
    hyde_cosseno = None
    hyde_reranker = None
    hyde_rejeitado = False
    hyde_copiou = False
    fusao_aplicada = False
    if top1 >= 0.25 and not continuacao:
        registrar("4/6", "TRADUTOR + PASSAGEM 2", ["PULADO (score inicial suficiente)"])
    else:
        motivos = []
        if top1 < 0.25:
            motivos.append("score < 0.25")
        if continuacao:
            motivos.append("continuacao_curta")
        t2 = time.perf_counter()
        consulta_traduzida, hyde_copiou = traduzir_para_juridico(
            pergunta_limpa, historico, modelo=modelo_escolhido
        )
        tempo_tradutor = time.perf_counter() - t2
        detalhe = ["motivo: {}".format(" e ".join(motivos)), "tradutor: {}".format(consulta_traduzida or "(vazio)")]
        if consulta_traduzida:
            hyde_cosseno, hyde_reranker = _medir_drift_hyde(pergunta_limpa, consulta_traduzida, embedding)
            hyde_rejeitado = rejeitar_hyde_por_drift(hyde_cosseno, hyde_reranker)
            detalhe.append("hyde_cosseno: {:.3f}".format(hyde_cosseno))
            detalhe.append("hyde_reranker: {:.3f}".format(hyde_reranker))
            detalhe.append("drift: {}".format("rejeitado" if hyde_rejeitado else "aceito"))
        if not consulta_traduzida or hyde_rejeitado:
            detalhe.append("2ª busca não executada")
            registrar("4/6", "TRADUTOR + PASSAGEM 2", detalhe, tempo_tradutor)
        else:
            etapa("Buscando de novo com a frase jurídica...")
            t3 = time.perf_counter()
            embedding_2 = gerar_embedding(consulta_traduzida, convert_to_tensor=True)
            roteamento_2 = avaliar_intencao(consulta_traduzida, embedding=embedding_2)
            busca_2 = _sem_vetor(
                buscar_contexto(consulta_traduzida, roteamento_2, embedding=embedding_2, composta=False)
            )
            tempo_busca_2 = time.perf_counter() - t3
            top2 = float(busca_2.get("top1_score") or 0.0)
            top1_bruto_p2 = top2
            if top2 > top1:
                busca = busca_2
                roteamento = roteamento_2
                top1 = top2
                passagem = 2
                modo_busca = busca.get("modo_busca") or modo_busca
            detalhe.append("tempo do tradutor: {:.2f} s".format(tempo_tradutor))
            detalhe.append("passagem escolhida: {}".format(passagem))
            detalhe.extend(_tabela(busca_2.get("top_candidatos_brutos") or []))
            registrar("4/6", "TRADUTOR + PASSAGEM 2", detalhe, tempo_tradutor + tempo_busca_2)

    modo = modo_pelo_topo(top1)
    if modo == "MODO_CONVERSA_LIVRE":
        artigos = []
    elif modo == "MODO_RAG_ZONA_CINZENTA":
        artigos = list(busca.get("top_candidatos_brutos") or [])[:3]
    else:
        artigos = list(busca.get("resultados") or [])
    if passagem == 2 and top1_bruto_p2 is not None:
        artigos, fusao_aplicada = fundir_top1_p1(artigos, chunk_top1_p1, top1_passagem_1, top1_bruto_p2)

    ja_limpos = modo == "MODO_RAG_ALTA_CONFIANCA"
    artigos, extra_removidas = deduplicar_chunks(artigos)
    removidas = (int(busca.get("duplicatas_removidas") or 0) if ja_limpos else 0) + extra_removidas
    previa = montar_prompt(pergunta_limpa, artigos, modo, historico)
    prompt_chars = sum(len(str(item.get("content") or "")) for item in previa)
    url, modelo = configuracao_servidor()
    plano = plano_geracao(modo, classe == "COMPOSTA", modelo, modo_raciocinio, usar_think=usar_think)
    irmaos = sum(1 for item in artigos if item.get("origem") == "irmao_adjacente")
    registrar(
        "5/6",
        "DECISAO + CONTEXTO",
        [
            "modo: {}".format(modo),
            "fusao_p1_p2: {}".format("sim" if fusao_aplicada else "não"),
            "chunks_enviados: {} (irmãos adjacentes: {})".format(len(artigos), irmaos),
            "parent_document: {} documento(s), {} filho(s) consolidado(s)".format(
                sum(1 for item in artigos if item.get("origem") == "parent_document"),
                sum(int(item.get("filhos") or 0) for item in artigos if item.get("origem") == "parent_document"),
            ),
            "duplicatas_removidas: {}".format(removidas),
            "prompt_chars: {}".format(prompt_chars),
            "LLM_MODEL: {}".format(modelo),
            "LLM_URL: {}".format(url),
            "temperature: {}".format(plano["temperature"]),
            "num_ctx: {}".format(plano["num_ctx"]),
            "num_predict: {}".format(plano["num_predict"]),
            "think: {}".format(plano["think"]),
            "modo_raciocinio: {}".format(plano["modo_raciocinio"]),
        ],
    )

    if not gerar:
        geracao = {
            "resposta": "",
            "raciocinio": None,
            "modelo_usado": None,
            "tokens_prompt": None,
            "tokens_resposta": None,
            "erro": None,
            "ttft_s": None,
            "tempo_thinking_s": None,
            "prefill_s": None,
            "eval_s": None,
            "tokens_entrada": None,
        }
        resposta_final = ""
        auditoria = None
        tok_s = None
        tempo_gerador = 0.0
        total = time.perf_counter() - inicio
        registrar("6/6", "GERADOR LLM", ["pulado pelo modo so-retriever", "total_s: {:.2f} s".format(total)], 0.0)
    else:
        etapa("Redigindo resposta...")
        anterior = os.environ.get("LLM_URL")
        if simular_offline:
            os.environ["LLM_URL"] = "http://127.0.0.1:9/api/chat"
        t4 = time.perf_counter()
        try:
            geracao = gerar_resposta(
                pergunta_limpa,
                artigos,
                stream=stream,
                on_token=on_token,
                historico=[],
                modo=modo,
                composta=classe == "COMPOSTA",
                num_predict=plano["num_predict"],
                num_ctx=plano["num_ctx"],
                on_etapa=etapa,
                think=plano["think"],
                usar_think=usar_think,
                modelo=modelo_escolhido,
            )
        finally:
            if simular_offline:
                if anterior:
                    os.environ["LLM_URL"] = anterior
                else:
                    os.environ.pop("LLM_URL", None)
        tempo_gerador = time.perf_counter() - t4
        total = time.perf_counter() - inicio
        resposta_final = geracao.get("resposta") or ""
        if modo == "MODO_CONVERSA_LIVRE":
            resposta_final = prefixar_aviso_livre(resposta_final)
        auditoria = auditar_citacoes(resposta_final, artigos)
        tok_s = geracao.get("tok_s")
        if tok_s is None and geracao.get("tokens_resposta") and geracao.get("eval_s"):
            tok_s = geracao["tokens_resposta"] / geracao["eval_s"]
        registrar(
            "6/6",
            "GERADOR LLM",
            [
                "status: {}".format(geracao.get("erro") or "ok"),
                "tempo_thinking_s: {}".format(
                    "n/d" if geracao.get("tempo_thinking_s") is None else "{:.2f} s".format(geracao["tempo_thinking_s"])
                ),
                "prefill_s: {}".format(
                    "n/d" if geracao.get("prefill_s") is None else "{:.2f} s".format(geracao["prefill_s"])
                ),
                "tokens_entrada: {}".format(
                    "n/d" if geracao.get("tokens_entrada") is None else geracao["tokens_entrada"]
                ),
                "ttft_s: {}".format("n/d" if geracao.get("ttft_s") is None else "{:.2f} s".format(geracao["ttft_s"])),
                "geracao_s: {:.2f} s".format(tempo_gerador),
                "tok/s: {}".format("n/d" if tok_s is None else "{:.1f}".format(tok_s)),
                "total_s: {:.2f} s".format(total),
                "auditar_citacoes: status={} artigos_inventados={} subdispositivos_nao_confirmados={}".format(
                    auditoria.get("status"),
                    auditoria.get("artigos_inventados"),
                    auditoria.get("subdispositivos_nao_confirmados"),
                ),
            ],
            tempo_gerador,
        )
    busca.pop("cossenos", None)

    def _publico(item: dict) -> dict:
        copia = dict(item)
        copia.pop("_indice", None)
        copia.pop("cossenos", None)
        return copia

    artigos = [_publico(item) if isinstance(item, dict) else item for item in artigos]
    brutos_publicos = [_publico(item) for item in (busca.get("top_candidatos_brutos") or [])]
    return {
        "pergunta": pergunta_limpa,
        "roteamento": roteamento,
        "modo_busca": busca.get("modo_busca"),
        "classe_consulta": classe,
        "subconsultas": subconsultas,
        "modo_resposta": modo,
        "modo_rag": modo,
        "consulta_traduzida": consulta_traduzida or None,
        "query_traduzida": consulta_traduzida,
        "tradutor": consulta_traduzida,
        "passagem": passagem,
        "top1_score_bruto_p1": top1_passagem_1,
        "top1_score_bruto_p2": top1_bruto_p2,
        "hyde_cosseno": hyde_cosseno,
        "hyde_reranker": hyde_reranker,
        "hyde_rejeitado_por_drift": hyde_rejeitado or (not consulta_traduzida and hyde_copiou),
        "hyde_copiou_exemplo": hyde_copiou,
        "fusao_p1_p2_aplicada": fusao_aplicada,
        "usar_think": bool(plano["think"]),
        "think_chars": 0 if not plano["think"] else int(geracao.get("think_chars") or 0),
        "think_s": 0.0 if not plano["think"] else geracao.get("think_s"),
        "artigos_recuperados": artigos,
        "top_candidatos_brutos": brutos_publicos,
        "top1_score": top1,
        "resposta_llm": resposta_final,
        "raciocinio_llm": geracao.get("raciocinio"),
        "modelo_usado": geracao.get("modelo_usado"),
        "tokens_prompt": geracao.get("tokens_prompt"),
        "tokens_resposta": geracao.get("tokens_resposta"),
        "erro_llm": geracao.get("erro"),
        "ttft_s": geracao.get("ttft_s"),
        "prefill_s": geracao.get("prefill_s"),
        "eval_s": geracao.get("eval_s"),
        "tok_s": tok_s,
        "duplicatas_removidas": removidas,
        "prompt_chars": prompt_chars,
        "auditoria": auditoria,
        "temperature": plano["temperature"],
        "num_ctx": plano["num_ctx"],
        "num_predict": plano["num_predict"],
        "think": plano["think"],
        "estourou_no_think": bool(geracao.get("estourou_no_think")),
        "tempo_thinking_s": 0.0 if not plano["think"] else geracao.get("think_s"),
        "cache": False,
        "tempos_s": {
            "roteador": tempo_roteador,
            "retriever": tempo_busca_1 + tempo_busca_2,
            "tradutor": tempo_tradutor,
            "gerador": tempo_gerador,
            "total": total,
        },
    }


if __name__ == "__main__":
    duvida = "O Estado pode intervir na economia para criar um monopólio de mineração?"
    trace = executar_rag(duvida)
    print(trace["modo_resposta"], trace["tempos_s"])
