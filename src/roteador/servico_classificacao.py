# -*- coding: utf-8 -*-
"""Serviço de classificação por probabilidade.

O classificador é uma regressão logística sobre o embedding denso.
Carrega uma vez. Se a pipeline já vetorizou a frase, avaliar_intencao
reutiliza esse vetor e o MiniLM não corre de novo.
"""

from pathlib import Path
from typing import Any, TypedDict

import joblib
import numpy as np

from src.rag.encoder import gerar_embedding


class AvaliacaoIntencao(TypedDict):
    """Contrato do roteador. A margem é diferença de probabilidade, não distância de SVM."""

    intencao: str
    confianca_alta: bool
    prob_top1: float
    margem: float
    limiar: float


_RAIZ = Path(__file__).resolve().parents[2]
_CAMINHO_MODELO = _RAIZ / "modelos" / "roteador_constitucional.joblib"

if not _CAMINHO_MODELO.is_file():
    raise FileNotFoundError(
        "Modelo do roteador não encontrado em {}. Rode src/roteador/treinar_roteador.py.".format(
            _CAMINHO_MODELO
        )
    )

# Singleton do classificador. O encoder vive noutro módulo, também único.
_ROTEADOR = joblib.load(_CAMINHO_MODELO)


def _como_matriz(embedding: Any) -> np.ndarray:
    if hasattr(embedding, "detach"):
        embedding = embedding.detach().cpu().numpy()
    matriz = np.asarray(embedding, dtype=np.float64)
    if matriz.ndim == 1:
        return matriz.reshape(1, -1)
    if matriz.ndim == 2 and matriz.shape[0] == 1:
        return matriz
    return matriz.reshape(1, -1)


def avaliar_intencao(texto: str, limiar: float = 0.15, embedding: Any = None) -> AvaliacaoIntencao:
    """Devolve a classe mais provável e a folga para a segunda.

    predict_proba dá uma distribuição que soma 1. prob_top1 é a maior,
    prob_top2 a seguinte, margem é a diferença. confianca_alta só quando
    essa folga atinge o limiar. Igualdade conta como confiança alta.
    Se embedding vier preenchido, esta função não chama o MiniLM.
    """
    if texto is None or not str(texto).strip():
        raise ValueError("A frase para classificar está vazia.")
    if limiar < 0:
        raise ValueError("O limiar da margem não pode ser negativo.")

    vetor = _como_matriz(embedding) if embedding is not None else _como_matriz(
        gerar_embedding(str(texto), convert_to_tensor=False)
    )
    probabilidades = _ROTEADOR.predict_proba(vetor)[0]
    ordem = np.argsort(probabilidades)[::-1]
    prob_top1 = float(probabilidades[ordem[0]])
    prob_top2 = float(probabilidades[ordem[1]]) if len(ordem) > 1 else 0.0
    margem = prob_top1 - prob_top2
    limiar_usado = float(limiar)
    return {
        "intencao": str(_ROTEADOR.classes_[ordem[0]]),
        "confianca_alta": margem >= limiar_usado,
        "prob_top1": prob_top1,
        "margem": margem,
        "limiar": limiar_usado,
    }
