# -*- coding: utf-8 -*-
"""Encoder denso e reranker, cada um carregado uma vez por processo.

O BGE-M3 gera o vetor de 1.024 dimensões, já normalizado. O reranker
é o BGE em ONNX INT8: o grafo devolve um logit e a sigmoide entra uma
vez, em Python, para o score ficar em [0, 1].
"""

from typing import Any

from sentence_transformers import SentenceTransformer

from src.rag.reranker import carregar_onnx_para_producao, detectar_escala, pontuar_pares

_NOME_ENCODER = "BAAI/bge-m3"
_ENCODER: SentenceTransformer | None = None
_RERANKER = None
_ESCALA: str | None = None


def obter_encoder() -> SentenceTransformer:
    """Devolve o BGE-M3 já carregado, ou carrega-o agora."""
    global _ENCODER
    if _ENCODER is None:
        _ENCODER = SentenceTransformer(_NOME_ENCODER)
    return _ENCODER


def obter_reranker():
    """Devolve a sessão ONNX INT8 já carregada, ou carrega-a do disco."""
    global _RERANKER, _ESCALA
    if _RERANKER is None:
        _RERANKER = carregar_onnx_para_producao()
        _ESCALA = detectar_escala(_RERANKER)
    return _RERANKER


def max_length_reranker() -> int:
    """Janela efectiva depois da prova de 512 no boot."""
    return int(obter_reranker().max_length)


def gerar_embedding(texto: str, convert_to_tensor: bool = True) -> Any:
    """Vetoriza uma frase. Os vetores saem com norma 1 para o cosseno ser um produto interno."""
    if texto is None or not str(texto).strip():
        raise ValueError("Não há texto para vetorizar.")
    return obter_encoder().encode(
        str(texto),
        convert_to_tensor=convert_to_tensor,
        normalize_embeddings=True,
        show_progress_bar=False,
    )


def reordenar_pares(pergunta: str, textos: list[str], batch_size: int = 4) -> list[float]:
    """Pontua cada trecho. Lote de 4, pares curtos juntos, uma sigmoide no máximo.

    O ONNX devolve logit. Se a escala detectada já for probabilidade,
    a sigmoide não é aplicada de novo.
    """
    if not textos:
        return []
    obter_reranker()
    return pontuar_pares(
        _RERANKER,
        pergunta,
        textos,
        batch_size=batch_size,
        modo_escala=_ESCALA or "logit_sigmoide_python",
        ordenar_por_tamanho=True,
    )
