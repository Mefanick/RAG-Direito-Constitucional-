# -*- coding: utf-8 -*-
"""Etapa 1 — ingestão e filtragem das provas oficiais da OAB.

O script é linear de propósito. Ele para na tabela que a Etapa 2 vai
ler como X (enunciado) e y (intenção). Não há vetorização, não há
TF-IDF e não há classificador: esses passos usariam o CSV produzido
aqui e misturariam a limpeza do corpus com o treino.

O que esta etapa entrega
------------------------
Um CSV com duas colunas, texto e intencao, restrito às 127 questões
cuja área manual é constitucional. Cada intenção é um macrotema da
Constituição de 1988, obtido por regras de palavras-chave. O roteador
do RAG, mais adiante, usará esse rótulo para escolher o bloco da Carta
em que a busca deve acontecer.
"""

# =============================================================================
# PASSO 1 — IMPORTAÇÃO
# =============================================================================
# pandas segura a tabela. json entra na consolidação: a lista de
# questões vira texto JSON e volta como lista de dicionários simples,
# então um enunciado vazio ou um campo ausente chega ao DataFrame como
# None, nunca como um tipo opaco herdado do arquivo.
import json
import pandas as pd

# Biblioteca padrão. re e unicodedata só normalizam o texto para as
# regras de palavras-chave. pathlib localiza a pasta de provas sem
# depender do diretório em que o script foi chamado.
import re
import unicodedata
from pathlib import Path


# Pasta do projeto, não o diretório de trabalho. Assim o script acha
# os .txt mesmo quando é disparado de outro lugar.
RAIZ = Path(__file__).resolve().parents[1]
PASTA_PROVAS = RAIZ / "datasets" / "oab" / "util" / "provas_oficiais"
ARQUIVO_SAIDA = RAIZ / "datasets" / "oab_treino_limpo.csv"

# Contrato deste corpus: 27 provas em texto, das quais só as que foram
# rotuladas à mão trazem AREA CONSTITUTIONAL. A contagem fechada é 127.
# Provas mais novas deixam a linha AREA vazia; sem rótulo manual elas
# não entram, porque adivinhar a área já seria um classificador.
QUESTOES_CONSTITUCIONAIS_ESPERADAS = 127

# Cabeçalho de cada questão no formato descrito no README das provas:
# "Questão 13", às vezes com NULL ou com espaços no fim da linha.
PADRAO_QUESTAO = re.compile(r"(?m)^Quest[aã]o\s+(\d+)[ \t]*(.*?)\s*$")


def ler_prova(caminho):
    """Lê uma prova em texto. utf-8-sig engole o BOM; latin-1 é a rede
    de segurança se algum arquivo antigo tiver sido gravado em Windows-1252.
    """
    bruto = caminho.read_bytes()
    for codec in ("utf-8-sig", "latin-1"):
        try:
            return bruto.decode(codec)
        except UnicodeDecodeError:
            continue
    return bruto.decode("utf-8", errors="replace")


def normalizar_area(bruta):
    """Reduz o rótulo da prova a uma chave estável.

    O arquivo original usa o inglês CONSTITUTIONAL, não a palavra
    "constitucional". A tradução é literal e só vale para a tag exata.
    "INTERNATIONAL CONSTITUTIONAL" permanece composta e morre no filtro:
    é uma questão de internacional que cita a Constituição, não uma das
    127 de direito constitucional.
    """
    if bruta is None:
        return ""
    area = str(bruta).strip()
    if not area or area.casefold() == "nan":
        return ""
    if area.upper() == "CONSTITUTIONAL":
        return "constitucional"
    return area.casefold()


def enunciado_da_questao(bloco):
    """Separa área e enunciado de um bloco que vai até a questão seguinte.

    O marcador CORRECT vive nas alternativas e indica o gabarito. Ele
    não entra no texto de treino. Se a alternativa correta fosse parar
    no enunciado, o TF-IDF futuro aprenderia o jeito de a banca escrever
    a resposta, não o tema da pergunta. OPTIONS é a cerca: tudo o que
    vem depois dela é alternativa e fica de fora.

    Várias provas põem uma linha só de espaços entre "Questão N" e
    "AREA". Por isso a área não é lida por posição fixa; é a primeira
    linha, depois dos espaços, que começa com AREA.
    """
    area = ""
    linhas_enunciado = []
    area_encontrada = False

    for linha in bloco.splitlines():
        linha_limpa = linha.strip()
        if not area_encontrada:
            if linha_limpa.upper().startswith("AREA"):
                area = normalizar_area(linha_limpa[4:])
                area_encontrada = True
            continue
        if linha_limpa.upper().startswith("OPTIONS"):
            break
        linhas_enunciado.append(linha_limpa)

    texto = re.sub(r"\s+", " ", " ".join(linhas_enunciado)).strip()
    return texto, area


def consolidar_provas(pasta):
    """Empilha as 27 provas numa lista de registros {texto, area}.

    Não existe um arquivo único no repositório. O "consolidado" é esta
    leitura: cada .txt é uma prova, e a tabela só nasce aqui. O README
    da pasta não é prova e fica de fora pelo sufixo.
    """
    if not pasta.is_dir():
        raise FileNotFoundError("Pasta de provas oficiais não encontrada: {}".format(pasta))

    registros = []
    arquivos = sorted(pasta.glob("*.txt"))
    if not arquivos:
        raise FileNotFoundError("Nenhuma prova .txt em {}".format(pasta))

    for arquivo in arquivos:
        conteudo = ler_prova(arquivo)
        marcas = list(PADRAO_QUESTAO.finditer(conteudo))
        for indice, marca in enumerate(marcas):
            fim = marcas[indice + 1].start() if indice + 1 < len(marcas) else len(conteudo)
            texto, area = enunciado_da_questao(conteudo[marca.end() : fim])
            registros.append({"texto": texto, "area": area})

    # Ida e volta em JSON: garante que cada célula é str ou um valor
    # que o pandas converte em nulo. Não grava arquivo intermediário.
    registros = json.loads(json.dumps(registros, ensure_ascii=False))
    return pd.DataFrame(registros, columns=["texto", "area"])


def descartar_vazias(df):
    """Tira enunciado vazio e área vazia antes do corte de domínio.

    Questão sem texto não tem termo para pesar na matriz. Questão com
    AREA em branco não tem domínio confirmado: as provas de 2016 em
    diante estão nesse estado, e tratá-las como constitucionais seria
    inventar rótulo. Nulos do pandas e string vazia caem juntos.
    """
    tabela = df.copy()
    tabela["texto"] = tabela["texto"].fillna("").astype(str).str.strip()
    tabela["area"] = tabela["area"].fillna("").astype(str).str.strip().str.casefold()
    tabela.loc[tabela["texto"].str.casefold().isin(["", "none", "nan"]), "texto"] = ""
    tabela.loc[tabela["area"].str.casefold().isin(["", "none", "nan"]), "area"] = ""
    return tabela.loc[(tabela["texto"] != "") & (tabela["area"] != "")].copy()


# =============================================================================
# PASSO 2 — CARREGAMENTO
# =============================================================================
# A tabela bruta ainda mistura ética, civil, penal, trabalho, tributário
# e constitucional. O corte vem no passo 3. Aqui só se consolida.
df = descartar_vazias(consolidar_provas(PASTA_PROVAS))


# =============================================================================
# PASSO 3 — FILTRO DE DOMÍNIO ESTRITO
# =============================================================================
# Por que ficar só nas 127 questões constitucionais
# -------------------------------------------------
# O TF-IDF da etapa seguinte monta uma coluna por termo e pesa cada
# coluna por IDF = log(N / df), onde N é o número de enunciados e df é
# em quantos deles o termo aparece.
#
# Se N fosse as 2220 questões da OAB, dois estragos aconteceriam ao
# mesmo tempo. Primeiro, palavras que atravessam todas as áreas
# ("lei", "direito", "assinale", "correta") teriam df perto de N e IDF
# perto de zero: o peso que deveria separar capítulos some. Segundo,
# termos que parecem específicos, mas se repetem em outra área
# ("competência" no processo civil, "servidor" no trabalho, "prisão"
# no penal), ganhariam df fora da Constituição. A coluna deixa de
# apontar para um capítulo da Carta e passa a apontar para "prova da
# OAB" em geral. O roteador, treinado em cima dessa matriz, diluiria
# a intenção constitucional no meio das outras bancas.
#
# Com N = 127, df só conta ocorrência dentro do direito constitucional.
# "Súmula vinculante" pesa porque distingue controle de constitucionalidade
# dos outros macrotemas, não porque distingue constitucional de ética.
# O .copy() corta o vínculo com o DataFrame cheio: nenhuma operação
# posterior reintroduz as linhas descartadas por visão de memória.
mascara_constitucional = df["area"].eq("constitucional")
df_const = df.loc[mascara_constitucional].copy()

if df_const.shape[0] != QUESTOES_CONSTITUCIONAIS_ESPERADAS:
    raise ValueError(
        "O filtro constitucional devolveu {} linhas; este corpus tem {} "
        "questões com AREA CONSTITUTIONAL.".format(
            df_const.shape[0], QUESTOES_CONSTITUCIONAIS_ESPERADAS
        )
    )


# =============================================================================
# PASSO 4 — MAPEAMENTO DE RÓTULOS
# =============================================================================
# A área "constitucional" é o domínio. A intenção é o capítulo. Sem esta
# coluna o roteador só saberia que a pergunta é de Constituição, e o RAG
# buscaria na Carta inteira. As regras abaixo são o y deste CSV.
#
# A ordem é a regra de desempate. ADI, súmula vinculante e controle
# difuso vêm antes de "Presidente" ou "competência", porque uma questão
# de ADI quase sempre cita também um órgão ou um ente federativo. O
# primeiro termo que casa define o rótulo. Não há voto entre regras:
# voto seria um modelo, e esta etapa ainda não modela.
#
# Estado de defesa e estado de sítio ficam em Direitos e Garantias.
# São o Título V, mas neste recorte aparecem numa questão só, e o
# enunciado fala em suspensão de garantias. Uma classe com um exemplo
# não sustenta frequência; o capítulo de garantias absorve o caso e o
# comentário registra a escolha.

REGRAS_DE_INTENCAO = (
    (
        "Controle de Constitucionalidade",
        (
            "acao direta",
            "acao declaratoria de constitucionalidade",
            "arguicao de descumprimento",
            "adpf",
            "adi",
            "adc",
            "controle de constitucionalidade",
            "controle difuso",
            "controle concentrado",
            "sumula vinculante",
            "sumulas vinculantes",
            "jurisdicao constitucional",
            "reclamacao constitucional",
            "reserva de plenario",
            "deliberacao plenaria",
            "efeito vinculante",
            "eficacia contra todos",
            "declarou inconstitucional",
            "a inconstitucionalidade",
        ),
    ),
    (
        "Direitos e Garantias Fundamentais",
        (
            "habeas corpus",
            "habeas data",
            "mandado de seguranca",
            "mandado de injuncao",
            "acao popular",
            "remedio constitucional",
            "remedios constitucionais",
            "direito fundamental",
            "direitos fundamentais",
            "direitos e garantias",
            "garantia constitucional",
            "garantias constitucionais",
            "sigilo bancario",
            "liberdade de associacao",
            "liberdade de reuniao",
            "reunir se",
            "nacionalidade",
            "brasileiro nato",
            "naturalizado",
            "direitos politicos",
            "inalistaveis",
            "inelegiveis",
            "elegibilidade",
            "partido politico",
            "partidos politicos",
            "fidelidade partidaria",
            "extradicao",
            "expulsao",
            "inviolabilidade do domicilio",
            "acesso a informac",
            "acesso ao poder judiciario",
            "iniciativa popular",
            "sistema eleitoral",
            "direitos economicos sociais e culturais",
            "direitos humanos",
            "estado de defesa",
            "estado de sitio",
            "acusado em outro pais",
            "artigo 5",
            "art 5",
        ),
    ),
    (
        "Organização dos Poderes",
        (
            "poder legislativo",
            "poder executivo",
            "poder judiciario",
            "congresso nacional",
            "camara dos deputados",
            "senado",
            "deputad",
            "senador",
            "presidente da republica",
            "vice presidente",
            "ministro de estado",
            "ministros de estado",
            "medida provisoria",
            "processo legislativo",
            "veto presidencial",
            "vetado",
            "conselho nacional de justica",
            "tribunal de contas",
            "ministerio publico",
            "procurador geral",
            "procuradores gerais",
            "magistrad",
            "quinto constitucional",
            "superior tribunal de justica",
            "processar e julgar",
            "advocacia publica",
            "imunidade formal",
            "imunidade material",
            "lei complementar",
            "lei ordinaria",
            "iniciativa parlamentar",
            "emenda constitucional",
            "emendas constitucionais",
            "nao pode ser emendada",
            "advogado e indispensavel",
            "juiz federal",
            "prestacao jurisdicional",
            "justica federal",
            "justica estadual",
            "impedimento do presidente",
            "vacancia",
        ),
    ),
    (
        "Ordem Econômica e Financeira",
        (
            "atividade economica",
            "ordem economica",
            "reforma agraria",
            "desapropriacao",
            "plano diretor",
            "zoneamento",
            "capital estrangeiro",
            "politica urbana",
        ),
    ),
    (
        "Ordem Social",
        (
            "ordem social",
            "prestacao da saude",
            "direito a educacao",
            "direito a saude",
            "previdencia",
            "seguridade social",
            "universidade",
            "justica desportiva",
            "ensino publico",
        ),
    ),
    (
        "Organização do Estado",
        (
            "entes federativos",
            "ente federativo",
            "estado membro",
            "organizacao do estado",
            "federalismo",
            "federacao",
            "intervencao",
            "administracao publica",
            "servidores publicos",
            "servidor publico",
            "paridade remuneratoria",
            "reparticao de competencia",
            "distribuicao de competencia",
            "competencias",
            "competencia legislativa",
            "normas gerais",
            "mototaxi",
            "novo municipio",
            "integra a federacao",
            "autonomos e compoem",
        ),
    ),
)

ROTULO_RESIDUAL = "Princípios Fundamentais"


def texto_para_regra(texto):
    """Minúsculas, sem acento e sem pontuação, só para casar a regra.

    O enunciado exportado não passa por aqui. "Súmula" e "sumula"
    precisam casar a mesma chave, mas o CSV guarda a grafia da prova
    para a Etapa 2 decidir a limpeza do TF-IDF num lugar só.
    """
    if texto is None or (isinstance(texto, float) and pd.isna(texto)):
        return ""
    texto = str(texto).strip().lower()
    if texto in ("", "none", "nan"):
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(caractere for caractere in texto if not unicodedata.combining(caractere))
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def termo_presente(texto_normalizado, termo):
    """Casa termo já normalizado. Expressão exige fronteira de palavra;
    sigla curta (ADI, ADC, ADPF) também, para não pegar pedaço de outra.
    """
    if not termo or not texto_normalizado:
        return False
    if " " in termo:
        return " {} ".format(termo) in " {} ".format(texto_normalizado)
    return re.search(r"\b{}\b".format(re.escape(termo)), texto_normalizado) is not None


def mapear_intencao(texto):
    """Aplica as regras na ordem e devolve um rótulo não nulo.

    Enunciado vazio não deveria chegar aqui: o passo 3 já tirou as
    linhas sem texto. Se chegar, o residual evita NaN na coluna que
    será y. NaN quebraria o treino supervisionado e, no IDF, a linha
    entraria sem classe, desperdiçando uma posição de N.
    """
    normalizado = texto_para_regra(texto)
    if not normalizado:
        return ROTULO_RESIDUAL
    for rotulo, termos in REGRAS_DE_INTENCAO:
        for termo in termos:
            if termo_presente(normalizado, termo):
                return rotulo
    return ROTULO_RESIDUAL


df_const["intencao"] = df_const["texto"].apply(mapear_intencao)


# =============================================================================
# PASSO 5 — LIMPEZA E EXPORTAÇÃO
# =============================================================================
# Só sobrevivem as duas colunas que a Etapa 2 lê como X e y. Prova,
# número da questão e área ficam de fora: a área já foi o filtro, e
# repetir "constitucional" em toda linha não adiciona termo nem classe.
df_limpo = df_const.loc[:, ["texto", "intencao"]].copy()
df_limpo["texto"] = df_limpo["texto"].fillna("").astype(str).str.strip()
df_limpo["intencao"] = df_limpo["intencao"].fillna("").astype(str).str.strip()
df_limpo = df_limpo.loc[(df_limpo["texto"] != "") & (df_limpo["intencao"] != "")].copy()

if df_limpo["intencao"].eq("").any() or df_limpo["texto"].eq("").any():
    raise ValueError("A tabela final ainda tem enunciado ou intenção vazio.")

if df_limpo.shape[0] != QUESTOES_CONSTITUCIONAIS_ESPERADAS or df_limpo.shape[1] != 2:
    raise ValueError(
        "A exportação deveria ser (127, 2) e saiu {}.".format(df_limpo.shape)
    )

print(df_limpo.shape)
print(df_limpo["intencao"].value_counts().to_string())

ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
df_limpo.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8")
