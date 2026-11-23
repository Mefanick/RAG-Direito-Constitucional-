# -*- coding: utf-8 -*-
"""Checkpoints do servidor. Cada etapa sai na hora, com hora e duração."""

from datetime import datetime


def registrar(etapa: str, titulo: str, detalhes: list[str], segundos: float | None = None) -> None:
    hora = datetime.now().strftime("%H:%M:%S")
    duracao = "" if segundos is None else "  {:.2f} s".format(segundos)
    print("[{}] [CP {} | {}]{}".format(hora, etapa, titulo, duracao), flush=True)
    for linha in detalhes:
        print("    {}".format(linha), flush=True)
