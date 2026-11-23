# -*- coding: utf-8 -*-
"""Duas chamadas curtas ao Ollama, só quando a busca directa não basta.

detectar_pergunta_composta é local e barato. decompor_consulta parte um
enunciado em 2 ou 3 frases. traduzir_para_juridico reescreve a dúvida no
estilo literal da Constituição, sem número de artigo e sem rótulo doutrinário.
"""

import re
import unicodedata

import requests

from src.rag.catalogo_modelos import modelo_suporta_think
from src.rag.gerador import (
    MODELO_PADRAO,
    NUM_CTX_AUX,
    TIMEOUT_LIGACAO_S,
    _eh_ollama,
    _url_ollama,
    configuracao_servidor,
    num_thread_ollama,
)

FORA = "FORA_CF88"
_TIMEOUT_LEITURA_S = 180

_PROMPT_TRADUTOR = (
    "Reescreva a pergunta do cidadão em 1 ou 2 frases curtas, no estilo "
    "normativo literal da Constituição Federal de 1988. Descreva a regra, "
    "a vedação, o direito ou o prazo perguntado, com verbos do texto "
    "constitucional, como 'é vedado instituir impostos sobre', 'é vedado "
    "cobrar tributos', 'são direitos dos trabalhadores urbanos e rurais' "
    "e 'compete a'. "
    "Preserve rigorosamente o fato concreto e específico perguntado. "
    "NUNCA generalize uma dúvida infraconstitucional específica, como prazo "
    "de devolução de produto, infração ou colisão de trânsito, pena de crime "
    "específico ou cláusula de contrato privado, para princípios "
    "constitucionais genéricos ou regras de competência legislativa. "
    "Não inclua número de artigo, inciso, parágrafo ou lei. Não use rótulo "
    "doutrinário nem sigla quando a regra pode ser dita por extenso. "
    "Devolva só o texto normativo, numa única linha, sem prefácio e sem aspas. "
    "Se a pergunta tratar de um fato cotidiano sem norma constitucional correspondente, "
    "NÃO force uma regra constitucional e NÃO troque o assunto para outro ramo do Direito, "
    "como tributos, impostos ou princípios genéricos. Apenas reescreva a própria dúvida "
    "de forma clara e formal, preservando exatamente o fato e o domínio original. "
    "Nunca copie nem reutilize frases dos exemplos em outra pergunta. "
    "Escreva sempre em forma declarativa (nunca em forma de pergunta); se a dúvida "
    "perguntar qual ente ou órgão tem competência ('quem cobra', 'a quem cabe'), "
    "use 'compete à União, aos Estados, ao Distrito Federal ou aos Municípios...', "
    "nunca 'é vedado...'."
)
CORTE_HYDE_COSSENO = 0.52
CORTE_HYDE_RERANKER = 0.002
_EXEMPLOS_HYDE = (
    (
        "Posso criar um perfil falso na internet para criticar alguém sem mostrar meu nome?",
        "é livre a manifestação do pensamento, sendo vedado o anonimato",
    ),
    (
        "O governo pode cobrar um imposto tão alto que tome quase todo o meu patrimônio?",
        "é vedado à União, aos Estados, ao Distrito Federal e aos Municípios utilizar tributo com efeito de confisco",
    ),
    (
        "Todo trabalhador registrado tem direito a um salário extra no fim do ano?",
        "direito dos trabalhadores urbanos e rurais ao décimo terceiro salário com base na remuneração integral",
    ),
    (
        "Se eu atrasar o aluguel do meu apartamento em dois dias, o dono pode trocar a fechadura?",
        "atraso no pagamento de aluguel residencial e retomada de imóvel pelo locador em contrato de locação",
    ),
)
_STOPWORDS = {
    "para", "como", "pelo", "pela", "pelos", "pelas", "entre", "sobre", "sem",
    "com", "que", "uma", "uns", "este", "esta", "esse", "essa", "isso", "isto",
    "todo", "toda", "todos", "todas", "sendo", "numa", "num", "desde", "ate",
    "apos", "contra", "sob", "seu", "sua", "seus", "suas", "dele", "dela",
    "eles", "elas", "nao", "nem", "mas", "pois", "porque", "quando", "onde",
    "quem", "qual", "quais", "mais", "muito", "pode", "podem", "sera", "ser",
    "ter", "tem", "foi", "sao", "dos", "das", "nos", "nas", "por", "aos",
}
_RE_THINK = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)
_RE_NUMERO_NORMATIVO = re.compile(
    r"\b(?:art\.?|artigo|inciso|par[aá]grafo|al[ií]nea)\s*\d*\s*[ºo°]?",
    re.IGNORECASE,
)

_PROMPT_DECOMPOSICAO = (
    "Quebre o enunciado em 2 ou 3 sub-consultas atômicas para busca na "
    "Constituição Federal de 1988, uma por instituto ou requisito pedido. "
    "Responda só as frases, uma por linha, sem numeração e sem explicação. "
    "Não passe de 3 linhas."
)

_MARCAS_COMPOSICAO = (
    "e qual",
    "além disso",
    "alem disso",
    "papel do",
    "papel da",
    "também",
    "tambem",
    "além de",
    "alem de",
    "ao mesmo tempo",
    "bem como",
)


def _plano(texto: str) -> str:
    base = unicodedata.normalize("NFKD", str(texto or ""))
    base = "".join(letra for letra in base if not unicodedata.combining(letra))
    return " ".join(base.lower().split())


_RE_SEGUNDO_QUESTIONAMENTO = re.compile(
    r"(?:,|;|\s)+(?:e|mas|porem)\s+"
    r"(?:qual|quais|como|quando|onde|quem|quanto|quantos|"
    r"ate\s+quando|em\s+que\s+prazo|existe|ha|pode)\b"
)
_RE_DUPLA_DEMANDA = re.compile(
    r"\b(?:alem\s+disso|tambem\s+(?:quero|gostaria|pode|existe|qual)|"
    r"e\s+tambem|ao\s+mesmo\s+tempo|por\s+outro\s+lado)\b"
)
_RE_INTERROGATIVA = re.compile(r"\b(?:qual|quais|como|quando|onde|quem|quanto|quantos)\b")


def _sinais(baixo: str) -> int:
    sinais = sum(baixo.count(marca) for marca in _MARCAS_COMPOSICAO)
    if baixo.count("?") >= 2:
        sinais += 1
    if len(re.findall(r"\b(?:e|ou|mas)\b", baixo)) >= 2:
        sinais += 1
    if len(re.findall(r"\b(?:qual|quais|como)\b", baixo)) >= 2:
        sinais += 1
    return sinais


def detectar_pergunta_composta(pergunta: str) -> bool:
    """Duas perguntas na mesma fala. Um único 'e' enumerativo continua simples."""
    texto = " ".join(str(pergunta or "").split())
    if not texto:
        return False
    baixo = _plano(texto)
    if baixo.count("?") >= 2:
        return True
    if _RE_SEGUNDO_QUESTIONAMENTO.search(baixo):
        return True
    if _RE_DUPLA_DEMANDA.search(baixo) and (baixo.count("?") >= 1 or _RE_INTERROGATIVA.search(baixo)):
        return True
    return len(texto.split()) >= 10 and _sinais(baixo) >= 2


def rejeitar_hyde_por_drift(cosseno: float, reranker: float) -> bool:
    """Descarte a reescrita quando ela troca o assunto da pergunta."""
    return float(reranker) < CORTE_HYDE_RERANKER or float(cosseno) < CORTE_HYDE_COSSENO


def deve_reforcar_apos_fora(margem: float, resposta: str) -> bool:
    """Roteador confiante não aceita um FORA_CF88 sem uma segunda tentativa."""
    try:
        folga = float(margem)
    except (TypeError, ValueError):
        return False
    return str(resposta or "").strip().upper() == FORA and folga >= 0.15


def _historico(historico: list[dict] | None) -> list[dict]:
    recente = []
    for mensagem in (historico or [])[-4:]:
        papel = mensagem.get("role")
        texto = str(mensagem.get("content") or "").strip()
        if papel not in ("user", "assistant") or not texto:
            continue
        if len(texto) > 280:
            texto = texto[:280].rstrip() + "..."
        recente.append({"role": papel, "content": texto})
    return recente


def _completar(
    mensagens: list[dict],
    num_predict: int,
    num_ctx: int,
    temperatura: float = 0.1,
    modelo: str | None = None,
) -> str:
    """Chamada curta, sem stream. Vazio se o Ollama não responder."""
    url, padrao = configuracao_servidor()
    modelo = modelo or padrao or MODELO_PADRAO
    destino = _url_ollama(url) if _eh_ollama(url) else url
    if _eh_ollama(url):
        corpo = {
            "model": modelo,
            "messages": mensagens,
            "stream": False,
            "keep_alive": "15m",
            "options": {
                "temperature": temperatura,
                "num_predict": num_predict,
                "num_ctx": num_ctx,
                "num_thread": num_thread_ollama(),
            },
        }
        if modelo_suporta_think(modelo):
            corpo["think"] = False
    else:
        corpo = {
            "model": modelo,
            "messages": mensagens,
            "temperature": temperatura,
            "max_tokens": num_predict,
            "stream": False,
        }
    try:
        resposta = requests.post(destino, json=corpo, timeout=(TIMEOUT_LIGACAO_S, _TIMEOUT_LEITURA_S))
    except requests.exceptions.RequestException:
        return ""
    if resposta.status_code != 200:
        return ""
    try:
        dados = resposta.json()
        if _eh_ollama(url):
            texto = str((dados.get("message") or {}).get("content") or "")
        else:
            texto = str(dados["choices"][0]["message"]["content"])
    except (ValueError, KeyError, IndexError, TypeError):
        return ""
    return texto.replace("\r\n", "\n").replace("\r", "\n")


def _linhas(texto: str) -> list[str]:
    frases = []
    for bruta in str(texto or "").splitlines():
        linha = re.sub(r"^[\s\d\)\.\-\*]+", "", bruta).strip()
        linha = " ".join(linha.split())
        if not linha or linha.upper().startswith(FORA):
            continue
        if linha not in frases:
            frases.append(linha)
        if len(frases) == 3:
            break
    return frases


def decompor_consulta(
    pergunta: str,
    historico: list[dict] | None = None,
    modelo: str | None = None,
) -> list[str]:
    """Devolve 2 ou 3 sub-consultas. Lista vazia se o modelo não partir o enunciado."""
    mensagens = [
        {"role": "system", "content": _PROMPT_DECOMPOSICAO},
        *_historico(historico),
        {"role": "user", "content": str(pergunta).strip()},
    ]
    texto = _completar(mensagens, num_predict=120, num_ctx=NUM_CTX_AUX, modelo=modelo)
    frases = _linhas(texto)
    if len(frases) < 2:
        return []
    return frases


def _termos_substantivos(texto: str) -> set[str]:
    return {termo for termo in re.findall(r"[a-z]{4,}", _plano(texto)) if termo not in _STOPWORDS}


def hyde_copiou_exemplo(pergunta: str, hyde: str) -> bool:
    """Verdadeiro quando a reescrita repete um exemplo que a pergunta não contém."""
    termos_hyde = _termos_substantivos(hyde)
    termos_pergunta = _termos_substantivos(pergunta)
    if not termos_hyde:
        return False
    for _, saida in _EXEMPLOS_HYDE:
        termos_exemplo = _termos_substantivos(saida)
        if not termos_exemplo:
            continue
        intersecao = termos_hyde & termos_exemplo
        if not intersecao or intersecao <= termos_pergunta:
            continue
        uniao = termos_hyde | termos_exemplo
        jaccard = len(intersecao) / len(uniao)
        cobertura = len(intersecao) / len(termos_exemplo)
        if max(jaccard, cobertura) >= 0.60:
            return True
    return False


def limpar_saida_tradutor(texto: str) -> str:
    """Tira raciocínio, aspas e número de artigo. A frase normativa fica."""
    limpo = _RE_THINK.sub(" ", str(texto or ""))
    limpo = limpo.replace("\n", " ").strip()
    limpo = limpo.strip("\"'“”«»")
    limpo = _RE_NUMERO_NORMATIVO.sub(" ", limpo)
    limpo = re.sub(r"\bFORA_CF88\b", " ", limpo, flags=re.IGNORECASE)
    limpo = " ".join(limpo.split())
    return re.sub(r"\?+$", "", limpo).strip()


def _mensagens_hyde(pergunta: str, historico: list[dict] | None, reforco: str | None = None) -> list[dict]:
    mensagens = [{"role": "system", "content": _PROMPT_TRADUTOR}]
    for entrada, saida in _EXEMPLOS_HYDE:
        mensagens.append({"role": "user", "content": entrada})
        mensagens.append({"role": "assistant", "content": saida})
    mensagens.extend(_historico(historico))
    pedido = str(pergunta).strip()
    if reforco:
        pedido = pedido + "\n\n" + reforco
    mensagens.append({"role": "user", "content": pedido})
    return mensagens


def traduzir_para_juridico(
    pergunta: str,
    historico: list[dict] | None = None,
    modelo: str | None = None,
) -> tuple[str, bool]:
    """Devolve a reescrita e se ela copiou um exemplo fixo."""
    primeira = limpar_saida_tradutor(
        _completar(_mensagens_hyde(pergunta, historico), num_predict=100, num_ctx=NUM_CTX_AUX, modelo=modelo)
    )
    if not hyde_copiou_exemplo(pergunta, primeira):
        return primeira, False
    segunda = limpar_saida_tradutor(
        _completar(
            _mensagens_hyde(
                pergunta,
                historico,
                "Reescreva apenas o assunto da pergunta do usuário, sem copiar exemplos.",
            ),
            num_predict=100,
            num_ctx=NUM_CTX_AUX,
            temperatura=0.2,
            modelo=modelo,
        )
    )
    if hyde_copiou_exemplo(pergunta, segunda):
        return "", True
    return segunda, False
