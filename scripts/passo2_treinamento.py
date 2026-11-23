# -*- coding: utf-8 -*-
"""Etapa 2 — vectorização TF-IDF e treino do roteador constitucional.

O script é linear: lê o CSV limpo, separa treino de teste, ajusta o
pipeline só no treino, mede no teste e grava o modelo. Não há funções
auxiliares. O artefacto final é modelos/roteador_constitucional.joblib, pronto
para o serviço de classificação carregar.
"""

# =============================================================================
# 1. IMPORTAÇÕES
# =============================================================================
# pandas lê a tabela. O resto é o mínimo do scikit-learn para cortar
# os dados, vectorizar, classificar, medir e gravar o objecto inteiro.
# joblib serializa objectos Python com arrays NumPy sem os converter
# numa representação textual.
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import joblib


# A raiz vem do próprio ficheiro, para o CSV e o .joblib serem encontrados
# mesmo que o comando seja lançado fora da pasta do projecto.
_raiz = str(Path(__file__).resolve().parents[1]).replace("\\", "/")
_csv = _raiz + "/datasets/dataset_hibrido_treino.csv"
_modelo = _raiz + "/modelos/roteador_constitucional.joblib"


# =============================================================================
# 2. INGESTÃO — X É O ENUNCIADO, y É A INTENÇÃO
# =============================================================================
# O CSV da Etapa 1 já traz só as 127 questões constitucionais, com as
# colunas texto e intencao. Separar já aqui impede que o rótulo entre
# no vectorizador: se a palavra da classe fosse colada ao enunciado,
# o TF-IDF trataria "Controle de Constitucionalidade" como um termo do
# documento e o modelo acertaria por ler a resposta, não por ler a pergunta.
df = pd.read_csv(_csv, encoding="utf-8")
X = df["texto"]
y = df["intencao"]


# =============================================================================
# 3. DIVISÃO TREINO / TESTE
# =============================================================================
# 80% ajusta o vocabulário, o idf e o hiperplano. 20% fica de fora até
# ao predict. random_state=42 fixa a permutação: a mesma semente devolve
# o mesmo corte, e o relatório não muda entre execuções.
#
# stratify=y é o que torna o corte honesto num corpus jurídico pequeno
# e desequilibrado. Há intenções com dezenas de enunciados e outras com
# quatro ou cinco. Um sorteio simples de 20% pode mandar uma classe rara
# toda para o treino, ou toda para o teste. No primeiro caso o relatório
# não mede essa intenção; no segundo o SVM nunca viu um exemplo e o F1
# dessa classe não tem leitura. A estratificação obriga cada lado a
# repetir a proporção de macrotemas do corpus, por isso a prevalência
# P(intenção) do teste acompanha a do treino. Com 127 linhas, essa
# garantia não é um pormenor: é a diferença entre avaliar o roteador e
# avaliar um acaso da amostra.
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42,
)


# =============================================================================
# 4. PIPELINE — TF-IDF E SVM LINEAR NA MESMA CADEIA
# =============================================================================
# O Pipeline é a função composta f = clf ∘ tfidf. No fit, o vectorizador
# aprende o vocabulário e o vector idf só com X_train e entrega a matriz
# esparsa ao LinearSVC. No predict, o teste passa por transform, nunca
# por um segundo fit: um bigrama que só exista no teste não abre coluna
# nova, e o idf não é recalculado com perguntas que o modelo não pode
# ter visto. É isto que corta a fuga de dados. Ajustar o TF-IDF no
# corpus inteiro antes do split faria o idf de "habeas corpus" contar
# as ocorrências do teste, e a precisão sairia optimista. Como o
# vocabulário vive dentro do Pipeline, o ficheiro do passo 6 congela a
# transformação e o classificador juntos. Dois ficheiros soltos
# permitiriam servir o vocabulário de uma execução e o w de outra.
#
# Matemática do TF-IDF, por termo t no enunciado d:
#   tf-idf(t, d) = tf(t, d) * idf(t)
# sublinear_tf=True troca a contagem crua por 1 + log(tf) quando tf > 0.
# Repetir "lei" três vezes num enunciado longo não triplica o peso: o
# logaritmo achata a frequência. O idf suavizado do scikit-learn é
#   idf(t) = log( (1 + N) / (1 + df(t)) ) + 1
# N é o número de enunciados de treino e df(t) é em quantos deles t
# aparece. "Assinale" e "correta" atravessam quase todas as classes e
# ficam com idf baixo. O termo que distingue um macrotema pesa mais.
# ngram_range=(1, 2) guarda a palavra e o par de palavras contíguas.
# "habeas corpus" e "súmula vinculante" passam a ser uma coluna só,
# em vez de dois unigramas que se misturam com outros usos de "corpus"
# ou de "mínimo". A matriz continua esparsa: cada enunciado ocupa
# poucas dezenas de colunas num vocabulário de milhares de n-gramas,
# e o resto são zeros que não são guardados.
#
# O LinearSVC procura, em one-versus-rest, o hiperplano w·x + b de
# maior margem. x é o vector tf-idf, quase todo nulo. Um núcleo não
# linear teria de comparar pares de enunciados ou encher a matriz; o
# núcleo linear usa o produto interno esparso, que é o regime certo
# quando há muito mais colunas do que linhas. random_state=42 fixa a
# ordem interna do solver quando o dual tem empates numéricos.
#
# class_weight='balanced' muda a função de custo, não o TF-IDF. Sem
# peso, cada enunciado entra na hinge loss com o mesmo coeficiente, e
# a classe com dezenas de questões ("Organização dos Poderes") domina
# a soma: errar uma de "Ordem Social" custa o mesmo que errar uma da
# classe grande, mas a classe grande contribui muito mais termos à
# soma. O peso de uma classe c fica
#   peso(c) = N / (n_classes * n_c)
# N é o tamanho do treino, n_classes o número de intenções e n_c a
# contagem dessa intenção. A classe rara recebe peso alto, a frequente
# peso baixo. Errar o enunciado minoritário passa a penalizar o w com
# mais força, e o hiperplano deixa de poder ignorá-lo para acertar a
# maioria. O equilíbrio é calculado só em y_train, dentro do fit.
pipeline = Pipeline(
    steps=[
        (
            "tfidf",
            TfidfVectorizer(
                ngram_range=(1, 2),
                sublinear_tf=True,
            ),
        ),
        (
            "clf",
            LinearSVC(class_weight="balanced", random_state=42),
        ),
    ]
)


# =============================================================================
# 5. TREINO NO TREINO, PREVISÃO NO TESTE, RELATÓRIO CEGO
# =============================================================================
# y_test não entra no fit nem no predict. A etiqueta verdadeira só
# aparece no relatório, depois da decisão. Precisão: entre o que o
# modelo chamou de uma intenção, a fracção que estava certa. Recall:
# entre as questões dessa intenção, a fracção que o modelo encontrou.
# O F1 é a média harmónica das duas. Um modelo que apenas decorasse as
# palavras do treino perderia o F1 aqui, porque estes enunciados não
# entraram na estimativa do idf nem nos coeficientes w.
pipeline.fit(X_train, y_train)
previsoes = pipeline.predict(X_test)

print(classification_report(y_test, previsoes))


# =============================================================================
# 6. SERIALIZAÇÃO — O MODELO CONGELADO PARA A API DO RAG
# =============================================================================
# O dump grava o Pipeline completo: vocabulário, pesos idf, n-gramas,
# coeficientes w, ordenada na origem b e a lista de classes. Não é uma
# tabela de pesos solta. A API futura faz joblib.load deste ficheiro e
# chama predict numa pergunta nova. O fit não volta a correr em cada
# pedido. A resposta do roteador é o produto w · tfidf(pergunta), com
# o vocabulário que foi estimado neste treino e em mais nenhum.
# O relatório acima mede um corte do híbrido. O artefacto que o serviço
# carrega é outro fit: todas as linhas de dataset_hibrido_treino.csv,
# com o mesmo TF-IDF e o LinearSVC balanceado. Assim o .joblib deixa de
# ser o modelo das 127 questões.
pipeline_hibrido = Pipeline(
    steps=[
        (
            "tfidf",
            TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True),
        ),
        (
            "clf",
            LinearSVC(class_weight="balanced", random_state=42),
        ),
    ]
)
pipeline_hibrido.fit(X, y)
Path(_modelo).parent.mkdir(parents=True, exist_ok=True)
joblib.dump(pipeline_hibrido, _modelo)
print("Modelo híbrido gravado em {} ({} linhas).".format(_modelo, len(X)))
