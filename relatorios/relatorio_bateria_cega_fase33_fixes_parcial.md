# Bateria cega da Fase 3.3 — fase33_fixes_parcial

## Resumo executivo

Perfil fase33_fixes_parcial. Este relatório audita 15 perguntas inéditas e 2 regressões históricas. O histórico de cada chamada fica vazio. As três colunas do placar são independentes.

| Métrica | Resultado |
| --- | --- |
| Recuperação na 1ª passagem (12 inéditas) | 3/12 |
| Artigo esperado recuperado (12 inéditas) | 3/12 |
| Auditoria FIEL (12 inéditas) | 3/12 |
| Recuperação na 1ª passagem (2 regressões) | 0/2 |
| Auditoria FIEL (2 regressões) | 0/2 |
| Fora de escopo sem artigo inventado | 2/2 |
| Atalho social abaixo de 0,1 s | 0/1 |
| Retriever médio (s) | 36.64 |
| Prefill médio (s) | 80.35 |
| Pensamento médio (s) | 0.00 |
| Gerador médio (s) | 214.75 |
| Total médio (s) | 273.49 |

## Placar

| Caso | 1. Artigo na 1ª passagem | 2. Auditor FIEL | 3. Checklist de revisão humana |
| --- | --- | --- | --- |
| 01 LEIGO / EXCECAO | não | pendente | Art. 5º, XI: ordem judicial só de dia; à noite, flagrante, desastre ou socorro. |
| 02 LEIGO / EXCECAO | não | pendente | Art. 5º, LXVII: vedada a prisão civil por dívida, com as ressalvas do próprio inciso. |
| 03 TRIBUTACAO / LEIGO | não | SEM_CITACAO | Art. 150, VI, b: imunidade dos templos. Classe Tributação e Orçamento. |
| 04 TRIBUTACAO / PRAZO | não | ALERTA_SUBDISPOSITIVO | Art. 150, III, b e c: anterioridade anual e nonagesimal, com exceções. |
| 05 TRIBUTACAO / COMPETENCIA | não | sim | Art. 155, I: Estados e Distrito Federal. |
| 06 ADCT / LEIGO | não | pendente | ADCT, Art. 10, II, b: da confirmação da gravidez até cinco meses após o parto. |
| 07 PARENT-DOC / NUMERO | não | pendente | Art. 14, § 3º, VI, a: 35 anos. |
| 08 PARENT-DOC / INCISOS | não | pendente | Art. 12, § 4º, fiel ao texto vigente recuperado, sem inciso inventado. |
| 09 COMPOSTA / MULTI-HOP | sim | sim | Art. 37, XVI, a e Art. 37, XI. |
| 10 COMPOSTA / MULTI-HOP | sim | sim | Art. 62, § 1º, I, b e Art. 62, § 3º. |
| 11 ORDEM SOCIAL / LEIGO | não | pendente | Art. 199: livre à iniciativa privada; § 2º veda recursos públicos a entidades com fins lucrativos. |
| 12 TRABALHO / LEIGO | não | SEM_CITACAO | Art. 7º, XIII e XVI: 8 horas, 44 semanais e hora extra de pelo menos 50%. |
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

- Intenção: Tributação e Orçamento (margem 0.22761961674172612)
- modo_busca: densa_com_boost
- classe: SIMPLES
- passagem: 2 | tradutor: Imunidade tributária da igreja e competência tributária da prefeitura sobre o IPTU. | sub-consultas: []
- Modo final: MODO_CONVERSA_LIVRE
- Entregue ao LLM: (nenhum)
- Checklist humano: Art. 150, VI, b: imunidade dos templos. Classe Tributação e Orçamento.
- Auditoria: {"status": "SEM_CITACAO", "artigos_citados": [], "subdispositivos_citados": [], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 30.76 | prefill 14.49 | thinking n/d | gerador 78.93 | total 190.13

Resposta integral:

A prefeitura pode cobrar IPTU de uma igreja, desde que essa instituição possua imóvel imóvel em território municipal e esteja em situação de posse legal. O IPTU é um tributo municipal que incide sobre a propriedade imobiliária, e sua cobrança é prevista no Código Tributário Nacional, que estabelece as regras gerais sobre tributos no Brasil. No entanto, em alguns casos, instituições religiosas podem ter benefícios fiscais ou isenções, dependendo da legislação municipal e das normas específicas aplicáveis em cada cidade. É importante ressaltar que o tema não foi localizado na base constitucional carregada, e as informações apresentadas são baseadas em princípios gerais do direito tributário brasileiro.

### 04 — TRIBUTACAO / PRAZO

Pergunta: O governo pode criar um imposto hoje e começar a cobrar na semana que vem?

Esperado: Art. 150, III, b e c: anterioridade anual e nonagesimal, com exceções.

- Intenção: Tributação e Orçamento (margem 0.06024994261951566)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 2 | tradutor: Princípio da anterioridade e competência tributária. | sub-consultas: []
- Modo final: MODO_RAG_ZONA_CINZENTA
- Entregue ao LLM: Art. 37, XVIII [reranker]; Art. 37, XXII [reranker]; Art. 153, § 2º [reranker]
- Checklist humano: Art. 150, III, b e c: anterioridade anual e nonagesimal, com exceções.
- Auditoria: {"status": "ALERTA_SUBDISPOSITIVO", "artigos_citados": ["Art. 153"], "subdispositivos_citados": ["Art. 153, § 2º, I", "Art. 153, § 1º"], "artigos_inventados": [], "subdispositivos_nao_confirmados": ["Art. 153, § 1º"]}
- Tempos (s): retriever 14.65 | prefill 87.64 | thinking n/d | gerador 324.92 | total 352.96

Resposta integral:

A Constituição Federal de 1988 não estabelece um prazo específico para a criação e implementação de impostos. No entanto, o art. 153, § 2º, inciso I, determina que os impostos devem ser criados com base em critérios de generalidade, universalidade e progressividade, mas não menciona limites temporais para sua instituição. 

A criação de um imposto exige a tramitação e aprovação por meio da Lei, conforme previsto no art. 153, § 1º, que atribui à União o poder de instituir impostos. A implementação prática, como a cobrança, depende da legislação complementar e da capacidade administrativa do Poder Executivo, mas não pode ser feita em um prazo tão curto quanto uma semana, pois envolve processos legislativos e técnicos. 

Portanto, **não é possível** que o governo crie e comece a cobrar um imposto em um período tão breve, pois a Constituição exige a formalização legal e a observância de princípios como legalidade e publicidade, que demandam tempo para serem cumpridos.

### 05 — TRIBUTACAO / COMPETENCIA

Pergunta: Se eu receber um terreno de doação em vida, quem cobra o imposto sobre essa doação: a Prefeitura, o Estado ou a União?

Esperado: Art. 155, I: Estados e Distrito Federal.

- Intenção: Tributação e Orçamento (margem 0.06608776840299713)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 2 | tradutor: Competência tributária da União, Estado ou Município sobre imposto sobre doação de terreno. | sub-consultas: []
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 155, § 1º (2 filhos); Art. 147 (1 filhos); Art. 157 (1 filhos); Art. 155, I [reranker]; Art. 155 [irmao_adjacente]; Art. 155, II [irmao_adjacente]; Art. 155, III [irmao_adjacente]
- Checklist humano: Art. 155, I: Estados e Distrito Federal.
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 155"], "subdispositivos_citados": ["Art. 155, I, \"a\"", "Art. 155, I, II"], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 37.61 | prefill 121.64 | thinking n/d | gerador 199.46 | total 269.14

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas a doações em vida, e o imposto sobre essa doação é cobrado pelo Estado ou pelo Distrito Federal, conforme o domicílio do doador, conforme previsto no art. 155, I, alínea a, que estabelece que "se o doador tiver domicílio ou residência no exterior" a competência é regulada por lei complementar. No entanto, se o doador tiver domicílio ou residência no Brasil, o imposto sobre a doação de terreno será cobrado pelo Estado onde o doador tem domicílio, ou pelo Distrito Federal, conforme previsto no art. 155, I, inciso II. A Prefeitura e a União não têm competência para cobrar esse imposto, salvo em casos específicos previstos em lei complementar.

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
- passagem: 1 | tradutor: None | sub-consultas: ['Art. 37, X da Constituição Federal estabelece que a remuneração do servidor público não poderá ultrapassar o limite máximo estabelecido em lei.', 'Art. 37, XI determina que o servidor público não poderá acumular cargos, funções ou empregos que exijam exercício simultâneo de atividades de responsabilidade pública.', 'Art. 37, XII prevê que o servidor público não poderá acumular cargo de professor com outro cargo de professor na mesma rede pública.']
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 37, § 10º (2 filhos); Art. 39, § 5º (2 filhos); Art. 37, XI [reranker]; Art. 37, XVI [reranker]; Art. 37, X [reranker]; Art. 37, XVII [reranker]; Art. 37, XIV [reranker]; Art. 37, XII [irmao_adjacente]; Art. 37, XIII [irmao_adjacente]
- Checklist humano: Art. 37, XVI, a e Art. 37, XI.
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 37"], "subdispositivos_citados": ["Art. 37, XVI", "Art. 37, XI"], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 85.42 | prefill 211.65 | thinking n/d | gerador 466.27 | total 554.75

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas aos servidores públicos que acumulam cargos de professor, conforme Art. 37, XVI, alínea **a**, que permite a acumulação de dois cargos de professor, desde que haja compatibilidade de horários. O limite máximo de remuneração é estabelecido no Art. 37, XI, que determina que a remuneração e os proventos dos ocupantes de cargos públicos não podem exceder o subsídio mensal em espécie dos Ministros do Supremo Tribunal Federal, aplicando-se como limite, nos Municípios, o subsídio do Prefeito; nos Estados e no Distrito Federal, o subsídio mensal do Governador no âmbito do Poder Executivo, o subsídio dos Deputados Estaduais e Distritais no âmbito do Poder Legislativo e o subsídio dos Desembargadores do Tribunal de Justiça, limitado a noventa inteiros e vinte e cinco centésimos por cento do subsídio mensal dos Ministros do Supremo Tribunal Federal. Não há base para generalizar para outros tipos de cargos ou remunerações.

### 10 — COMPOSTA / MULTI-HOP

Pergunta: O Presidente da República pode editar medida provisória sobre direito penal, e qual é o prazo máximo de vigência de uma medida provisória antes de perder a eficácia?

Esperado: Art. 62, § 1º, I, b e Art. 62, § 3º.

- Intenção: Organização dos Poderes (margem 0.1468399415376374)
- modo_busca: multi_query
- classe: COMPOSTA
- passagem: 1 | tradutor: None | sub-consultas: ['Art. 62. § 5º. A medida provisória não poderá conter norma que torne penal ou aumente a pena prevista em lei.', 'Art. 62. § 6º. A medida provisória terá validade de sessenta dias, podendo ser convertida em lei antes da expiração do prazo.']
- Modo final: MODO_RAG_ALTA_CONFIANCA
- Entregue ao LLM: Art. 62, § 1º (2 filhos); Art. 62, § 6º (2 filhos); Art. 62, § 5º (2 filhos); Art. 62, § 3º (2 filhos); Art. 62, § 2º (2 filhos); Art. 62, § 7º (2 filhos)
- Checklist humano: Art. 62, § 1º, I, b e Art. 62, § 3º.
- Auditoria: {"status": "FIEL", "artigos_citados": ["Art. 62"], "subdispositivos_citados": ["Art. 62, § 1º, I", "Art. 62, § 3º"], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 72.76 | prefill 186.23 | thinking n/d | gerador 398.27 | total 471.79

Resposta integral:

Nas fontes recuperadas, a regra aplica-se apenas a **medidas provisórias sobre direito penal**, vedadas expressamente no **Art. 62, § 1º, I, b** da Constituição. O Presidente da República **não pode editar medida provisória** sobre matéria relativa ao direito penal, processual penal e processual civil.  

Quanto ao prazo máximo de vigência, **Art. 62, § 3º** estabelece que as medidas provisórias perderão eficácia **após sessenta dias** de sua publicação, **salvo prorrogação** prevista no **§ 7º**, que permite uma única prorrogação por igual período. Portanto, o prazo máximo de vigência é de **120 dias** (60 + 60), desde que a medida provisória não seja convertida em lei.  

Não há base para generalizar para outras matérias ou prazos além dos explicitamente mencionados nas fontes.

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

- Intenção: Ordem Social (margem 0.011335789128238516)
- modo_busca: densa_global
- classe: SIMPLES
- passagem: 1 | tradutor: None | sub-consultas: []
- Modo final: MODO_CONVERSA_LIVRE
- Entregue ao LLM: (nenhum)
- Checklist humano: Art. 7º, XIII e XVI: 8 horas, 44 semanais e hora extra de pelo menos 50%.
- Auditoria: {"status": "SEM_CITACAO", "artigos_citados": [], "subdispositivos_citados": [], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 16.98 | prefill 14.08 | thinking n/d | gerador 87.14 | total 136.22

Resposta integral:

No Brasil, é proibido que o patrão obrigue alguém a trabalhar 10 horas por dia sem pagar nada a mais, já que isso viola as normas trabalhistas e constitucionais que protegem os direitos do trabalhador. De acordo com o Código Trabalhista, o horário de trabalho diário não pode ultrapassar oito horas, sendo permitido um horário extra de até duas horas, desde que haja compensação ou pagamento de horas extras. Além disso, a Constituição Federal garante ao trabalhador o direito à remuneração pelo tempo de serviço e à proteção contra condições de trabalho que possam prejudicar sua saúde ou segurança.

Obrigar alguém a trabalhar além do limite legal sem compensação ou pagamento é ilegal e pode resultar em multas, responsabilização civil e até penal. O trabalhador tem direito a receber remuneração proporcional ao tempo trabalhado e a não ser submetido a condições que comprometam seu bem-estar. O tema não foi localizado na base constitucional carregada.

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
- Tempos (s): retriever 6.55 | prefill 3.59 | thinking n/d | gerador 85.61 | total 98.81

Resposta integral:

Sim, caso você tenha comprado um celular pela internet e se arrependido da compra dentro do prazo legal, a loja pode ser obrigada a devolver o dinheiro, desde que você solicite a devolução dentro do prazo estabelecido pela legislação brasileira. De acordo com o Código de Defesa do Consumidor, o consumidor tem direito a arrependimento e devolução do produto em até 7 dias corridos, contados a partir do momento em que o produto foi entregue. Nesse período, você pode solicitar a devolução do dinheiro ou a troca do produto, desde que o item esteja em perfeito estado e não tenha sido utilizado.

É importante lembrar que esse direito de arrependimento aplica-se a compras feitas por meio de meios eletrônicos, como internet, e é um dos mecanismos de proteção ao consumidor previstos na legislação. Se a loja recusar a devolução, você pode procurar a Procon ou recorrer judicialmente para garantir seus direitos. O tema não foi localizado na base constitucional carregada.

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
- Auditoria: {"status": "SEM_CITACAO", "artigos_citados": [], "subdispositivos_citados": [], "artigos_inventados": [], "subdispositivos_nao_confirmados": []}
- Tempos (s): retriever 28.39 | prefill 3.45 | thinking n/d | gerador 77.43 | total 114.12

Resposta integral:

Se você acidentemente bater no carro de alguém no trânsito, o valor da multa depende de vários fatores, como a gravidade do dano, a responsabilidade envolvida e a legislação aplicável. Em geral, a responsabilidade pelo acidente é determinada por meio de uma análise de culpa, que pode envolver a aplicação do Código de Trânsito Brasileiro (CTB) e da legislação civil. A multa pode variar conforme a gravidade do dano, podendo incluir multas administrativas, reparação civil e, em alguns casos, responsabilização criminal.

É importante lembrar que, mesmo que o acidente tenha ocorrido por acidente, você ainda pode ser obrigado a reparar os danos causados ao outro veículo, seja através de indenização ou reparação direta. Recomenda-se sempre procurar um profissional, como um advogado ou uma seguradora, para entender melhor suas obrigações e os possíveis encargos legais.

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

