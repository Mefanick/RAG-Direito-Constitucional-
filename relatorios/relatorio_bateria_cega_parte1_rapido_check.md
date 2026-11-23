# Bateria cega da Fase 3.3 — parte1_rapido_check

## Resumo executivo

Perfil parte1_rapido_check. Este relatório audita 15 perguntas inéditas e 2 regressões históricas. O histórico de cada chamada fica vazio. As três colunas do placar são independentes.

| Métrica | Resultado |
| --- | --- |
| Recuperação na 1ª passagem (12 inéditas) | 2/12 |
| Artigo esperado recuperado (12 inéditas) | 3/12 |
| Auditoria FIEL (12 inéditas) | 2/12 |
| Recuperação na 1ª passagem (2 regressões) | 0/2 |
| Auditoria FIEL (2 regressões) | 0/2 |
| Fora de escopo sem artigo inventado | 0/2 |
| Atalho social abaixo de 0,1 s | 0/1 |
| Retriever médio (s) | 71.32 |
| Prefill médio (s) | 152.41 |
| Pensamento médio (s) | 0.00 |
| Gerador médio (s) | 253.43 |
| Total médio (s) | 359.94 |

## Placar

| Caso | 1. Artigo na 1ª passagem | 2. Auditor FIEL | 3. Checklist de revisão humana |
| --- | --- | --- | --- |
| 01 LEIGO / EXCECAO | sim | sim | Art. 5º, XI: ordem judicial só de dia; à noite, flagrante, desastre ou socorro. |
| 02 LEIGO / EXCECAO | não | pendente | Art. 5º, LXVII: vedada a prisão civil por dívida, com as ressalvas do próprio inciso. |
| 03 TRIBUTACAO / LEIGO | não | pendente | Art. 150, VI, b: imunidade dos templos. Classe Tributação e Orçamento. |
| 04 TRIBUTACAO / PRAZO | não | pendente | Art. 150, III, b e c: anterioridade anual e nonagesimal, com exceções. |
| 05 TRIBUTACAO / COMPETENCIA | não | pendente | Art. 155, I: Estados e Distrito Federal. |
| 06 ADCT / LEIGO | não | pendente | ADCT, Art. 10, II, b: da confirmação da gravidez até cinco meses após o parto. |
| 07 PARENT-DOC / NUMERO | não | pendente | Art. 14, § 3º, VI, a: 35 anos. |
| 08 PARENT-DOC / INCISOS | não | pendente | Art. 12, § 4º, fiel ao texto vigente recuperado, sem inciso inventado. |
| 09 COMPOSTA / MULTI-HOP | sim | ALERTA_SUBDISPOSITIVO | Art. 37, XVI, a e Art. 37, XI. |
| 10 COMPOSTA / MULTI-HOP | sim | sim | Art. 62, § 1º, I, b e Art. 62, § 3º. |
| 11 ORDEM SOCIAL / LEIGO | não | pendente | Art. 199: livre à iniciativa privada; § 2º veda recursos públicos a entidades com fins lucrativos. |
| 12 TRABALHO / LEIGO | não | pendente | Art. 7º, XIII e XVI: 8 horas, 44 semanais e hora extra de pelo menos 50%. |
| 13 FORA DE ESCOPO / CDC | não se aplica | pendente | Conversa livre ou zona cinzenta, Código de Defesa do Consumidor, sem artigo inventado da CF/88. |
| 14 FORA DE ESCOPO / TRANSITO | não se aplica | pendente | Conversa livre, CTB ou Código Civil, sem artigo inventado da CF/88. |
| 15 ATALHO SOCIAL | não se aplica | pendente | MODO_ATALHO_SOCIAL em menos de 0,1 s, sem BGE-M3 e sem Ollama. |
| 16 REGRESSAO / ESCOPO - MINERACAO | não | pendente | Não começar com Sim. Restringir a minérios nucleares (Art. 177, V ou § 4º) e ao regime de autorização ou concessão (Art. 176). Sem generalizar. |
| 17 REGRESSAO / LIMITE NUMERICO - USUCAPIAO | não | pendente | Art. 191: até 50 hectares, cinco anos, trabalho da família, moradia, sem outro imóvel. Não misturar o Art. 186. |

## Resposta integral e checklist

### 01 — LEIGO / EXCECAO

Pergunta: A polícia pode arrombar a porta da minha casa à noite só com ordem do juiz?

Esperado: Art. 5º, XI: ordem judicial só de dia; à noite, flagrante, desastre ou socorro.

- Intenção: Direitos e Garantias Fundamentais (margem 0.17552641440349417)
- modo_busca: densa_com_boost
- classe: SIMPLES
- passagem: 1 | tradutor: é vedado à autoridade policial realizar entrada em domicílio sem prévia comunicação ao interessado ou autorização judicial específica | sub-consultas: []
- Modo final: MODO_RAG_ZONA_CINZENTA
- Entregue ao LLM: Art. 5º, XI [reranker]; Art. 5º, LXI [reranker]; Art. 136, § 3º [reranker]
- Checklist humano: Art. 5º, XI: ordem judicial só de dia; à noite, flagrante, desastre ou socorro.
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 5"], "subdispositivos_citados": ["Art. 5, XI"], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 34.25 | prefill 95.24 | thinking 0.00 | gerador 163.65 | total 294.56

Resposta integral:

A polícia não pode arrombar a porta da sua casa à noite só com ordem do juiz. O art. 5º, XI da Constituição estabelece que a casa é asilo inviolável do indivíduo, e ninguém nela pode penetrar sem consentimento do morador, salvo em caso de flagrante delito ou desastre, ou para prestar socorro, ou, durante o dia, por determinação judicial. Portanto, a entrada na casa à noite, mesmo com ordem judicial, não é permitida, a menos que haja flagrante delito ou outro motivo previsto na Constituição.

### 02 — LEIGO / EXCECAO

Pergunta: Se eu dever um empréstimo no banco e não pagar, posso ir preso?

Esperado: Art. 5º, LXVII: vedada a prisão civil por dívida, com as ressalvas do próprio inciso.

- Intenção: None (margem None)
- modo_busca: None
- classe: None
- passagem: None | tradutor: None | sub-consultas: None
- Modo final: None
- Entregue ao LLM: (nenhum)
- Checklist humano: Art. 5º, LXVII: vedada a prisão civil por dívida, com as ressalvas do próprio inciso.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 0.00 | prefill n/d | thinking n/d | gerador 0.00 | total 0.00

Resposta integral:

(sem resposta)

### 03 — TRIBUTACAO / LEIGO

Pergunta: A prefeitura pode cobrar IPTU de uma igreja do meu bairro?

Esperado: Art. 150, VI, b: imunidade dos templos. Classe Tributação e Orçamento.

- Intenção: None (margem None)
- modo_busca: None
- classe: None
- passagem: None | tradutor: None | sub-consultas: None
- Modo final: None
- Entregue ao LLM: (nenhum)
- Checklist humano: Art. 150, VI, b: imunidade dos templos. Classe Tributação e Orçamento.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 0.00 | prefill n/d | thinking n/d | gerador 0.00 | total 0.00

Resposta integral:

(sem resposta)

### 04 — TRIBUTACAO / PRAZO

Pergunta: O governo pode criar um imposto hoje e começar a cobrar na semana que vem?

Esperado: Art. 150, III, b e c: anterioridade anual e nonagesimal, com exceções.

- Intenção: None (margem None)
- modo_busca: None
- classe: None
- passagem: None | tradutor: None | sub-consultas: None
- Modo final: None
- Entregue ao LLM: (nenhum)
- Checklist humano: Art. 150, III, b e c: anterioridade anual e nonagesimal, com exceções.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 0.00 | prefill n/d | thinking n/d | gerador 0.00 | total 0.00

Resposta integral:

(sem resposta)

### 05 — TRIBUTACAO / COMPETENCIA

Pergunta: Se eu receber um terreno de doação em vida, quem cobra o imposto sobre essa doação: a Prefeitura, o Estado ou a União?

Esperado: Art. 155, I: Estados e Distrito Federal.

- Intenção: None (margem None)
- modo_busca: None
- classe: None
- passagem: None | tradutor: None | sub-consultas: None
- Modo final: None
- Entregue ao LLM: (nenhum)
- Checklist humano: Art. 155, I: Estados e Distrito Federal.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 0.00 | prefill n/d | thinking n/d | gerador 0.00 | total 0.00

Resposta integral:

(sem resposta)

### 06 — ADCT / LEIGO

Pergunta: Uma funcionária grávida pode ser demitida sem justa causa logo depois de ter o bebê?

Esperado: ADCT, Art. 10, II, b: da confirmação da gravidez até cinco meses após o parto.

- Intenção: None (margem None)
- modo_busca: None
- classe: None
- passagem: None | tradutor: None | sub-consultas: None
- Modo final: None
- Entregue ao LLM: (nenhum)
- Checklist humano: ADCT, Art. 10, II, b: da confirmação da gravidez até cinco meses após o parto.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 0.00 | prefill n/d | thinking n/d | gerador 0.00 | total 0.00

Resposta integral:

(sem resposta)

### 07 — PARENT-DOC / NUMERO

Pergunta: Com quantos anos uma pessoa pode se candidatar a senador ou a presidente da República?

Esperado: Art. 14, § 3º, VI, a: 35 anos.

- Intenção: None (margem None)
- modo_busca: None
- classe: None
- passagem: None | tradutor: None | sub-consultas: None
- Modo final: None
- Entregue ao LLM: (nenhum)
- Checklist humano: Art. 14, § 3º, VI, a: 35 anos.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 0.00 | prefill n/d | thinking n/d | gerador 0.00 | total 0.00

Resposta integral:

(sem resposta)

### 08 — PARENT-DOC / INCISOS

Pergunta: Em quais situações um brasileiro nato pode acabar perdendo a nacionalidade brasileira?

Esperado: Art. 12, § 4º, fiel ao texto vigente recuperado, sem inciso inventado.

- Intenção: None (margem None)
- modo_busca: None
- classe: None
- passagem: None | tradutor: None | sub-consultas: None
- Modo final: None
- Entregue ao LLM: (nenhum)
- Checklist humano: Art. 12, § 4º, fiel ao texto vigente recuperado, sem inciso inventado.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 0.00 | prefill n/d | thinking n/d | gerador 0.00 | total 0.00

Resposta integral:

(sem resposta)

### 09 — COMPOSTA / MULTI-HOP

Pergunta: Um servidor público efetivo pode acumular dois cargos de professor na rede pública, e qual é o limite máximo que ele pode receber de remuneração?

Esperado: Art. 37, XVI, a e Art. 37, XI.

- Intenção: Tributação e Orçamento (margem 0.0036294082907716296)
- modo_busca: multi_query
- classe: COMPOSTA
- passagem: 1 | tradutor: None | sub-consultas: ['Art. 37, X da Constituição Federal estabelece que a remuneração do servidor público não pode ultrapassar o limite máximo estabelecido em lei.', 'Art. 37, II da Constituição Federal determina que o servidor público não pode acumular cargos, empregos ou funções que exijam exercício simultâneo de atividades de natureza diversa.', 'Art. 37, XI da Constituição Federal prevê que a remuneração do servidor público é paga em regime de competência, com base']
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 37, § 10º (2 filhos); Art. 39, § 5º (2 filhos); Art. 37, XI [reranker]; Art. 37, XVI [reranker]; Art. 37, X [reranker]; Art. 37, XVII [reranker]
- Checklist humano: Art. 37, XVI, a e Art. 37, XI.
- Auditoria: {"status": "ALERTA_SUBDISPOSITIVO", "artigos_citados": ["Art. 37"], "subdispositivos_citados": ["Art. 37, IV", "Art. 37, XI"], "artigos_inventados": [], "subdispositivos_nao_confirmados": ["Art. 37, IV"]}
- Tempos (s): retriever 108.31 | prefill 196.93 | thinking 0.00 | gerador 360.79 | total 471.31

Resposta integral:

Um servidor público efetivo pode acumular dois cargos de professor na rede pública, desde que haja compatibilidade de horários, conforme previsto no inciso IV do art. 37, que permite a acumulação remunerada de cargos públicos, exceto quando houver incompatibilidade de horários. Especificamente, o inciso IV, alínea "a", estabelece que é permitida a acumulação de dois cargos de professor.

Quanto ao limite máximo de remuneração, o art. 37, XI, determina que a remuneração e o subsídio dos ocupantes de cargos, funções e empregos públicos, incluindo os proventos, pensões ou outra espécie remuneratória, não poderão exceder o subsídio mensal, em espécie, dos Ministros do Supremo Tribunal Federal. Nos Municípios, o limite é o subsídio do Prefeito; nos Estados e no Distrito Federal, o subsídio mensal do Governador no âmbito do Poder Executivo, o subsídio dos Deputados Estaduais e Distritais no âmbito do Poder Legislativo e o subsídio dos Desembargadores do Tribunal de Justiça, limitado a noventa inteiros e vinte e cinco centésimos por cento do subsídio mensal, em espécie, dos Ministros do Supremo Tribunal Federal, no âmbito do Poder Judiciário, aplicável este limite aos membros do Ministério Público, aos Procuradores e aos Defensores Públicos.

### 10 — COMPOSTA / MULTI-HOP

Pergunta: O Presidente da República pode editar medida provisória sobre direito penal, e qual é o prazo máximo de vigência de uma medida provisória antes de perder a eficácia?

Esperado: Art. 62, § 1º, I, b e Art. 62, § 3º.

- Intenção: Organização dos Poderes (margem 0.1468399415376374)
- modo_busca: multi_query
- classe: COMPOSTA
- passagem: 1 | tradutor: None | sub-consultas: ['Art. 62. § 5º. A medida provisória não poderá conter norma que torne penal ou aumente a pena ou o custo da pena pecuniária.', 'Art. 62. § 6º. A medida provisória terá validade de sessenta dias, podendo ser convertida em lei antes da expiração do prazo.']
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 62, § 5º (2 filhos); Art. 62, § 6º (2 filhos); Art. 62, § 1º (2 filhos); Art. 62, § 3º (2 filhos); Art. 62, § 7º (2 filhos)
- Checklist humano: Art. 62, § 1º, I, b e Art. 62, § 3º.
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 62"], "subdispositivos_citados": ["Art. 62, § 1º, I", "Art. 62, § 3º", "Art. 62, § 7º"], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 71.39 | prefill 165.06 | thinking 0.00 | gerador 235.85 | total 313.96

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas a medida provisória sobre direito penal, que é vedada, conforme **Art. 62, § 1º, I, b**, e, portanto, o Presidente da República **não pode** editar medida provisória sobre direito penal. O prazo máximo de vigência de uma medida provisória antes de perder a eficácia é de **sessenta dias**, conforme **Art. 62, § 3º**, prorrogável uma única vez por igual período, conforme **Art. 62, § 7º**.

### 11 — ORDEM SOCIAL / LEIGO

Pergunta: Um hospital particular pode cobrar pelo atendimento, ou a saúde no Brasil é proibida para empresas privadas?

Esperado: Art. 199: livre à iniciativa privada; § 2º veda recursos públicos a entidades com fins lucrativos.

- Intenção: None (margem None)
- modo_busca: None
- classe: None
- passagem: None | tradutor: None | sub-consultas: None
- Modo final: None
- Entregue ao LLM: (nenhum)
- Checklist humano: Art. 199: livre à iniciativa privada; § 2º veda recursos públicos a entidades com fins lucrativos.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 0.00 | prefill n/d | thinking n/d | gerador 0.00 | total 0.00

Resposta integral:

(sem resposta)

### 12 — TRABALHO / LEIGO

Pergunta: O patrão pode obrigar alguém a trabalhar 10 horas por dia todos os dias sem pagar nada a mais?

Esperado: Art. 7º, XIII e XVI: 8 horas, 44 semanais e hora extra de pelo menos 50%.

- Intenção: None (margem None)
- modo_busca: None
- classe: None
- passagem: None | tradutor: None | sub-consultas: None
- Modo final: None
- Entregue ao LLM: (nenhum)
- Checklist humano: Art. 7º, XIII e XVI: 8 horas, 44 semanais e hora extra de pelo menos 50%.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 0.00 | prefill n/d | thinking n/d | gerador 0.00 | total 0.00

Resposta integral:

(sem resposta)

### 13 — FORA DE ESCOPO / CDC

Pergunta: Comprei um celular na internet faz 3 dias e me arrependi, a loja é obrigada a devolver meu dinheiro?

Esperado: Conversa livre ou zona cinzenta, Código de Defesa do Consumidor, sem artigo inventado da CF/88.

- Intenção: None (margem None)
- modo_busca: None
- classe: None
- passagem: None | tradutor: None | sub-consultas: None
- Modo final: None
- Entregue ao LLM: (nenhum)
- Checklist humano: Conversa livre ou zona cinzenta, Código de Defesa do Consumidor, sem artigo inventado da CF/88.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 0.00 | prefill n/d | thinking n/d | gerador 0.00 | total 0.00

Resposta integral:

(sem resposta)

### 14 — FORA DE ESCOPO / TRANSITO

Pergunta: Se eu bater no carro de alguém no trânsito sem querer, qual é o valor da multa que eu levo?

Esperado: Conversa livre, CTB ou Código Civil, sem artigo inventado da CF/88.

- Intenção: None (margem None)
- modo_busca: None
- classe: None
- passagem: None | tradutor: None | sub-consultas: None
- Modo final: None
- Entregue ao LLM: (nenhum)
- Checklist humano: Conversa livre, CTB ou Código Civil, sem artigo inventado da CF/88.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 0.00 | prefill n/d | thinking n/d | gerador 0.00 | total 0.00

Resposta integral:

(sem resposta)

### 15 — ATALHO SOCIAL

Pergunta: Boa tarde, tudo bem?

Esperado: MODO_ATALHO_SOCIAL em menos de 0,1 s, sem BGE-M3 e sem Ollama.

- Intenção: None (margem None)
- modo_busca: None
- classe: None
- passagem: None | tradutor: None | sub-consultas: None
- Modo final: None
- Entregue ao LLM: (nenhum)
- Checklist humano: MODO_ATALHO_SOCIAL em menos de 0,1 s, sem BGE-M3 e sem Ollama.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 0.00 | prefill n/d | thinking n/d | gerador 0.00 | total 0.00

Resposta integral:

(sem resposta)

### 16 — REGRESSAO / ESCOPO - MINERACAO

Pergunta: A União detém o monopólio de toda a atividade de mineração no Brasil?

Esperado: Não começar com Sim. Restringir a minérios nucleares (Art. 177, V ou § 4º) e ao regime de autorização ou concessão (Art. 176). Sem generalizar.

- Intenção: None (margem None)
- modo_busca: None
- classe: None
- passagem: None | tradutor: None | sub-consultas: None
- Modo final: None
- Entregue ao LLM: (nenhum)
- Checklist humano: Não começar com Sim. Restringir a minérios nucleares (Art. 177, V ou § 4º) e ao regime de autorização ou concessão (Art. 176). Sem generalizar.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 0.00 | prefill n/d | thinking n/d | gerador 0.00 | total 0.00

Resposta integral:

(sem resposta)

### 17 — REGRESSAO / LIMITE NUMERICO - USUCAPIAO

Pergunta: Quem ocupa e trabalha numa terra rural de 40 hectares por 5 anos sem ser dono de outro imóvel pode adquirir a propriedade por usucapião?

Esperado: Art. 191: até 50 hectares, cinco anos, trabalho da família, moradia, sem outro imóvel. Não misturar o Art. 186.

- Intenção: None (margem None)
- modo_busca: None
- classe: None
- passagem: None | tradutor: None | sub-consultas: None
- Modo final: None
- Entregue ao LLM: (nenhum)
- Checklist humano: Art. 191: até 50 hectares, cinco anos, trabalho da família, moradia, sem outro imóvel. Não misturar o Art. 186.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 0.00 | prefill n/d | thinking n/d | gerador 0.00 | total 0.00

Resposta integral:

(sem resposta)

