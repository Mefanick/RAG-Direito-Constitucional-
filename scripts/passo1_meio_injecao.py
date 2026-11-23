# -*- coding: utf-8 -*-
"""Etapa 1,5 — injecção do texto da Constituição no treino da OAB.

As classes "Ordem Econômica e Financeira", "Ordem Social" e "Princípios
Fundamentais" ficaram com F1 zero porque o CSV da OAB quase não tinha
linhas delas. Este script não retreina o SVM. Só constrói um corpus
maior: as 127 questões mais os artigos da Carta, já com a mesma coluna
intencao, gravado em datasets/dataset_hibrido_treino.csv.
"""

# =============================================================================
# 1. IMPORTAÇÕES
# =============================================================================
# pandas segura as duas tabelas e faz o concat. json lê a árvore da
# Constituição vigente (EC 108, 26/08/2020). Não há vectorizador aqui:
# a matriz TF-IDF só existe no passo 2, quando este CSV for lido.
import json
from pathlib import Path

import pandas as pd


_raiz = str(Path(__file__).resolve().parents[1]).replace("\\", "/")
_csv_oab = _raiz + "/datasets/oab_treino_limpo.csv"
_json_cf = _raiz + "/datasets/constituicao/util/vigente/20200826_EMC108.json"
_csv_saida = _raiz + "/datasets/dataset_hibrido_treino.csv"

# O rótulo tem de ser idêntico ao do CSV da OAB. Um acento a mais cria
# uma classe nova e o stratify do passo 2 deixa de ver a classe antiga.
MAPA_TITULO = {
    "1": "Princípios Fundamentais",
    "2": "Direitos e Garantias Fundamentais",
    # Título V (estado de defesa e de sítio) não tem classe própria no
    # CSV. No passo 1 essas questões caíram em Direitos e Garantias,
    # porque o enunciado fala em suspensão de garantias. O texto da lei
    # segue o mesmo rótulo, senão o vocabulário de "estado de sítio"
    # ficaria sem coluna de classe.
    "5": "Direitos e Garantias Fundamentais",
    "3": "Organização do Estado",
    "4": "Organização dos Poderes",
    "7": "Ordem Econômica e Financeira",
    "8": "Ordem Social",
}

# Título VI (tributação), Título IX (disposições gerais) e o ADCT não
# entram. Não existe intenção "Tributário" nem "ADCT" nas 127 questões.
# Forçar esses artigos para Princípios Fundamentais, que só tem quatro
# artigos no Título I, afogava a classe que estamos a tentar alimentar.
TITULOS_DE_FORA = {"6", "9", "10"}

# Estes artigos do Título IV são o controle de constitucionalidade, não
# a organização genérica do Judiciário. Se fossem parar em Organização
# dos Poderes, "ação direta" e "súmula vinculante" treinavam a classe
# errada e o F1 de Controle piorava.
ARTIGOS_DE_CONTROLE = {"97", "103", "103-A"}
INTENCAO_CONTROLE = "Controle de Constitucionalidade"

# Termos do art. 102 que separam a guarda da Constituição (controle) da
# competência ordinária do STF (organização do Judiciário). O art. 102
# mistura as duas coisas no mesmo artigo.
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


def texto_limpo(valor):
    """Junta o campo texto do JSON, que vem numa lista de um só item."""
    if valor is None:
        return ""
    if isinstance(valor, str):
        pedacos = [valor]
    elif isinstance(valor, list):
        pedacos = [pedaco for pedaco in valor if isinstance(pedaco, str)]
    else:
        return ""
    return " ".join(" ".join(pedaco.split()) for pedaco in pedacos if pedaco.strip())


# Troca de acento sem unicodedata: o bloco de importações fica só em
# pandas e json, como esta etapa pede. O ü de "argüição" (grafia antiga
# do art. 102) também cai, senão "descumprimento" não casa.
_SEM_ACENTO = str.maketrans(
    "áàâãäéèêëíìîïóòôõöúùûüýÿçñ",
    "aaaaaeeeeiiiiooooouuuuyycn",
)


def normalizar_para_regra(texto):
    """Minúsculas e sem acento, só para achar o termo. O CSV guarda o original."""
    if not texto:
        return ""
    return " ".join(texto.lower().translate(_SEM_ACENTO).split())


def e_controle(texto):
    """Verdadeiro se o dispositivo fala de controle, não de outro processo do STF."""
    base = normalizar_para_regra(texto)
    if not base:
        return False
    return any(termo in base for termo in TERMOS_CONTROLE)


def coletar_artigos(no, achados):
    """Desce título, capítulo, secção e subsecção até cada artigo.

    O JSON não põe os artigos todos no título. Do Título II ao VIII eles
    estão dentro de capítulos. Parar no primeiro nível perderia a Ordem
    Econômica inteira, que é justamente uma das classes com fome de dados.
    """
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
                coletar_artigos(filho, achados)


def dispositivos(no):
    """Lista o caput e, por baixo, incisos, parágrafos e alíneas, na ordem do ficheiro."""
    if not isinstance(no, dict):
        return []
    saida = []
    proprio = texto_limpo(no.get("texto"))
    if proprio:
        saida.append(proprio)
    for chave in ("incisos", "paragrafos", "alineas"):
        filhos = no.get(chave) or {}
        if isinstance(filhos, dict):
            for filho in filhos.values():
                saida.extend(dispositivos(filho))
    return saida


def conteudo_do_artigo(artigo):
    """Um artigo vira uma linha. O inciso não fica de fora: entra no texto do artigo.

    Uma linha por artigo, e não por inciso, evita partir "Art. 170. A ordem
    econômica..." dos incisos que lhe dão o sentido. O bigrama "ordem
    econômica" fica no mesmo documento que "propriedade privada".
    """
    return " ".join(dispositivos(artigo)).strip()


def separar_artigo_102(artigo):
    """Reparte o art. 102 entre Controle e Organização dos Poderes.

    O caput, o inciso III (recurso extraordinário), os parágrafos (ADPF,
    efeito da ADI e repercussão geral) e as alíneas que nomeiam a ação
    direta vão para Controle. O resto do artigo é competência originária
    e recurso ordinário: continua em Organização dos Poderes. Sem este
    corte, ou o Controle não recebia o vocabulário da ADI, ou o Poderes
    perdia o resto do STF.
    """
    controle = []
    poderes = []

    def visitar(no, forcar):
        if not isinstance(no, dict):
            return
        classe = no.get("classe") or []
        numero = ""
        bruto = no.get("numero") or []
        if isinstance(bruto, list) and bruto:
            numero = str(bruto[0])
        texto = texto_limpo(no.get("texto"))
        forca_filhos = forcar or ("inciso" in classe and numero == "3") or ("paragrafo" in classe)
        if texto and classe != ["artigo"]:
            if forca_filhos or forcar or e_controle(texto):
                controle.append(texto)
            else:
                poderes.append(texto)
        elif texto and "artigo" in classe and e_controle(texto):
            controle.append(texto)
        elif texto and "artigo" in classe:
            poderes.append(texto)
        for chave in ("incisos", "paragrafos", "alineas"):
            filhos = no.get(chave) or {}
            if isinstance(filhos, dict):
                for filho in filhos.values():
                    visitar(filho, forca_filhos)

    visitar(artigo, False)
    return " ".join(controle).strip(), " ".join(poderes).strip()


def linhas_da_constituicao(arvore):
    """Converte a árvore de títulos numa tabela texto / intencao."""
    titulos = arvore.get("titulos") if isinstance(arvore, dict) else None
    if not isinstance(titulos, dict):
        raise ValueError("O JSON da Constituição não tem a chave 'titulos'.")

    linhas = []
    for numero_titulo, titulo in titulos.items():
        numero_titulo = str(numero_titulo)
        if numero_titulo in TITULOS_DE_FORA:
            continue
        intencao = MAPA_TITULO.get(numero_titulo)
        if not intencao:
            continue
        artigos = []
        coletar_artigos(titulo, artigos)
        for artigo in artigos:
            bruto = artigo.get("numero") or []
            numero_artigo = str(bruto[0]) if isinstance(bruto, list) and bruto else ""
            if numero_artigo == "102":
                texto_controle, texto_poderes = separar_artigo_102(artigo)
                if texto_controle:
                    linhas.append({"texto": texto_controle, "intencao": INTENCAO_CONTROLE})
                if texto_poderes:
                    linhas.append({"texto": texto_poderes, "intencao": intencao})
                continue
            if numero_artigo in ARTIGOS_DE_CONTROLE:
                intencao_artigo = INTENCAO_CONTROLE
            else:
                intencao_artigo = intencao
            texto = conteudo_do_artigo(artigo)
            if texto:
                linhas.append({"texto": texto, "intencao": intencao_artigo})
    return linhas


# =============================================================================
# 2. CARREGAMENTO DUPLO
# =============================================================================
# A OAB traz a pergunta de exame, curta e já rotulada. A Constituição
# traz o capítulo que essa pergunta devia reconhecer. São fontes
# diferentes com o mesmo par de colunas, para o concat não alinhar por
# posição errada.
df_oab = pd.read_csv(_csv_oab, encoding="utf-8")
if not {"texto", "intencao"}.issubset(df_oab.columns):
    raise ValueError("oab_treino_limpo.csv precisa das colunas texto e intencao.")
df_oab = df_oab.loc[:, ["texto", "intencao"]].copy()
df_oab["texto"] = df_oab["texto"].fillna("").astype(str).str.strip()
df_oab["intencao"] = df_oab["intencao"].fillna("").astype(str).str.strip()
df_oab = df_oab.loc[(df_oab["texto"] != "") & (df_oab["intencao"] != "")].copy()

with open(_json_cf, encoding="utf-8") as ficheiro_json:
    constituicao = json.load(ficheiro_json)

df_lei = pd.DataFrame(linhas_da_constituicao(constituicao), columns=["texto", "intencao"])
df_lei["texto"] = df_lei["texto"].fillna("").astype(str).str.strip()
df_lei["intencao"] = df_lei["intencao"].fillna("").astype(str).str.strip()
df_lei = df_lei.loc[(df_lei["texto"] != "") & (df_lei["intencao"] != "")].copy()

if df_lei.empty:
    raise ValueError("Nenhum artigo constitucional foi mapeado para uma intenção.")


# =============================================================================
# 3 e 4. MAPEAMENTO JÁ APLICADO — FUSÃO
# =============================================================================
# Por que isto ataca a esparsidade das classes minoritárias
# ---------------------------------------------------------
# O TF-IDF do passo 2 monta uma matriz de linhas = documentos e colunas
# = termos. Uma classe com quatro questões ocupa quatro linhas. Quase
# todas as colunas dessas linhas são zero: o enunciado da OAB não usa
# "seguridade social", "previdência" ou "soberania" com a frequência do
# capítulo. O LinearSVC estima w·x a partir dessas linhas. Sem massa nas
# colunas do capítulo, o hiperplano dessa classe não tem para onde
# apontar e o F1 no teste cai a zero. Não é um defeito do peso
# balanceado: o peso aumenta o custo do erro, mas não inventa termos
# que nunca apareceram.
#
# Cada artigo injectado é uma linha nova cuja etiqueta é o título. A
# submatriz da classe deixa de ser quatro vectores quase vazios e passa
# a incluir o vocabulário normativo ("ordem econômica", "ordem social",
# "fundamentos" do art. 1º). O idf continua a baixar a palavra que está
# em toda a parte; o que muda é df dentro da classe. "Previdência" passa
# a ocorrer em documentos marcados Ordem Social, e o produto tf-idf
# dessa coluna deixa de ser zero nessa intenção. É essa coluna, não o
# número de questões de exame, que o SVM usa para separar o macrotema.
#
# O Título I só tem quatro artigos. Princípios Fundamentais ganha o
# texto exacto dos arts. 1º a 4º, não um volume comparável ao Título
# VIII. O ganho aí é lexical: os fundamentos da República entram no
# vocabulário com o rótulo certo.
df_hibrido = pd.concat([df_oab, df_lei], ignore_index=True)


# =============================================================================
# 5. EMBARALHAMENTO E EXPORTAÇÃO
# =============================================================================
# sample(frac=1) permuta todas as linhas e não deita nenhuma fora.
# random_state=42 fixa a permutação. Sem isto, o ficheiro ficava com as
# 127 questões juntas e, a seguir, o bloco inteiro da lei. Quem lesse o
# CSV por fatias veria só exame ou só norma. O split estratificado do
# passo 2 volta a baralhar, mas o artefacto já sai misturado: pergunta
# da OAB e artigo da Carta alternam-se com a mesma semente.
df_hibrido = df_hibrido.sample(frac=1, random_state=42).reset_index(drop=True)

if df_hibrido.shape[1] != 2 or list(df_hibrido.columns) != ["texto", "intencao"]:
    raise ValueError("O CSV híbrido tem de sair só com texto e intencao.")
if len(df_hibrido) <= len(df_oab):
    raise ValueError("A fusão não acrescentou artigos da Constituição.")

print("OAB: {}".format(df_oab.shape))
print("Constituição injectada: {}".format(df_lei.shape))
print("Híbrido: {}".format(df_hibrido.shape))
print(df_hibrido["intencao"].value_counts().to_string())

df_hibrido.to_csv(_csv_saida, index=False, encoding="utf-8")
print("CSV gravado em {}".format(_csv_saida))
