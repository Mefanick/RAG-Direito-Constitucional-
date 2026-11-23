# -*- coding: utf-8 -*-
"""Catálogo, troca de modelo e LLM puro. Sem geração longa."""

import os
import sys
from pathlib import Path

os.environ["CF88_SEM_PRECARGA"] = "1"
_RAIZ = Path(__file__).resolve().parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(1, str(_RAIZ))

from unittest.mock import patch

from fastapi.testclient import TestClient

import src.rag.catalogo_modelos as catalogo
from src.api.server import app
from src.rag.catalogo_modelos import preparar_modelo, validar_modelo
from src.rag.gerador import _corpo_ollama, montar_prompt, plano_geracao
from src.rag.tradutor_consulta import _completar


def _limpar_ultimo() -> None:
    catalogo._ultimo_modelo_usado = None


def testar_allowlist() -> None:
    if validar_modelo(None) != "qwen3:8b" or validar_modelo("  ") != "qwen3:8b":
        raise SystemExit("modelo omitido deveria ser qwen3:8b")
    try:
        validar_modelo("llama3:8b")
    except catalogo.ModeloNaoPermitido:
        return
    raise SystemExit("modelo fora da lista deveria ser rejeitado")


def testar_payloads() -> None:
    puro = plano_geracao("MODO_LLM_PURO", modelo="qwen2.5:7b", usar_think=True)
    if puro["think"] or puro["num_ctx"] != 2048 or puro["num_predict"] != 450 or puro["temperature"] != 0.1:
        raise SystemExit("qwen2.5:7b em LLM puro não deveria pensar: {}".format(puro))
    pensante = plano_geracao("MODO_LLM_PURO", modelo="qwen3:4b", usar_think=True)
    if not pensante["think"] or pensante["num_predict"] != 1200:
        raise SystemExit("qwen3:4b com think deveria usar 1200 tokens")
    sem_chave = _corpo_ollama("qwen2.5:7b", [{"role": "user", "content": "oi"}], False, 0.1, 450, 2048, False)
    if "think" in sem_chave or sem_chave["model"] != "qwen2.5:7b":
        raise SystemExit("qwen2.5 não pode receber a chave think: {}".format(sem_chave))
    com_chave = _corpo_ollama("qwen3:8b", [{"role": "user", "content": "oi"}], False, 0.1, 1200, 2048, True)
    if com_chave.get("think") is not True:
        raise SystemExit("qwen3:8b deveria receber think true")
    mensagens = montar_prompt(
        "pergunta atual",
        [],
        "MODO_LLM_PURO",
        [{"role": "user", "content": "turno antigo"}],
    )
    if [item["role"] for item in mensagens] != ["system", "user"] or "turno antigo" in mensagens[1]["content"]:
        raise SystemExit("LLM puro ainda carregou histórico ou fonte")
    if "Fontes:" in mensagens[1]["content"]:
        raise SystemExit("LLM puro não deveria injetar fontes")


def testar_tradutor_mesmo_modelo() -> None:
    capturado = {}

    class Resposta:
        status_code = 200

        def json(self):
            return {"message": {"content": "texto normativo"}}

    def falso_post(url, json, timeout):
        capturado.clear()
        capturado.update(json)
        return Resposta()

    with patch("src.rag.tradutor_consulta.requests.post", falso_post):
        _completar([{"role": "user", "content": "oi"}], 20, 2048, modelo="qwen2.5:7b")
    if capturado.get("model") != "qwen2.5:7b" or "think" in capturado:
        raise SystemExit("o tradutor mudou de modelo ou mandou think: {}".format(capturado))
    with patch("src.rag.tradutor_consulta.requests.post", falso_post):
        _completar([{"role": "user", "content": "oi"}], 20, 2048, modelo="qwen3:8b")
    if capturado.get("model") != "qwen3:8b" or capturado.get("think") is not False:
        raise SystemExit("o tradutor qwen3 deveria ir com think false: {}".format(capturado))


def testar_troca_de_ram() -> None:
    _limpar_ultimo()
    chamadas = []

    def falso_post(url, json, timeout):
        chamadas.append(json)
        class Resposta:
            status_code = 200
        return Resposta()

    with patch("src.rag.catalogo_modelos.requests.post", falso_post):
        preparar_modelo("qwen3:8b")
        preparar_modelo("qwen3:8b")
        preparar_modelo("qwen3:4b")
    if chamadas != [{"model": "qwen3:8b", "keep_alive": 0}]:
        raise SystemExit("a descarga deveria ocorrer só na troca: {}".format(chamadas))
    _limpar_ultimo()


def testar_api() -> None:
    def leitor():
        return {"models": [{"name": "qwen3:8b"}, {"name": "qwen2.5:7b"}]}

    with TestClient(app) as cliente, patch("src.rag.catalogo_modelos.consultar_instalados", return_value={"qwen3:8b", "qwen2.5:7b"}):
        resposta = cliente.get("/api/modelos")
        if resposta.status_code != 200:
            raise SystemExit("GET /api/modelos falhou: {}".format(resposta.status_code))
        corpo = resposta.json()
        ids = [item["id"] for item in corpo["modelos"]]
        if ids != ["qwen3:4b", "qwen2.5:7b", "qwen3:8b"]:
            raise SystemExit("catálogo inesperado: {}".format(ids))
        instalados = {item["id"]: item["instalado"] for item in corpo["modelos"]}
        if instalados["qwen3:4b"] or not instalados["qwen3:8b"] or not instalados["qwen2.5:7b"]:
            raise SystemExit("marcação de instalado incorreta: {}".format(instalados))
        if not any(item["padrao"] and item["id"] == "qwen3:8b" for item in corpo["modelos"]):
            raise SystemExit("qwen3:8b deveria ser o padrão")
        if cliente.get("/modelos").status_code != 200:
            raise SystemExit("GET /modelos deveria responder")
        recusado = cliente.post("/api/perguntar", json={"pergunta": "oi", "modelo": "llama3:8b"})
        if recusado.status_code != 400:
            raise SystemExit("modelo desconhecido deveria ser HTTP 400, veio {}".format(recusado.status_code))
    del leitor


def main() -> None:
    testar_allowlist()
    testar_payloads()
    testar_tradutor_mesmo_modelo()
    testar_troca_de_ram()
    testar_api()
    print("ok modelos, llm puro e api")


if __name__ == "__main__":
    main()
