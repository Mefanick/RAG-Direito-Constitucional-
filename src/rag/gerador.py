# -*- coding: utf-8 -*-
"""Geração local no formato chat do Ollama.

LLM_URL e LLM_MODEL vêm do ambiente. O padrão é qwen3:8b em
127.0.0.1:11434/api/chat. O raciocínio, em message.thinking ou em
<think>, fica fora do texto mostrado no chat.
"""

import os
import re
import time
from typing import Any

import requests

from src.rag.catalogo_modelos import modelo_suporta_think

URL_PADRAO = "http://127.0.0.1:11434/api/chat"
MODELO_PADRAO = "qwen3:8b"
TEMPERATURA = 0.1
TOP_P = 0.9
MAX_TOKENS = 400
NUM_CTX = 3072
NUM_CTX_LIVRE = 2048
NUM_CTX_AUX = 2048
NUM_PREDICT_THINK_SIMPLES = 1200
NUM_PREDICT_THINK_COMPOSTA = 1600
NUM_PREDICT_RAG_SEM_THINK = 450
NUM_PREDICT_LIVRE = 360
AVISO_CONVERSA_LIVRE = (
    "Aviso: este tema não foi localizado na base constitucional carregada (CF/88). "
    "A explicação abaixo é apenas orientativa e não possui verificação normativa.\n\n"
)


def prefixar_aviso_livre(resposta: str) -> str:
    """Garante o aviso fixo no começo da conversa livre, sem duplicar."""
    texto = str(resposta or "").strip()
    if texto.startswith("Aviso: este tema não foi localizado na base constitucional carregada"):
        return texto
    return AVISO_CONVERSA_LIVRE + texto
# Calibrado no i5-1235U com flash attention e KV q8_0: 10 fios
# venceram 4, 6 e 8 no prefill e no decode. LLM_NUM_THREAD substitui isto.
NUM_THREAD_PADRAO = 10
TIMEOUT_LIGACAO_S = 2.0
TIMEOUT_LEITURA_S = 720.0

FRASE_SEM_BASE = "Não encontrei base suficiente nos artigos recuperados da Constituição"
PROMPT_LLM_PURO = (
    "Você é um assistente jurídico geral e responde em português, de forma clara e curta. "
    "Nesta conversa não há fontes recuperadas. Não invente número de artigo, inciso, "
    "parágrafo, alínea ou lei."
)

_RE_THINK_FECHADO = re.compile(r"<think\b[^>]*>(.*?)</think>", re.IGNORECASE | re.DOTALL)
_RE_THINK_ABERTO = re.compile(r"<think\b[^>]*>(.*)\Z", re.IGNORECASE | re.DOTALL)
_RE_FECHA_THINK = re.compile(r"</think>", re.IGNORECASE)


def configuracao_servidor() -> tuple[str, str]:
    """Lê o endereço e o modelo no momento da chamada."""
    url = os.getenv("LLM_URL", URL_PADRAO).strip() or URL_PADRAO
    modelo = os.getenv("LLM_MODEL", MODELO_PADRAO).strip() or MODELO_PADRAO
    return url, modelo


def separar_raciocinio(texto: str) -> tuple[str, str | None]:
    """Tira o pensamento do texto visível, mesmo com a tag aberta ou só o fechamento."""
    bruto = str(texto or "")
    pedacos: list[str] = []

    def guardar(miolo: str) -> None:
        limpo = str(miolo or "").strip()
        if limpo:
            pedacos.append(limpo)

    for bloco in _RE_THINK_FECHADO.finditer(bruto):
        guardar(bloco.group(1))
    sem_fechados = _RE_THINK_FECHADO.sub(" ", bruto)
    aberto = _RE_THINK_ABERTO.search(sem_fechados)
    if aberto:
        guardar(aberto.group(1))
        sem_fechados = sem_fechados[: aberto.start()]
    fecha = _RE_FECHA_THINK.search(sem_fechados)
    if fecha:
        guardar(sem_fechados[: fecha.start()])
        sem_fechados = sem_fechados[fecha.end() :]
    visivel = sem_fechados.strip()
    return visivel, ("\n\n".join(pedacos) if pedacos else None)


def _chars_uteis(texto: str) -> int:
    return len(re.sub(r"\s+", "", str(texto or "")))


def estourou_no_pensamento(visivel: str, pensamento: str | None) -> bool:
    """A resposta sumiu e só sobrou raciocínio."""
    return _chars_uteis(visivel) < 20 and bool(str(pensamento or "").strip())


def _com_diretiva_think(mensagens: list[dict], modelo: str, usar_think: bool) -> list[dict]:
    """O template do qwen3 abre <think> mesmo com think false. /no_think fecha esse bloco."""
    if usar_think or not modelo_suporta_think(modelo):
        return mensagens
    saida = [dict(item) for item in mensagens]
    for item in reversed(saida):
        if item.get("role") != "user":
            continue
        texto = str(item.get("content") or "").rstrip()
        if "/no_think" not in texto:
            item["content"] = texto + "\n/no_think"
        break
    return saida


def _eh_qwen3(modelo: str) -> bool:
    return "qwen3" in str(modelo or "").lower()


def num_thread_ollama() -> int:
    """Fios do Ollama. LLM_NUM_THREAD ganha do valor calibrado nesta máquina."""
    bruto = os.getenv("LLM_NUM_THREAD", "").strip()
    if bruto.isdigit() and int(bruto) >= 1:
        return int(bruto)
    return NUM_THREAD_PADRAO


def plano_geracao(
    modo: str,
    composta: bool = False,
    modelo: str | None = None,
    modo_raciocinio: str = "desligado",
    *,
    usar_think: bool = False,
) -> dict[str, Any]:
    """O raciocínio só liga quando usar_think vem verdadeiro. Zona cinzenta e composta não ligam sozinhas."""
    del composta, modo_raciocinio
    if not modelo:
        _, modelo = configuracao_servidor()
    think = bool(usar_think) and modelo_suporta_think(modelo)
    if modo == "MODO_LLM_PURO":
        return {
            "think": think,
            "num_predict": NUM_PREDICT_THINK_SIMPLES if think else NUM_PREDICT_RAG_SEM_THINK,
            "num_ctx": NUM_CTX_LIVRE,
            "temperature": 0.1,
            "modelo": modelo,
            "modo_raciocinio": "sempre" if think else "desligado",
            "usar_think": think,
        }
    if think:
        num_predict = NUM_PREDICT_THINK_SIMPLES
    elif modo == "MODO_CONVERSA_LIVRE":
        num_predict = NUM_PREDICT_LIVRE
    else:
        num_predict = NUM_PREDICT_RAG_SEM_THINK
    return {
        "think": think,
        "num_predict": num_predict,
        "num_ctx": NUM_CTX_LIVRE if modo == "MODO_CONVERSA_LIVRE" else NUM_CTX,
        "temperature": 0.5 if modo == "MODO_CONVERSA_LIVRE" else 0.2,
        "modelo": modelo,
        "modo_raciocinio": "sempre" if think else "desligado",
        "usar_think": think,
    }


def _ns_para_s(valor: Any) -> float | None:
    if valor is None:
        return None
    try:
        return float(valor) / 1_000_000_000.0
    except (TypeError, ValueError):
        return None


def _inteiro(valor: Any) -> int | None:
    if valor is None:
        return None
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def extrair_telemetria(
    dados: dict | None,
    usar_think: bool = False,
    think_s_medido: float | None = None,
    think_chars_brutos: int = 0,
) -> dict[str, Any]:
    """Lê prompt_eval_* e eval_* do /api/chat. Com think desligado, o raciocínio conta zero."""
    bruto = dados or {}
    tokens_entrada = _inteiro(bruto.get("prompt_eval_count"))
    tokens_saida = _inteiro(bruto.get("eval_count"))
    prefill_s = _ns_para_s(bruto.get("prompt_eval_duration"))
    decode_s = _ns_para_s(bruto.get("eval_duration"))
    tok_s = None
    if tokens_saida and decode_s and decode_s > 0:
        tok_s = tokens_saida / decode_s
    if usar_think:
        think_s = think_s_medido
        think_chars = int(think_chars_brutos or 0)
    else:
        think_s = 0.0
        think_chars = 0
    return {
        "tokens_entrada": tokens_entrada,
        "tokens_saida": tokens_saida,
        "prefill_s": prefill_s,
        "decode_s": decode_s,
        "tok_s": tok_s,
        "think_s": think_s,
        "think_chars": think_chars,
    }


def _pacote(
    resposta: str,
    modelo: str | None,
    raciocinio: str | None = None,
    tokens_prompt: int | None = None,
    tokens_resposta: int | None = None,
    erro: str | None = None,
    ttft_s: float | None = None,
    tempo_thinking_s: float | None = None,
    prefill_s: float | None = None,
    eval_s: float | None = None,
) -> dict[str, Any]:
    return {
        "resposta": resposta,
        "raciocinio": raciocinio,
        "modelo_usado": modelo,
        "tokens_prompt": tokens_prompt,
        "tokens_resposta": tokens_resposta,
        "erro": erro,
        "ttft_s": ttft_s,
        "tempo_thinking_s": tempo_thinking_s,
        "prefill_s": prefill_s,
        "tokens_entrada": tokens_prompt,
        "eval_s": eval_s,
        "decode_s": eval_s,
        "tok_s": None,
        "think_s": None,
        "think_chars": 0,
    }


def _fonte(indice: int, artigo: Any) -> str:
    if isinstance(artigo, dict):
        ident = str(artigo.get("artigo_id") or "?")
        try:
            score = float(artigo.get("score_reranker") or 0.0)
        except (TypeError, ValueError):
            score = 0.0
        texto = str(artigo.get("texto") or "")
    else:
        ident = "?"
        score = 0.0
        texto = str(artigo)
    return "[FONTE {} | {} | Relevância: {:.3f}]\n{}".format(indice, ident, score, texto)


def montar_prompt(pergunta: str, artigos: list, modo: str = "MODO_RAG_ALTA_CONFIANCA", historico: list[dict] | None = None) -> list[dict]:
    """Monta só o system e a pergunta atual. O histórico é aceito e ignorado."""
    del historico
    if modo == "MODO_LLM_PURO":
        return [
            {"role": "system", "content": PROMPT_LLM_PURO},
            {"role": "user", "content": str(pergunta).strip()},
        ]
    blocos = [_fonte(indice, artigo) for indice, artigo in enumerate(artigos, start=1)]
    contexto = "\n\n".join(blocos)
    if modo == "MODO_CONVERSA_LIVRE":
        sistema = (
            "Você está respondendo SEM fontes legais recuperadas no contexto. "
            "É ESTRITAMENTE PROIBIDO citar qualquer número de artigo, parágrafo, "
            "inciso, alínea ou número de lei (como 'Art. 5º', 'Art. 302', "
            "'Lei nº X' ou 'LC nº Y'). Você pode mencionar apenas o nome geral "
            "da legislação aplicável (ex.: Código de Defesa do Consumidor, "
            "Código de Trânsito Brasileiro, CLT) e explicar o conceito de forma "
            "clara e resumida em até 2 parágrafos curtos."
        )
        atual = pergunta
    elif modo == "MODO_RAG_ZONA_CINZENTA":
        sistema = (
            "Você conversa em português, de forma natural, sobre a Constituição "
            "de 1988. A resposta visível é um texto corrido, sem cabeçalho. "
            "O raciocínio fica só no bloco interno.\n"
            "Antes de responder, faça no raciocínio interno uma checagem breve "
            "e objetiva: (a) liste cada parte da pergunta; (b) mapeie qual "
            "trecho sustenta cada parte, copiando literalmente artigo, "
            "parágrafo, inciso e alínea como estão na fonte; (c) descarte de "
            "forma explícita os distratores que não respondem ao tema, por "
            "exemplo um trecho sobre tratados internacionais numa pergunta "
            "sobre cláusula pétrea; (d) revise se a conclusão não contradiz "
            "nenhuma frase anterior.\n"
            "Os trechos abaixo são possivelmente relacionados e têm baixa "
            "confiança. Se responderem de fato à pergunta, use-os e cite. "
            "Se não responderem, ignore-os e converse sem citar artigo.\n"
            "Só cite um parágrafo (§), um inciso romano (I, II, IV, XLVII) ou "
            "uma alínea (\"a\") se esse marcador estiver escrito explicitamente "
            "nos trechos. Preserve negações, exceções (\"vedado\", \"salvo\", "
            "\"exceto\") e todos os limites numéricos. Quando o trecho tratar "
            "apenas de um subconjunto (por exemplo, minérios nucleares), não "
            "comece com 'Sim' e deixe o limite explícito.\n"
            "Se a pergunta exigir um ponto jurídico consolidado que não esteja "
            "escrito expressamente no texto da Constituição (por exemplo, "
            "mandado de segurança preventivo impetrado por parlamentar no STF "
            "para trancar a tramitação de PEC violadora de cláusula pétrea), "
            "pode complementar com o entendimento consolidado do STF, desde que "
            "a fronteira fique explícita: 'Embora não conste expressamente na "
            "letra da Constituição, a jurisprudência consolidada do STF "
            "admite...'. Não invente número de artigo nem número de súmula que "
            "não esteja nos trechos."
        )
        atual = "Trechos possivelmente relacionados (baixa confiança):\n{}\n\nPergunta: {}".format(
            contexto or "(nenhum)", pergunta
        )
    else:
        sistema = (
            "Você conversa em português, de forma natural, sobre a Constituição "
            "de 1988. A resposta visível é um texto corrido, sem cabeçalho e "
            "sem checklist. O raciocínio fica só no bloco interno.\n"
            "Antes de responder, faça no raciocínio interno uma checagem breve "
            "e objetiva: (a) liste cada parte da pergunta; (b) mapeie qual "
            "fonte recuperada sustenta cada parte, copiando literalmente "
            "artigo, parágrafo, inciso e alínea como estão na fonte; "
            "(c) descarte de forma explícita os distratores que não respondem "
            "ao tema, por exemplo um trecho sobre tratados internacionais numa "
            "pergunta sobre cláusula pétrea; (d) revise se a conclusão não "
            "contradiz nenhuma frase anterior.\n"
            "Na resposta visível, use apenas as fontes. Responda a todas as "
            "partes do enunciado e integre a citação no meio da frase. Só cite "
            "um parágrafo (§), um inciso romano (I, II, IV, XLVII) ou uma "
            "alínea (\"a\") se esse marcador estiver escrito explicitamente nas "
            "fontes recuperadas. Preserve negações, exceções (\"vedado\", "
            "\"salvo\", \"exceto\") e todos os limites numéricos (hectares, "
            "anos, quóruns, idades, valores). Quando a fonte tratar apenas de "
            "um subconjunto específico do tema perguntado (por exemplo, "
            "minérios nucleares diante de uma pergunta sobre mineração em "
            "geral), NUNCA inicie a resposta com 'Sim'. Inicie restringindo o "
            "escopo: 'Nas fontes recuperadas, a regra aplica-se apenas a...; "
            "não há base para generalizar para...'.\n"
            "Se a pergunta exigir um ponto jurídico consolidado que não esteja "
            "escrito expressamente no texto da Constituição (por exemplo, "
            "mandado de segurança preventivo impetrado por parlamentar no STF "
            "para trancar a tramitação de PEC violadora de cláusula pétrea), "
            "pode complementar com o entendimento consolidado do STF, desde que "
            "a fronteira fique explícita: 'Embora não conste expressamente na "
            "letra da Constituição, a jurisprudência consolidada do STF "
            "admite...'. Não invente número de artigo nem número de súmula que "
            "não esteja nas fontes."
        )
        atual = "Fontes:\n{}\n\nPergunta: {}".format(contexto or "(nenhuma fonte)", pergunta)
    return [
        {"role": "system", "content": sistema},
        {"role": "user", "content": atual},
    ]


def _eh_ollama(url: str) -> bool:
    return ":11434" in url


def _url_ollama(url: str) -> str:
    limpa = url.rstrip("/")
    if limpa.endswith("/api/chat"):
        return limpa
    base = limpa.split("/v1/")[0].rstrip("/")
    return base + "/api/chat"


def _opcoes_ollama(temperatura: float = 0.2, num_predict: int = NUM_PREDICT_RAG_SEM_THINK, num_ctx: int = NUM_CTX) -> dict[str, Any]:
    return {
        "temperature": temperatura,
        "top_p": TOP_P,
        "num_predict": num_predict,
        "num_ctx": num_ctx,
        "num_thread": num_thread_ollama(),
    }


def _corpo_openai(
    modelo: str,
    mensagens: list[dict],
    stream: bool,
    temperatura: float,
    num_predict: int,
) -> dict[str, Any]:
    return {
        "model": modelo,
        "temperature": temperatura,
        "top_p": TOP_P,
        "max_tokens": num_predict,
        "stream": stream,
        "messages": mensagens,
    }


def _corpo_ollama(
    modelo: str,
    mensagens: list[dict],
    stream: bool,
    temperatura: float,
    num_predict: int,
    num_ctx: int,
    think: bool | None = None,
) -> dict[str, Any]:
    corpo = {
        "model": modelo,
        "messages": mensagens,
        "stream": stream,
        "keep_alive": "15m",
        "options": _opcoes_ollama(temperatura, num_predict, num_ctx),
    }
    if think is not None and modelo_suporta_think(modelo):
        corpo["think"] = bool(think)
    return corpo


def _texto_visivel(acumulado: str) -> str:
    visivel, _ = separar_raciocinio(acumulado)
    return visivel.strip()


def _visivel_novo(acumulado: str, ja_emitido: int) -> tuple[str, int, bool]:
    """Devolve o pedaço visível ainda não enviado e se há um <think> aberto."""
    visivel, _ = separar_raciocinio(acumulado)
    aberto = "<think" in acumulado.lower() and "</think>" not in acumulado.lower()
    if aberto or not visivel:
        if aberto:
            return "", ja_emitido, True
    if len(visivel) <= ja_emitido:
        return "", ja_emitido, False
    return visivel[ja_emitido:], len(visivel), False


def _ler_fluxo(
    resposta: requests.Response,
    inicio: float,
    on_token,
    on_etapa,
    ollama: bool,
) -> tuple[str, str | None, float | None, float | None, int | None, int | None]:
    import json

    conteudo = []
    pensado = []
    emitido = 0
    ttft = None
    inicio_think = None
    fim_think = None
    avisou = False
    tokens_prompt = None
    tokens_resposta = None
    prefill_s = None
    eval_s = None
    for linha in resposta.iter_lines():
        if not linha:
            continue
        if isinstance(linha, bytes):
            linha = linha.decode("utf-8")
        trecho = linha[5:].strip() if linha.startswith("data:") else linha
        if trecho == "[DONE]":
            break
        try:
            dados = json.loads(trecho)
        except json.JSONDecodeError:
            continue
        if ollama:
            mensagem = dados.get("message") or {}
            pensamento = str(mensagem.get("thinking") or "")
            pedaco = str(mensagem.get("content") or "")
            if dados.get("done"):
                tokens_prompt = dados.get("prompt_eval_count")
                tokens_resposta = dados.get("eval_count")
                prefill_s = _ns_para_s(dados.get("prompt_eval_duration"))
                eval_s = _ns_para_s(dados.get("eval_duration"))
        else:
            pensamento = ""
            escolhas = dados.get("choices") or []
            delta = (escolhas[0].get("delta") or {}) if escolhas else {}
            pedaco = str(delta.get("content") or "")
            uso = dados.get("usage") or {}
            if uso.get("prompt_tokens") is not None:
                tokens_prompt = uso.get("prompt_tokens")
            if uso.get("completion_tokens") is not None:
                tokens_resposta = uso.get("completion_tokens")
        if pensamento:
            if inicio_think is None:
                inicio_think = time.perf_counter()
            if not avisou and on_etapa is not None:
                on_etapa("Verificando dispositivos e raciocínio jurídico...")
                avisou = True
            pensado.append(pensamento)
        if not pedaco:
            continue
        conteudo.append(pedaco)
        texto_parcial = "".join(conteudo)
        novo, emitido, aberto = _visivel_novo(texto_parcial, emitido)
        if (aberto or "<think>" in texto_parcial.lower()) and not avisou and on_etapa is not None:
            on_etapa("Verificando dispositivos e raciocínio jurídico...")
            avisou = True
            if inicio_think is None:
                inicio_think = time.perf_counter()
        if not novo:
            continue
        if inicio_think is not None and fim_think is None:
            fim_think = time.perf_counter()
        if ttft is None and ("".join(conteudo) and separar_raciocinio("".join(conteudo))[0].strip()):
            ttft = time.perf_counter() - inicio
        if on_token is not None:
            on_token(novo)
    texto = "".join(conteudo)
    visivel, interno = separar_raciocinio(texto)
    blocos = [parte.strip() for parte in pensado if parte.strip()]
    if interno:
        blocos.append(interno)
    if inicio_think is not None and fim_think is None:
        fim_think = time.perf_counter()
    tempo_think = None if inicio_think is None or fim_think is None else fim_think - inicio_think
    return {
        "visivel": visivel,
        "raciocinio": "\n\n".join(blocos) or None,
        "ttft_s": ttft,
        "tempo_thinking_s": tempo_think,
        "tokens_prompt": tokens_prompt,
        "tokens_resposta": tokens_resposta,
        "prefill_s": prefill_s,
        "eval_s": eval_s,
    }


def gerar_resposta(
    pergunta: str,
    artigos: list,
    stream: bool = False,
    on_token=None,
    historico: list[dict] | None = None,
    modo: str = "MODO_RAG_ALTA_CONFIANCA",
    composta: bool = False,
    num_predict: int | None = None,
    num_ctx: int | None = None,
    on_etapa=None,
    think: bool | None = None,
    modo_raciocinio: str = "desligado",
    usar_think: bool = False,
    modelo: str | None = None,
    _sem_repetir: bool = False,
) -> dict[str, Any]:
    """Chama o servidor local e devolve a resposta já sem o bloco de raciocínio.

    No Ollama a chamada vai para /api/chat, com o modelo mantido na RAM.
    Falha de ligação ou de leitura volta no campo erro. O prompt não é impresso.
    """
    if pergunta is None or not str(pergunta).strip():
        raise ValueError("A pergunta para o gerador está vazia.")

    url, modelo_ambiente = configuracao_servidor()
    modelo = modelo or modelo_ambiente
    ligado = bool(usar_think) if think is None else bool(think)
    if not modelo_suporta_think(modelo):
        ligado = False
    plano = plano_geracao(modo, composta, modelo, modo_raciocinio, usar_think=ligado)
    temperatura = plano["temperature"]
    teto = num_predict if num_predict is not None else plano["num_predict"]
    contexto = num_ctx if num_ctx is not None else plano["num_ctx"]
    usar_think = plano["think"]
    mensagens = _com_diretiva_think(
        montar_prompt(str(pergunta), list(artigos), modo, historico),
        modelo,
        usar_think,
    )
    ollama = _eh_ollama(url)
    destino = _url_ollama(url) if ollama else url
    corpo = (
        _corpo_ollama(modelo, mensagens, stream, temperatura, teto, contexto, usar_think)
        if ollama
        else _corpo_openai(modelo, mensagens, stream, temperatura, teto)
    )
    inicio = time.perf_counter()
    try:
        resposta = requests.post(
            destino,
            json=corpo,
            timeout=(TIMEOUT_LIGACAO_S, TIMEOUT_LEITURA_S),
            stream=stream,
        )
    except requests.exceptions.RequestException as exc:
        return _pacote("", modelo, erro="Falha de conexão com {}: {}".format(destino, type(exc).__name__))

    if resposta.status_code != 200:
        return _pacote("", modelo, erro="O servidor local respondeu com HTTP {}.".format(resposta.status_code))

    fluxo = {
        "visivel": "",
        "raciocinio": None,
        "ttft_s": None,
        "tempo_thinking_s": None,
        "tokens_prompt": None,
        "tokens_resposta": None,
        "prefill_s": None,
        "eval_s": None,
    }
    try:
        if stream:
            fluxo = _ler_fluxo(resposta, inicio, on_token, on_etapa, ollama)
            dados = {}
        else:
            dados = resposta.json()
            if ollama:
                mensagem = dados.get("message") or {}
                bruto = str(mensagem.get("content") or "")
                pensado = str(mensagem.get("thinking") or "").strip()
                fluxo["tokens_prompt"] = dados.get("prompt_eval_count")
                fluxo["tokens_resposta"] = dados.get("eval_count")
                fluxo["prefill_s"] = _ns_para_s(dados.get("prompt_eval_duration"))
                fluxo["eval_s"] = _ns_para_s(dados.get("eval_duration"))
            else:
                pensado = ""
                bruto = str(dados["choices"][0]["message"]["content"])
                uso = dados.get("usage") if isinstance(dados.get("usage"), dict) else {}
                fluxo["tokens_prompt"] = uso.get("prompt_tokens")
                fluxo["tokens_resposta"] = uso.get("completion_tokens")
            visivel, interno = separar_raciocinio(bruto)
            # message.thinking nunca entra na resposta. Só nos metadados.
            blocos = [parte for parte in (pensado, interno) if parte]
            fluxo["visivel"] = visivel
            fluxo["raciocinio"] = "\n\n".join(blocos) or None
            fluxo["estourou_no_think"] = estourou_no_pensamento(visivel, fluxo["raciocinio"])
            if fluxo["estourou_no_think"]:
                fluxo["visivel"] = ""
    except (ValueError, KeyError, IndexError, TypeError):
        return _pacote("", modelo, erro="O servidor local respondeu sem o texto da escolha.")

    if not fluxo.get("estourou_no_think"):
        fluxo["estourou_no_think"] = estourou_no_pensamento(
            fluxo.get("visivel") or "",
            fluxo.get("raciocinio"),
        )
    if fluxo["estourou_no_think"]:
        fluxo["visivel"] = ""

    raciocinio = fluxo.get("raciocinio")
    if ollama and not stream:
        bruto_tele = dados
    else:
        bruto_tele = {
            "prompt_eval_count": fluxo.get("tokens_prompt"),
            "eval_count": fluxo.get("tokens_resposta"),
            "prompt_eval_duration": None if fluxo.get("prefill_s") is None else float(fluxo["prefill_s"]) * 1_000_000_000,
            "eval_duration": None if fluxo.get("eval_s") is None else float(fluxo["eval_s"]) * 1_000_000_000,
        }
    tele = extrair_telemetria(
        bruto_tele,
        usar_think=usar_think,
        think_s_medido=fluxo.get("tempo_thinking_s"),
        think_chars_brutos=len(raciocinio or ""),
    )
    pacote = _pacote(
        fluxo.get("visivel") or "",
        str(dados.get("model") or modelo) if not stream else modelo,
        raciocinio=None if not usar_think else raciocinio,
        tokens_prompt=tele["tokens_entrada"],
        tokens_resposta=tele["tokens_saida"],
        ttft_s=fluxo.get("ttft_s"),
        tempo_thinking_s=tele["think_s"],
        prefill_s=tele["prefill_s"],
        eval_s=tele["decode_s"],
    )
    pacote["tok_s"] = tele["tok_s"]
    pacote["think_s"] = tele["think_s"]
    pacote["think_chars"] = tele["think_chars"]
    pacote["usar_think"] = usar_think
    pacote["estourou_no_think"] = bool(fluxo.get("estourou_no_think"))
    if pacote["estourou_no_think"] and usar_think and not _sem_repetir:
        repetido = gerar_resposta(
            pergunta,
            artigos,
            stream=False,
            historico=[],
            modo=modo,
            composta=composta,
            num_predict=NUM_PREDICT_RAG_SEM_THINK,
            num_ctx=num_ctx,
            think=False,
            usar_think=False,
            modelo=modelo,
            _sem_repetir=True,
        )
        repetido["estourou_no_think"] = True
        return repetido
    return pacote
