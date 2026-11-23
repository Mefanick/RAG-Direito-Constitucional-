"""Retriever semântico. Não importa o classificador no carregamento do pacote.

O módulo retriever é que pede avaliar_intencao, e só quando a busca corre.
Assim um import de src.rag não dispara o SentenceTransformer.
"""
