# Bateria cega da Fase 3.3 — baseline_sem_ponte

## Resumo executivo

Perfil baseline_sem_ponte. Este relatório audita 15 perguntas inéditas e 2 regressões históricas. O histórico de cada chamada fica vazio. As três colunas do placar são independentes.

| Métrica | Resultado |
| --- | --- |
| Recuperação na 1ª passagem (12 inéditas) | 10/12 |
| Artigo esperado recuperado (12 inéditas) | 9/12 |
| Auditoria FIEL (12 inéditas) | 9/12 |
| Recuperação na 1ª passagem (2 regressões) | 2/2 |
| Auditoria FIEL (2 regressões) | 2/2 |
| Fora de escopo sem artigo inventado | 1/2 |
| Atalho social abaixo de 0,1 s | 1/1 |
| Retriever médio (s) | 10.21 |
| Prefill médio (s) | 40.85 |
| Pensamento médio (s) | 0.00 |
| Gerador médio (s) | 118.16 |
| Total médio (s) | 136.20 |

## Placar

| Caso | 1. Artigo na 1ª passagem | 2. Auditor FIEL | 3. Checklist de revisão humana |
| --- | --- | --- | --- |
| 01 LEIGO / EXCECAO | sim | sim | Art. 5º, XI: ordem judicial só de dia; à noite, flagrante, desastre ou socorro. |
| 02 LEIGO / EXCECAO | sim | sim | Art. 5º, LXVII: vedada a prisão civil por dívida, com as ressalvas do próprio inciso. |
| 03 TRIBUTACAO / LEIGO | não | ALUCINACAO_ARTIGO | Art. 150, VI, b: imunidade dos templos. Classe Tributação e Orçamento. |
| 04 TRIBUTACAO / PRAZO | não | SEM_CITACAO | Art. 150, III, b e c: anterioridade anual e nonagesimal, com exceções. |
| 05 TRIBUTACAO / COMPETENCIA | não | sim | Art. 155, I: Estados e Distrito Federal. |
| 06 ADCT / LEIGO | sim | sim | ADCT, Art. 10, II, b: da confirmação da gravidez até cinco meses após o parto. |
| 07 PARENT-DOC / NUMERO | sim | sim | Art. 14, § 3º, VI, a: 35 anos. |
| 08 PARENT-DOC / INCISOS | sim | sim | Art. 12, § 4º, fiel ao texto vigente recuperado, sem inciso inventado. |
| 09 COMPOSTA / MULTI-HOP | sim | sim | Art. 37, XVI, a e Art. 37, XI. |
| 10 COMPOSTA / MULTI-HOP | sim | sim | Art. 62, § 1º, I, b e Art. 62, § 3º. |
| 11 ORDEM SOCIAL / LEIGO | sim | sim | Art. 199: livre à iniciativa privada; § 2º veda recursos públicos a entidades com fins lucrativos. |
| 12 TRABALHO / LEIGO | não | ALUCINACAO_ARTIGO | Art. 7º, XIII e XVI: 8 horas, 44 semanais e hora extra de pelo menos 50%. |
| 13 FORA DE ESCOPO / CDC | não se aplica | SEM_CITACAO | Conversa livre ou zona cinzenta, Código de Defesa do Consumidor, sem artigo inventado da CF/88. |
| 14 FORA DE ESCOPO / TRANSITO | não se aplica | ALUCINACAO_ARTIGO | Conversa livre, CTB ou Código Civil, sem artigo inventado da CF/88. |
| 15 ATALHO SOCIAL | não se aplica | SEM_CITACAO | MODO_ATALHO_SOCIAL em menos de 0,1 s, sem BGE-M3 e sem Ollama. |
| 16 REGRESSAO / ESCOPO - MINERACAO | sim | sim | Não começar com Sim. Restringir a minérios nucleares (Art. 177, V ou § 4º) e ao regime de autorização ou concessão (Art. 176). Sem generalizar. |
| 17 REGRESSAO / LIMITE NUMERICO - USUCAPIAO | sim | sim | Art. 191: até 50 hectares, cinco anos, trabalho da família, moradia, sem outro imóvel. Não misturar o Art. 186. |

## Resposta integral e checklist

### 01 — LEIGO / EXCECAO

Pergunta: A polícia pode arrombar a porta da minha casa à noite só com ordem do juiz?

Esperado: Art. 5º, XI: ordem judicial só de dia; à noite, flagrante, desastre ou socorro.

- Intenção: Direitos e Garantias Fundamentais (margem 0.17552641440349417)
- modo_busca: densa_com_boost
- classe: SIMPLES
- passagem: 1 | tradutor: None | sub-consultas: []
- Modo final: MODO_RAG_ZONA_CINZENTA
- Entregue ao LLM: Art. 5º, XI [reranker]; Art. 5º, LXI [reranker]; Art. 136, § 3º [reranker]
- Checklist humano: Art. 5º, XI: ordem judicial só de dia; à noite, flagrante, desastre ou socorro.
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 5"], "subdispositivos_citados": ["Art. 5, XI"], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 17.94 | prefill 94.36 | thinking n/d | gerador 268.43 | total 319.67

Resposta integral:

A polícia não pode arrombar a porta da sua casa à noite apenas com ordem do juiz. O Art. 5º, XI da Constituição estabelece que a casa é asilo inviolável, e a entrada é permitida apenas em casos de flagrante delito, desastre, para prestar socorro ou, durante o dia, por determinação judicial. A menção a "durante o dia" indica que, à noite, a autoridade judicial não basta; seria necessário outro fundamento, como o flagrante delito, para que a entrada seja autorizada. Portanto, a simples ordem judicial não é suficiente para autorizar a violação da inviolabilidade da casa em horário noturno.

### 02 — LEIGO / EXCECAO

Pergunta: Se eu dever um empréstimo no banco e não pagar, posso ir preso?

Esperado: Art. 5º, LXVII: vedada a prisão civil por dívida, com as ressalvas do próprio inciso.

- Intenção: Direitos e Garantias Fundamentais (margem 0.14846565362037512)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 1 | tradutor: None | sub-consultas: []
- Modo final: MODO_RAG_ZONA_CINZENTA
- Entregue ao LLM: Art. 5º, LXVII [reranker]; ADCT, Art. 97, IV [reranker]; Art. 5º, LXXV [reranker]
- Checklist humano: Art. 5º, LXVII: vedada a prisão civil por dívida, com as ressalvas do próprio inciso.
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 5"], "subdispositivos_citados": ["Art. 5, LXVII"], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 7.08 | prefill 42.24 | thinking n/d | gerador 286.41 | total 299.73

Resposta integral:

A Constituição Federal de 1988 estabelece que **não haverá prisão civil por dívida**, salvo em casos específicos. O Art. 5º, LXVII da Constituição afirma: *"não haverá prisão civil por dívida, salvo a do responsável pelo inadimplemento voluntário e inescusável de obrigação alimentícia e a do depositário infiel"*. Isso significa que, em geral, não é possível ser preso por não pagar um empréstimo comum, a menos que a dívida esteja ligada a uma obrigação alimentar (como pensão) ou envolva um depositário infiel (quem recebeu bens em depósito e os perdeu). 

Ainda que haja outras medidas, como penhora de bens ou restrições ao crédito, a prisão por dívida não é uma consequência prevista no texto constitucional. Portanto, **não é possível ser preso por não pagar um empréstimo no banco** em situação normal.

### 03 — TRIBUTACAO / LEIGO

Pergunta: A prefeitura pode cobrar IPTU de uma igreja do meu bairro?

Esperado: Art. 150, VI, b: imunidade dos templos. Classe Tributação e Orçamento.

- Intenção: Tributação e Orçamento (margem 0.13231282637331582)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 2 | tradutor: competência municipal IPTU bens imóveis religiosos | sub-consultas: []
- Modo final: MODO_CONVERSA_LIVRE
- Entregue ao LLM: (nenhum)
- Checklist humano: Art. 150, VI, b: imunidade dos templos. Classe Tributação e Orçamento.
- Auditoria: {"status": "ALUCINACAO_ARTIGO", "artigos_citados": ["Art. 150"], "subdispositivos_citados": [], "artigos_inventados": ["Art. 150"], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 11.03 | prefill 13.06 | thinking n/d | gerador 98.90 | total 121.55

Resposta integral:

A prefeitura **pode cobrar IPTU de uma igreja**, desde que ela possua **imóvel urbano** e esteja **localizado em área urbana**, conforme previsto na Constituição Federal de 1988.

A Constituição Federal, em seu **Artigo 150**, estabelece que os **imóveis urbanos** são tributados com o **IPTU** (Imposto Predial e Territorial Urbano), independentemente da natureza da pessoa que os possua — seja pessoa física, pessoa jurídica, ou mesmo entidades religiosas, como igrejas.

No entanto, é importante destacar que, em alguns casos, **igrejas podem ter isenção ou redução de IPTU**, conforme previsto em **Lei Complementar nº 87/1996**, que estabelece normas sobre a **isenção de tributos** para **entidades religiosas**, **filantrópicas**

### 04 — TRIBUTACAO / PRAZO

Pergunta: O governo pode criar um imposto hoje e começar a cobrar na semana que vem?

Esperado: Art. 150, III, b e c: anterioridade anual e nonagesimal, com exceções.

- Intenção: Tributação e Orçamento (margem 0.3785086219118428)
- modo_busca: densa_com_boost
- classe: SIMPLES
- passagem: 1 | tradutor: None | sub-consultas: []
- Modo final: MODO_CONVERSA_LIVRE
- Entregue ao LLM: (nenhum)
- Checklist humano: Art. 150, III, b e c: anterioridade anual e nonagesimal, com exceções.
- Auditoria: {"status": "SEM_CITACAO", "artigos_citados": [], "subdispositivos_citados": [], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 13.92 | prefill 11.75 | thinking n/d | gerador 80.22 | total 130.48

Resposta integral:

Não, o governo **não pode criar um imposto e começar a cobrar na semana seguinte**. A Constituição Federal de 1988 estabelece que a criação de novos impostos exige **leis complementares**, que devem ser aprovadas pelo Congresso Nacional. Isso garante que a criação de impostos seja feita com transparência, com o devido debate e com o respeito aos direitos dos cidadãos.

Além disso, a Constituição prevê que **impostos não podem ser criados por meio de leis ordinárias**, apenas por leis complementares. Isso significa que o processo é mais rigoroso e demorado, garantindo que os impostos sejam criados com base em critérios técnicos, econômicos e sociais.

Se houver uma necessidade urgente, o governo pode propor uma **lei complementar** que inclua a criação do imposto, mas mesmo assim, o processo leva tempo para

### 05 — TRIBUTACAO / COMPETENCIA

Pergunta: Se eu receber um terreno de doação em vida, quem cobra o imposto sobre essa doação: a Prefeitura, o Estado ou a União?

Esperado: Art. 155, I: Estados e Distrito Federal.

- Intenção: Tributação e Orçamento (margem 0.17087174247952472)
- modo_busca: densa_com_boost
- classe: SIMPLES
- passagem: 2 | tradutor: imposto transmissão bens imóveis inter vivos ato oneroso ITBI competência municipal | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 156 (9 filhos); Art. 156, § 2º (2 filhos)
- Checklist humano: Art. 155, I: Estados e Distrito Federal.
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 156"], "subdispositivos_citados": ["Art. 156, I, II", "Art. 156, II, I"], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 13.34 | prefill 132.61 | thinking n/d | gerador 227.90 | total 255.03

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas aos impostos instituídos pelos Municípios, conforme Art. 156, I, II e III, e não há base para generalizar para outros níveis de governo. O imposto sobre a transmissão inter vivos de bens imóveis, como a doação em vida, é de competência dos Municípios, conforme Art. 156, II, I, que dispõe que "não incide sobre a transmissão de bens ou direitos incorporados ao patrimônio de pessoa jurídica em realização de capital, nem sobre a transmissão de bens ou direitos decorrente de fusão, incorporação, cisão ou extinção de pessoa jurídica, salvo se, nesses casos, a atividade preponderante do adquirente for a compra e venda desses bens ou direitos, locação de bens imóveis ou arrendamento mercantil". Portanto, se o terreno for recebido por doação em vida, o imposto sobre essa transmissão caberá à Prefeitura, ou seja, ao Município.

### 06 — ADCT / LEIGO

Pergunta: Uma funcionária grávida pode ser demitida sem justa causa logo depois de ter o bebê?

Esperado: ADCT, Art. 10, II, b: da confirmação da gravidez até cinco meses após o parto.

- Intenção: Direitos e Garantias Fundamentais (margem 0.019026537424854495)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 1 | tradutor: None | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: ADCT, Art. 10 (6 filhos)
- Checklist humano: ADCT, Art. 10, II, b: da confirmação da gravidez até cinco meses após o parto.
- Auditoria: {"status": "FIEL", "artigos_citados": ["ADCT Art. 10"], "subdispositivos_citados": ["ADCT Art. 10, II, \"b\""], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 5.04 | prefill 59.83 | thinking n/d | gerador 91.94 | total 97.43

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas à empregada gestante, não há base para generalizar para outras situações. A funcionária grávida **não pode ser demitida sem justa causa** desde a confirmação da gravidez até cinco meses após o parto, conforme previsto no ADCT, Art. 10, II, alínea b.

### 07 — PARENT-DOC / NUMERO

Pergunta: Com quantos anos uma pessoa pode se candidatar a senador ou a presidente da República?

Esperado: Art. 14, § 3º, VI, a: 35 anos.

- Intenção: Organização dos Poderes (margem 0.031106052763537978)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 1 | tradutor: None | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 14, § 3º (2 filhos); Art. 82 (1 filhos)
- Checklist humano: Art. 14, § 3º, VI, a: 35 anos.
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 14"], "subdispositivos_citados": ["Art. 14, § 3º, VI, \"a\""], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 16.26 | prefill 33.97 | thinking n/d | gerador 74.02 | total 91.20

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas a condições de elegibilidade para cargos eletivos; não há base para generalizar para outros cargos. Para se candidatar a senador, a pessoa deve ter, no mínimo, trinta e cinco anos, conforme previsto no art. 14, § 3º, VI, alínea a, da Constituição. Para se candidatar a presidente da República, também é necessário ter, no mínimo, trinta e cinco anos, conforme previsto no mesmo dispositivo legal.

### 08 — PARENT-DOC / INCISOS

Pergunta: Em quais situações um brasileiro nato pode acabar perdendo a nacionalidade brasileira?

Esperado: Art. 12, § 4º, fiel ao texto vigente recuperado, sem inciso inventado.

- Intenção: Direitos e Garantias Fundamentais (margem 0.020589243677111596)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 1 | tradutor: None | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 12, § 4º (2 filhos)
- Checklist humano: Art. 12, § 4º, fiel ao texto vigente recuperado, sem inciso inventado.
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 12"], "subdispositivos_citados": ["Art. 12, § 4º, I"], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 4.51 | prefill 17.77 | thinking n/d | gerador 51.34 | total 57.19

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas a brasileiros naturalizados; não há base para generalizar para brasileiros natos. O art. 12, § 4º, I, da Constituição prevê que o brasileiro naturalizado pode perder a nacionalidade brasileira se tiver cancelada sua naturalização, por sentença judicial, em virtude de atividade nociva ao interesse nacional. Não há menção a brasileiros natos nesse dispositivo.

### 09 — COMPOSTA / MULTI-HOP

Pergunta: Um servidor público efetivo pode acumular dois cargos de professor na rede pública, e qual é o limite máximo que ele pode receber de remuneração?

Esperado: Art. 37, XVI, a e Art. 37, XI.

- Intenção: Tributação e Orçamento (margem 0.0036294082907716296)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 1 | tradutor: None | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 37, XVI [reranker]
- Checklist humano: Art. 37, XVI, a e Art. 37, XI.
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 37"], "subdispositivos_citados": ["Art. 37, XVI, \"a\""], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 17.87 | prefill 20.99 | thinking n/d | gerador 76.91 | total 95.95

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas a servidores públicos que acumulam cargos de professor na rede pública; não há base para generalizar para outros tipos de cargos. De acordo com o art. 37, XVI, a) é permitida a acumulação remunerada de dois cargos de professor, desde que haja compatibilidade de horários. Não há menção explícita ao limite máximo de remuneração, mas o inciso XI do mesmo artigo estabelece que, em qualquer caso, deve-se observar o disposto no inciso XI, o que pode implicar limites previstos em normas complementares ou em leis específicas que regulamentam a remuneração dos servidores públicos.

### 10 — COMPOSTA / MULTI-HOP

Pergunta: O Presidente da República pode editar medida provisória sobre direito penal, e qual é o prazo máximo de vigência de uma medida provisória antes de perder a eficácia?

Esperado: Art. 62, § 1º, I, b e Art. 62, § 3º.

- Intenção: Organização dos Poderes (margem 0.1468399415376374)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 1 | tradutor: None | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 62, § 3º (2 filhos); Art. 62, § 11º (2 filhos); Art. 62, § 7º (2 filhos)
- Checklist humano: Art. 62, § 1º, I, b e Art. 62, § 3º.
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 62"], "subdispositivos_citados": ["Art. 62, § 3º, § 11º", "Art. 62, § 7º"], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 11.57 | prefill 106.84 | thinking n/d | gerador 201.19 | total 213.54

Resposta integral:

O Presidente da República pode editar medida provisória sobre direito penal, desde que haja relevância e urgência, conforme previsto no art. 62, § 3º, que estabelece que as medidas provisórias, ressalvado o disposto nos §§ 11 e 12, perderão eficácia desde a edição, se não forem convertidas em lei no prazo de sessenta dias, prorrogável, nos termos do § 7º, uma vez por igual período. O prazo máximo de vigência de uma medida provisória antes de perder a eficácia é de sessenta dias, podendo ser prorrogado uma única vez por igual período, conforme previsto no art. 62, § 7º. Nas fontes recuperadas, a regra aplica-se apenas a medidas provisórias editadas em caso de relevância e urgência; não há base para generalizar para outros casos.

### 11 — ORDEM SOCIAL / LEIGO

Pergunta: Um hospital particular pode cobrar pelo atendimento, ou a saúde no Brasil é proibida para empresas privadas?

Esperado: Art. 199: livre à iniciativa privada; § 2º veda recursos públicos a entidades com fins lucrativos.

- Intenção: Ordem Social (margem 0.0703199784223576)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 1 | tradutor: None | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 199 (1 filhos)
- Checklist humano: Art. 199: livre à iniciativa privada; § 2º veda recursos públicos a entidades com fins lucrativos.
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 199"], "subdispositivos_citados": ["Art. 199, § 1º", "Art. 199, § 2º", "Art. 199, § 3º"], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 16.72 | prefill 30.01 | thinking n/d | gerador 90.57 | total 108.40

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas à assistência à saúde, não há base para generalizar para outros setores. Um hospital particular pode cobrar pelo atendimento, pois a assistência à saúde é livre à iniciativa privada. Art. 199, § 1º. A saúde no Brasil não é proibida para empresas privadas, mas é vedada a destinação de recursos públicos para auxílios ou subvenções às instituições privadas com fins lucrativos. Art. 199, § 2º. Além disso, é vedada a participação direta ou indireta de empresas ou capitais estrangeiros na assistência à saúde no País, salvo nos casos previstos em lei. Art. 199, § 3º.

### 12 — TRABALHO / LEIGO

Pergunta: O patrão pode obrigar alguém a trabalhar 10 horas por dia todos os dias sem pagar nada a mais?

Esperado: Art. 7º, XIII e XVI: 8 horas, 44 semanais e hora extra de pelo menos 50%.

- Intenção: Ordem Social (margem 0.011335789128238516)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 1 | tradutor: None | sub-consultas: []
- Modo final: MODO_CONVERSA_LIVRE
- Entregue ao LLM: (nenhum)
- Checklist humano: Art. 7º, XIII e XVI: 8 horas, 44 semanais e hora extra de pelo menos 50%.
- Auditoria: {"status": "ALUCINACAO_ARTIGO", "artigos_citados": ["Art. 70", "Art. 71"], "subdispositivos_citados": [], "artigos_inventados": ["Art. 70", "Art. 71"], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 4.21 | prefill 12.12 | thinking n/d | gerador 78.55 | total 96.30

Resposta integral:

Não, o patrão **não pode obrigar alguém a trabalhar 10 horas por dia sem pagar nada a mais**, e isso viola tanto a **Lei do Trabalho (CLT)** quanto a **Constituição Federal de 1988**.

### De acordo com a **CLT**:
- O **horário de trabalho** em regime normal é de **oito horas por dia**, com **uma pausa para alimentação de uma hora** (art. 70 da CLT).
- A **jornada de trabalho** não pode ultrapassar **oito horas diárias** ou **quatro quartos de hora por dia** (art. 70 da CLT).
- **Horas extras** são aquelas que ultrapassam o horário normal e **devem ser remuneradas** com **50% a mais do valor da hora normal** (art. 71 da CLT).

### Da Constituição Federal:
- A **Constituição de 1988

### 13 — FORA DE ESCOPO / CDC

Pergunta: Comprei um celular na internet faz 3 dias e me arrependi, a loja é obrigada a devolver meu dinheiro?

Esperado: Conversa livre ou zona cinzenta, Código de Defesa do Consumidor, sem artigo inventado da CF/88.

- Intenção: Direitos e Garantias Fundamentais (margem 0.07763119785845599)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 1 | tradutor: None | sub-consultas: []
- Modo final: MODO_CONVERSA_LIVRE
- Entregue ao LLM: (nenhum)
- Checklist humano: Conversa livre ou zona cinzenta, Código de Defesa do Consumidor, sem artigo inventado da CF/88.
- Auditoria: {"status": "SEM_CITACAO", "artigos_citados": [], "subdispositivos_citados": [], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 4.45 | prefill 3.53 | thinking n/d | gerador 70.33 | total 80.23

Resposta integral:

Se você comprou um celular na internet e se arrependeu, a loja **não é obrigada a devolver o dinheiro automaticamente**, mas pode haver possibilidades de resolver a situação, dependendo do que você fez e da legislação aplicável.

Vamos analisar com base na **Constituição Federal de 1988** e outras leis relevantes:

### 1. **Direito de arrependimento (retracto)**
A **Lei nº 13.307/2016** (Lei do Consumidor) estabelece que o consumidor tem o direito de **arrependimento** (retracto) em compras feitas **via internet ou telefone**, **dentro de 7 dias corridos**, contados a partir da data de recebimento do produto.

Se você se arrependeu **dentro desse prazo**, **você pode pedir a devolução do dinheiro**, desde que o produto não ten

### 14 — FORA DE ESCOPO / TRANSITO

Pergunta: Se eu bater no carro de alguém no trânsito sem querer, qual é o valor da multa que eu levo?

Esperado: Conversa livre, CTB ou Código Civil, sem artigo inventado da CF/88.

- Intenção: Tributação e Orçamento (margem 0.05187448780927245)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 1 | tradutor: None | sub-consultas: []
- Modo final: MODO_CONVERSA_LIVRE
- Entregue ao LLM: (nenhum)
- Checklist humano: Conversa livre, CTB ou Código Civil, sem artigo inventado da CF/88.
- Auditoria: {"status": "ALUCINACAO_ARTIGO", "artigos_citados": ["Art. 302"], "subdispositivos_citados": [], "artigos_inventados": ["Art. 302"], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 13.01 | prefill 3.42 | thinking n/d | gerador 70.73 | total 89.46

Resposta integral:

A multa por acidente de trânsito, como o que você descreve — bater no carro de alguém sem querer —, **não é definida em valores fixos na Constituição de 1988**, pois esse tipo de infração é regulado por leis específicas, como a **Lei de Trânsito (Lei nº 9.503/97)** e o **Código de Trânsito Brasileiro (CTB)**.

Essa situação pode envolver tanto uma **multa administrativa** quanto uma **responsabilidade civil**, dependendo do dano causado. Se houver danos materiais, você pode ser responsabilizado civilmente, e o proprietário do carro pode solicitar indenização.

Além disso, se o acidente resultar em **ferimentos ou morte**, pode haver envolvimento com o **Código Penal**, como o artigo 302 (dano culposo), que prevê penas de pris

### 15 — ATALHO SOCIAL

Pergunta: Boa tarde, tudo bem?

Esperado: MODO_ATALHO_SOCIAL em menos de 0,1 s, sem BGE-M3 e sem Ollama.

- Intenção: None (margem None)
- modo_busca: atalho_social
- classe: SIMPLES
- passagem: 0 | tradutor: None | sub-consultas: []
- Modo final: MODO_ATALHO_SOCIAL
- Entregue ao LLM: (nenhum)
- Checklist humano: MODO_ATALHO_SOCIAL em menos de 0,1 s, sem BGE-M3 e sem Ollama.
- Auditoria: {"status": "SEM_CITACAO", "artigos_citados": [], "subdispositivos_citados": [], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 0.00 | prefill 0.00 | thinking 0.00 | gerador 0.00 | total 0.00

Resposta integral:

Olá. Posso ajudar com dúvidas sobre a Constituição de 1988.

### 16 — REGRESSAO / ESCOPO - MINERACAO

Pergunta: A União detém o monopólio de toda a atividade de mineração no Brasil?

Esperado: Não começar com Sim. Restringir a minérios nucleares (Art. 177, V ou § 4º) e ao regime de autorização ou concessão (Art. 176). Sem generalizar.

- Intenção: Ordem Econômica e Financeira (margem 0.2701002354528488)
- modo_busca: densa_com_boost
- classe: SIMPLES
- passagem: 1 | tradutor: None | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 177, § 2º (2 filhos); Art. 177, V [reranker]; Art. 177, II [irmao_adjacente]; Art. 177, III [irmao_adjacente]; Art. 177, IV [irmao_adjacente]; Art. 21, XXIII [reranker]
- Checklist humano: Não começar com Sim. Restringir a minérios nucleares (Art. 177, V ou § 4º) e ao regime de autorização ou concessão (Art. 176). Sem generalizar.
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 177", "Art. 21"], "subdispositivos_citados": [], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 3.26 | prefill 76.34 | thinking n/d | gerador 145.11 | total 149.28

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas aos minérios e minerais nucleares, não há base para generalizar para toda a atividade de mineração no Brasil. A Constituição de 1988 estabelece que a União detém o monopólio sobre a pesquisa, a lavra, o enriquecimento, o reprocessamento, a industrialização e o comércio de minérios e minerais nucleares, conforme o inciso V do art. 177, com exceção dos radioisótopos, cuja produção, comercialização e utilização são autorizadas sob regime de permissão, conforme as alíneas b e c do inciso XXIII do art. 21. Portanto, a União não detém monopólio sobre toda a atividade de mineração, mas apenas sobre os minérios e minerais nucleares.

### 17 — REGRESSAO / LIMITE NUMERICO - USUCAPIAO

Pergunta: Quem ocupa e trabalha numa terra rural de 40 hectares por 5 anos sem ser dono de outro imóvel pode adquirir a propriedade por usucapião?

Esperado: Art. 191: até 50 hectares, cinco anos, trabalho da família, moradia, sem outro imóvel. Não misturar o Art. 186.

- Intenção: Ordem Econômica e Financeira (margem 0.08990046248446809)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 1 | tradutor: None | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 191 (1 filhos); Art. 183 (1 filhos)
- Checklist humano: Art. 191: até 50 hectares, cinco anos, trabalho da família, moradia, sem outro imóvel. Não misturar o Art. 186.
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 191"], "subdispositivos_citados": ["Art. 191, parágrafo único"], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 13.40 | prefill 35.55 | thinking n/d | gerador 96.07 | total 109.94

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas a área de terra, em zona rural, não superior a cinqüenta hectares, tornando-a produtiva por seu trabalho ou de sua família, tendo nela sua moradia, e não sendo proprietário de imóvel rural ou urbano (Art. 191, parágrafo único). Não há base para generalizar para áreas maiores ou para possuidores que já sejam proprietários de outro imóvel. Portanto, quem ocupa e trabalha numa terra rural de 40 hectares por 5 anos sem ser dono de outro imóvel pode adquirir a propriedade por usucapião, desde que cumpra os requisitos previstos no Art. 191.

