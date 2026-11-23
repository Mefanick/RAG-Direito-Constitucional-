# Bateria cega da Fase 3.3 — fase33_hyde_parcial

## Resumo executivo

Perfil fase33_hyde_parcial. Este relatório audita 15 perguntas inéditas e 2 regressões históricas. O histórico de cada chamada fica vazio. As três colunas do placar são independentes.

| Métrica | Resultado |
| --- | --- |
| Recuperação na 1ª passagem (12 inéditas) | 0/12 |
| Artigo esperado recuperado (12 inéditas) | 3/12 |
| Auditoria FIEL (12 inéditas) | 3/12 |
| Recuperação na 1ª passagem (2 regressões) | 0/2 |
| Auditoria FIEL (2 regressões) | 0/2 |
| Fora de escopo sem artigo inventado | 1/2 |
| Atalho social abaixo de 0,1 s | 0/1 |
| Retriever médio (s) | 29.23 |
| Prefill médio (s) | 50.55 |
| Pensamento médio (s) | 0.00 |
| Gerador médio (s) | 103.12 |
| Total médio (s) | 161.43 |

## Placar

| Caso | 1. Artigo na 1ª passagem | 2. Auditor FIEL | 3. Checklist de revisão humana |
| --- | --- | --- | --- |
| 01 LEIGO / EXCECAO | não | pendente | Art. 5º, XI: ordem judicial só de dia; à noite, flagrante, desastre ou socorro. |
| 02 LEIGO / EXCECAO | não | pendente | Art. 5º, LXVII: vedada a prisão civil por dívida, com as ressalvas do próprio inciso. |
| 03 TRIBUTACAO / LEIGO | não | sim | Art. 150, VI, b: imunidade dos templos. Classe Tributação e Orçamento. |
| 04 TRIBUTACAO / PRAZO | não | sim | Art. 150, III, b e c: anterioridade anual e nonagesimal, com exceções. |
| 05 TRIBUTACAO / COMPETENCIA | não | pendente | Art. 155, I: Estados e Distrito Federal. |
| 06 ADCT / LEIGO | não | pendente | ADCT, Art. 10, II, b: da confirmação da gravidez até cinco meses após o parto. |
| 07 PARENT-DOC / NUMERO | não | pendente | Art. 14, § 3º, VI, a: 35 anos. |
| 08 PARENT-DOC / INCISOS | não | pendente | Art. 12, § 4º, fiel ao texto vigente recuperado, sem inciso inventado. |
| 09 COMPOSTA / MULTI-HOP | não | pendente | Art. 37, XVI, a e Art. 37, XI. |
| 10 COMPOSTA / MULTI-HOP | não | pendente | Art. 62, § 1º, I, b e Art. 62, § 3º. |
| 11 ORDEM SOCIAL / LEIGO | não | pendente | Art. 199: livre à iniciativa privada; § 2º veda recursos públicos a entidades com fins lucrativos. |
| 12 TRABALHO / LEIGO | não | sim | Art. 7º, XIII e XVI: 8 horas, 44 semanais e hora extra de pelo menos 50%. |
| 13 FORA DE ESCOPO / CDC | não se aplica | SEM_CITACAO | Conversa livre ou zona cinzenta, Código de Defesa do Consumidor, sem artigo inventado da CF/88. |
| 14 FORA DE ESCOPO / TRANSITO | não se aplica | SEM_CITACAO | Conversa livre, CTB ou Código Civil, sem artigo inventado da CF/88. |
| 15 ATALHO SOCIAL | não se aplica | pendente | MODO_ATALHO_SOCIAL em menos de 0,1 s, sem BGE-M3 e sem Ollama. |
| 16 REGRESSAO / ESCOPO - MINERACAO | não | pendente | Não começar com Sim. Restringir a minérios nucleares (Art. 177, V ou § 4º) e ao regime de autorização ou concessão (Art. 176). Sem generalizar. |
| 17 REGRESSAO / LIMITE NUMERICO - USUCAPIAO | não | pendente | Art. 191: até 50 hectares, cinco anos, trabalho da família, moradia, sem outro imóvel. Não misturar o Art. 186. |

## Resposta integral e checklist

### 01 — LEIGO / EXCECAO

Pergunta: A polícia pode arrombar a porta da minha casa à noite só com ordem do juiz?

Esperado: Art. 5º, XI: ordem judicial só de dia; à noite, flagrante, desastre ou socorro.

- Intenção: None (margem None)
- modo_busca: None
- classe: None
- passagem: None | tradutor: None | sub-consultas: None
- Modo final: None
- Entregue ao LLM: (nenhum)
- Checklist humano: Art. 5º, XI: ordem judicial só de dia; à noite, flagrante, desastre ou socorro.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 0.00 | prefill n/d | thinking n/d | gerador 0.00 | total 0.00

Resposta integral:

(sem resposta)

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

- Intenção: Tributação e Orçamento (margem 0.2719448878098402)
- modo_busca: densa_com_boost
- classe: SIMPLES
- passagem: 2 | tradutor: é vedado cobrar tributos de entidade religiosa que não tenha fins lucrativos e que esteja isenta de contribuições de qualquer natureza | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 150, VI [reranker]
- Checklist humano: Art. 150, VI, b: imunidade dos templos. Classe Tributação e Orçamento.
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 150"], "subdispositivos_citados": ["Art. 150, VI"], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 36.08 | prefill 69.80 | thinking n/d | gerador 107.08 | total 218.32

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas a impostos sobre templos de qualquer culto, vedado à União, aos Estados, ao Distrito Federal e aos Municípios, conforme explicitado no art. 150, VI, letra b. Portanto, a prefeitura não pode cobrar IPTU de uma igreja do seu bairro, pois tal cobrança seria violatória da vedação constitucional.

### 04 — TRIBUTACAO / PRAZO

Pergunta: O governo pode criar um imposto hoje e começar a cobrar na semana que vem?

Esperado: Art. 150, III, b e c: anterioridade anual e nonagesimal, com exceções.

- Intenção: Tributação e Orçamento (margem 0.27338235676845707)
- modo_busca: densa_com_boost
- classe: SIMPLES
- passagem: 2 | tradutor: é vedado instituir impostos sobre renda, ganho de capital e outros tributos sem previsão de data de início da cobrança | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 151 (1 filhos); Art. 150, III [reranker]; Art. 150, VI [reranker]
- Checklist humano: Art. 150, III, b e c: anterioridade anual e nonagesimal, com exceções.
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 150"], "subdispositivos_citados": ["Art. 150, III, \"b\""], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 18.54 | prefill 64.59 | thinking n/d | gerador 113.04 | total 145.85

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas à cobrança de tributos instituídos em lei, não há base para generalizar para outros casos. De acordo com o Art. 150, III, alínea b, é vedado cobrar tributos no mesmo exercício financeiro em que haja sido publicada a lei que os instituiu ou aumentou. Portanto, o governo não pode criar um imposto hoje e começar a cobrar na semana que vem, pois a cobrança só pode ocorrer após o término do prazo de noventa dias da publicação da lei.

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

- Intenção: None (margem None)
- modo_busca: None
- classe: None
- passagem: None | tradutor: None | sub-consultas: None
- Modo final: None
- Entregue ao LLM: (nenhum)
- Checklist humano: Art. 37, XVI, a e Art. 37, XI.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 0.00 | prefill n/d | thinking n/d | gerador 0.00 | total 0.00

Resposta integral:

(sem resposta)

### 10 — COMPOSTA / MULTI-HOP

Pergunta: O Presidente da República pode editar medida provisória sobre direito penal, e qual é o prazo máximo de vigência de uma medida provisória antes de perder a eficácia?

Esperado: Art. 62, § 1º, I, b e Art. 62, § 3º.

- Intenção: None (margem None)
- modo_busca: None
- classe: None
- passagem: None | tradutor: None | sub-consultas: None
- Modo final: None
- Entregue ao LLM: (nenhum)
- Checklist humano: Art. 62, § 1º, I, b e Art. 62, § 3º.
- Auditoria: {"status": null, "artigos_citados": null, "subdispositivos_citados": null, "artigos_inventados": null, "subdispositivos_nao_confirmados": null}
- Tempos (s): retriever 0.00 | prefill n/d | thinking n/d | gerador 0.00 | total 0.00

Resposta integral:

(sem resposta)

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

- Intenção: Ordem Econômica e Financeira (margem 0.03922928774975093)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 2 | tradutor: é vedado ao empregador exigir do trabalhador jornada diária superior a oito horas sem pagamento de horas extras | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 7º, XIII [reranker]; Art. 7º, XI [irmao_adjacente]; Art. 7º, XII [irmao_adjacente]
- Checklist humano: Art. 7º, XIII e XVI: 8 horas, 44 semanais e hora extra de pelo menos 50%.
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 7"], "subdispositivos_citados": ["Art. 7, XIII"], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 33.89 | prefill 33.71 | thinking n/d | gerador 102.41 | total 156.10

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas à duração do trabalho normal, que não pode ser superior a oito horas diárias, conforme previsto no art. 7º, XIII. Portanto, o patrão não pode obrigar alguém a trabalhar 10 horas por dia todos os dias, pois isso viola a limitação estabelecida na Constituição. Além disso, a fonte não menciona a possibilidade de compensação de horários ou redução da jornada em casos de trabalho extraordinário, o que reforça que a duração do trabalho normal está limitada a oito horas diárias. Não há base para generalizar para outros tipos de trabalho ou regimes horários.

### 13 — FORA DE ESCOPO / CDC

Pergunta: Comprei um celular na internet faz 3 dias e me arrependi, a loja é obrigada a devolver meu dinheiro?

Esperado: Conversa livre ou zona cinzenta, Código de Defesa do Consumidor, sem artigo inventado da CF/88.

- Intenção: Direitos e Garantias Fundamentais (margem 0.09001316975204851)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 2 | tradutor: é direito do consumidor a reembolso do valor pago quando houver arrependimento dentro do prazo legal de 7 dias corridos | sub-consultas: []
- Modo final: MODO_CONVERSA_LIVRE
- Entregue ao LLM: (nenhum)
- Checklist humano: Conversa livre ou zona cinzenta, Código de Defesa do Consumidor, sem artigo inventado da CF/88.
- Auditoria: {"status": "SEM_CITACAO", "artigos_citados": [], "subdispositivos_citados": [], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 16.91 | prefill 13.61 | thinking n/d | gerador 82.86 | total 114.63

Resposta integral:

Aviso: este tema não foi localizado na base constitucional carregada (CF/88). A explicação abaixo é apenas orientativa e não possui verificação normativa.

Sim, se você comprou um celular na internet e se arrependeu, a loja pode ser obrigada a devolver o dinheiro, desde que você tenha exercido o direito de arrependimento dentro do prazo legal. Esse direito é previsto no Código de Defesa do Consumidor, que garante ao consumidor o direito de cancelar a compra e receber o dinheiro de volta, desde que o produto não tenha sido utilizado ou danificado. O prazo geralmente é de 7 dias corridos, contados a partir do momento em que você recebeu o produto.

No entanto, é importante verificar se a loja oferece um prazo maior para o arrependimento, especialmente se o produto for mais caro ou de maior valor. Nesse caso, o prazo pode ser de até 14 dias. Se a loja não aceitar o cancelamento, você pode recorrer à Procon ou ao Poder Judiciário para proteger seus direitos.

### 14 — FORA DE ESCOPO / TRANSITO

Pergunta: Se eu bater no carro de alguém no trânsito sem querer, qual é o valor da multa que eu levo?

Esperado: Conversa livre, CTB ou Código Civil, sem artigo inventado da CF/88.

- Intenção: Tributação e Orçamento (margem 0.28434449091492725)
- modo_busca: densa_com_boost
- classe: SIMPLES
- passagem: 2 | tradutor: é vedado cobrar tributo que não esteja previsto em lei ou que seja contrário ao princípio da legalidade | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 151 (1 filhos); Art. 150, I [reranker]; Art. 150 [irmao_adjacente]; Art. 150, II [irmao_adjacente]; Art. 150, III [reranker]
- Checklist humano: Conversa livre, CTB ou Código Civil, sem artigo inventado da CF/88.
- Auditoria: {"status": "SEM_CITACAO", "artigos_citados": [], "subdispositivos_citados": [], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 40.71 | prefill 71.03 | thinking n/d | gerador 110.19 | total 172.26

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas a tributos e não há base para generalizar para situações de infração penal ou civil, como o ato de bater em outro veículo. A Constituição de 1988 não prevê valores de multas para tais situações, sendo necessário consultar a legislação penal e as normas específicas de trânsito, como o Código de Trânsito Brasileiro.

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

