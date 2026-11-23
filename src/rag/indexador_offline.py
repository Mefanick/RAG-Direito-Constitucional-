# -*- coding: utf-8 -*-
"""Indexação offline dos embeddings da Constituição.

Corre uma vez. Lê o JSON vigente, incluindo tributação, disposições
gerais e ADCT. Artigos longos são partidos por inciso e parágrafo.
Grava artigo_id, texto, intenção e a matriz densa.
"""

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

import torch
from src.rag.encoder import obter_encoder

_RAIZ = Path(__file__).resolve().parents[2]
_JSON_CF = _RAIZ / "datasets" / "constituicao" / "util" / "vigente" / "20200826_EMC108.json"
_DESTINO = _RAIZ / "modelos" / "constituicao_vetorizada.pkl"
_MODELO_NOME = "BAAI/bge-m3"

# Rótulos idênticos aos do LinearSVC. Um acento a menos faz o filtro
# do retriever não encontrar linha nenhuma.
MAPA_TITULO = {
    "1": "Princípios Fundamentais",
    "2": "Direitos e Garantias Fundamentais",
    "5": "Direitos e Garantias Fundamentais",
    "3": "Organização do Estado",
    "4": "Organização dos Poderes",
    "7": "Ordem Econômica e Financeira",
    "8": "Ordem Social",
    # O SVM não tem classe tributária. "Ordem Econômica e Financeira" é o
    # Título VII, outro capítulo. Rotular o Título VI com o nome do próprio
    # título evita misturar imposto com monopólio no filtro estrito. A busca
    # global continua a alcançar o art. 150.
    "6": "Tributação e Orçamento",
    "9": "Disposições Gerais / ADCT",
    "10": "Disposições Gerais / ADCT",
}
# Artigos acima disto são partidos. O art. 5º deixa de ser um vector só,
# senão o inciso do anonimato dilui-se no bloco.
LIMITE_CARACTERES = 1200
ARTIGOS_DE_CONTROLE = {"97", "103", "103-A"}
INTENCAO_CONTROLE = "Controle de Constitucionalidade"
TERMOS_CONTROLE = (
    "inconstitucional",
    "descumprimento de preceito",
    "acao direta",
    "acao declaratoria",
    "sumula vinculante",
    "guarda da constituicao",
    "recurso extraordinario",
    "repercussao geral",
)
_SEM_ACENTO = str.maketrans(
    "áàâãäéèêëíìîïóòôõöúùûüýÿçñ",
    "aaaaaeeeeiiiiooooouuuuyycn",
)


_STOPWORDS_BM25 = {
    "a", "o", "os", "as", "um", "uma", "uns", "umas",
    "de", "da", "do", "das", "dos", "e", "em", "na", "no", "nas", "nos",
    "para", "por", "com", "que", "se", "ao", "aos", "as", "a",
    "pelo", "pela", "pelos", "pelas", "como", "mais", "mas", "ou",
    "seu", "sua", "seus", "suas", "este", "esta", "esse", "essa",
    "isto", "isso", "aquele", "aquela", "ele", "ela", "eles", "elas",
    "eu", "tu", "me", "te", "lhe", "lhes", "ser", "estar", "ter",
    "foi", "sao", "era", "ha", "ja", "tambem", "muito", "sobre",
}


def tokenizar_bm25(texto: str) -> list[str]:
    """Normaliza o texto para o BM25: minúsculas, sem acento, só letras e números.

    Não, nem e nunca ficam. O número do artigo também fica. O resto das
    palavras funcionais sai, para o ranking lexical não se apoiar em "de" e "que".
    """
    if texto is None:
        return ["vazio"]
    base = unicodedata.normalize("NFKD", str(texto).lower())
    base = "".join(caractere for caractere in base if not unicodedata.combining(caractere))
    tokens = re.findall(r"[a-z0-9]+", base)
    uteis = [token for token in tokens if token.isdigit() or token not in _STOPWORDS_BM25]
    return uteis or ["vazio"]


def _texto_limpo(valor: Any) -> str:
    """O JSON guarda cada dispositivo numa lista. Sai uma string só."""
    if valor is None:
        return ""
    if isinstance(valor, str):
        pedacos = [valor]
    elif isinstance(valor, list):
        pedacos = [pedaco for pedaco in valor if isinstance(pedaco, str)]
    else:
        return ""
    return " ".join(" ".join(pedaco.split()) for pedaco in pedacos if pedaco.strip())


def _sem_acento(texto: str) -> str:
    return " ".join(str(texto).lower().translate(_SEM_ACENTO).split())


def _e_controle(texto: str) -> bool:
    base = _sem_acento(texto)
    return bool(base) and any(termo in base for termo in TERMOS_CONTROLE)


def _coletar_artigos(no: Any, achados: list[dict[str, Any]]) -> None:
    """Desce capítulo, secção e subsecção até ao artigo."""
    if not isinstance(no, dict):
        return
    classe = no.get("classe") or []
    if isinstance(classe, list) and "artigo" in classe:
        achados.append(no)
        return
    for chave in ("capitulos", "secoes", "subsecoes", "artigos"):
        bloco = no.get(chave)
        if isinstance(bloco, dict):
            for filho in bloco.values():
                _coletar_artigos(filho, achados)


def _dispositivos(no: Any) -> list[str]:
    """Caput, incisos, parágrafos e alíneas, na ordem do ficheiro."""
    if not isinstance(no, dict):
        return []
    saida: list[str] = []
    proprio = _texto_limpo(no.get("texto"))
    if proprio:
        saida.append(proprio)
    for chave in ("incisos", "paragrafos", "alineas"):
        filhos = no.get(chave) or {}
        if isinstance(filhos, dict):
            for filho in filhos.values():
                saida.extend(_dispositivos(filho))
    return saida


def _id_base(numero: str, titulo: str, caput: str) -> str:
    """Usa a grafia do caput (Art. 5º, Art. 173). O ADCT leva prefixo para não colidir."""
    achado = re.match(r"^(Art\.\s*\d+[ºo]?(?:-[A-Za-z])?)", caput.strip())
    if achado:
        nucleo = re.sub(r"\s+", " ", achado.group(1))
    else:
        nucleo = "Art. {}".format(numero or "?")
    if titulo == "10":
        return "ADCT, " + nucleo
    return nucleo


def _sem_marcador_inicial(texto: str) -> str:
    """Tira o 'IV -' ou o '§ 1º' do início, porque o artigo_id já traz esse marcador."""
    texto = texto.strip()
    texto = re.sub(r"^[IVXLCDM]+\s*[-–]\s*", "", texto)
    texto = re.sub(r"^§+\s*\d+[ºo]?\s*", "", texto)
    texto = re.sub(r"^Parágrafo único\.?\s*", "", texto, flags=re.IGNORECASE)
    return texto.strip()


def _rotulo_filho(filho: dict[str, Any]) -> str:
    texto = _texto_limpo(filho.get("texto"))
    classe = filho.get("classe") or []
    bruto = filho.get("numero") or []
    numero = str(bruto[0]) if isinstance(bruto, list) and bruto else ""
    romano = re.match(r"^([IVXLCDM]+)\s*[-–]", texto.strip())
    if romano:
        return romano.group(1)
    normal = _sem_acento(texto)
    if "paragrafo" in classe and "paragrafo unico" in normal:
        return "parágrafo único"
    if "paragrafo" in classe:
        return "§ {}º".format(numero) if numero.isdigit() else "§ {}".format(numero or "?")
    alinea = re.match(r"^([a-z])\)", texto.strip(), re.IGNORECASE)
    if alinea:
        return alinea.group(1).lower() + ")"
    if "inciso" in classe and numero:
        return "inciso " + numero
    return numero or "trecho"


def _intencao_do_filho(numero_artigo: str, filho: dict[str, Any] | None, intencao_padrao: str, forcar: bool) -> str:
    """No art. 102, ADI e recurso extraordinário não herdam a intenção do Poder Judiciário."""
    if numero_artigo != "102":
        return intencao_padrao
    if filho is None:
        return INTENCAO_CONTROLE if forcar else intencao_padrao
    classe = filho.get("classe") or []
    bruto = filho.get("numero") or []
    numero = str(bruto[0]) if isinstance(bruto, list) and bruto else ""
    texto = " ".join(_dispositivos(filho))
    if forcar or ("inciso" in classe and numero == "3") or ("paragrafo" in classe) or _e_controle(texto):
        return INTENCAO_CONTROLE
    return intencao_padrao


_LIMITE_CONTEXTO_CAPUT = 280


def _resumo_caput(caput: str) -> str:
    """Cabeçalho semântico do artigo, curto o bastante para não comer o inciso."""
    corpo = re.sub(r"^Art\.\s*\d+[ºo]?(?:-[A-Za-z])?\.?\s*", "", caput.strip())
    if len(corpo) <= _LIMITE_CONTEXTO_CAPUT:
        return corpo
    return corpo[:_LIMITE_CONTEXTO_CAPUT].rstrip() + "..."


def _explodir(
    no: dict[str, Any],
    artigo_id: str,
    intencao: str,
    numero_artigo: str,
    forcar: bool,
    id_artigo: str,
    contexto_caput: str,
) -> list[dict[str, str]]:
    """Um chunk se o bloco cabe. Senão, caput e um chunk por inciso ou parágrafo.

    O chunk filho leva o caput do artigo, cortado em 280 caracteres, para o
    inciso não perder o assunto. O identificador continua a ser "Art. 5º, IV".
    """
    texto = " ".join(_dispositivos(no)).strip()
    if not texto:
        return []
    filhos = []
    for chave in ("incisos", "paragrafos", "alineas"):
        bloco = no.get(chave) or {}
        if isinstance(bloco, dict):
            filhos.extend(filho for filho in bloco.values() if isinstance(filho, dict))
    if len(texto) <= LIMITE_CARACTERES or not filhos:
        if contexto_caput:
            marcador = artigo_id[len(id_artigo):].lstrip(", ").strip()
            miolo = _sem_marcador_inicial(texto)
            if marcador:
                corpo = "{} (Contexto: {}) | {} - {}".format(id_artigo, contexto_caput, marcador, miolo)
            else:
                corpo = "{} (Contexto: {}) | {}".format(id_artigo, contexto_caput, miolo)
        elif texto.startswith("Art.") or texto.startswith(artigo_id):
            corpo = texto
        else:
            corpo = "{} - {}".format(artigo_id, _sem_marcador_inicial(texto))
        return [{"artigo_id": artigo_id, "texto": corpo, "intencao": intencao}]

    chunks: list[dict[str, str]] = []
    caput = _texto_limpo(no.get("texto"))
    contexto_filhos = contexto_caput or (_resumo_caput(caput) if caput else "")
    if caput and not contexto_caput:
        corpo_caput = caput if caput.startswith("Art.") else "{} - {}".format(artigo_id, caput)
        chunks.append({"artigo_id": artigo_id, "texto": corpo_caput, "intencao": intencao})
    elif caput and contexto_caput:
        chunks.extend(
            _explodir(
                {"classe": no.get("classe"), "numero": no.get("numero"), "texto": no.get("texto")},
                artigo_id,
                intencao,
                numero_artigo,
                forcar,
                id_artigo,
                contexto_caput,
            )
        )
    for filho in filhos:
        classe = filho.get("classe") or []
        bruto = filho.get("numero") or []
        numero_filho = str(bruto[0]) if isinstance(bruto, list) and bruto else ""
        forcar_filho = forcar or (
            numero_artigo == "102" and (("inciso" in classe and numero_filho == "3") or "paragrafo" in classe)
        )
        intencao_filho = _intencao_do_filho(numero_artigo, filho, intencao, forcar_filho)
        ident = "{}, {}".format(id_artigo, _rotulo_filho(filho))
        chunks.extend(
            _explodir(filho, ident, intencao_filho, numero_artigo, forcar_filho, id_artigo, contexto_filhos)
        )
    return chunks


def ler_artigos(caminho_json: Path | None = None) -> list[dict[str, str]]:
    """Lê o JSON vigente inteiro e devolve um chunk por artigo ou por inciso.

    Nenhum título é descartado. O Título VI fica em Tributação e Orçamento.
    O Título IX e o ADCT partilham o rótulo Disposições Gerais / ADCT.
    Artigo com mais de LIMITE_CARACTERES abre-se: o caput é o primeiro
    chunk e cada inciso ou parágrafo vira outro, com o número do artigo
    no artigo_id e no início do texto.
    """
    caminho = caminho_json or _JSON_CF
    if not caminho.is_file():
        raise FileNotFoundError("JSON da Constituição não encontrado: {}".format(caminho))

    with caminho.open(encoding="utf-8") as ficheiro:
        arvore = json.load(ficheiro)
    titulos = arvore.get("titulos") if isinstance(arvore, dict) else None
    if not isinstance(titulos, dict):
        raise ValueError("O JSON da Constituição não tem a chave 'titulos'.")

    linhas: list[dict[str, str]] = []
    for numero_titulo, titulo in titulos.items():
        numero_titulo = str(numero_titulo)
        intencao = MAPA_TITULO.get(numero_titulo)
        if not intencao:
            continue
        artigos: list[dict[str, Any]] = []
        _coletar_artigos(titulo, artigos)
        for artigo in artigos:
            bruto = artigo.get("numero") or []
            numero_artigo = str(bruto[0]) if isinstance(bruto, list) and bruto else ""
            ident = _id_base(numero_artigo, numero_titulo, _texto_limpo(artigo.get("texto")))
            if numero_artigo == "102":
                intencao_artigo = (
                    INTENCAO_CONTROLE
                    if _e_controle(_texto_limpo(artigo.get("texto")))
                    else intencao
                )
            elif numero_artigo in ARTIGOS_DE_CONTROLE:
                intencao_artigo = INTENCAO_CONTROLE
            else:
                intencao_artigo = intencao
            linhas.extend(_explodir(artigo, ident, intencao_artigo, numero_artigo, False, ident, ""))

    if not linhas:
        raise ValueError("Nenhum artigo foi etiquetado a partir do JSON.")
    return linhas


def reconstruir_com_ponte(destino: Path | None = None, cache_ponte: Path | None = None) -> Path:
    """Regrava o índice com textos_busca e novos embeddings.

    textos, artigo_ids e intencoes permanecem os da cópia atual.
    O arquivo anterior é copiado para *.bak_pre_33 na primeira vez.
    """
    import shutil

    caminho = destino or _DESTINO
    if not caminho.is_file():
        raise FileNotFoundError("Índice atual não encontrado em {}.".format(caminho))
    cache = torch.load(caminho, weights_only=False)
    textos = list(cache["textos"])
    ids = list(cache["artigo_ids"])
    ponte: dict[int, str] = {}
    arquivo = cache_ponte or (caminho.parent / "ponte_leiga_cache.jsonl")
    if arquivo.is_file():
        brutas = arquivo.read_text(encoding="utf-8").splitlines()
        for posicao, linha in enumerate(brutas):
            if not linha.strip():
                continue
            try:
                item = json.loads(linha)
            except json.JSONDecodeError:
                if posicao == len(brutas) - 1:
                    print("Última linha do cache da ponte está truncada e foi ignorada.", flush=True)
                    continue
                raise
            indice = int(item["chunk_idx"])
            if indice < 0 or indice >= len(textos):
                raise SystemExit("chunk_idx {} fora do índice ({} chunks).".format(indice, len(textos)))
            if str(item.get("artigo_id")) != str(ids[indice]):
                raise SystemExit(
                    "artigo_id divergente no idx {}: cache '{}' e pkl '{}'.".format(
                        indice, item.get("artigo_id"), ids[indice]
                    )
                )
            esperado = hashlib.sha256(textos[indice].encode("utf-8")).hexdigest()[:12]
            if item.get("texto_hash") and item["texto_hash"] != esperado:
                raise SystemExit(
                    "texto_hash divergente no idx {} ({}).".format(indice, ids[indice])
                )
            frase = " ".join(str(item.get("ponte_leiga") or "").split())
            if frase:
                ponte[indice] = frase
    backup = caminho.parent / (caminho.name + ".bak_pre_33")
    if not backup.is_file():
        shutil.copy2(caminho, backup)
        print("Backup: {}".format(backup), flush=True)
    textos_busca = []
    for indice, oficial in enumerate(textos):
        if indice in ponte:
            textos_busca.append(oficial + "\nTermos cotidianos: " + ponte[indice])
        else:
            textos_busca.append(oficial)
    modelo = obter_encoder()
    embeddings = modelo.encode(
        textos_busca,
        convert_to_tensor=True,
        normalize_embeddings=True,
        batch_size=32,
        show_progress_bar=True,
    )
    if not isinstance(embeddings, torch.Tensor):
        embeddings = torch.as_tensor(embeddings)
    cache["textos"] = textos
    cache["textos_busca"] = textos_busca
    cache["embeddings"] = embeddings.cpu()
    cache["modelo"] = _MODELO_NOME
    torch.save(cache, caminho)
    print("Ponte aplicada em {} de {} chunks.".format(len(ponte), len(textos)), flush=True)
    print("Forma dos embeddings: {}".format(tuple(cache["embeddings"].shape)), flush=True)
    return caminho


def indexar(destino: Path | None = None) -> Path:
    """Calcula os embeddings densos e grava o artefacto.

    O tensor tem uma linha por chunk e 1.024 colunas, o tamanho do BGE-M3.
    Os tokens do BM25 viajam no mesmo ficheiro para o retriever não
    reprocessar a Constituição a cada consulta.
    """
    linhas = ler_artigos()
    textos = [linha["texto"] for linha in linhas]
    intencoes = [linha["intencao"] for linha in linhas]
    artigo_ids = [linha["artigo_id"] for linha in linhas]

    modelo = obter_encoder()
    embeddings = modelo.encode(
        textos,
        convert_to_tensor=True,
        normalize_embeddings=True,
        batch_size=32,
        show_progress_bar=True,
    )
    if not isinstance(embeddings, torch.Tensor):
        embeddings = torch.as_tensor(embeddings)

    caminho = destino or _DESTINO
    caminho.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "artigo_ids": artigo_ids,
            "textos": textos,
            "intencoes": intencoes,
            "embeddings": embeddings.cpu(),
            "tokens_bm25": [tokenizar_bm25(texto) for texto in textos],
            "modelo": _MODELO_NOME,
        },
        caminho,
    )
    return caminho


if __name__ == "__main__":
    import sys

    if "--com-ponte" in sys.argv:
        gravado = reconstruir_com_ponte()
        print("Artefacto: {}".format(gravado))
    else:
        print("Para fundir a ponte leiga sem recriar os chunks:")
        print("  python -m src.rag.indexador_offline --com-ponte")
        print("A indexação desde o JSON não roda daqui, para não deslocar o chunk_idx.")
