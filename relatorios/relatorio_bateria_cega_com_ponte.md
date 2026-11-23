# Bateria cega da Fase 3.3 — com_ponte

## Resumo executivo

Perfil com_ponte. Este relatório audita 15 perguntas inéditas e 2 regressões históricas. O histórico de cada chamada fica vazio. As três colunas do placar são independentes.

| Métrica | Resultado |
| --- | --- |
| Recuperação na 1ª passagem (12 inéditas) | 10/12 |
| Artigo esperado recuperado (12 inéditas) | 8/12 |
| Auditoria FIEL (12 inéditas) | 8/12 |
| Recuperação na 1ª passagem (2 regressões) | 2/2 |
| Auditoria FIEL (2 regressões) | 1/2 |
| Fora de escopo sem artigo inventado | 0/2 |
| Atalho social abaixo de 0,1 s | 1/1 |
| Retriever médio (s) | 15.43 |
| Prefill médio (s) | 40.47 |
| Pensamento médio (s) | 0.00 |
| Gerador médio (s) | 124.98 |
| Total médio (s) | 148.38 |

## Placar

| Caso | 1. Artigo na 1ª passagem | 2. Auditor FIEL | 3. Checklist de revisão humana |
| --- | --- | --- | --- |
| 01 LEIGO / EXCECAO | sim | sim | Art. 5º, XI: ordem judicial só de dia; à noite, flagrante, desastre ou socorro. |
| 02 LEIGO / EXCECAO | não | SEM_CITACAO | Art. 5º, LXVII: vedada a prisão civil por dívida, com as ressalvas do próprio inciso. |
| 03 TRIBUTACAO / LEIGO | não | sim | Art. 150, VI, b: imunidade dos templos. Classe Tributação e Orçamento. |
| 04 TRIBUTACAO / PRAZO | não | ALUCINACAO_ARTIGO | Art. 150, III, b e c: anterioridade anual e nonagesimal, com exceções. |
| 05 TRIBUTACAO / COMPETENCIA | não | sim | Art. 155, I: Estados e Distrito Federal. |
| 06 ADCT / LEIGO | sim | sim | ADCT, Art. 10, II, b: da confirmação da gravidez até cinco meses após o parto. |
| 07 PARENT-DOC / NUMERO | sim | sim | Art. 14, § 3º, VI, a: 35 anos. |
| 08 PARENT-DOC / INCISOS | sim | SEM_CITACAO | Art. 12, § 4º, fiel ao texto vigente recuperado, sem inciso inventado. |
| 09 COMPOSTA / MULTI-HOP | sim | sim | Art. 37, XVI, a e Art. 37, XI. |
| 10 COMPOSTA / MULTI-HOP | sim | sim | Art. 62, § 1º, I, b e Art. 62, § 3º. |
| 11 ORDEM SOCIAL / LEIGO | sim | sim | Art. 199: livre à iniciativa privada; § 2º veda recursos públicos a entidades com fins lucrativos. |
| 12 TRABALHO / LEIGO | não | ALUCINACAO_ARTIGO | Art. 7º, XIII e XVI: 8 horas, 44 semanais e hora extra de pelo menos 50%. |
| 13 FORA DE ESCOPO / CDC | não se aplica | ALUCINACAO_ARTIGO | Conversa livre ou zona cinzenta, Código de Defesa do Consumidor, sem artigo inventado da CF/88. |
| 14 FORA DE ESCOPO / TRANSITO | não se aplica | ALUCINACAO_ARTIGO | Conversa livre, CTB ou Código Civil, sem artigo inventado da CF/88. |
| 15 ATALHO SOCIAL | não se aplica | SEM_CITACAO | MODO_ATALHO_SOCIAL em menos de 0,1 s, sem BGE-M3 e sem Ollama. |
| 16 REGRESSAO / ESCOPO - MINERACAO | sim | sim | Não começar com Sim. Restringir a minérios nucleares (Art. 177, V ou § 4º) e ao regime de autorização ou concessão (Art. 176). Sem generalizar. |
| 17 REGRESSAO / LIMITE NUMERICO - USUCAPIAO | sim | ALERTA_SUBDISPOSITIVO | Art. 191: até 50 hectares, cinco anos, trabalho da família, moradia, sem outro imóvel. Não misturar o Art. 186. |

## Resposta integral e checklist

### 01 — LEIGO / EXCECAO

Pergunta: A polícia pode arrombar a porta da minha casa à noite só com ordem do juiz?

Esperado: Art. 5º, XI: ordem judicial só de dia; à noite, flagrante, desastre ou socorro.

- Intenção: Direitos e Garantias Fundamentais (margem 0.17552641440349417)
- modo_busca: densa_com_boost
- classe: SIMPLES
- passagem: 1 | tradutor: None | sub-consultas: []
- Modo final: MODO_RAG_ZONA_CINZENTA
- Entregue ao LLM: Art. 5º, XI [reranker]; Art. 5º, LXI [reranker]; Art. 5º, LXII [reranker]
- Checklist humano: Art. 5º, XI: ordem judicial só de dia; à noite, flagrante, desastre ou socorro.
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 5"], "subdispositivos_citados": ["Art. 5, XI"], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 23.94 | prefill 82.02 | thinking n/d | gerador 406.01 | total 468.17

Resposta integral:

A polícia **não pode arrombar a porta da sua casa à noite apenas com ordem do juiz**, conforme previsto no **Art. 5º, XI** da Constituição de 1988. O texto estabelece que a casa é asilo inviolável, e a entrada é permitida **"salvo em caso de flagrante delito ou desastre, ou para prestar socorro, ou, durante o dia, por determinação judicial"**. 

Isso significa que:  
1. **À noite**, a autoridade policial **não pode agir apenas com ordem judicial** (como em casos de flagrante delito ou desastre), pois a entrada exigiria **justificativa imediata** (como a comprovação de um crime em execução ou emergência).  
2. **Durante o dia**, a entrada em casa é permitida **apenas com ordem judicial**, mas essa regra **não se aplica à noite**.  

Portanto, a ação da polícia à noite **precisaria de uma justificativa específica**, como a comprovação de um crime em flagrante, e não apenas uma ordem judicial. A Constituição protege a inviolabilidade do domicílio, limitando a intervenção estatal a situações excepcionais e com base em fundamentos claros.

### 02 — LEIGO / EXCECAO

Pergunta: Se eu dever um empréstimo no banco e não pagar, posso ir preso?

Esperado: Art. 5º, LXVII: vedada a prisão civil por dívida, com as ressalvas do próprio inciso.

- Intenção: Direitos e Garantias Fundamentais (margem 0.14846565362037512)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 1 | tradutor: None | sub-consultas: []
- Modo final: MODO_CONVERSA_LIVRE
- Entregue ao LLM: (nenhum)
- Checklist humano: Art. 5º, LXVII: vedada a prisão civil por dívida, com as ressalvas do próprio inciso.
- Auditoria: {"status": "SEM_CITACAO", "artigos_citados": [], "subdispositivos_citados": [], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 13.60 | prefill 11.34 | thinking n/d | gerador 77.92 | total 98.81

Resposta integral:

A Constituição da República Federativa do Brasil, promulgada em 1988, não prevê a prisão por dívida civil, como empréstimo comum a um banco. A Constituição estabelece que a prisão é um recurso judicial que só pode ser aplicado em casos específicos, como crimes penais, e com observância de direitos fundamentais, como o devido processo legal e o da não bis in idem (não se pode ser julgado duas vezes por um mesmo crime).

No caso de não pagamento de um empréstimo, isso configura uma **dívida civil**, que é regulada por leis como o **Código Civil** e o **Código de Defesa do Consumidor**. O banco pode buscar a execução judicial da dívida, mas isso não resulta em prisão. Em alguns casos, pode haver a **penhora de bens** ou a **proibição de sair do país**, mas a prisão não é uma medida prev

### 03 — TRIBUTACAO / LEIGO

Pergunta: A prefeitura pode cobrar IPTU de uma igreja do meu bairro?

Esperado: Art. 150, VI, b: imunidade dos templos. Classe Tributação e Orçamento.

- Intenção: Tributação e Orçamento (margem 0.13231282637331582)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 2 | tradutor: competência municipal IPTU bens imóveis religiosos | sub-consultas: []
- Modo final: MODO_RAG_ZONA_CINZENTA
- Entregue ao LLM: Art. 155, § 1º [reranker]; Art. 156, § 2º [reranker]; Art. 156, II [reranker]
- Checklist humano: Art. 150, VI, b: imunidade dos templos. Classe Tributação e Orçamento.
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 156"], "subdispositivos_citados": ["Art. 156, II", "Art. 156, § 2º"], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 15.69 | prefill 49.77 | thinking n/d | gerador 340.88 | total 363.63

Resposta integral:

A prefeitura pode cobrar IPTU de uma igreja, desde que a propriedade da igreja esteja localizada em área urbana e seja considerada bens imóveis. O art. 156, II da Constituição de 1988 estabelece que o IPTU incide sobre a transmissão inter vivos de bens imóveis, incluindo direitos reais sobre imóveis, exceto os de garantia. Além disso, o art. 156, § 2º afirma que o imposto não se aplica a transmissões decorrentes de fusão, incorporação ou cisão de pessoas jurídicas, mas isso não se aplica a bens de instituições religiosas. Portanto, a prefeitura tem competência para cobrar o IPTU, salvo se houver lei específica que isene a igreja, o que não está mencionado nos trechos fornecidos.

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
- Auditoria: {"status": "ALUCINACAO_ARTIGO", "artigos_citados": ["Art. 150"], "subdispositivos_citados": ["Art. 150, I", "Art. 150, II"], "artigos_inventados": ["Art. 150"], "subdispositivos_nao_confirmados": ["Art. 150, I", "Art. 150, II"]}
- Tempos (s): retriever 20.68 | prefill 2.73 | thinking n/d | gerador 73.78 | total 103.37

Resposta integral:

A Constituição Federal de 1988 estabelece limites claros sobre a criação e a cobrança de impostos. De acordo com o artigo 150, inciso I, da Constituição, **os impostos só podem ser criados por lei complementar**, e **não podem ser instituídos por meio de lei ordinária**. Isso significa que o governo não pode simplesmente criar um novo imposto e começar a cobrá-lo na semana seguinte, pois isso violaria o princípio da legalidade tributária.

Além disso, o artigo 150, inciso II, determina que **os impostos só podem ser criados com base em lei complementar**, que é um tipo de lei mais restritiva e que exige maior formalidade e deliberação. A lei complementar é a única que pode estabelecer novos impostos, taxas, contribuições e outros tributos.

Portanto, **não é possível que o governo crie

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
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 156"], "subdispositivos_citados": ["Art. 156, I, II", "Art. 156, II"], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 28.09 | prefill 133.97 | thinking n/d | gerador 185.01 | total 227.28

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas aos impostos instituídos pelos Municípios, conforme Art. 156, I, II e III, e não há base para generalizar para outros níveis de governo. O imposto sobre a transmissão inter vivos de bens imóveis, como a doação em vida, é de competência dos Municípios, conforme Art. 156, II, e, portanto, a Prefeitura é a autoridade responsável pela cobrança. A União e o Estado não têm competência para instituir tal imposto.

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
- Tempos (s): retriever 7.63 | prefill 58.25 | thinking n/d | gerador 89.27 | total 97.47

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
- Tempos (s): retriever 22.56 | prefill 75.89 | thinking n/d | gerador 138.21 | total 162.29

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas a condições de elegibilidade para cargos eletivos, e não há base para generalizar para outros cargos. Para se candidatar a senador, a pessoa deve ter, no mínimo, trinta e cinco anos, conforme previsto no art. 14, § 3º, VI, alínea a, da Constituição. Para se candidatar a presidente da República, também é necessário ter, no mínimo, trinta e cinco anos, conforme previsto no mesmo dispositivo.

### 08 — PARENT-DOC / INCISOS

Pergunta: Em quais situações um brasileiro nato pode acabar perdendo a nacionalidade brasileira?

Esperado: Art. 12, § 4º, fiel ao texto vigente recuperado, sem inciso inventado.

- Intenção: Direitos e Garantias Fundamentais (margem 0.020589243677111596)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 1 | tradutor: None | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 12, § 4º (2 filhos); Art. 12, I [reranker]
- Checklist humano: Art. 12, § 4º, fiel ao texto vigente recuperado, sem inciso inventado.
- Auditoria: {"status": "SEM_CITACAO", "artigos_citados": [], "subdispositivos_citados": [], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 10.62 | prefill 34.57 | thinking n/d | gerador 69.61 | total 82.36

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas aos brasileiros natos que adquiram outra nacionalidade, salvo nos casos de reconhecimento de nacionalidade originária pela lei estrangeira ou de imposição de naturalização, pela norma estrangeira, ao brasileiro residente em Estado estrangeiro, como condição para permanência em seu território ou para o exercício de direitos civis. Não há base para generalizar para outros casos.

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
- Tempos (s): retriever 11.34 | prefill 20.28 | thinking n/d | gerador 61.58 | total 73.53

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas a servidores públicos que acumulam cargos de professor na rede pública; não há base para generalizar para outros tipos de cargos. De acordo com o art. 37, XVI, a) é permitida a acumulação remunerada de dois cargos de professor, desde que haja compatibilidade de horários. Não há menção expressa ao limite máximo de remuneração, ou seja, não há previsão legal sobre o valor máximo que o servidor pode receber com essa acumulação.

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
- Tempos (s): retriever 20.34 | prefill 69.39 | thinking n/d | gerador 145.25 | total 167.80

Resposta integral:

O Presidente da República pode editar medida provisória sobre direito penal, desde que haja relevância e urgência, conforme previsto no art. 62, § 3º, que estabelece que as medidas provisórias, ressalvado o disposto nos §§ 11 e 12, perderão eficácia desde a edição, se não forem convertidas em lei no prazo de sessenta dias, prorrogável, nos termos do § 7º, uma vez por igual período. O prazo máximo de vigência de uma medida provisória antes de perder a eficácia é de sessenta dias, podendo ser prorrogado uma única vez por igual período, conforme previsto no art. 62, § 7º. Nas fontes recuperadas, a regra aplica-se apenas a medidas provisórias editadas em casos de relevância e urgência, não há base para generalizar para outros casos.

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
- Tempos (s): retriever 10.02 | prefill 24.50 | thinking n/d | gerador 84.36 | total 96.07

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas à assistência à saúde, não há base para generalizar para outros setores. Um hospital particular pode cobrar pelo atendimento, pois a assistência à saúde é livre à iniciativa privada, conforme previsto no Art. 199, § 1º. Por outro lado, é vedada a destinação de recursos públicos para auxílios ou subvenções às instituições privadas com fins lucrativos, conforme previsto no Art. 199, § 2º. Além disso, é vedada a participação direta ou indireta de empresas ou capitais estrangeiros na assistência à saúde no País, salvo nos casos previstos em lei, conforme previsto no Art. 199, § 3º.

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
- Auditoria: {"status": "ALUCINACAO_ARTIGO", "artigos_citados": ["Art. 7"], "subdispositivos_citados": ["Art. 7, II", "Art. 7, XIV"], "artigos_inventados": ["Art. 7"], "subdispositivos_nao_confirmados": ["Art. 7, II", "Art. 7, XIV"]}
- Tempos (s): retriever 8.97 | prefill 12.03 | thinking n/d | gerador 80.44 | total 111.98

Resposta integral:

Não, o patrão **não pode obrigar alguém a trabalhar 10 horas por dia sem pagar nada a mais**, e isso é previsto tanto pela **Constituição Federal de 1988** quanto por outras leis trabalhistas.

Primeiro, vamos ver o que diz a Constituição:

- A **Constituição Federal de 1988**, em seu **Artigo 7º**, garante direitos trabalhistas, incluindo o direito à **remuneração mínima**, à **segurança no trabalho**, e à **limitação do horário de trabalho**.
- O **Artigo 7º, II**, diz que o trabalhador tem direito à **remuneração mínima**, e o **Artigo 7º, XIV**, estabelece que o **horário de trabalho não pode ultrapassar oito horas diárias** e quarenta e quatro horas semanais, **salvo com acordo coletivo** que possa aumentar esse limite,

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
- Auditoria: {"status": "ALUCINACAO_ARTIGO", "artigos_citados": ["Art. 49"], "subdispositivos_citados": ["Art. 49, § 2º"], "artigos_inventados": ["Art. 49"], "subdispositivos_nao_confirmados": ["Art. 49, § 2º"]}
- Tempos (s): retriever 34.24 | prefill 3.51 | thinking n/d | gerador 74.14 | total 125.09

Resposta integral:

Se você comprou um celular na internet e se arrependeu, a loja **não está obrigada a devolver o dinheiro automaticamente**, mas há algumas possibilidades que você pode explorar, dependendo do tempo em que passou desde a compra e das condições do contrato.

### 1. **Período de arrependimento (7 dias)**
Se a compra foi feita **via internet** e você se arrependeu **nos 7 dias seguintes**, você tem direito ao **arrependimento** previsto no **Art. 49, § 2º, da Lei nº 8.078/1990 (Código de Defesa do Consumidor)**. Nesse caso, você pode solicitar o **reembolso integral do valor pago**, desde que o produto não tenha sido utilizado ou danificado.

> ⚠️ Importante: esse direito só vale se a compra foi feita **via internet** e **não houve envio de documento

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
- Auditoria: {"status": "ALUCINACAO_ARTIGO", "artigos_citados": ["Art. 5"], "subdispositivos_citados": [], "artigos_inventados": ["Art. 5"], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 10.73 | prefill 3.41 | thinking n/d | gerador 74.46 | total 94.73

Resposta integral:

A multa por bater no carro de alguém no trânsito depende de vários fatores, como o dano causado, a responsabilidade legal e a legislação específica do Estado onde o acidente ocorreu. A Constituição Federal de 1988 não estabelece valores de multas, pois essa é uma questão regulada por leis infraconstitucionais, como o Código de Trânsito Brasileiro (CTB) e as leis estaduais.

No entanto, a Constituição garante alguns direitos e princípios que podem influenciar o tratamento legal do caso, como o direito à vida, à integridade física e à propriedade (artigos 5º, 196 e 197). Além disso, o Código Penal pode ser aplicado em casos de dolo (intenção de danificar) ou culposo (erro ou imprudência), o que pode levar a responsabilização penal ou civil.

Se o acidente

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
- Tempos (s): retriever 0.00 | prefill 0.00 | thinking 0.00 | gerador 0.00 | total 0.01

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
- Tempos (s): retriever 15.95 | prefill 74.88 | thinking n/d | gerador 143.13 | total 160.14

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas aos minérios e minerais nucleares, não há base para generalizar para toda a atividade de mineração no Brasil. A Constituição de 1988 estabelece que a União detém o monopólio sobre a pesquisa, a lavra, o enriquecimento, o reprocessamento, a industrialização e o comércio de minérios e minerais nucleares, conforme o inciso V do art. 177, com exceção dos radioisótopos, cuja produção, comercialização e utilização poderão ser autorizadas sob regime de permissão, conforme as alíneas b e c do inciso XXIII do art. 21. Portanto, a União não detém monopólio sobre toda a atividade de mineração, apenas sobre os minérios e minerais nucleares.

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
- Auditoria: {"status": "ALERTA_SUBDISPOSITIVO", "artigos_citados": ["Art. 191"], "subdispositivos_citados": ["Art. 191, § 1º"], "artigos_inventados": [], "subdispositivos_nao_confirmados": ["Art. 191, § 1º"]}
- Tempos (s): retriever 8.00 | prefill 31.47 | thinking n/d | gerador 80.61 | total 89.74

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas a área de terra, em zona rural, não superior a cinqüenta hectares, tornando-a produtiva por seu trabalho ou de sua família, tendo nela sua moradia, e que o possuidor não seja proprietário de imóvel rural ou urbano. Assim, quem ocupa e trabalha numa terra rural de 40 hectares por 5 anos sem ser dono de outro imóvel pode adquirir a propriedade por usucapião, conforme o disposto no art. 191, § 1º, da Constituição. Não há base para generalizar para áreas maiores ou para situações em que o possuidor já possua outro imóvel.

