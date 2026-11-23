# -*- coding: utf-8 -*-
"""
Prova de conceito: classificador de intenções para um chatbot
sobre a Constituição da República Federativa do Brasil de 1988.

O script é linear de propósito. Ele mostra, em uma única execução, o
caminho clássico de um classificador de texto:

    texto bruto -> limpeza -> TF-IDF -> Naive Bayes -> intenção prevista

O que este arquivo faz agora
----------------------------
Aprende a separar perguntas curtas em três intenções jurídicas
(Direitos Trabalhistas, Impostos e Penal) e classifica frases que
não estavam no treino.

O que o projeto final fará no lugar disto
------------------------------------------
A intenção deixa de ser a resposta mostrada ao usuário. Ela vira um
roteador do sistema de RAG (Retrieval-Augmented Generation):

    1. Este classificador escolhe o capítulo constitucional.
    2. Um retriever busca os artigos correspondentes em uma base vetorial.
    3. Um modelo de linguagem responde citando somente esses trechos.

Nenhuma linha daqui produz aconselhamento jurídico. A PoC só demonstra
que o algoritmo consegue aprender a diferença entre os temas.

Dependência externa (biblioteca, não arquivo de dados):
    pip install scikit-learn
"""

# =============================================================================
# IMPORTS
# =============================================================================
# Biblioteca padrão: normalização de acentos sem instalar nada além do
# scikit-learn. No projeto final, esta etapa tende a sair daqui e ir
# para um pipeline do spaCy (modelo pt_core_news), que também faz
# lematização e reconhecimento de entidades como "União" e "CLT".
import re
import sys
import unicodedata

# scikit-learn é a escolha didática da disciplina: a mesma API serve
# para a PoC de 15 frases e, depois, para o corpus real.
# Pipeline encadeia limpeza, vetorização e classificador para que a
# frase nova passe exatamente pelas mesmas transformações do treino.
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer


# =============================================================================
# DATASET DE AMOSTRA
# =============================================================================
# ATENÇÃO DIDÁTICA: estes 15 pares são um brinquedo embutido no código
# para a PoC rodar em qualquer computador, sem CSV, sem Kaggle e sem rede.
#
# No projeto final, as duas listas abaixo são substituídas por um dataset
# carregado de arquivo, por exemplo:
#
#     df = pd.read_csv("intencoes_constitucionais.csv")
#     textos = df["pergunta"].tolist()
#     rotulos = df["intencao"].tolist()
#
# Esse CSV deve nascer de perguntas reais (ou parafraseadas por alunos)
# rotuladas à mão. A meta da disciplina não é "acertar 15 frases", e sim
# mostrar o método que continua válido quando o arquivo tiver milhares
# de linhas.
#
# Os rótulos apontam para blocos da Constituição de 1988 que o RAG, mais
# adiante, usará como filtro de busca:
#   - Direitos Trabalhistas -> art. 7º (e normas correlatas)
#   - Impostos               -> arts. 145 a 162 (Sistema Tributário)
#   - Penal                  -> art. 5º, incisos sobre liberdade, pena
#                               e processo penal (LIV, LVII, LXI, LXVIII, XLIII)
#
# As frases de teste, no final do arquivo, NÃO aparecem aqui. Se a frase
# de demonstração estiver no treino, o print só prova memorização.

textos = [
    # --- Direitos Trabalhistas (art. 7º) ---
    "O trabalhador tem direito a férias anuais remuneradas?",
    "Qual é o valor do salário mínimo previsto na Constituição?",
    "A jornada de trabalho pode ultrapassar oito horas diárias?",
    "A empregada gestante possui estabilidade no emprego?",
    "O décimo terceiro salário é um direito do trabalhador urbano e rural?",
    # --- Impostos (arts. 145 a 162) ---
    "Quem tem competência para instituir um novo imposto?",
    "A legalidade tributária exige lei para criar um tributo?",
    "Templos de qualquer culto possuem imunidade de impostos?",
    "O imposto de renda é de competência da União?",
    "A anterioridade tributária impede cobrar o tributo no mesmo exercício?",
    # --- Penal (art. 5º, garantias penais e processuais) ---
    "Quando a Constituição permite a prisão em flagrante?",
    "O que significa a presunção de inocência no processo penal?",
    "A Constituição admite pena de morte no Brasil?",
    "O habeas corpus protege a liberdade de locomoção?",
    "Crimes hediondos seguem regras mais severas de prisão?",
]

rotulos = [
    "Direitos Trabalhistas",
    "Direitos Trabalhistas",
    "Direitos Trabalhistas",
    "Direitos Trabalhistas",
    "Direitos Trabalhistas",
    "Impostos",
    "Impostos",
    "Impostos",
    "Impostos",
    "Impostos",
    "Penal",
    "Penal",
    "Penal",
    "Penal",
    "Penal",
]

# Palavras funcionais do português. Removê-las ajuda o TF-IDF a olhar
# para "ferias", "imposto" e "prisao" em vez de "de", "para" e "que".
# No corpus grande, a lista pode vir do NLTK
# (stopwords.words("portuguese")) ou do spaCy.
#
# "nao" e "sem" ficam de fora de propósito: em texto jurídico a negação
# muda o sentido ("pode criar imposto" x "nao pode criar imposto").
# Um pré-processador de produção precisa tratar negação com regra própria,
# não jogá-la fora junto com as stopwords.
STOPWORDS_PT = {
    "a", "o", "os", "as", "um", "uma", "uns", "umas",
    "de", "da", "do", "das", "dos", "em", "na", "no", "nas", "nos",
    "por", "para", "com", "sob", "sobre", "entre",
    "e", "ou", "mas", "que", "se", "como", "qual", "quais",
    "ao", "aos", "pelo", "pela", "pelos", "pelas",
    "eu", "me", "meu", "minha", "isso", "este", "esta", "esse", "essa",
    "ser", "sao", "foi", "era", "ter", "tem", "ha",
    "sua", "seu", "seus", "suas",
    # Verbos e dêiticos da pergunta ("tenho direito", "pode instituir").
    # Não carregam o tema. Sem este corte, o TF-IDF destaca "pode" com o
    # mesmo peso de "imposto" e a explicação do seminário fica turva.
    "tenho", "temos", "tinha", "pode", "posso", "podem", "poderia",
    "quando", "onde", "porque", "significa", "previsto", "prevista",
}


# =============================================================================
# ETAPA 1 — LIMPEZA E PRÉ-PROCESSAMENTO
# =============================================================================
def limpar_texto(texto):
    """Normaliza uma frase para o vocabulário ficar estável.

    O que acontece agora
    --------------------
    Minúsculas, remoção de acento, troca de pontuação por espaço e corte
    de stopwords. "Férias" e "ferias" viram o mesmo token. Sem isso, o
    TF-IDF trataria as duas grafias como palavras sem relação.

    O que acontece no projeto final
    --------------------------------
    Esta função ganha lematização ("preso" e "prisão" -> mesmo lema) e
    um dicionário jurídico pequeno (CLT, IR, HC) para não quebrar siglas.
    A limpeza passa a ser um passo versionado do pipeline, igual para
    treino, validação e pergunta do usuário. Limpar só o treino e esquecer
    a pergunta nova é um erro clássico: o modelo não reconhece o que viu.
    """
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(caractere for caractere in texto if not unicodedata.combining(caractere))
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()

    tokens = [token for token in texto.split() if token not in STOPWORDS_PT and len(token) > 1]
    return " ".join(tokens)


def limpar_corpus(textos_brutos):
    """Aplica a limpeza a uma lista de frases.

    O Pipeline do scikit-learn entrega o lote inteiro, não uma string
    isolada. Por isso existe este adaptador. No projeto final, o mesmo
    contrato (entra uma sequência, sai uma sequência) permite trocar a
    função por um serviço de pré-processamento sem reescrever o treino.
    """
    return [limpar_texto(texto) for texto in textos_brutos]


# =============================================================================
# ETAPA 2 — VETORIZAÇÃO (TF-IDF)
# =============================================================================
def criar_vetorizador():
    """Converte cada frase limpa em um vetor numérico de TF-IDF.

    O que acontece agora
    --------------------
    TF-IDF (Term Frequency – Inverse Document Frequency) conta quantas
    vezes o termo aparece na frase e reduz o peso dos termos que aparecem
    em quase todas as classes. "direito" ajuda menos do que "ferias" ou
    "flagrante", porque estes últimos distinguem o tema.

    ngram_range=(1, 2) guarda a palavra e o par de palavras vizinhas.
    Assim "habeas corpus" e "salario minimo" podem pesar como uma unidade,
    não só como dois termos soltos. Em 15 frases o efeito é pequeno; em
    um código comentado artigo por artigo, o bigrama evita misturar
    "pena de morte" com qualquer outra ocorrência de "pena".

    O que acontece no projeto final
    --------------------------------
    Aqui a string vira uma matriz esparsa. Com 15 exemplos o número de
    colunas é da ordem das dezenas. No corpus completo (Constituição,
    leis complementares e julgados), o vocabulário passa facilmente de
    dezenas de milhares de colunas. A matriz continua esparsa (scipy),
    então não é obrigatório materializá-la densa; ainda assim, uma máquina
    com memória folgada — na ordem de 24 GB de RAM — permite experimentar
    vocabulários grandes, n-gramas de caracteres e mais de um vetorizador
    em paralelo durante a validação.

    Quando o trabalho migrar para RAG, este TF-IDF pode continuar como
    classificador de intenção (barato e explicável) enquanto a BUSCA dos
    artigos usa embeddings densos. São dois vetores com papéis diferentes:
    um escolhe o tema, o outro recupera o trecho.
    """
    return TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
        # A limpeza já fez minúsculas e tirou acento. Manter lowercase aqui
        # é só uma rede de segurança, caso alguma frase pule a etapa 1.
        lowercase=True,
    )


# =============================================================================
# ETAPA 3 — MODELO (NAIVE BAYES MULTINOMIAL)
# =============================================================================
def criar_classificador():
    """Escolhe o algoritmo que aprende a ligar o vetor TF-IDF à intenção.

    O que acontece agora
    --------------------
    MultinomialNB trata o vetor como evidência de contagem (valores
    não negativos, exatamente o que o TF-IDF entrega) e estima, para cada
    classe, quais termos são mais típicos. Com poucas frases e três temas
    bem separados no vocabulário, ele é estável e ainda devolve
    probabilidade — útil para mostrar "o quanto" o modelo acredita.

    alpha=1.0 é o suavizador de Laplace: um termo que nunca apareceu em
    uma classe não zera a probabilidade da frase inteira. Em amostra
    minúscula isso importa, porque quase todo termo é raro.

    O que acontece no projeto final
    --------------------------------
    A alternativa natural, quando as classes passarem a se sobrepor
    (a mesma pergunta toca trabalho e tributo, por exemplo), é um
    SVM linear (sklearn.svm.LinearSVC) ou uma regressão logística,
    comparados por validação cruzada. O Naive Bayes permanece como
    linha de base: se o modelo mais caro não ganhar dele por uma margem
    clara, não há motivo para carregá-lo no chatbot.

    O SVM não entrega probabilidade nativa. Se a interface precisar de
    um limiar de confiança antes de chamar o RAG, será preciso calibrar
    (CalibratedClassifierCV) ou ficar com um modelo probabilístico.
    """
    return MultinomialNB(alpha=1.0)


def criar_pipeline():
    """Monta limpeza + TF-IDF + Naive Bayes em um único estimador.

    O que acontece agora
    --------------------
    O objeto Pipeline garante a ordem. fit() só olha o treino.
    predict() aplica a mesma limpeza e o mesmo vocabulário já aprendido
    (transform, não fit_transform) na frase nova.

    O que acontece no projeto final
    --------------------------------
    Este objeto é o artefato salvo com joblib e carregado pela API do
    chatbot. O vocabulário do TF-IDF precisa viajar junto com o modelo:
    treinar de novo a cada pergunta mudaria as colunas e invalidaria os
    pesos. Em produção também entram métricas (matriz de confusão,
    macro-F1) e um conjunto de validação separado. Aqui não há split:
    15 linhas não sustentam uma acurácia digna de relatório. O print
    final é uma demonstração qualitativa, não um resultado experimental.
    """
    return Pipeline(
        steps=[
            ("limpeza", FunctionTransformer(limpar_corpus, validate=False)),
            ("tfidf", criar_vetorizador()),
            ("classificador", criar_classificador()),
        ]
    )


# =============================================================================
# ETAPA 4 — INFERÊNCIA
# =============================================================================
def prever_intencao(frase, pipeline_treinado):
    """Classifica uma frase inédita e devolve um dicionário explicável.

    O que acontece agora
    --------------------
    A frase entra crua. O pipeline limpa, projeta no vocabulário do treino
    e o Naive Bayes escolhe a classe de maior probabilidade. Também
    devolvemos o ranking das classes e os termos da pergunta com maior
    TF-IDF, para o seminário mostrar o porquê da decisão — não só o rótulo.

    O que acontece no projeto final
    --------------------------------
    A chave "intencao" não vai para a tela como resposta final. Ela
    seleciona o filtro do retriever:

        Direitos Trabalhistas -> chunks do art. 7º
        Impostos               -> chunks dos arts. 145–162
        Penal                  -> chunks penais do art. 5º

    Se a probabilidade máxima ficar abaixo do limiar, o sistema não deve
    inventar um capítulo. O caminho seguro é pedir reformulação ou buscar
    na Constituição inteira, sem filtro. Isso evita uma resposta de
    "Impostos" para uma pergunta de "Penal" só porque o modelo foi forçado
    a escolher uma das três.
    """
    classe = pipeline_treinado.predict([frase])[0]
    probabilidades = pipeline_treinado.predict_proba([frase])[0]
    nomes_das_classes = pipeline_treinado.named_steps["classificador"].classes_

    distribuicao = sorted(
        zip(nomes_das_classes, probabilidades),
        key=lambda par: par[1],
        reverse=True,
    )

    frase_limpa = limpar_texto(frase)
    vetor = pipeline_treinado.named_steps["tfidf"].transform([frase_limpa])
    nomes_dos_termos = pipeline_treinado.named_steps["tfidf"].get_feature_names_out()
    pesos = vetor.toarray()[0]
    termos_relevantes = sorted(
        (
            (nomes_dos_termos[indice], pesos[indice])
            for indice in vetor.nonzero()[1]
        ),
        key=lambda par: par[1],
        reverse=True,
    )[:5]

    return {
        "frase": frase,
        "frase_limpa": frase_limpa,
        "intencao": classe,
        "distribuicao": distribuicao,
        "termos_relevantes": termos_relevantes,
    }


def imprimir_predicao(resultado):
    """Mostra a decisão em texto corrido, legível na defesa do trabalho.

    O percentual do Naive Bayes nesta PoC fica perto de 1/3 mesmo quando
    a ordem das classes está certa. alpha=1 soma um "voto fantasma" a
    cada termo do vocabulário, e o vocabulário (com bigramas) é muito
    maior do que as 15 frases. A leitura honesta para o seminário é a
    ordem, não um número que pareça certeza. O limiar que autoriza
    filtrar o RAG só deve ser fixado depois, com validação cruzada.
    """
    print("-" * 72)
    print("Pergunta:          {}".format(resultado["frase"]))
    print("Após a limpeza:    {}".format(resultado["frase_limpa"]))
    print("Intenção prevista: {}".format(resultado["intencao"]))
    print("Probabilidades (ordem do modelo, não certeza calibrada):")
    for classe, probabilidade in resultado["distribuicao"]:
        print("  - {:<24} {:.1%}".format(classe, probabilidade))

    if resultado["termos_relevantes"]:
        termos_formatados = ", ".join(
            "{} ({:.2f})".format(termo, peso)
            for termo, peso in resultado["termos_relevantes"]
        )
        print("Termos de maior TF-IDF na pergunta: {}".format(termos_formatados))
    else:
        # Vocabulário sem interseção: o modelo só tem a frequência das
        # classes para se apoiar. No chatbot real, este caso volta para
        # uma pergunta de esclarecimento em vez de seguir para o RAG.
        print("Nenhum termo da pergunta existe no vocabulário de treino.")

    print(
        "Leitura da PoC: a classe vencedora é '{}'. "
        "No RAG ela escolheria o capítulo correspondente. "
        "O percentual ainda não serve de limiar — falta amostra de validação.".format(
            resultado["intencao"]
        )
    )


def configurar_terminal():
    """Força UTF-8 na saída do console.

    O Prompt clássico do Windows ainda usa a página 1252. Sem este ajuste,
    'Constituição' e 'férias' aparecem quebrados justamente na hora da
    demonstração. A API do projeto final responde JSON em UTF-8; este
    cuidado fica restrito ao script de seminário.
    """
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
            ctypes.windll.kernel32.SetConsoleCP(65001)
        except (AttributeError, OSError):
            pass

    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            try:
                fluxo.reconfigure(encoding="utf-8")
            except (AttributeError, OSError, ValueError):
                pass


# =============================================================================
# EXECUÇÃO FINAL — TREINA NA HORA E TESTA FRASES INÉDITAS
# =============================================================================
def main():
    """Treina o pipeline na amostra e classifica duas perguntas novas.

    Não há modelo pré-gravado. Cada execução reaprende os 15 exemplos,
    o que é correto para uma PoC reprodutível: quem abrir o arquivo vê
    o treino acontecer. No projeto final, o fit sai da requisição do
    usuário e vai para um script de treino agendado; a API só dá load
    no arquivo .joblib.
    """
    configurar_terminal()

    if len(textos) != len(rotulos):
        raise ValueError("Cada frase de treino precisa de exatamente um rótulo.")

    print("=" * 72)
    print("PoC — classificador de intenções da Constituição de 1988")
    print("Treino em memória, sem CSV. O modelo nasce e é testado nesta execução.")
    print("=" * 72)

    pipeline = criar_pipeline()
    pipeline.fit(textos, rotulos)

    matriz = pipeline.named_steps["tfidf"].transform(limpar_corpus(textos))
    vocabulario = pipeline.named_steps["tfidf"].get_feature_names_out()

    print("Exemplos de treino: {}".format(len(textos)))
    print("Classes aprendidas: {}".format(", ".join(pipeline.classes_)))
    print("Termos no vocabulário TF-IDF: {}".format(len(vocabulario)))
    print(
        "Formato da matriz de treino (linhas = frases, colunas = termos): {}".format(
            matriz.shape
        )
    )
    print(
        "No corpus real essa segunda dimensão deixa de ser um número pequeno "
        "e passa a refletir o vocabulário jurídico inteiro, ainda em matriz esparsa."
    )

    # Frases inéditas: não estão na lista `textos`. Elas reutilizam termos
    # típicos de cada classe ("ferias", "imposto", "prisao") porque, sem
    # lematizador e com 15 linhas, o modelo só generaliza por vocabulário
    # compartilhado. É exatamente o limite que o seminário deve enxergar
    # antes de prometer um chatbot jurídico.
    perguntas_de_teste = [
        "Tenho direito a férias?",
        "A União pode instituir um imposto novo?",
    ]

    for pergunta in perguntas_de_teste:
        imprimir_predicao(prever_intencao(pergunta, pipeline))

    print("-" * 72)
    print(
        "Fim da demonstração. O próximo passo do trabalho não é aumentar "
        "este arquivo: é trocar a lista manual por um CSV rotulado e usar "
        "a intenção prevista como filtro do retriever do RAG."
    )


if __name__ == "__main__":
    main()
