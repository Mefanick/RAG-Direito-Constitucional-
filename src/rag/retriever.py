# -*- coding: utf-8 -*-
"""Busca densa com bónus de capítulo e reranker.

O índice e os dois modelos nascem no import. A classe prevista não
apaga os outros capítulos: soma 0,05 ao cosseno. Os 8 melhores desse
ranking passam pelo cross-encoder. Só segue quem passa de 0,25.
"""

import re
from pathlib import Path
from typing import Any, TypedDict

import torch
from sentence_transformers import util

from src.rag.encoder import gerar_embedding, obter_encoder, reordenar_pares

_RAIZ = Path(__file__).resolve().parents[2]
_ARTEFACTO = _RAIZ / "modelos" / "constituicao_vetorizada.pkl"


class ChunkRecuperado(TypedDict):
    artigo_id: str
    texto: str
    score_cosseno: float
    score_reranker: float
    origem: str


class BuscaContexto(TypedDict):
    modo_busca: str
    resultados: list[ChunkRecuperado]
    top_candidatos_brutos: list[dict]
    top1_score: float


def _carregar_indice() -> dict:
    if not _ARTEFACTO.is_file():
        raise FileNotFoundError(
            "Índice não encontrado em {}. Rode antes: python -m src.rag.indexador_offline".format(
                _ARTEFACTO
            )
        )
    cache = torch.load(_ARTEFACTO, weights_only=False)
    obrigatorias = ("textos", "intencoes", "artigo_ids", "embeddings")
    faltam = [chave for chave in obrigatorias if chave not in cache]
    if faltam:
        raise ValueError("O índice não tem as chaves {}.".format(", ".join(faltam)))
    embeddings = cache["embeddings"]
    if not isinstance(embeddings, torch.Tensor):
        embeddings = torch.as_tensor(embeddings)
    n = len(cache["textos"])
    if not (n == len(cache["intencoes"]) == len(cache["artigo_ids"]) == int(embeddings.shape[0])):
        raise ValueError("O índice constitucional está inconsistente.")
    cache["embeddings"] = embeddings
    return cache


_CACHE = _carregar_indice()
_TEXTOS: list[str] = list(_CACHE["textos"])
_BUSCA = _CACHE.get("textos_busca")
_TEXTOS_BUSCA: list[str] = list(_BUSCA) if isinstance(_BUSCA, list) and len(_BUSCA) == len(_TEXTOS) else list(_TEXTOS)
_INTENCOES: list[str] = list(_CACHE["intencoes"])
_ARTIGO_IDS: list[str] = list(_CACHE["artigo_ids"])
_EMBEDDINGS: torch.Tensor = _CACHE["embeddings"]
_ID_PARA_INDICE: dict[str, int] = {}
for _posicao, _ident in enumerate(_ARTIGO_IDS):
    _ID_PARA_INDICE.setdefault(_ident, _posicao)
_ENCODER = obter_encoder()


def _como_tensor(embedding: Any) -> torch.Tensor:
    if isinstance(embedding, torch.Tensor):
        return embedding
    return torch.as_tensor(embedding)


def _ranking_denso(pergunta: str, roteamento: dict, embedding: Any, boost_intencao: float) -> dict:
    vetor = _como_tensor(embedding) if embedding is not None else gerar_embedding(pergunta, convert_to_tensor=True)
    cossenos = util.cos_sim(vetor, _EMBEDDINGS)[0]
    ajustado = cossenos.clone()
    confianca_alta = bool(roteamento.get("confianca_alta"))
    if confianca_alta:
        for indice, rotulo in enumerate(_INTENCOES):
            if rotulo == roteamento.get("intencao"):
                ajustado[indice] = ajustado[indice] + boost_intencao
    ordem = sorted(range(len(_TEXTOS)), key=lambda i: float(ajustado[i]), reverse=True)
    return {
        "modo": "densa_com_boost" if confianca_alta else "densa_global",
        "cossenos": [float(valor) for valor in cossenos.tolist()],
        "ordem": ordem,
    }


_RE_BASE = re.compile(
    r"^(?:ADCT,\s*)?Art\.\s*\d+[ºo°]?(?:-[A-Za-z])?",
    re.IGNORECASE,
)
_TAMANHO_CURTO = 450
_EXTRA_SIMPLES = 700
_EXTRA_COMPOSTA = 1200
_RE_DISPOSITIVO = re.compile(
    r"^(?:ADCT,\s*)?Art\.\s*\d+[ºo°]?(?:-[A-Za-z])?(?:\s*,\s*§\s*\d+[ºo°]?)?",
    re.IGNORECASE,
)


def _base_dispositivo(artigo_id: str) -> str | None:
    """Art. 60, § 4º, I e II partilham a base 'art. 60, § 4º'. Art. 103-A fica de fora."""
    achado = _RE_DISPOSITIVO.match(str(artigo_id).strip())
    if not achado:
        return None
    return re.sub(r"\s+", " ", achado.group(0)).casefold()


def _artigo_base(artigo_id: str) -> str | None:
    achado = _RE_BASE.match(str(artigo_id).strip())
    if not achado:
        return None
    return re.sub(r"\s+", " ", achado.group(0)).casefold()


def _e_fatia(artigo_id: str) -> bool:
    base = _artigo_base(artigo_id)
    if not base:
        return False
    achado = _RE_BASE.match(str(artigo_id).strip())
    resto = str(artigo_id).strip()[achado.end() :].strip()
    return resto.startswith(",") or resto.startswith("§")


def _chunk(indice: int, nota: float, cossenos: list[float], origem: str) -> ChunkRecuperado:
    return {
        "artigo_id": _ARTIGO_IDS[indice],
        "texto": _TEXTOS[indice],
        "score_cosseno": cossenos[indice],
        "score_reranker": float(nota),
        "origem": origem,
        "chunk_idx": int(indice),
    }


def _idx(item: dict) -> int | None:
    if item.get("chunk_idx") is not None:
        return int(item["chunk_idx"])
    if item.get("_indice") is not None:
        return int(item["_indice"])
    return None


def _assinatura(ident: str, texto: str) -> tuple[str, str]:
    ident_n = re.sub(r"\s+", " ", str(ident or "").strip()).casefold()
    texto_n = re.sub(r"\s+", " ", str(texto or "").strip()).casefold()
    return ident_n, texto_n


def deduplicar_chunks(itens: list) -> tuple[list, int]:
    """Tira repetição por índice real e por artigo+texto normalizados. A ordem fica."""
    vistos_idx: set[int] = set()
    vistos_sig: set[tuple[str, str]] = set()
    saida = []
    removidas = 0
    for item in itens or []:
        if not isinstance(item, dict):
            saida.append(item)
            continue
        idx = _idx(item)
        sig = _assinatura(item.get("artigo_id"), item.get("texto"))
        repetido = (idx is not None and idx in vistos_idx) or (bool(sig[1]) and sig in vistos_sig)
        if repetido:
            removidas += 1
            continue
        if idx is not None:
            vistos_idx.add(idx)
        if sig[1]:
            vistos_sig.add(sig)
        saida.append(item)
    return saida, removidas


def _teto_dinamico(topo: float, top_k: int, composta: bool) -> int:
    """Pergunta simples com top-1 >= 0,85 fica em 3. Composta chega a 8. O resto fica em 5."""
    if composta:
        return min(8, max(top_k, 8))
    if topo >= 0.85:
        return min(3, top_k)
    return min(5, top_k)


def _anexar_irmaos(
    resultados: list[ChunkRecuperado],
    indices: list[int],
    cossenos_por_item: list[list[float]],
    orcamento: int,
) -> list[ChunkRecuperado]:
    """Para cada inciso curto, puxa os vizinhos do mesmo artigo ou parágrafo até ao teto de caracteres."""
    if not resultados or orcamento <= 0:
        return resultados
    ja = set(indices)
    emitidos: set[int] = set()
    assinaturas: set[tuple[str, str]] = set()
    gastos = 0
    saida: list[ChunkRecuperado] = []
    for posicao, (item, centro) in enumerate(zip(resultados, indices)):
        sig = _assinatura(item.get("artigo_id"), item.get("texto"))
        if centro in emitidos or sig in assinaturas:
            continue
        saida.append(item)
        emitidos.add(centro)
        assinaturas.add(sig)
        if len(item["texto"]) > _TAMANHO_CURTO or not _e_fatia(item["artigo_id"]):
            continue
        base = _base_dispositivo(item["artigo_id"])
        if not base:
            continue
        cossenos = cossenos_por_item[posicao]
        novos: list[int] = []
        for sentido in (-1, 1):
            vizinho = centro
            while True:
                vizinho += sentido
                if vizinho < 0 or vizinho >= len(_TEXTOS):
                    break
                if _base_dispositivo(_ARTIGO_IDS[vizinho]) != base:
                    break
                if len(_TEXTOS[vizinho]) > _TAMANHO_CURTO:
                    break
                if vizinho in ja or vizinho in emitidos:
                    continue
                sig_vizinho = _assinatura(_ARTIGO_IDS[vizinho], _TEXTOS[vizinho])
                if sig_vizinho in assinaturas:
                    emitidos.add(vizinho)
                    continue
                if gastos + len(_TEXTOS[vizinho]) > orcamento:
                    break
                gastos += len(_TEXTOS[vizinho])
                novos.append(vizinho)
                ja.add(vizinho)
                emitidos.add(vizinho)
                assinaturas.add(sig_vizinho)
        for vizinho in sorted(novos):
            extra = _chunk(vizinho, cossenos[vizinho], cossenos, "irmao_adjacente")
            extra["subconsulta"] = item.get("subconsulta") or ""
            saida.append(extra)
    return saida


def encaixar_ponte_na_janela(pergunta: str, texto: str, tokenizador, max_length: int = 512) -> str:
    """Encolhe só o texto oficial para o sufixo cotidiano caber na janela do reranker.

    O texto devolvido é temporário. textos e textos_busca permanecem inteiros.
    """
    marca = "\nTermos cotidianos: "
    if marca not in str(texto):
        return texto

    def tamanho(documento: str) -> int:
        ids = tokenizador(str(pergunta), documento, truncation=False, add_special_tokens=True)["input_ids"]
        if ids and isinstance(ids[0], list):
            ids = ids[0]
        return len(ids)

    if tamanho(texto) <= max_length:
        return texto
    oficial, resto = str(texto).split(marca, 1)
    sufixo = marca + resto
    ids_oficial = tokenizador(oficial, add_special_tokens=False)["input_ids"]
    if ids_oficial and isinstance(ids_oficial[0], list):
        ids_oficial = ids_oficial[0]
    melhor = 0
    baixo, alto = 0, len(ids_oficial)
    while baixo <= alto:
        meio = (baixo + alto) // 2
        pedaco = tokenizador.decode(ids_oficial[:meio], skip_special_tokens=True).rstrip()
        candidato = pedaco + sufixo if pedaco else sufixo
        if tamanho(candidato) <= max_length:
            melhor = meio
            baixo = meio + 1
        else:
            alto = meio - 1
    pedaco = tokenizador.decode(ids_oficial[:melhor], skip_special_tokens=True).rstrip()
    return pedaco + sufixo if pedaco else sufixo


def _textos_para_reranker(pergunta: str, indices: list[int]) -> list[str]:
    from src.rag.encoder import obter_reranker

    modelo = obter_reranker()
    tokenizador = getattr(modelo, "tokenizador", None) or getattr(modelo, "tokenizer", None)
    limite = int(getattr(modelo, "max_length", 512))
    saida = []
    for indice in indices:
        texto = _TEXTOS_BUSCA[indice]
        if tokenizador is None:
            saida.append(texto)
        else:
            saida.append(encaixar_ponte_na_janela(pergunta, texto, tokenizador, limite))
    return saida


def _reranquear(
    pergunta: str,
    ordem: list[int],
    cossenos: list[float],
    top_k: int,
    candidatos_rerank: int,
    limiar_reranker: float,
) -> tuple[list[ChunkRecuperado], float]:
    escolhidos = ordem[:candidatos_rerank]
    notas = reordenar_pares(str(pergunta), _textos_para_reranker(str(pergunta), escolhidos))
    ordenados = sorted(zip(escolhidos, notas), key=lambda par: par[1], reverse=True)
    topo = float(ordenados[0][1]) if ordenados else 0.0
    resultados: list[ChunkRecuperado] = []
    for indice, nota in ordenados:
        if nota < limiar_reranker or len(resultados) >= top_k:
            break
        item = _chunk(indice, nota, cossenos, "reranker")
        item["_indice"] = indice  # type: ignore[typeddict-unknown-key]
        resultados.append(item)
    return resultados, topo


def _status(nota: float, limiar_reranker: float) -> str:
    if nota >= limiar_reranker:
        return "APROVADO"
    if nota >= 0.12:
        return "CINZA"
    return "DESCARTADO"


def _marcar(item: dict, subconsulta: str, limiar_reranker: float) -> dict:
    copia = dict(item)
    indice = _idx(copia)
    if indice is not None:
        copia["chunk_idx"] = indice
    copia["subconsulta"] = subconsulta
    copia["status"] = _status(float(copia.get("score_reranker") or 0.0), limiar_reranker)
    return copia


def _sem_indice(item: dict) -> dict:
    copia = dict(item)
    copia.pop("_indice", None)
    return copia


_RE_RAIZ_ART = re.compile(
    r"^(?:ADCT,\s*)?Art\.\s*\d+[ºo°]?(?:-[A-Za-z])?",
    re.IGNORECASE,
)
_RE_RAIZ_PAR = re.compile(
    r"^(?:ADCT,\s*)?Art\.\s*\d+[ºo°]?(?:-[A-Za-z])?\s*,\s*§\s*\d+[ºo°]?",
    re.IGNORECASE,
)
_TETO_PAI = 2200
_TETO_PARAGRAFO = 1800


def _rotulo(artigo_id: str, com_paragrafo: bool) -> str | None:
    achado = (_RE_RAIZ_PAR if com_paragrafo else _RE_RAIZ_ART).match(str(artigo_id).strip())
    if not achado:
        return None
    return re.sub(r"\s+", " ", achado.group(0)).strip()


def _chave_rotulo(rotulo: str | None) -> str | None:
    if not rotulo:
        return None
    return re.sub(r"\s+", " ", rotulo).casefold()


def _indices_com_rotulo(com_paragrafo: bool, chave: str) -> list[int]:
    achados = []
    for indice, artigo_id in enumerate(_ARTIGO_IDS):
        rotulo = _rotulo(artigo_id, com_paragrafo)
        if _chave_rotulo(rotulo) == chave:
            achados.append(indice)
    return achados


def _caput_curto(chave_artigo: str) -> int | None:
    for indice, artigo_id in enumerate(_ARTIGO_IDS):
        if _chave_rotulo(_rotulo(artigo_id, False)) != chave_artigo:
            continue
        if _e_fatia(artigo_id) or len(_TEXTOS[indice]) > _TAMANHO_CURTO:
            continue
        return indice
    return None


def _soma(indices: list[int]) -> int:
    return sum(len(_TEXTOS[indice]) for indice in indices)


def _juntar(indices: list[int]) -> str:
    return "\n\n".join(_TEXTOS[indice] for indice in indices)


def _pacote_pai(indices: list[int], rotulo: str, item: dict) -> dict:
    return {
        "indices": list(indices),
        "rotulo": rotulo,
        "texto": _juntar(indices),
        "score": float(item.get("score_reranker") or 0.0),
        "cosseno": float(item.get("score_cosseno") or 0.0),
        "subconsulta": item.get("subconsulta") or "",
        "child_ids": [_ARTIGO_IDS[indice] for indice in indices],
        "chunk_idx": int(item.get("chunk_idx") or indices[0]),
    }


def _tentar_pai(item: dict) -> dict | None:
    artigo_id = str(item.get("artigo_id") or "")
    raiz = _rotulo(artigo_id, False)
    paragrafo = _rotulo(artigo_id, True)
    if not raiz:
        return None
    chave_artigo = _chave_rotulo(raiz)
    artigo = _indices_com_rotulo(False, chave_artigo) if chave_artigo else []
    paragrafo_idx = []
    if paragrafo and paragrafo.casefold() != raiz.casefold():
        chave_paragrafo = _chave_rotulo(paragrafo)
        paragrafo_idx = _indices_com_rotulo(True, chave_paragrafo) if chave_paragrafo else []
        caput = _caput_curto(chave_artigo) if chave_artigo else None
        com_caput = list(paragrafo_idx)
        if caput is not None and caput not in com_caput:
            com_caput = sorted(com_caput + [caput])
        if com_caput and _soma(com_caput) <= _TETO_PAI:
            return _pacote_pai(com_caput, paragrafo, item)
    if artigo and _soma(artigo) <= _TETO_PAI:
        return _pacote_pai(artigo, raiz, item)
    if paragrafo_idx and _soma(paragrafo_idx) <= _TETO_PARAGRAFO:
        return _pacote_pai(paragrafo_idx, paragrafo or raiz, item)
    return None


def _montar_pais(
    resultados: list[ChunkRecuperado],
    indices: list[int],
    cossenos_por_item: list[list[float]],
    composta: bool,
) -> list[ChunkRecuperado]:
    """Troca o chunk vencedor pelo dispositivo pai quando ele cabe no teto."""
    grupos: dict[tuple[int, ...], dict] = {}
    fallback: list[ChunkRecuperado] = []
    fallback_idx: list[int] = []
    fallback_vetores: list[list[float]] = []
    for item, centro, vetor in zip(resultados, indices, cossenos_por_item):
        item = dict(item)
        item["chunk_idx"] = int(item.get("chunk_idx") or centro)
        pai = _tentar_pai(item)
        if pai is None:
            fallback.append(item)
            fallback_idx.append(centro)
            fallback_vetores.append(vetor)
            continue
        chave = tuple(pai["indices"])
        atual = grupos.get(chave)
        if atual is None or pai["score"] > atual["score"]:
            if atual is not None:
                pai["child_ids"] = list(dict.fromkeys(atual["child_ids"] + pai["child_ids"]))
            grupos[chave] = pai
        else:
            atual["child_ids"] = list(dict.fromkeys(atual["child_ids"] + pai["child_ids"]))
    saida: list[ChunkRecuperado] = []
    for pai in grupos.values():
        saida.append(
            {
                "artigo_id": pai["rotulo"],
                "texto": pai["texto"],
                "score_cosseno": pai["cosseno"],
                "score_reranker": pai["score"],
                "origem": "parent_document",
                "chunk_idx": pai["chunk_idx"],
                "child_ids": pai["child_ids"],
                "filhos": len(pai["indices"]),
                "subconsulta": pai["subconsulta"],
            }
        )
    if fallback:
        orcamento = _EXTRA_COMPOSTA if composta else _EXTRA_SIMPLES
        saida.extend(_anexar_irmaos(fallback, fallback_idx, fallback_vetores, orcamento))
    return saida


def buscar_contexto(
    pergunta: str,
    roteamento: dict,
    top_k: int = 5,
    limiar_cosseno: float = 0.45,
    embedding: Any = None,
    boost_intencao: float = 0.05,
    candidatos_rerank: int = 8,
    limiar_reranker: float = 0.25,
    ao_reranquear=None,
    composta: bool = False,
    subconsulta: str = "",
    anexar_irmaos: bool = True,
) -> BuscaContexto:
    """Ordena pelo cosseno, reranqueia 8 e corta pelo score do reranker.

    limiar_cosseno permanece na assinatura para chamadas antigas. O freio
    que esvazia a lista é limiar_reranker. Confiança alta só soma o bónus.
    Não há exclusão de capítulo. Pergunta composta não aplica o teto de 3.
    """
    if pergunta is None or not str(pergunta).strip():
        raise ValueError("A pergunta para a busca está vazia.")
    if "intencao" not in roteamento or "confianca_alta" not in roteamento:
        raise ValueError("O roteamento precisa de intencao e confianca_alta.")
    if top_k < 1:
        raise ValueError("top_k tem de ser pelo menos 1.")
    del limiar_cosseno

    pacote = _ranking_denso(str(pergunta), roteamento, embedding, boost_intencao)
    if ao_reranquear is not None:
        ao_reranquear()
    limite = 8 if composta else max(top_k, 5)
    coletados, topo = _reranquear(
        str(pergunta),
        pacote["ordem"],
        pacote["cossenos"],
        limite,
        candidatos_rerank,
        0.0,
    )
    brutos = [_marcar(item, subconsulta, limiar_reranker) for item in coletados[:5]]
    teto = _teto_dinamico(topo, top_k, composta) if topo >= limiar_reranker else 0
    principais = [item for item in coletados if float(item["score_reranker"]) >= limiar_reranker][:teto]
    indices = [int(item.pop("_indice")) for item in principais]
    for item in principais:
        item.pop("_indice", None)
        item["subconsulta"] = subconsulta
    if anexar_irmaos and principais:
        resultados = _montar_pais(
            principais,
            indices,
            [pacote["cossenos"] for _ in principais],
            composta,
        )
    else:
        resultados = principais
    for item in resultados:
        item.setdefault("subconsulta", subconsulta)
    resultados, removidas = deduplicar_chunks(resultados)
    return {
        "modo_busca": pacote["modo"],
        "resultados": resultados,
        "top_candidatos_brutos": brutos,
        "top1_score": topo,
        "cossenos": pacote["cossenos"],
        "duplicatas_removidas": removidas,
    }


def fundir_subconsultas(buscas: list[dict], rotulos: list[str]) -> dict:
    """Une as sub-consultas sem repetir o mesmo chunk. Ids iguais com índices diferentes permanecem."""
    melhor: dict[int, dict] = {}
    for busca, rotulo in zip(buscas, rotulos):
        for item in busca.get("top_candidatos_brutos") or []:
            indice = _idx(item)
            if indice is None:
                continue
            copia = dict(item)
            copia["chunk_idx"] = indice
            copia["subconsulta"] = rotulo
            anterior = melhor.get(indice)
            if anterior is None or float(copia["score_reranker"]) > float(anterior["score_reranker"]):
                melhor[indice] = copia
    brutos = [_sem_indice(item) for item in sorted(melhor.values(), key=lambda item: float(item["score_reranker"]), reverse=True)]
    top1 = float(brutos[0]["score_reranker"]) if brutos else 0.0
    melhores = []
    for busca, rotulo in zip(buscas, rotulos):
        topo_sub = (busca.get("top_candidatos_brutos") or [None])[0]
        if topo_sub:
            melhores.append(
                "{} -> {} {:.3f}".format(
                    rotulo,
                    topo_sub.get("artigo_id"),
                    float(topo_sub.get("score_reranker") or 0.0),
                )
            )

    grupos: list[list[dict]] = []
    for busca, rotulo in zip(buscas, rotulos):
        grupo = []
        for item in busca.get("top_candidatos_brutos") or []:
            if item.get("status") != "APROVADO":
                continue
            copia = dict(item)
            copia["subconsulta"] = rotulo
            grupo.append(copia)
            if len(grupo) == 3:
                break
        grupos.append(grupo)

    escolhidos: list[dict] = []
    ja: set[int] = set()
    for rodada in range(3):
        for grupo in grupos:
            if rodada >= len(grupo) or len(escolhidos) >= 8:
                continue
            item = grupo[rodada]
            indice = _idx(item)
            if indice is None or indice in ja:
                continue
            escolhido = dict(melhor.get(indice, item))
            escolhido["chunk_idx"] = indice
            escolhidos.append(escolhido)
            ja.add(indice)

    principais: list[ChunkRecuperado] = []
    indices: list[int] = []
    vetores: list[list[float]] = []
    for item in escolhidos:
        indice = _idx(item)
        if indice is None:
            indice = _ID_PARA_INDICE.get(item["artigo_id"])
        if indice is None:
            continue
        principais.append(
            {
                "artigo_id": _ARTIGO_IDS[indice],
                "texto": _TEXTOS[indice],
                "score_cosseno": float(item.get("score_cosseno") or 0.0),
                "score_reranker": float(item.get("score_reranker") or 0.0),
                "origem": "reranker",
                "subconsulta": item.get("subconsulta") or "",
                "chunk_idx": int(indice),
            }
        )
        indices.append(indice)
        vetor = next(
            (
                busca.get("cossenos")
                for busca, rotulo in zip(buscas, rotulos)
                if rotulo == item.get("subconsulta") and busca.get("cossenos")
            ),
            None,
        )
        vetores.append(vetor or [0.0] * len(_TEXTOS))
    resultados = _montar_pais(principais, indices, vetores, True) if principais else []
    for item in resultados:
        item.setdefault("subconsulta", "")
    resultados, removidas = deduplicar_chunks(resultados)
    return {
        "modo_busca": "multi_query",
        "resultados": resultados,
        "top_candidatos_brutos": brutos[:5],
        "top1_score": top1,
        "melhores_sub": melhores,
        "duplicatas_removidas": removidas,
    }


def diagnosticar_busca(
    pergunta: str,
    roteamento: dict,
    embedding: Any = None,
    top_k: int = 5,
    candidatos_rerank: int = 8,
    limiar_reranker: float = 0.25,
    boost_intencao: float = 0.05,
) -> dict:
    """Devolve o ranking denso, o ranking com bónus e o do reranker."""
    import time

    inicio = time.perf_counter()
    pacote = _ranking_denso(str(pergunta), roteamento, embedding, boost_intencao)
    denso_s = time.perf_counter() - inicio
    sem_bonus = _ranking_denso(
        str(pergunta),
        {"intencao": roteamento.get("intencao"), "confianca_alta": False},
        embedding,
        0.0,
    )
    inicio_rerank = time.perf_counter()
    resultados, topo = _reranquear(
        str(pergunta),
        pacote["ordem"],
        pacote["cossenos"],
        top_k,
        candidatos_rerank,
        0.0,
    )
    rerank_s = time.perf_counter() - inicio_rerank
    finais = [item["artigo_id"] for item in resultados if item["score_reranker"] >= limiar_reranker][:top_k]
    return {
        "denso": [_ARTIGO_IDS[i] for i in sem_bonus["ordem"][:top_k]],
        "hibrido": [_ARTIGO_IDS[i] for i in pacote["ordem"][:top_k]],
        "reranker": finais,
        "top1_reranker": topo,
        "tempo_hibrido_s": denso_s,
        "tempo_reranker_s": rerank_s,
        "modo": pacote["modo"],
    }
