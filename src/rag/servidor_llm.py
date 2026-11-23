# -*- coding: utf-8 -*-
"""Sobe o LLM local se ele já estiver instalado, sem baixar pesos.

Procura um servidor OpenAI em 11434 (Ollama) e em 8080 (Llamafile).
Se nenhum responder e houver Ollama com um modelo já puxado, sobe
`ollama serve` desacoplado. Sem modelo na máquina, devolve o comando
para o utilizador puxar um, e não inicia download.
"""

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

LLM_URL: str | None = None
LLM_MODEL: str | None = None

_URL_MODELOS_OLLAMA = "http://127.0.0.1:11434/v1/models"
_URL_MODELOS_LLAMAFILE = "http://127.0.0.1:8080/v1/models"
_URL_CHAT_OLLAMA = "http://127.0.0.1:11434/v1/chat/completions"
_URL_CHAT_LLAMAFILE = "http://127.0.0.1:8080/v1/chat/completions"

# Ordem de preferência. O primeiro que existir na lista do servidor ganha.
_PREFERIDOS = (
    "qwen3:8b",
    "qwen2.5:7b",
    "qwen2.5",
    "qwen3",
    "llama3.1",
    "llama3.2",
    "llama3",
)

COMANDO_MANUAL = (
    "winget install --id Ollama.Ollama -e\n"
    "ollama pull qwen3:8b\n"
    "set OLLAMA_FLASH_ATTENTION=1\n"
    "set OLLAMA_KV_CACHE_TYPE=q8_0\n"
    "ollama serve"
)

_ESTADO: dict | None = None
_RAIZ = Path(__file__).resolve().parents[2]


def _pedido(url: str, timeout: float) -> dict | None:
    """GET com tempo curto. Porta fechada ou muda devolve None."""
    pedido = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(pedido, timeout=timeout) as resposta:
            if resposta.status != 200:
                return None
            return json.loads(resposta.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError, ValueError):
        return None


def ids_de_modelos(payload: dict | None) -> list[str]:
    """Lê o campo data[].id do /v1/models."""
    if not isinstance(payload, dict):
        return []
    dados = payload.get("data")
    if not isinstance(dados, list):
        return []
    ids = []
    for item in dados:
        if isinstance(item, dict) and item.get("id"):
            ids.append(str(item["id"]))
    return ids


def escolher_modelo(ids: list[str]) -> str | None:
    """Prefere um modelo de conversa já citado. Ignora embeddings."""
    conversa = [
        nome
        for nome in ids
        if "embed" not in nome.lower() and not nome.lower().startswith("bge")
    ]
    for prefixo in _PREFERIDOS:
        for nome in conversa:
            if nome == prefixo or nome.startswith(prefixo + ":") or nome.startswith(prefixo + "-"):
                return nome
    return conversa[0] if conversa else None


def caminho_ollama() -> str | None:
    """Caminho do executável, no PATH ou nas pastas habituais do Windows."""
    encontrado = shutil.which("ollama")
    if encontrado:
        return encontrado
    candidatos = [
        Path.home() / "AppData" / "Local" / "Programs" / "Ollama" / "ollama.exe",
        Path.home() / "AppData" / "Local" / "Ollama" / "ollama.exe",
        Path("C:/Program Files/Ollama/ollama.exe"),
    ]
    for caminho in candidatos:
        if caminho.is_file():
            return str(caminho)
    return None


def modelos_ollama_locais(executavel: str) -> list[str]:
    """Nomes da primeira coluna de `ollama list`. Lista vazia se o comando falhar."""
    try:
        concluido = subprocess.run(
            [executavel, "list"],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    nomes = []
    for linha in (concluido.stdout or "").splitlines()[1:]:
        partes = linha.split()
        if partes and partes[0].lower() != "name":
            nomes.append(partes[0])
    return nomes


def procurar_llamafile() -> Path | None:
    """Primeiro .llamafile no projecto, no Ambiente de Trabalho ou em Transferências."""
    raizes = [_RAIZ, Path.home() / "Desktop", Path.home() / "Downloads"]
    for raiz in raizes:
        if not raiz.is_dir():
            continue
        try:
            encontrado = next(raiz.rglob("*.llamafile"), None)
        except OSError:
            continue
        if encontrado is not None:
            return encontrado
    return None


def _subir_desacoplado(executavel: str, argumentos: list[str]) -> None:
    """Arranca o processo sem prender este terminal. No Windows usa Start-Process."""
    os.environ["OLLAMA_FLASH_ATTENTION"] = "1"
    os.environ["OLLAMA_KV_CACHE_TYPE"] = "q8_0"
    if sys.platform == "win32":
        linha = "set OLLAMA_FLASH_ATTENTION=1&& set OLLAMA_KV_CACHE_TYPE=q8_0&& \"{}\" {}".format(
            executavel,
            " ".join(argumentos),
        )
        comando = "Start-Process -FilePath 'cmd.exe' -ArgumentList '/c','{}' -WindowStyle Hidden".format(
            linha.replace("'", "''")
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", comando],
            check=False,
            timeout=20,
        )
        return
    subprocess.Popen(
        [executavel, *argumentos],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def _esperar_modelos(url: str, espera_s: float) -> dict | None:
    limite = time.perf_counter() + espera_s
    while time.perf_counter() < limite:
        payload = _pedido(url, timeout=0.4)
        if payload is not None:
            return payload
        time.sleep(0.4)
    return None


def _publicar(url: str | None, modelo: str | None, origem: str, comando: str | None) -> dict:
    global LLM_URL, LLM_MODEL, _ESTADO
    LLM_URL = url
    LLM_MODEL = modelo
    if url:
        os.environ["LLM_URL"] = url
    if modelo and not os.getenv("LLM_MODEL"):
        os.environ["LLM_MODEL"] = modelo
    elif os.getenv("LLM_MODEL"):
        modelo = os.getenv("LLM_MODEL")
    _ESTADO = {"url": url, "model": modelo, "origem": origem, "comando": comando}
    return _ESTADO


def garantir_servidor(espera_s: float = 15, forcar: bool = False) -> dict:
    """Garante um servidor local ou explica o comando que falta.

    Não faz `ollama pull` nem transfere um Llamafile. Espera no máximo
    espera_s segundos depois de subir um processo que já existia no disco.
    """
    if _ESTADO is not None and not forcar:
        return _ESTADO

    for url_modelos, url_chat, origem in (
        (_URL_MODELOS_OLLAMA, _URL_CHAT_OLLAMA, "ollama"),
        (_URL_MODELOS_LLAMAFILE, _URL_CHAT_LLAMAFILE, "llamafile"),
    ):
        payload = _pedido(url_modelos, timeout=0.4)
        if payload is None:
            continue
        return _publicar(url_chat, escolher_modelo(ids_de_modelos(payload)) or "local-model", origem, None)

    executavel = caminho_ollama()
    if executavel:
        instalados = modelos_ollama_locais(executavel)
        escolhido = escolher_modelo(instalados)
        if escolhido:
            _subir_desacoplado(executavel, ["serve"])
            payload = _esperar_modelos(_URL_MODELOS_OLLAMA, espera_s)
            if payload is not None:
                modelo = escolher_modelo(ids_de_modelos(payload)) or escolhido
                return _publicar(_URL_CHAT_OLLAMA, modelo, "ollama", None)

    llamafile = procurar_llamafile()
    if llamafile is not None:
        _subir_desacoplado(str(llamafile), ["--server", "--nobrowser", "-addr", "127.0.0.1:8080"])
        payload = _esperar_modelos(_URL_MODELOS_LLAMAFILE, espera_s)
        if payload is not None:
            modelo = escolher_modelo(ids_de_modelos(payload)) or "local-model"
            return _publicar(_URL_CHAT_LLAMAFILE, modelo, "llamafile", None)

    return _publicar(None, None, "ausente", COMANDO_MANUAL)
