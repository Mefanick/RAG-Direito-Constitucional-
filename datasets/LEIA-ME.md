# Datasets brutos

Extraídos de `constituicao-main.zip` (Explorador da Constituição, abjur) e `oab-exams-master.zip` (provas da OAB). Nada foi apagado: o que não entra no chatbot ficou em `nao_util`. O recorte fino (quais áreas, qual formato, quais artigos) fica para a próxima instrução.

A lista arquivo a arquivo está em `inventario.csv`.

## constituicao/util

Texto compilado vigente, depois da EC 108 (26/08/2020). Os três arquivos são o mesmo texto em formatos diferentes.

| Arquivo | Uso |
|---|---|
| `vigente/20200826_EMC108.json` | Árvore por título, artigo, inciso e alínea. Melhor candidato a base do RAG. |
| `vigente/20200826_EMC108.csv` | Uma linha por dispositivo, com a posição na árvore. |
| `vigente/CONSTITUICAO.md` | Texto corrido para leitura. |
| `documentacao/` | README e licença de origem. |

## constituicao/nao_util

| Pasta | Por que ficou de fora |
|---|---|
| `historico_csv`, `historico_json` | 92 compilações anteriores. É a mesma Constituição em datas passadas. |
| `html` | HTML do Senado já convertido para JSON, CSV e Markdown. |
| `codigo` | `fonte.R`, o script que gerou os arquivos. |
| `imagens` | Figuras do README. |

## oab/util

Perguntas para o classificador de intenção. As provas oficiais marcam a alternativa certa com `CORRECT` e, quando há rótulo, a área numa linha `AREA`.

| Pasta | Conteúdo |
|---|---|
| `provas_oficiais` | 27 provas (2010 a 2018), 2220 questões. 1289 têm área; 931 estão com `AREA` vazio. |
| `provas_simuladas` | 30 simulados da FGV Direito Rio, já em texto. |
| `justificativas/const.yaml` | Algumas questões de constitucional ligadas ao artigo que fundamenta a resposta. |
| `normas_constitucionais` | `1988.xml` e `adct.xml`. Podem estar defasados em relação à EC 108. |
| `auxiliar` | Stopwords do português. |
| `documentacao` | READMEs, licença, errata e `classify.org` (o critério dos rótulos). |

Áreas já preenchidas nas provas oficiais:

| Área | Questões |
|---|---|
| ETHICS | 185 |
| CONSTITUTIONAL | 127 |
| CIVIL | 115 |
| CIVIL-PROCEDURE | 102 |
| ADMINISTRATIVE | 100 |
| LABOUR | 94 |
| CRIMINAL | 90 |
| CRIMINAL-PROCEDURE | 87 |
| LABOUR-PROCEDURE | 80 |
| TAXES | 77 |
| BUSINESS | 71 |
| HUMAN-RIGHTS | 32 |
| CONSUMER | 30 |
| CHILDREN | 30 |
| INTERNATIONAL | 28 |
| ENVIRONMENTAL | 26 |
| PHILOSOPHY | 12 |
| PHILOSHOPY | 2 |
| INTERNATIONAL CONSTITUTIONAL | 1 |

`PHILOSHOPY` é erro de grafia no arquivo original. `INTERNATIONAL CONSTITUTIONAL` é um rótulo duplo numa questão só.

## oab/nao_util

| Pasta | Por que ficou de fora |
|---|---|
| `pdf_oficiais` | PDF da prova. O texto já está em `provas_oficiais`. |
| `docx_simulados`, `gabaritos_odt` | Fontes dos simulados. O texto e a resposta já estão no `.txt`. |
| `experimentos` | Saídas e scripts de PMI, IR e WSD. Não são questões. |
| `codigo` | Parsers do repositório original. |
| `outras_normas` | Estatuto da OAB, código de ética, leis esparsas e os `.doc` de origem. |
| `justificativas_etica` | Fundamento de questões de ética, fora do chatbot da Constituição. |
| `outros` | `.gitignore` do repositório de origem. |
