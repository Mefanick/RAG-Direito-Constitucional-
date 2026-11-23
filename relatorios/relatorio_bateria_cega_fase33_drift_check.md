# Bateria cega da Fase 3.3 — fase33_drift_check

## Resumo executivo

Perfil fase33_drift_check. Este relatório audita 15 perguntas inéditas e 2 regressões históricas. O histórico de cada chamada fica vazio. As três colunas do placar são independentes.

| Métrica | Resultado |
| --- | --- |
| Recuperação na 1ª passagem (12 inéditas) | 6/12 |
| Artigo esperado recuperado (12 inéditas) | 10/12 |
| Auditoria FIEL (12 inéditas) | 0/12 |
| Recuperação na 1ª passagem (2 regressões) | 2/2 |
| Auditoria FIEL (2 regressões) | 0/2 |
| Fora de escopo sem artigo inventado | 2/2 |
| Atalho social abaixo de 0,1 s | 1/1 |
| Retriever médio (s) | 10.79 |
| Prefill médio (s) | 0.00 |
| Pensamento médio (s) | 0.00 |
| Gerador médio (s) | 0.00 |
| Total médio (s) | 21.60 |

## Placar

| Caso | 1. Artigo na 1ª passagem | 2. Auditor FIEL | 3. Checklist de revisão humana |
| --- | --- | --- | --- |
| 01 LEIGO / EXCECAO | não | pendente | Art. 5º, XI: ordem judicial só de dia; à noite, flagrante, desastre ou socorro. |
| 02 LEIGO / EXCECAO | não | pendente | Art. 5º, LXVII: vedada a prisão civil por dívida, com as ressalvas do próprio inciso. |
| 03 TRIBUTACAO / LEIGO | não | pendente | Art. 150, VI, b: imunidade dos templos. Classe Tributação e Orçamento. |
| 04 TRIBUTACAO / PRAZO | não | pendente | Art. 150, III, b e c: anterioridade anual e nonagesimal, com exceções. |
| 05 TRIBUTACAO / COMPETENCIA | sim | pendente | Art. 155, I: Estados e Distrito Federal. |
| 06 ADCT / LEIGO | sim | pendente | ADCT, Art. 10, II, b: da confirmação da gravidez até cinco meses após o parto. |
| 07 PARENT-DOC / NUMERO | sim | pendente | Art. 14, § 3º, VI, a: 35 anos. |
| 08 PARENT-DOC / INCISOS | sim | pendente | Art. 12, § 4º, fiel ao texto vigente recuperado, sem inciso inventado. |
| 09 COMPOSTA / MULTI-HOP | sim | pendente | Art. 37, XVI, a e Art. 37, XI. |
| 10 COMPOSTA / MULTI-HOP | sim | pendente | Art. 62, § 1º, I, b e Art. 62, § 3º. |
| 11 ORDEM SOCIAL / LEIGO | sim | pendente | Art. 199: livre à iniciativa privada; § 2º veda recursos públicos a entidades com fins lucrativos. |
| 12 TRABALHO / LEIGO | não | pendente | Art. 7º, XIII e XVI: 8 horas, 44 semanais e hora extra de pelo menos 50%. |
| 13 FORA DE ESCOPO / CDC | não se aplica | pendente | Conversa livre ou zona cinzenta, Código de Defesa do Consumidor, sem artigo inventado da CF/88. |
| 14 FORA DE ESCOPO / TRANSITO | não se aplica | pendente | Conversa livre, CTB ou Código Civil, sem artigo inventado da CF/88. |
| 15 ATALHO SOCIAL | não se aplica | SEM_CITACAO | MODO_ATALHO_SOCIAL em menos de 0,1 s, sem BGE-M3 e sem Ollama. |
| 16 REGRESSAO / ESCOPO - MINERACAO | sim | pendente | Não começar com Sim. Restringir a minérios nucleares (Art. 177, V ou § 4º) e ao regime de autorização ou concessão (Art. 176). Sem generalizar. |
| 17 REGRESSAO / LIMITE NUMERICO - USUCAPIAO | sim | pendente | Art. 191: até 50 hectares, cinco anos, trabalho da família, moradia, sem outro imóvel. Não misturar o Art. 186. |

## Resposta integral e checklist

### 01 — LEIGO / EXCECAO

Pergunta: A polícia pode arrombar a porta da minha casa à noite só com ordem do juiz?

Esperado: Art. 5º, XI: ordem judicial só de dia; à noite, flagrante, desastre ou socorro.

- Intenção: Direitos e Garantias Fundamentais (margem 0.15923728293128298)
- modo_busca: densa_com_boost
- classe: SIMPLES
- passagem: 2 | tradutor: é vedado à autoridade policial invadir domicílio sem prévia autorização judicial ou mandado específico | sub-consultas: []
- Modo final: MODO_RAG_ZONA_CINZENTA
- Entregue ao LLM: Art. 5º, XI [reranker]; Art. 5º, XXXIX [reranker]; Art. 5º, LXI [reranker]
- Checklist humano: Art. 5º, XI: ordem judicial só de dia; à noite, flagrante, desastre ou socorro.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 18.25 | prefill n/d | thinking n/d | gerador 0.00 | total 86.09

Resposta integral:

(sem resposta)

### 02 — LEIGO / EXCECAO

Pergunta: Se eu dever um empréstimo no banco e não pagar, posso ir preso?

Esperado: Art. 5º, LXVII: vedada a prisão civil por dívida, com as ressalvas do próprio inciso.

- Intenção: Direitos e Garantias Fundamentais (margem 0.1527822482778701)
- modo_busca: densa_com_boost
- classe: SIMPLES
- passagem: 2 | tradutor: é vedado à autoridade judicial aplicar prisão por dívida de natureza civil ou trabalhista, salvo em caso de execução penal ou por crime próprio | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 5º, LXVII [reranker]; Art. 5º, LXVI [irmao_adjacente]
- Checklist humano: Art. 5º, LXVII: vedada a prisão civil por dívida, com as ressalvas do próprio inciso.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 10.71 | prefill n/d | thinking n/d | gerador 0.00 | total 27.04

Resposta integral:

(sem resposta)

### 03 — TRIBUTACAO / LEIGO

Pergunta: A prefeitura pode cobrar IPTU de uma igreja do meu bairro?

Esperado: Art. 150, VI, b: imunidade dos templos. Classe Tributação e Orçamento.

- Intenção: Tributação e Orçamento (margem 0.43900097599039983)
- modo_busca: densa_com_boost
- classe: SIMPLES
- passagem: 1 | tradutor: é vedado cobrar tributos de entidade religiosa que não tenha fins lucrativos e que esteja em atividade religiosa | sub-consultas: []
- Modo final: MODO_CONVERSA_LIVRE
- Entregue ao LLM: (nenhum)
- Checklist humano: Art. 150, VI, b: imunidade dos templos. Classe Tributação e Orçamento.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 3.39 | prefill n/d | thinking n/d | gerador 0.00 | total 16.18

Resposta integral:

(sem resposta)

### 04 — TRIBUTACAO / PRAZO

Pergunta: O governo pode criar um imposto hoje e começar a cobrar na semana que vem?

Esperado: Art. 150, III, b e c: anterioridade anual e nonagesimal, com exceções.

- Intenção: Tributação e Orçamento (margem 0.3785086219118428)
- modo_busca: densa_com_boost
- classe: SIMPLES
- passagem: 1 | tradutor: é vedado instituir impostos sobre a renda, o lucro e o patrimônio, salvo se previstos em lei e com eficácia a partir da data da publicação da lei | sub-consultas: []
- Modo final: MODO_CONVERSA_LIVRE
- Entregue ao LLM: (nenhum)
- Checklist humano: Art. 150, III, b e c: anterioridade anual e nonagesimal, com exceções.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 6.69 | prefill n/d | thinking n/d | gerador 0.00 | total 25.87

Resposta integral:

(sem resposta)

### 05 — TRIBUTACAO / COMPETENCIA

Pergunta: Se eu receber um terreno de doação em vida, quem cobra o imposto sobre essa doação: a Prefeitura, o Estado ou a União?

Esperado: Art. 155, I: Estados e Distrito Federal.

- Intenção: Tributação e Orçamento (margem 0.3352815187453403)
- modo_busca: densa_com_boost
- classe: SIMPLES
- passagem: 1 | tradutor: é vedado à União, aos Estados, ao Distrito Federal e aos Municípios utilizar tributo com efeito de confisco | sub-consultas: []
- Modo final: MODO_RAG_ZONA_CINZENTA
- Entregue ao LLM: Art. 147 [reranker]; Art. 155, § 1º [reranker]; Art. 155, I [reranker]
- Checklist humano: Art. 155, I: Estados e Distrito Federal.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 4.60 | prefill n/d | thinking n/d | gerador 0.00 | total 19.39

Resposta integral:

(sem resposta)

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
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 6.08 | prefill n/d | thinking n/d | gerador 0.00 | total 7.04

Resposta integral:

(sem resposta)

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
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 4.87 | prefill n/d | thinking n/d | gerador 0.00 | total 5.80

Resposta integral:

(sem resposta)

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
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 3.07 | prefill n/d | thinking n/d | gerador 0.00 | total 3.87

Resposta integral:

(sem resposta)

### 09 — COMPOSTA / MULTI-HOP

Pergunta: Um servidor público efetivo pode acumular dois cargos de professor na rede pública, e qual é o limite máximo que ele pode receber de remuneração?

Esperado: Art. 37, XVI, a e Art. 37, XI.

- Intenção: Tributação e Orçamento (margem 0.0036294082907716296)
- modo_busca: multi_query
- classe: COMPOSTA
- passagem: 1 | tradutor: None | sub-consultas: ['Art. 37, X da Constituição Federal estabelece que a remuneração do servidor público não poderá ultrapassar o limite máximo estabelecido em lei.', 'Art. 37, XI determina que o servidor público não poderá acumular cargos, funções ou empregos que exijam exercício simultâneo de atividades de responsabilidade pública.', 'Art. 37, XII prevê que o servidor público não poderá acumular cargo de professor na rede pública, salvo em casos de exercício de atividade docente em instit']
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 37, § 10º (2 filhos); Art. 39, § 5º (2 filhos); Art. 37, § 13º (2 filhos); Art. 37, XI [reranker]; Art. 37, XVI [reranker]; Art. 37, X [reranker]; Art. 37, XVII [reranker]
- Checklist humano: Art. 37, XVI, a e Art. 37, XI.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 61.23 | prefill n/d | thinking n/d | gerador 0.00 | total 62.08

Resposta integral:

(sem resposta)

### 10 — COMPOSTA / MULTI-HOP

Pergunta: O Presidente da República pode editar medida provisória sobre direito penal, e qual é o prazo máximo de vigência de uma medida provisória antes de perder a eficácia?

Esperado: Art. 62, § 1º, I, b e Art. 62, § 3º.

- Intenção: Organização dos Poderes (margem 0.1468399415376374)
- modo_busca: multi_query
- classe: COMPOSTA
- passagem: 1 | tradutor: None | sub-consultas: ['Art. 62. § 5º. A medida provisória não poderá conter norma que torne aplicável a pessoa física ou jurídica penalidade prevista em lei penal, salvo em caso de flagrante delito.', 'Art. 62. § 6º. A medida provisória terá validade de sessenta dias, podendo ser convertida em lei antes da expiração do prazo.']
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 62, § 5º (2 filhos); Art. 62, § 6º (2 filhos); Art. 62, § 1º (2 filhos); Art. 62, § 3º (2 filhos); Art. 62, § 11º (2 filhos); Art. 62, § 7º (2 filhos)
- Checklist humano: Art. 62, § 1º, I, b e Art. 62, § 3º.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 39.78 | prefill n/d | thinking n/d | gerador 0.00 | total 40.47

Resposta integral:

(sem resposta)

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
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 4.25 | prefill n/d | thinking n/d | gerador 0.00 | total 4.90

Resposta integral:

(sem resposta)

### 12 — TRABALHO / LEIGO

Pergunta: O patrão pode obrigar alguém a trabalhar 10 horas por dia todos os dias sem pagar nada a mais?

Esperado: Art. 7º, XIII e XVI: 8 horas, 44 semanais e hora extra de pelo menos 50%.

- Intenção: Organização dos Poderes (margem 0.016653795002015248)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 2 | tradutor: é vedado ao empregador estabelecer jornada de trabalho superior a oito horas diárias e a quatro horas semanais, salvo em caso de força maior, sem garantir remuneração adicional | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 7º, XIII [reranker]; Art. 7º, XI [irmao_adjacente]; Art. 7º, XII [irmao_adjacente]
- Checklist humano: Art. 7º, XIII e XVI: 8 horas, 44 semanais e hora extra de pelo menos 50%.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 5.90 | prefill n/d | thinking n/d | gerador 0.00 | total 25.63

Resposta integral:

(sem resposta)

### 13 — FORA DE ESCOPO / CDC

Pergunta: Comprei um celular na internet faz 3 dias e me arrependi, a loja é obrigada a devolver meu dinheiro?

Esperado: Conversa livre ou zona cinzenta, Código de Defesa do Consumidor, sem artigo inventado da CF/88.

- Intenção: Direitos e Garantias Fundamentais (margem 0.07763119785845599)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 1 | tradutor: é vedado cobrar tributos sobre o direito de ressarcimento por arrependimento de compra realizada na internet | sub-consultas: []
- Modo final: MODO_CONVERSA_LIVRE
- Entregue ao LLM: (nenhum)
- Checklist humano: Conversa livre ou zona cinzenta, Código de Defesa do Consumidor, sem artigo inventado da CF/88.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 4.01 | prefill n/d | thinking n/d | gerador 0.00 | total 17.10

Resposta integral:

(sem resposta)

### 14 — FORA DE ESCOPO / TRANSITO

Pergunta: Se eu bater no carro de alguém no trânsito sem querer, qual é o valor da multa que eu levo?

Esperado: Conversa livre, CTB ou Código Civil, sem artigo inventado da CF/88.

- Intenção: Tributação e Orçamento (margem 0.05187448780927245)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 1 | tradutor: é vedado cobrar tributo que não seja previsto em lei e que não tenha caráter punitivo ou reparatório | sub-consultas: []
- Modo final: MODO_CONVERSA_LIVRE
- Entregue ao LLM: (nenhum)
- Checklist humano: Conversa livre, CTB ou Código Civil, sem artigo inventado da CF/88.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 3.00 | prefill n/d | thinking n/d | gerador 0.00 | total 16.69

Resposta integral:

(sem resposta)

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
- Tempos (s): retriever 0.00 | prefill 0.00 | thinking 0.00 | gerador 0.00 | total 0.02

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
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 3.30 | prefill n/d | thinking n/d | gerador 0.00 | total 4.06

Resposta integral:

(sem resposta)

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
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 4.25 | prefill n/d | thinking n/d | gerador 0.00 | total 5.02

Resposta integral:

(sem resposta)

