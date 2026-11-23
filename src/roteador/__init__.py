"""Caixa preta do classificador. O RAG só vê avaliar_intencao."""

from src.roteador.servico_classificacao import avaliar_intencao

__all__ = ["avaliar_intencao"]
