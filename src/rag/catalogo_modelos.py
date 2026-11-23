# -*- coding: utf-8 -*-
"""Allowlist dos três modelos oficiais e a troca que libera a RAM."""

import threading

import requests

OLLAMA_TAGS = "http://127.0.0.1:11434/api/tags"
OLLAMA_GENERATE = "http://127.0.0.1:11434/api/generate"
TIMEOUT_TAGS_S = 3.0
TIMEOUT_DESCARGA_S = 5.0

CATALOGO = (
    {
        "id": "qwen3:4b",
        "label": "Rápido (Qwen3 4B)",
        "suporta_think": True,
        "padrao": False,
    },
    {
        "id": "qwen2.5:7b",
        "label": "Equilibrado (Qwen2.5 7B)",
        "suporta_think": False,
        "padrao": False,
    },
    {
        "id": "qwen3:8b",
        "label": "Máxima Precisão (Qwen3 8B)",
        "suporta_think": True,
        "padrao": True,
    },
)
MODELO_PADRAO = "qwen3:8b"
_IDS = {item["id"]: item for item in CATALOGO}
_trava = threading.Lock()
_ultimo_modelo_usado: str | None = None


class ModeloNaoPermitido(ValueError):
    """O cliente pediu um modelo fora da allowlist."""


def validar_modelo(modelo: str | None) -> str:
    """Vazio vira qwen3:8b. Qualquer outro id fora da lista é rejeitado."""
    escolhido = str(modelo or "").strip()
    if not escolhido:
        return MODELO_PADRAO
    if escolhido not in _IDS:
        raise ModeloNaoPermitido(
            "Modelo não permitido. Use qwen3:4b, qwen2.5:7b ou qwen3:8b."
        )
    return escolhido


def modelo_suporta_think(modelo: str) -> bool:
    item = _IDS.get(str(modelo or "").strip())
    return bool(item and item["suporta_think"])


def modelo_ativo_atual() -> str:
    with _trava:
        return _ultimo_modelo_usado or MODELO_PADRAO


def preparar_modelo(modelo: str) -> None:
    """Descarrega o modelo anterior só quando a requisição pede outro."""
    global _ultimo_modelo_usado
    with _trava:
        anterior = _ultimo_modelo_usado
        if anterior and anterior != modelo:
            _descarregar(anterior)
        _ultimo_modelo_usado = modelo


def _descarregar(modelo: str) -> None:
    try:
        requests.post(
            OLLAMA_GENERATE,
            json={"model": modelo, "keep_alive": 0},
            timeout=TIMEOUT_DESCARGA_S,
        )
    except requests.exceptions.RequestException:
        return


def _instalado(nome: str, presentes: set[str]) -> bool:
    if nome in presentes:
        return True
    prefixo = nome + ":"
    return any(item.startswith(prefixo) for item in presentes)


def consultar_instalados(leitor=None) -> set[str]:
    """Nomes devolvidos por /api/tags. Conjunto vazio se o Ollama não responder."""
    if leitor is None:
        try:
            resposta = requests.get(OLLAMA_TAGS, timeout=TIMEOUT_TAGS_S)
        except requests.exceptions.RequestException:
            return set()
        if resposta.status_code != 200:
            return set()
        try:
            dados = resposta.json()
        except ValueError:
            return set()
    else:
        dados = leitor()
    nomes = set()
    for item in (dados or {}).get("models") or []:
        if not isinstance(item, dict):
            continue
        for chave in ("name", "model"):
            valor = str(item.get(chave) or "").strip()
            if valor:
                nomes.add(valor)
    return nomes


def listar_catalogo(leitor=None) -> dict:
    presentes = consultar_instalados(leitor)
    return {
        "modelos": [
            {
                "id": item["id"],
                "label": item["label"],
                "suporta_think": item["suporta_think"],
                "instalado": _instalado(item["id"], presentes),
                "padrao": item["padrao"],
            }
            for item in CATALOGO
        ],
        "modelo_ativo_atual": modelo_ativo_atual(),
    }
