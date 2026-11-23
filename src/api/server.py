# -*- coding: utf-8 -*-
"""Interface da Etapa 5. O motor sobe no boot e a resposta sai em SSE."""

import asyncio
import json
import os
import queue
import re
import threading
import time
from pathlib import Path

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

_RAIZ = Path(__file__).resolve().parents[2]
_FRONTEND = _RAIZ / "frontend"
_COMANDO = "ollama serve"
_CACHE: dict[str, dict] = {}


class Mensagem(BaseModel):
    role: str
    content: str


class Pedido(BaseModel):
    pergunta: str
    historico: list[Mensagem] = []
    usar_cache: bool = False
    simular_offline: bool = False
    modo_raciocinio: str = "desligado"
    usar_think: bool = False
    modelo: str | None = None
    usar_rag: bool = True


def historico_efetivo(pedido: Pedido) -> list:
    """O cliente pode mandar historico. O processamento ignora turnos anteriores."""
    del pedido
    return []


def _normalizar(pergunta: str) -> str:
    return re.sub(r"\s+", " ", pergunta.strip().lower())


def _evento(nome: str, dados: dict) -> str:
    return "event: {}\ndata: {}\n\n".format(nome, json.dumps(dados, ensure_ascii=False))


def _ollama_no_ar() -> bool:
    try:
        resposta = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
        return resposta.status_code == 200
    except requests.exceptions.RequestException:
        return False


def _precarga() -> None:
    from src.rag.encoder import obter_encoder, obter_reranker
    from src.rag.retriever import _EMBEDDINGS
    from src.roteador.servico_classificacao import _ROTEADOR

    obter_encoder()
    obter_reranker()
    _ = _EMBEDDINGS.shape
    _ = _ROTEADOR


def criar_app() -> FastAPI:
    app = FastAPI(title="Constituição 1988")

    @app.on_event("startup")
    def subir() -> None:
        os.environ.setdefault("LLM_URL", "http://127.0.0.1:11434/api/chat")
        os.environ.setdefault("LLM_MODEL", "qwen3:8b")
        if os.getenv("CF88_SEM_PRECARGA") == "1":
            return
        _precarga()

    @app.get("/modelos")
    @app.get("/api/modelos")
    def modelos() -> dict:
        from src.rag.catalogo_modelos import listar_catalogo

        return listar_catalogo()

    @app.get("/api/saude")
    def saude() -> dict:
        from src.rag.gerador import configuracao_servidor

        _, modelo = configuracao_servidor()
        return {
            "online": _ollama_no_ar(),
            "modelo": modelo,
            "motor": "BGE-M3 · ONNX INT8 · Corte 0,25",
        }

    @app.post("/api/cache/limpar")
    def limpar_cache() -> dict:
        _CACHE.clear()
        return {"limpo": True}

    @app.post("/api/perguntar")
    def perguntar(pedido: Pedido) -> StreamingResponse:
        from src.rag.catalogo_modelos import ModeloNaoPermitido, validar_modelo

        try:
            validar_modelo(pedido.modelo)
        except ModeloNaoPermitido as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return StreamingResponse(_fluxo(pedido), media_type="text/event-stream")

    if _FRONTEND.is_dir():
        app.mount("/", StaticFiles(directory=str(_FRONTEND), html=True), name="ui")
    return app


def _fluxo(pedido: Pedido):
    from src.rag.checkpoints import registrar
    from src.rag.pipeline import executar_rag

    chave = "{}||think={}||rag={}||modelo={}".format(
        _normalizar(pedido.pergunta),
        int(bool(pedido.usar_think)),
        int(bool(pedido.usar_rag)),
        (pedido.modelo or "qwen3:8b").strip(),
    )
    if pedido.usar_cache and not pedido.simular_offline and chave in _CACHE:
        registrar(
            "1/6",
            "ENTRADA",
            [pedido.pergunta.strip(), "histórico: ignorado (stateless)", "cache: HIT"],
        )
        guardado = dict(_CACHE[chave])
        guardado["cache"] = True
        yield _evento("cache", guardado)
        return

    caixa: queue.Queue = queue.Queue()

    def publicar(nome: str, dados: dict) -> None:
        caixa.put((nome, dados))

    def trabalho() -> None:
        artigos = []
        try:
            trace = executar_rag(
                pedido.pergunta.strip(),
                historico=historico_efetivo(pedido),
                stream=True,
                on_token=lambda pedaco: publicar("token", {"texto": pedaco}),
                on_etapa=lambda rotulo: publicar("etapa", {"rotulo": rotulo}),
                cache_status="MISS" if pedido.usar_cache else "DESLIGADO",
                simular_offline=pedido.simular_offline,
                usar_think=pedido.usar_think,
                modelo=pedido.modelo,
                usar_rag=pedido.usar_rag,
            )
            artigos = trace.get("artigos_recuperados") or []
            pacote = {
                "resposta": trace.get("resposta_llm") or "",
                "raciocinio": trace.get("raciocinio_llm"),
                "usar_think": bool(trace.get("usar_think")),
                "tempo_thinking_s": trace.get("tempo_thinking_s"),
                "think_s": trace.get("think_s"),
                "think_chars": trace.get("think_chars"),
                "prefill_s": trace.get("prefill_s"),
                "eval_s": trace.get("eval_s"),
                "duplicatas_removidas": trace.get("duplicatas_removidas"),
                "prompt_chars": trace.get("prompt_chars"),
                "roteamento": trace.get("roteamento"),
                "modo_busca": trace.get("modo_busca"),
                "modo_resposta": trace.get("modo_resposta"),
                "modo_rag": trace.get("modo_rag") or trace.get("modo_resposta"),
                "classe_consulta": trace.get("classe_consulta"),
                "subconsultas": trace.get("subconsultas") or [],
                "consulta_traduzida": trace.get("consulta_traduzida"),
                "passagem": trace.get("passagem"),
                "artigos": artigos,
                "top_candidatos_brutos": trace.get("top_candidatos_brutos") or [],
                "top1_score": trace.get("top1_score"),
                "modelo": trace.get("modelo_usado"),
                "tokens_prompt": trace.get("tokens_prompt"),
                "tokens_resposta": trace.get("tokens_resposta"),
                "ttft_s": trace.get("ttft_s"),
                "erro": trace.get("erro_llm"),
                "tempos_s": trace.get("tempos_s"),
                "tok_s": trace.get("tok_s"),
                "cache": False,
                "auditoria": trace.get("auditoria"),
                "comando": _COMANDO if trace.get("erro_llm") else None,
            }
            if pedido.usar_cache and not trace.get("erro_llm"):
                _CACHE[chave] = pacote
            publicar("fim", pacote)
        except Exception as exc:
            print("[ERRO] {}: {}".format(type(exc).__name__, exc), flush=True)
            publicar(
                "erro",
                {
                    "mensagem": "A consulta não terminou. Os artigos já recuperados continuam abaixo.",
                    "artigos": artigos,
                    "comando": _COMANDO,
                },
            )
        finally:
            caixa.put(None)

    threading.Thread(target=trabalho, daemon=True).start()
    while True:
        item = caixa.get()
        if item is None:
            break
        yield _evento(item[0], item[1])
app = criar_app()
