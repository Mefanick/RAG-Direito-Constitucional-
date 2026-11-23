# -*- coding: utf-8 -*-
"""Gera uma linha cotidiana por chunk e grava um cache retomável.

Não altera o texto oficial. Não conhece as perguntas da bateria cega.
--modo prioritario percorre os blocos de maior uso. --modo completo
completa o que ainda falta. --modo enxuto fica nos blocos de procura diária.
--artigos limita o ensaio a identificadores exatos.
"""

import argparse
import hashlib
import json
import re
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path

import requests
import torch

_RAIZ = Path(__file__).resolve().parents[2]
if str(_RAIZ) not in sys.path:
    sys.path.insert(0, str(_RAIZ))

_PKL = _RAIZ / "modelos" / "constituicao_vetorizada.pkl"
_CACHE = _RAIZ / "modelos" / "ponte_leiga_cache.jsonl"
_ERROS = _RAIZ / "modelos" / "ponte_leiga_erros.log"
_PISO_REMISSIVO = 55
_URL = "http://127.0.0.1:11434/api/chat"
_TAGS = "http://127.0.0.1:11434/api/tags"

_INTENCOES_PRIORITARIAS = {
    "Princípios Fundamentais",
    "Direitos e Garantias Fundamentais",
    "Tributação e Orçamento",
    "Ordem Social",
    "Ordem Econômica e Financeira",
    "Disposições Gerais / ADCT",
}
_ARTIGOS_NUCLEARES = set(range(37, 42)) | set(range(60, 63)) | {102, 103}

_PROMPT = (
    "Você traduz um dispositivo da Constituição para termos curtos de busca. "
    "Produza entre 4 e 12 termos curtos de busca, de 2 a 5 palavras por item, "
    "separados por vírgula, em quantidade proporcional às regras realmente presentes no trecho. "
    "Nunca invente situações extras nem repita a mesma ideia só para alongar a lista. "
    "Traduza o juridiquês para o português cotidiano. "
    "Sem frase completa. Sem pergunta. Sem ponto de interrogação. "
    "Não comece por quem, como, o que, qual, quando, onde ou por que. "
    "Não cite artigo, inciso, parágrafo, alínea nem número de artigo. "
    "Se o dispositivo trouxer vedação ou imunidade, preserve a negação ou a isenção. "
    "Nunca inverta uma proibição em permissão ou cobrança. "
    "Nunca generalize uma regra restrita. Se a proibição ou imunidade valer apenas entre entes públicos "
    "('uns dos outros'), explicite 'entre governos' ou 'imunidade recíproca'. "
    "Nunca escreva que o imposto é proibido em geral. "
    "Se a regra exigir ato pago ou oneroso, não inclua atos gratuitos. "
    "Se houver exceção expressa, não inclua a exceção como regra. "
    "Quando o dispositivo enumerar vários itens ou alíneas, dedique 1 termo curto a cada item principal até o fim do texto, sem repetir o primeiro. "
    "Inclua a sigla ou o nome popular consagrado apenas quando corresponder exatamente ao instituto do texto. "
    "Nunca misture termos dos exemplos. "
    "Converta expressões formais e latim jurídico para a forma como um cidadão comum pesquisaria na internet. "
    "Evite repetir palavras técnicas do próprio trecho quando existir equivalente popular direto. "
    "Quando o texto restringir uma regra a uma condição (como 'uns dos outros', 'por ato oneroso', 'sem fins lucrativos'), "
    "o qualificador em português simples deve aparecer dentro do próprio termo curto, nunca solto ou omitido."
)
_EXEMPLO_1 = "é livre a manifestação do pensamento, sendo vedado o anonimato"
_SAIDA_1 = "liberdade de expressão, opinião pública livre, proibição de anonimato, perfil anônimo vedado"
_EXEMPLO_2 = (
    "é vedado à União, aos Estados, ao Distrito Federal e aos Municípios "
    "utilizar tributo com efeito de confisco"
)
_SAIDA_2 = "proibição de imposto confiscatório, tributo abusivo vedado, limite contra confisco tributário"
_EXEMPLO_3 = "décimo terceiro salário com base na remuneração integral ou no valor da aposentadoria"
_SAIDA_3 = "décimo terceiro salário, 13º salário integral, gratificação natalina, 13º na aposentadoria"
_RE_PROIBIDO = re.compile(
    r"\b(?:art\.?|artigo|inciso|par[aá]grafo|al[ií]nea)\s*\d*",
    re.IGNORECASE,
)
_INICIOS = ("quem ", "como ", "o que ", "qual ", "quando ", "onde ", "por que ", "porque ")
_RE_THINK = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)
_REFORCO = "Responda apenas termos separados por vírgula, sem perguntas e sem citar artigo."


def _modelos() -> list[str]:
    resposta = requests.get(_TAGS, timeout=5)
    resposta.raise_for_status()
    return [str(item.get("name") or "") for item in resposta.json().get("models") or []]


def _escolher_modelo(pedido: str | None) -> str:
    if pedido:
        return pedido
    nomes = _modelos()
    if any(nome.startswith("qwen3:8b") for nome in nomes):
        return "qwen3:8b"
    if any(nome.startswith("qwen2.5:3b") for nome in nomes):
        return "qwen2.5:3b"
    raise RuntimeError("Nenhum de qwen3:8b ou qwen2.5:3b está no Ollama.")


def _numero_artigo(artigo_id: str) -> int | None:
    if re.search(r"Art\.\s*103-A", artigo_id, re.IGNORECASE):
        return None
    achado = re.search(r"Art\.\s*(\d+)", artigo_id)
    if not achado:
        return None
    return int(achado.group(1))


def _enxuto(artigo_id: str) -> bool:
    ident = str(artigo_id)
    if re.search(r"ADCT", ident, re.IGNORECASE) and re.search(r"Art\.\s*10\b", ident):
        return True
    numero = _numero_artigo(ident)
    if numero is None:
        return False
    return numero in set(range(5, 18)) | set(range(145, 163)) | set(range(170, 192)) | set(range(196, 215))


def _prioritario(artigo_id: str, intencao: str) -> bool:
    if intencao in _INTENCOES_PRIORITARIAS:
        return True
    numero = _numero_artigo(artigo_id)
    return numero in _ARTIGOS_NUCLEARES


def _hash_texto(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:12]


def _avisar_erro(mensagem: str) -> None:
    linha = "{} {}".format(datetime.now().isoformat(timespec="seconds"), mensagem)
    print(linha, flush=True)
    _ERROS.parent.mkdir(parents=True, exist_ok=True)
    with _ERROS.open("a", encoding="utf-8") as ficheiro:
        ficheiro.write(linha + "\n")
        ficheiro.flush()


def _registros_cache() -> list[dict]:
    if not _CACHE.is_file():
        return []
    brutas = _CACHE.read_text(encoding="utf-8").splitlines()
    registros = []
    for posicao, linha in enumerate(brutas):
        if not linha.strip():
            continue
        try:
            item = json.loads(linha)
            registros.append(item)
        except json.JSONDecodeError:
            if posicao == len(brutas) - 1:
                _avisar_erro("Última linha do cache está truncada e foi ignorada.")
                continue
            raise
    return registros


def _gravar_cache(registros: list[dict]) -> None:
    _CACHE.parent.mkdir(parents=True, exist_ok=True)
    _CACHE.write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in registros),
        encoding="utf-8",
    )


def _backfill_hash(textos: list[str]) -> None:
    registros = _registros_cache()
    mudou = False
    for item in registros:
        if item.get("texto_hash"):
            continue
        indice = int(item["chunk_idx"])
        item["texto_hash"] = _hash_texto(textos[indice])
        mudou = True
    if mudou:
        _gravar_cache(registros)
        print("texto_hash preenchido em {} registro(s) já existentes.".format(len(registros)), flush=True)


def _ja_gravados() -> set[int]:
    return {int(item["chunk_idx"]) for item in _registros_cache() if "chunk_idx" in item}


def _sem_acento(texto: str) -> str:
    base = unicodedata.normalize("NFKD", texto)
    return "".join(letra for letra in base if not unicodedata.combining(letra)).lower()


def _colapsar(texto: str) -> str:
    return " ".join(str(texto or "").split())


def _trecho_proprio(texto: str) -> str:
    colapsado = _colapsar(texto)
    if " | " in colapsado:
        return colapsado.split(" | ", 1)[1].strip()
    return colapsado


def _remissivo(texto: str) -> bool:
    completo = _colapsar(texto)
    if len(completo) < _PISO_REMISSIVO:
        return True
    base = _sem_acento(_trecho_proprio(texto))
    if re.search(r"\b(?:revogad[oa]|vetad[oa])\b", base):
        resto = re.sub(r"\b(?:revogad[oa]|vetad[oa])\b", " ", base)
        resto = re.sub(r"[^a-z\s]", " ", resto)
        if len([palavra for palavra in resto.split() if len(palavra) > 3]) <= 4:
            return True
    if "ate que seja promulgada a lei complementar" in base and not re.search(
        r"\b(?:fica|ficam|vedad|assegura|garante|dispensa|gestante|empregad)\b",
        base,
    ):
        return True
    return False


def _mensagens(texto: str, reforco: str | None = None) -> list[dict]:
    usuario = texto if not reforco else texto + "\n\n" + reforco
    return [
        {"role": "system", "content": _PROMPT},
        {"role": "user", "content": _EXEMPLO_1},
        {"role": "assistant", "content": _SAIDA_1},
        {"role": "user", "content": _EXEMPLO_2},
        {"role": "assistant", "content": _SAIDA_2},
        {"role": "user", "content": _EXEMPLO_3},
        {"role": "assistant", "content": _SAIDA_3},
        {"role": "user", "content": usuario},
    ]


def _chamar(texto: str, modelo: str, reforco: str | None = None) -> tuple[str, str]:
    corpo = {
        "model": modelo,
        "messages": _mensagens(texto, reforco),
        "stream": False,
        "keep_alive": "30m",
        "options": {
            "temperature": 0.15,
            "num_ctx": 2048,
            "num_predict": 90,
            "num_thread": 10,
        },
    }
    if "qwen3" in modelo.lower():
        corpo["think"] = False
    resposta = requests.post(_URL, json=corpo, timeout=(5, 240))
    resposta.raise_for_status()
    dados = resposta.json()
    bruto = str((dados.get("message") or {}).get("content") or "")
    bruto = _RE_THINK.sub(" ", bruto)
    if bruto.count(",") < 3 and "\n" in bruto:
        bruto = bruto.replace("\n", ", ")
    return _colapsar(bruto), str(dados.get("done_reason") or "")


def _item_ruim(parte: str) -> bool:
    baixo = parte.lower().strip()
    if not baixo or "?" in baixo:
        return True
    return baixo.startswith(_INICIOS)


def _podar(frase: str, cortada: bool) -> str:
    frase = _RE_PROIBIDO.sub(" ", frase).replace("?", " ")
    if cortada and "," in frase:
        frase = frase.rsplit(",", 1)[0]
    termos = []
    for parte in frase.split(","):
        parte = parte.strip(" \"'`-;.")
        parte = _colapsar(parte)
        if parte and not _item_ruim(parte) and not _RE_PROIBIDO.search(parte):
            termos.append(parte)
    return ", ".join(termos)


def _aceitavel(frase: str) -> bool:
    if not frase or "?" in frase or _RE_PROIBIDO.search(frase):
        return False
    return not any(_item_ruim(parte) for parte in frase.split(","))


def _linha(texto: str, modelo: str) -> str:
    frase, motivo = _chamar(texto, modelo)
    frase = _podar(frase, motivo == "length")
    if _aceitavel(frase):
        return frase
    frase, motivo = _chamar(texto, modelo, _REFORCO)
    frase = _podar(frase, motivo == "length")
    if _aceitavel(frase):
        return frase
    return _podar(frase, False)


def _descarregar(modelo: str) -> None:
    try:
        requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={"model": modelo, "keep_alive": 0},
            timeout=30,
        )
        print("{} descarregado da RAM.".format(modelo), flush=True)
    except requests.RequestException as exc:
        print("Não foi possível descarregar {}: {}".format(modelo, exc), flush=True)


def _norm_id(valor: str) -> str:
    return re.sub(r"\s+", " ", str(valor).strip()).casefold().replace(",", "")


def _indice_pedido(pedido: str, ids: list[str]) -> int:
    alvo = _norm_id(pedido)
    for indice, artigo_id in enumerate(ids):
        if _norm_id(artigo_id) == alvo:
            return indice
    raise SystemExit("Não achei o chunk exato de {}.".format(pedido))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--modo", choices=("prioritario", "completo", "enxuto"))
    parser.add_argument("--limite", type=int, default=0)
    parser.add_argument("--artigos", nargs="*")
    parser.add_argument("--modelo", default="")
    args = parser.parse_args()
    if not args.modo and not args.artigos:
        raise SystemExit("Informe --modo ou --artigos.")
    if not _PKL.is_file():
        raise FileNotFoundError("Índice não encontrado em {}.".format(_PKL))
    cache = torch.load(_PKL, weights_only=False)
    textos = list(cache["textos"])
    ids = list(cache["artigo_ids"])
    intencoes = list(cache["intencoes"])
    _backfill_hash(textos)
    enxutos = [i for i in range(len(textos)) if _enxuto(ids[i])]
    n_prioritario = sum(1 for i in range(len(textos)) if _prioritario(ids[i], intencoes[i]))
    n_enxuto_pular = sum(1 for i in enxutos if _remissivo(textos[i]))
    print(
        "Chunks prioritários: {}. Chunks enxutos: {}. Enxutos sem inferência (remissivos ou curtos): {}.".format(
            n_prioritario, len(enxutos), n_enxuto_pular
        ),
        flush=True,
    )
    if args.artigos:
        fila = [_indice_pedido(pedido, ids) for pedido in args.artigos]
        nome_modo = "artigos"
    elif args.modo == "prioritario":
        fila = [i for i in range(len(textos)) if _prioritario(ids[i], intencoes[i])]
        nome_modo = args.modo
    elif args.modo == "enxuto":
        fila = enxutos
        nome_modo = args.modo
    else:
        fila = list(range(len(textos)))
        nome_modo = "completo"
    prontos = _ja_gravados()
    pendentes = [i for i in fila if i not in prontos]
    if args.limite and args.limite > 0:
        pendentes = pendentes[: args.limite]
    print("Chunks no modo {}: {}".format(nome_modo, len(fila)), flush=True)
    print("Já no cache: {}. A processar agora: {}.".format(len(prontos), len(pendentes)), flush=True)
    if not pendentes:
        return
    modelo = _escolher_modelo(args.modelo or None)
    print("Modelo da ponte: {}".format(modelo), flush=True)
    _CACHE.parent.mkdir(parents=True, exist_ok=True)
    tempos_llm: list[float] = []
    with _CACHE.open("a", encoding="utf-8") as saida:
        for ordem, indice in enumerate(pendentes, start=1):
            t0 = time.perf_counter()
            if _remissivo(textos[indice]):
                frase = ""
                fase = "sem LLM"
            else:
                try:
                    frase = _linha(textos[indice], modelo)
                except requests.RequestException as exc:
                    _avisar_erro(
                        "idx {} {} não gravado: {}".format(indice, ids[indice], exc)
                    )
                    continue
                fase = "frio" if not tempos_llm else "quente"
            decorrido = time.perf_counter() - t0
            if fase != "sem LLM":
                tempos_llm.append(decorrido)
            registro = {
                "chunk_idx": indice,
                "artigo_id": ids[indice],
                "texto_hash": _hash_texto(textos[indice]),
                "ponte_leiga": frase,
            }
            saida.write(json.dumps(registro, ensure_ascii=False) + "\n")
            saida.flush()
            print(
                "[{}/{}] idx {} {} {} {:.2f}s {}".format(
                    ordem, len(pendentes), indice, ids[indice], fase, decorrido, frase or "(vazia)"
                ),
                flush=True,
            )
    if tempos_llm:
        frio = tempos_llm[0]
        quentes = tempos_llm[1:]
        media_quente = sum(quentes) / len(quentes) if quentes else frio
        substantivos = len(enxutos) - n_enxuto_pular
        print(
            "Frio: {:.2f}s. Quente médio: {:.2f}s em {} chunks.".format(frio, media_quente, len(quentes)),
            flush=True,
        )
        print(
            "ETA do modo enxuto: {:.1f} min para {} chunks com inferência ({} de {} são remissivos ou curtos e não chamam o modelo).".format(
                substantivos * media_quente / 60.0,
                substantivos,
                n_enxuto_pular,
                len(enxutos),
            ),
            flush=True,
        )
    _descarregar(modelo)


if __name__ == "__main__":
    main()
