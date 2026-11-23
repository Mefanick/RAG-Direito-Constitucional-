# -*- coding: utf-8 -*-
"""Abre a janela do chat e sobe o Ollama e a API local quando ainda não estão no ar."""

import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORTA_API = 8000
PORTA_OLLAMA = 11434
URL_API = "http://{}:{}".format(HOST, PORTA_API)
URL_OLLAMA = "http://{}:{}/api/tags".format(HOST, PORTA_OLLAMA)
ESPERA_OLLAMA_S = 30
ESPERA_API_S = 240


def _porta_aberta(porta):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexao:
        conexao.settimeout(0.4)
        return conexao.connect_ex((HOST, porta)) == 0


def _saude():
    try:
        resposta = requests.get(URL_API + "/api/saude", timeout=2)
    except requests.exceptions.RequestException:
        return None
    if resposta.status_code != 200:
        return None
    try:
        dados = resposta.json()
    except ValueError:
        return None
    if "online" not in dados or "motor" not in dados:
        return None
    return dados


def _ollama_no_ar():
    try:
        resposta = requests.get(URL_OLLAMA, timeout=2)
        return resposta.status_code == 200
    except requests.exceptions.RequestException:
        return False


def _executavel_ollama():
    encontrado = shutil.which("ollama")
    if encontrado:
        return encontrado
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe"
    if local.is_file():
        return str(local)
    return None


def _abrir_processo(comando):
    flags = 0
    if sys.platform == "win32":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP
    ambiente = os.environ.copy()
    ambiente.setdefault("PYTHONUNBUFFERED", "1")
    return subprocess.Popen(
        comando,
        cwd=str(RAIZ),
        env=ambiente,
        creationflags=flags,
    )


def _esperar(pronto, processo, limite_s, rotulo):
    inicio = time.monotonic()
    while time.monotonic() - inicio < limite_s:
        if processo is not None and processo.poll() is not None:
            raise SystemExit("{} encerrou antes de ficar pronto (código {}).".format(rotulo, processo.returncode))
        if pronto():
            return
        time.sleep(1)
    raise SystemExit("{} não respondeu em {} s.".format(rotulo, limite_s))


def garantir_ollama():
    if _ollama_no_ar():
        print("Ollama já está no ar.", flush=True)
        return None
    executavel = _executavel_ollama()
    if executavel is None:
        raise SystemExit("Ollama não está no ar e o comando ollama não foi encontrado.")
    print("Subindo ollama serve...", flush=True)
    processo = _abrir_processo([executavel, "serve"])
    _esperar(_ollama_no_ar, processo, ESPERA_OLLAMA_S, "Ollama")
    print("Ollama pronto.", flush=True)
    return processo


def garantir_api():
    saude = _saude()
    if saude is not None:
        print("API já está no ar em {}.".format(URL_API), flush=True)
        return None
    if _porta_aberta(PORTA_API):
        raise SystemExit("A porta {} já está em uso por outro programa.".format(PORTA_API))
    print("Subindo a API em {} ...".format(URL_API), flush=True)
    print("A primeira abertura espera a pré-carga do BGE-M3 e do reranker.", flush=True)
    processo = _abrir_processo(
        [sys.executable, "-m", "uvicorn", "src.api.server:app", "--host", HOST, "--port", str(PORTA_API)]
    )
    _esperar(lambda: _saude() is not None, processo, ESPERA_API_S, "API")
    print("API pronta.", flush=True)
    return processo


def encerrar(processo, rotulo):
    if processo is None or processo.poll() is not None:
        return
    processo.terminate()
    try:
        processo.wait(timeout=8)
    except subprocess.TimeoutExpired:
        processo.kill()
        processo.wait(timeout=5)
    print("{} encerrado.".format(rotulo), flush=True)


def main():
    if not (RAIZ / "frontend" / "index.html").is_file():
        raise SystemExit("frontend/index.html não está na pasta do projeto.")
    try:
        import webview
    except ImportError as exc:
        raise SystemExit("Instale a janela com: python -m pip install pywebview") from exc

    ollama = None
    api = None
    try:
        ollama = garantir_ollama()
        api = garantir_api()
        webview.create_window(
            title="Constituição de 1988",
            url=URL_API,
            width=1280,
            height=860,
            min_size=(1024, 680),
        )
        webview.start()
    finally:
        encerrar(api, "API")
        encerrar(ollama, "Ollama")


def __getattr__(nome):
    """Permite `uvicorn interface:app` sem carregar o FastAPI ao abrir a janela."""
    if nome == "app":
        from src.api.server import app
        return app
    raise AttributeError(nome)


if __name__ == "__main__":
    main()
