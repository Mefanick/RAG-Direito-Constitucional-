# -*- coding: utf-8 -*-
import re
from pathlib import Path

root = Path(__file__).resolve().parent / "oab" / "util" / "provas_oficiais"
out = Path(__file__).resolve().parent / "_enunciados_const.txt"
inicio = re.compile(r"(?m)^Quest[aã]o\s+(\d+)[ \t]*(.*?)\s*$")
partes = []
for arquivo in sorted(root.glob("*.txt")):
    texto = arquivo.read_text(encoding="utf-8")
    marcas = list(inicio.finditer(texto))
    for indice, match in enumerate(marcas):
        fim = marcas[indice + 1].start() if indice + 1 < len(marcas) else len(texto)
        bloco = texto[match.end() : fim]
        linhas = [linha.strip() for linha in bloco.splitlines()]
        area = ""
        corpo = []
        for linha in linhas:
            if not area and linha.upper().startswith("AREA"):
                area = linha[4:].strip()
                continue
            if area:
                if linha.upper().startswith("OPTIONS"):
                    break
                corpo.append(linha)
        if area != "CONSTITUTIONAL":
            continue
        enunciado = re.sub(r"\s+", " ", " ".join(corpo)).strip()
        partes.append(
            "[{:03d}] {} Q{}\n{}\n".format(len(partes) + 1, arquivo.name, match.group(1), enunciado)
        )
out.write_text("\n".join(partes), encoding="utf-8")
print(len(partes))
