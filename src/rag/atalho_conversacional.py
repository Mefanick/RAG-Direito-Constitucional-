# -*- coding: utf-8 -*-
"""Atalho social. Sai antes do embedding, do reranker e do Ollama.

Só entra uma fala curta que é saudação, agradecimento, despedida ou
pergunta sobre o próprio assistente. Qualquer termo jurídico devolve
None e o RAG segue.
"""

import re
import unicodedata

_LIMITE_PALAVRAS = 8

_RE_SAUDACAO = re.compile(
    r"^(?:oi|ol[aá]|opa|e a[ií]|bom dia|boa tarde|boa noite)"
    r"(?:[\s,]+(?:tudo bem|tudo bom|como vai|beleza|como est[aá]))?"
    r"[\s?!.]*$",
    re.IGNORECASE,
)
_RE_AGRADECIMENTO = re.compile(
    r"^(?:(?:muito\s+)?obrigad[oa]|valeu|vlw|grato|grata|agradecid[oa])"
    r"(?:[\s,]+(?:mesmo|pela ajuda|obrigad[oa]|valeu))?"
    r"[\s?!.]*$"
    r"|^(?:perfeito|show|certo|ok|beleza)[\s,]+(?:muito\s+)?(?:obrigad[oa]|valeu)[\s?!.]*$",
    re.IGNORECASE,
)
_RE_DESPEDIDA = re.compile(
    r"^(?:tchau|at[eé] mais|at[eé] logo|at[eé] breve|falou|fui)"
    r"(?:[\s,]+(?:obrigad[oa]|valeu))?"
    r"[\s?!.]*$",
    re.IGNORECASE,
)
_RE_META = re.compile(
    r"^(?:quem (?:e|é) (?:voce|você)"
    r"|o que (?:voce|você) faz"
    r"|como (?:voce|você) (?:pode|consegue) me ajudar"
    r"|em que (?:voce|você) (?:pode|consegue) ajudar"
    r"|qual (?:e|é) (?:o )?seu (?:papel|nome))"
    r"[\s?!.]*$",
    re.IGNORECASE,
)
_RE_CONTINUACAO = re.compile(
    r"\b(?:e se|e sobre|mas|nesse caso|nessa caso|ent[aã]o|isso|aquilo|heranca|heran[cç]a)\b",
    re.IGNORECASE,
)
_RE_JURIDICO = re.compile(
    r"\b(?:imposto|itbi|iptu|ipva|icms|casa|im[oó]vel|pena|morte|artigo|art|"
    r"constitui[cç][aã]o|heran[cç]a|crime|furto|homic[ií]dio|habeas|direito|"
    r"lei|c[oó]digo|tributo|compra|comprar|vender|contrato|trabalho|sal[aá]rio|"
    r"uni[aã]o|munic[ií]pio|estado|stf|pec|emenda|j[uú]ri|pris[aã]o|anonimato|"
    r"usucapi[aã]o|minera[cç][aã]o|senado|c[aâ]mara|deputado|presidente|voto|"
    r"elei[cç][aã]o|clt|civil|penal|juiz|tribunal|inconstituc)\w*",
    re.IGNORECASE,
)

_RESPOSTAS = {
    "saudacao": (
        "Olá. Posso ajudar com dúvidas sobre a Constituição de 1988.",
        "Oi. Em que ponto da Constituição você quer conversar?",
        "Olá. Pode perguntar sobre um direito, um artigo ou um limite da Carta.",
    ),
    "agradecimento": (
        "Por nada. Se quiser, seguimos em outro ponto da Constituição.",
        "Disponha. Pode trazer a próxima dúvida quando quiser.",
        "Fico à disposição para outra pergunta sobre a Constituição.",
    ),
    "despedida": (
        "Até mais. Quando quiser retomar a Constituição, é só chamar.",
        "Tchau. Fico por aqui se surgir outra dúvida constitucional.",
    ),
    "meta": (
        "Eu converso sobre a Constituição de 1988. Trago o artigo quando a busca encontra base e digo com clareza quando o tema é de outra lei.",
        "Posso explicar um direito, um limite ou um artigo da Constituição de 1988, e separar o que está na Carta do que está em outra lei.",
        "Meu papel é ajudar a ler a Constituição de 1988. Pergunte sobre um tema e, se houver artigo aplicável, eu cito a fonte.",
    ),
}


def _normalizar(pergunta: str) -> str:
    texto = str(pergunta or "").strip().lower()
    texto = "".join(
        caractere for caractere in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(caractere)
    )
    return " ".join(texto.replace("?", " ? ").split())


def _sem_acento_original(pergunta: str) -> str:
    """Mantém a pontuação, só tira acento e espaços repetidos, para o regex casar a frase inteira."""
    texto = " ".join(str(pergunta or "").strip().split())
    return "".join(
        caractere for caractere in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(caractere)
    )


def _escolher(tipo: str, texto: str) -> str:
    opcoes = _RESPOSTAS[tipo]
    indice = sum(ord(caractere) for caractere in texto) % len(opcoes)
    return opcoes[indice]


def detectar_atalho_trivial(pergunta: str, historico: list[dict] | None = None) -> dict | None:
    """Devolve o tipo e a resposta pronta, ou None para seguir no RAG.

    historico entra só para não tratar continuação curta de uma dúvida
    anterior como saudação. A função não chama modelo nenhum.
    """
    del historico
    bruto = " ".join(str(pergunta or "").split())
    if not bruto or len(bruto.split()) > _LIMITE_PALAVRAS:
        return None
    comparavel = _sem_acento_original(bruto)
    if _RE_JURIDICO.search(comparavel) or _RE_CONTINUACAO.search(comparavel):
        return None
    if _RE_SAUDACAO.match(comparavel):
        tipo = "saudacao"
    elif _RE_AGRADECIMENTO.match(comparavel):
        tipo = "agradecimento"
    elif _RE_DESPEDIDA.match(comparavel):
        tipo = "despedida"
    elif _RE_META.match(comparavel):
        tipo = "meta"
    else:
        return None
    return {"tipo": tipo, "resposta": _escolher(tipo, _normalizar(bruto))}
