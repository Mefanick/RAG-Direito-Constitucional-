# Bateria cega da Fase 3.3 — fase33_drift_check_v4

## Resumo executivo

Perfil fase33_drift_check_v4. Este relatório audita 15 perguntas inéditas e 2 regressões históricas. O histórico de cada chamada fica vazio. As três colunas do placar são independentes.

| Métrica | Resultado |
| --- | --- |
| Recuperação na 1ª passagem (12 inéditas) | 6/12 |
| Artigo esperado recuperado (12 inéditas) | 11/12 |
| Auditoria FIEL (12 inéditas) | 0/12 |
| Recuperação na 1ª passagem (2 regressões) | 2/2 |
| Auditoria FIEL (2 regressões) | 0/2 |
| Fora de escopo sem artigo inventado | 2/2 |
| Atalho social abaixo de 0,1 s | 1/1 |
| Retriever médio (s) | 16.41 |
| Prefill médio (s) | 0.00 |
| Pensamento médio (s) | 0.00 |
| Gerador médio (s) | 0.00 |
| Total médio (s) | 29.17 |

## Placar

| Caso | 1. Artigo na 1ª passagem | 2. Auditor FIEL | 3. Checklist de revisão humana |
| --- | --- | --- | --- |
| 01 LEIGO / EXCECAO | sim | pendente | Art. 5º, XI: ordem judicial só de dia; à noite, flagrante, desastre ou socorro. |
| 02 LEIGO / EXCECAO | não | pendente | Art. 5º, LXVII: vedada a prisão civil por dívida, com as ressalvas do próprio inciso. |
| 03 TRIBUTACAO / LEIGO | não | pendente | Art. 150, VI, b: imunidade dos templos. Classe Tributação e Orçamento. |
| 04 TRIBUTACAO / PRAZO | não | pendente | Art. 150, III, b e c: anterioridade anual e nonagesimal, com exceções. |
| 05 TRIBUTACAO / COMPETENCIA | não | pendente | Art. 155, I: Estados e Distrito Federal. |
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

- Intenção: Direitos e Garantias Fundamentais (margem 0.17552641440349417)
- modo_busca: densa_com_boost
- classe: SIMPLES
- passagem: 1 | tradutor: é vedado à autoridade policial realizar entrada em domicílio sem prévia comunicação ao interessado ou autorização judicial específica | sub-consultas: []
- Modo final: MODO_RAG_ZONA_CINZENTA
- Entregue ao LLM: Art. 5º, XI [reranker]; Art. 5º, LXI [reranker]; Art. 136, § 3º [reranker]
- Checklist humano: Art. 5º, XI: ordem judicial só de dia; à noite, flagrante, desastre ou socorro.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 22.70 | prefill n/d | thinking n/d | gerador 0.00 | total 117.82

Resposta integral:

(sem resposta)

### 02 — LEIGO / EXCECAO

Pergunta: Se eu dever um empréstimo no banco e não pagar, posso ir preso?

Esperado: Art. 5º, LXVII: vedada a prisão civil por dívida, com as ressalvas do próprio inciso.

- Intenção: Direitos e Garantias Fundamentais (margem 0.06398489220248899)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 2 | tradutor: é vedado ao Estado aplicar prisão por dívida de natureza civil ou trabalhista, salvo em caso de execução penal | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 5º, LXVII [reranker]; Art. 5º, LXVI [irmao_adjacente]
- Checklist humano: Art. 5º, LXVII: vedada a prisão civil por dívida, com as ressalvas do próprio inciso.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 12.35 | prefill n/d | thinking n/d | gerador 0.00 | total 27.06

Resposta integral:

(sem resposta)

### 03 — TRIBUTACAO / LEIGO

Pergunta: A prefeitura pode cobrar IPTU de uma igreja do meu bairro?

Esperado: Art. 150, VI, b: imunidade dos templos. Classe Tributação e Orçamento.

- Intenção: Tributação e Orçamento (margem 0.0702377720671917)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 2 | tradutor: compete aos Municípios instituir imposto sobre a propriedade territorial rural e urbana, incluindo imóveis de instituições religiosas | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 156 (9 filhos); Art. 158 (6 filhos)
- Checklist humano: Art. 150, VI, b: imunidade dos templos. Classe Tributação e Orçamento.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 13.34 | prefill n/d | thinking n/d | gerador 0.00 | total 31.00

Resposta integral:

(sem resposta)

### 04 — TRIBUTACAO / PRAZO

Pergunta: O governo pode criar um imposto hoje e começar a cobrar na semana que vem?

Esperado: Art. 150, III, b e c: anterioridade anual e nonagesimal, com exceções.

- Intenção: Tributação e Orçamento (margem 0.2772914740202086)
- modo_busca: densa_com_boost
- classe: SIMPLES
- passagem: 2 | tradutor: é vedado instituir imposto sem observância do prazo legal para sua entrada em vigor | sub-consultas: []
- Modo final: MODO_RAG_ZONA_CINZENTA
- Entregue ao LLM: Art. 150, III [reranker]; Art. 151 [reranker]; Art. 150, I [reranker]
- Checklist humano: Art. 150, III, b e c: anterioridade anual e nonagesimal, com exceções.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 13.36 | prefill n/d | thinking n/d | gerador 0.00 | total 24.41

Resposta integral:

(sem resposta)

### 05 — TRIBUTACAO / COMPETENCIA

Pergunta: Se eu receber um terreno de doação em vida, quem cobra o imposto sobre essa doação: a Prefeitura, o Estado ou a União?

Esperado: Art. 155, I: Estados e Distrito Federal.

- Intenção: Tributação e Orçamento (margem 0.14375497391415423)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 2 | tradutor: compete à União, aos Estados, ao Distrito Federal ou aos Municípios cobrar imposto sobre doação de imóvel urbano ou rural | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 155, § 1º (2 filhos); Art. 23 [reranker]; Art. 155 [reranker]; Art. 147 [fusao_p1]
- Checklist humano: Art. 155, I: Estados e Distrito Federal.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 15.33 | prefill n/d | thinking n/d | gerador 0.00 | total 33.99

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
- Tempos (s): retriever 8.50 | prefill n/d | thinking n/d | gerador 0.00 | total 9.57

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
- Tempos (s): retriever 8.87 | prefill n/d | thinking n/d | gerador 0.00 | total 9.74

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
- Tempos (s): retriever 6.13 | prefill n/d | thinking n/d | gerador 0.00 | total 7.61

Resposta integral:

(sem resposta)

### 09 — COMPOSTA / MULTI-HOP

Pergunta: Um servidor público efetivo pode acumular dois cargos de professor na rede pública, e qual é o limite máximo que ele pode receber de remuneração?

Esperado: Art. 37, XVI, a e Art. 37, XI.

- Intenção: Tributação e Orçamento (margem 0.0036294082907716296)
- modo_busca: multi_query
- classe: COMPOSTA
- passagem: 1 | tradutor: None | sub-consultas: ['Art. 37, X da Constituição Federal estabelece que a remuneração do servidor público não poderá ultrapassar o limite máximo estabelecido em lei.', 'Art. 37, XI determina que o servidor público não poderá acumular cargos, funções ou empregos que exijam exercício simultâneo de atividades de responsabilidade pública.', 'Art. 37, XII prevê que o servidor público não poderá acumular cargo de professor com outro cargo de professor na mesma rede pública.']
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 37, § 10º (2 filhos); Art. 39, § 5º (2 filhos); Art. 37, XI [reranker]; Art. 37, XVI [reranker]; Art. 37, X [reranker]; Art. 37, XVII [reranker]; Art. 37, XIV [reranker]; Art. 37, XII [irmao_adjacente]; Art. 37, XIII [irmao_adjacente]
- Checklist humano: Art. 37, XVI, a e Art. 37, XI.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 69.81 | prefill n/d | thinking n/d | gerador 0.00 | total 70.73

Resposta integral:

(sem resposta)

### 10 — COMPOSTA / MULTI-HOP

Pergunta: O Presidente da República pode editar medida provisória sobre direito penal, e qual é o prazo máximo de vigência de uma medida provisória antes de perder a eficácia?

Esperado: Art. 62, § 1º, I, b e Art. 62, § 3º.

- Intenção: Organização dos Poderes (margem 0.1468399415376374)
- modo_busca: multi_query
- classe: COMPOSTA
- passagem: 1 | tradutor: None | sub-consultas: ['Art. 62. § 5º. A medida provisória não poderá conter norma que torne aplicável a lei penal, salvo em caso de flagrante delito.', 'Art. 62. § 6º. A medida provisória terá validade de sessenta dias, podendo ser convertida em lei antes da expiração do prazo.']
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 62, § 5º (2 filhos); Art. 62, § 6º (2 filhos); Art. 62, § 1º (2 filhos); Art. 62, § 3º (2 filhos); Art. 62, § 11º (2 filhos); Art. 62, § 7º (2 filhos)
- Checklist humano: Art. 62, § 1º, I, b e Art. 62, § 3º.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 49.67 | prefill n/d | thinking n/d | gerador 0.00 | total 52.87

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
- Tempos (s): retriever 6.92 | prefill n/d | thinking n/d | gerador 0.00 | total 8.04

Resposta integral:

(sem resposta)

### 12 — TRABALHO / LEIGO

Pergunta: O patrão pode obrigar alguém a trabalhar 10 horas por dia todos os dias sem pagar nada a mais?

Esperado: Art. 7º, XIII e XVI: 8 horas, 44 semanais e hora extra de pelo menos 50%.

- Intenção: Ordem Econômica e Financeira (margem 0.016073996596375817)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 2 | tradutor: é vedado ao empregador exigir jornada diária superior a oito horas sem garantir intervalo para repouso e remuneração adicional | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 7º, XIII [reranker]; Art. 7º, XI [irmao_adjacente]; Art. 7º, XII [irmao_adjacente]
- Checklist humano: Art. 7º, XIII e XVI: 8 horas, 44 semanais e hora extra de pelo menos 50%.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 11.41 | prefill n/d | thinking n/d | gerador 0.00 | total 28.74

Resposta integral:

(sem resposta)

### 13 — FORA DE ESCOPO / CDC

Pergunta: Comprei um celular na internet faz 3 dias e me arrependi, a loja é obrigada a devolver meu dinheiro?

Esperado: Conversa livre ou zona cinzenta, Código de Defesa do Consumidor, sem artigo inventado da CF/88.

- Intenção: Direitos e Garantias Fundamentais (margem 0.08431007894437109)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 2 | tradutor: é direito do consumidor a ressarcimento integral do valor pago por produto adquirido em até 7 dias após a compra | sub-consultas: []
- Modo final: MODO_CONVERSA_LIVRE
- Entregue ao LLM: (nenhum)
- Checklist humano: Conversa livre ou zona cinzenta, Código de Defesa do Consumidor, sem artigo inventado da CF/88.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 12.27 | prefill n/d | thinking n/d | gerador 0.00 | total 27.35

Resposta integral:

(sem resposta)

### 14 — FORA DE ESCOPO / TRANSITO

Pergunta: Se eu bater no carro de alguém no trânsito sem querer, qual é o valor da multa que eu levo?

Esperado: Conversa livre, CTB ou Código Civil, sem artigo inventado da CF/88.

- Intenção: Tributação e Orçamento (margem 0.06284620453020048)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 2 | tradutor: é vedado cobrar multa por infração de trânsito sem observância da lei penal e do Código de Trânsito Brasileiro | sub-consultas: []
- Modo final: MODO_CONVERSA_LIVRE
- Entregue ao LLM: (nenhum)
- Checklist humano: Conversa livre, CTB ou Código Civil, sem artigo inventado da CF/88.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 13.40 | prefill n/d | thinking n/d | gerador 0.00 | total 29.68

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
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 6.87 | prefill n/d | thinking n/d | gerador 0.00 | total 7.92

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
- Tempos (s): retriever 7.97 | prefill n/d | thinking n/d | gerador 0.00 | total 9.30

Resposta integral:

(sem resposta)

