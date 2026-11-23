# -*- coding: utf-8 -*-
"""Auditoria de citações em dois níveis: artigo e subdispositivo.

O artigo confere o número (e o ADCT) com os chunks enviados ao modelo.
Parágrafo, inciso e alínea só passam se o marcador estiver no artigo_id
ou no texto de um chunk do mesmo artigo.
"""

import re

_RE_ARTIGO = re.compile(
    r"(?:(?P<adct>\bADCT)\s*,?\s*)?\bArt(?:igo)?s?\.?\s*(?P<num>\d+)\s*[ºo°]?",
    re.IGNORECASE,
)
_RE_PARAGRAFO = re.compile(r"§\s*(?P<num>\d+)\s*[ºo°]?", re.IGNORECASE)
_RE_UNICO = re.compile(r"par[aá]grafo\s+[uú]nico", re.IGNORECASE)
_RE_INCISO = re.compile(r"(?:inciso\s+|(?<=,))\s*(?P<romano>[IVXLCDM]+)\b", re.IGNORECASE)
_RE_ALINEA = re.compile(
    r"al[ií]nea\s+[\"'“”]?(?P<letra>[a-z])[\"'“”]?"
    r"|,\s*[\"'“”](?P<aspas>[a-z])[\"'“”]"
    r"|,\s*(?P<fecha>[a-z])\)",
    re.IGNORECASE,
)
_RE_ROMANO = re.compile(
    r"^M{0,4}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})$"
)


def _chave(adct: str | None, numero: str) -> str:
    if adct:
        return "ADCT Art. {}".format(numero)
    return "Art. {}".format(numero)


def extrair_artigos(texto: str) -> list[str]:
    """Números de artigo citados, na ordem, sem repetir."""
    vistos = []
    for achado in _RE_ARTIGO.finditer(str(texto or "")):
        chave = _chave(achado.group("adct"), achado.group("num"))
        if chave not in vistos:
            vistos.append(chave)
    return vistos


def _romano_valido(token: str) -> bool:
    return bool(token) and bool(_RE_ROMANO.match(token.upper()))


def _janela(texto: str, fim: int) -> str:
    resto = texto[fim : fim + 140]
    proximo = re.search(r"\bArt(?:igo)?s?\.?\s*\d", resto, re.IGNORECASE)
    if proximo:
        return resto[: proximo.start()]
    return resto


def _subdispositivos(texto: str) -> list[str]:
    """Citações com parágrafo, inciso ou alínea, na ordem e sem repetir."""
    vistos = []
    bruto = str(texto or "")
    for achado in _RE_ARTIGO.finditer(bruto):
        chave = _chave(achado.group("adct"), achado.group("num"))
        janela = _janela(bruto, achado.end())
        marcadores = []
        for paragrafo in _RE_PARAGRAFO.finditer(janela):
            marcadores.append("§ {}º".format(paragrafo.group("num")))
        if _RE_UNICO.search(janela):
            marcadores.append("parágrafo único")
        for inciso in _RE_INCISO.finditer(janela):
            romano = inciso.group("romano").upper()
            if _romano_valido(romano):
                marcadores.append(romano)
        for alinea in _RE_ALINEA.finditer(janela):
            letra = next(grupo for grupo in alinea.groups() if grupo)
            marcadores.append('"{}"'.format(letra.lower()))
        if not marcadores:
            continue
        citacao = "{}, {}".format(chave, ", ".join(marcadores))
        if citacao not in vistos:
            vistos.append(citacao)
    return vistos


def _partes(citacao: str) -> tuple[str, list[str]]:
    achado = _RE_ARTIGO.search(citacao)
    if not achado:
        return citacao, []
    chave = _chave(achado.group("adct"), achado.group("num"))
    resto = citacao[achado.end() :]
    marcadores = []
    for paragrafo in _RE_PARAGRAFO.finditer(resto):
        marcadores.append(("paragrafo", paragrafo.group("num")))
    if _RE_UNICO.search(resto):
        marcadores.append(("unico", ""))
    for inciso in _RE_INCISO.finditer(resto):
        romano = inciso.group("romano").upper()
        if _romano_valido(romano):
            marcadores.append(("inciso", romano))
    for alinea in _RE_ALINEA.finditer(resto):
        letra = next(grupo for grupo in alinea.groups() if grupo)
        marcadores.append(("alinea", letra.lower()))
    return chave, marcadores


def _confirmado(tipo: str, valor: str, blob: str) -> bool:
    if tipo == "paragrafo":
        return re.search(r"§\s*" + re.escape(valor) + r"\s*[ºo°]?", blob, re.IGNORECASE) is not None
    if tipo == "unico":
        return _RE_UNICO.search(blob) is not None
    if tipo == "inciso":
        return re.search(r"\b" + re.escape(valor) + r"\b", blob) is not None
    if tipo == "alinea":
        return (
            re.search(
                r"(?:al[ií]nea\s+[\"'“”]?" + re.escape(valor) + r"[\"'“”]?|\b" + re.escape(valor) + r"\))",
                blob,
                re.IGNORECASE,
            )
            is not None
        )
    return False


def auditar_citacoes(resposta_llm: str, artigos_recuperados: list) -> dict:
    """Confere artigo e, quando a resposta desce ao inciso, o marcador.

    citacao_alucinada fica verdadeiro se houver artigo inventado ou
    subdispositivo que não aparece nas fontes daquele artigo.
    As chaves citacoes, inventadas e recuperados permanecem para os
    chamadores antigos.
    """
    artigos_citados = extrair_artigos(resposta_llm)
    sub_citados = _subdispositivos(resposta_llm)
    recuperados = []
    por_artigo: dict[str, list[str]] = {}
    for artigo in artigos_recuperados or []:
        if isinstance(artigo, dict):
            ident = str(artigo.get("artigo_id") or "")
            texto = str(artigo.get("texto") or "")
        else:
            ident = str(artigo)
            texto = ""
        blob = ident + "\n" + texto
        for chave in extrair_artigos(ident):
            if chave not in recuperados:
                recuperados.append(chave)
            por_artigo.setdefault(chave, []).append(blob)

    artigos_inventados = [chave for chave in artigos_citados if chave not in recuperados]
    nao_confirmados = []
    for citacao in sub_citados:
        chave, marcadores = _partes(citacao)
        blobs = por_artigo.get(chave) or []
        if chave not in recuperados or not marcadores:
            if citacao not in nao_confirmados:
                nao_confirmados.append(citacao)
            continue
        unido = "\n".join(blobs)
        if any(not _confirmado(tipo, valor, unido) for tipo, valor in marcadores):
            nao_confirmados.append(citacao)

    if not artigos_citados and not sub_citados:
        status = "SEM_CITACAO"
    elif artigos_inventados:
        status = "ALUCINACAO_ARTIGO"
    elif nao_confirmados:
        status = "ALERTA_SUBDISPOSITIVO"
    else:
        status = "FIEL"
    return {
        "artigos_citados": artigos_citados,
        "subdispositivos_citados": sub_citados,
        "artigos_inventados": artigos_inventados,
        "subdispositivos_nao_confirmados": nao_confirmados,
        "status": status,
        "citacao_alucinada": bool(artigos_inventados or nao_confirmados),
        "citacoes": artigos_citados,
        "inventadas": artigos_inventados,
        "recuperados": recuperados,
    }
