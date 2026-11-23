# Dossiê de extração do algoritmo

Leitura do código em 23 de novembro de 2026. Sem inferência. Números saem dos JSON/JSONL citados. O solver da `LogisticRegression` e o `dtype` do tensor não estão escritos no fonte: onde isso importa, o dossiê diz que o código não fixa o valor.

## Bloco 1 — Vetor e fatiamento

Arquivo do índice: `modelos/constituicao_vetorizada.pkl`, 9.307.417 bytes (8,88 MB). O `indexar` grava `embeddings.cpu()` sem `.to(dtype)`. O encode do sentence-transformers, com `normalize_embeddings=True`, entrega vetor de norma 1. O índice ativo tem 1.772 linhas. `treinar_roteador.py` L152 exige `coef_.shape == (9, 1024)`, então cada vetor usado no treino tem 1.024 dimensões. Chaves gravadas em `indexar` L428–L436: `artigo_ids`, `textos`, `intencoes`, `embeddings`, `tokens_bm25`, `modelo`. Não há `textos_busca` no índice ativo.

`LIMITE_CARACTERES = 1200` em `src/rag/indexador_offline.py` L44. `ARTIGOS_DE_CONTROLE = {"97", "103", "103-A"}` em L45 muda só o rótulo de intenção para Controle de Constitucionalidade. Não impede o fatiamento.

```211:277:src/rag/indexador_offline.py
def _explodir(no, artigo_id, intencao, numero_artigo, forcar, id_artigo, contexto_caput):
    texto = " ".join(_dispositivos(no)).strip()
    if not texto:
        return []
    filhos = []
    for chave in ("incisos", "paragrafos", "alineas"):
        bloco = no.get(chave) or {}
        if isinstance(bloco, dict):
            filhos.extend(filho for filho in bloco.values() if isinstance(filho, dict))
    if len(texto) <= LIMITE_CARACTERES or not filhos:
        if contexto_caput:
            marcador = artigo_id[len(id_artigo):].lstrip(", ").strip()
            miolo = _sem_marcador_inicial(texto)
            if marcador:
                corpo = "{} (Contexto: {}) | {} - {}".format(id_artigo, contexto_caput, marcador, miolo)
            else:
                corpo = "{} (Contexto: {}) | {}".format(id_artigo, contexto_caput, miolo)
        elif texto.startswith("Art.") or texto.startswith(artigo_id):
            corpo = texto
        else:
            corpo = "{} - {}".format(artigo_id, _sem_marcador_inicial(texto))
        return [{"artigo_id": artigo_id, "texto": corpo, "intencao": intencao}]
    chunks = []
    caput = _texto_limpo(no.get("texto"))
    contexto_filhos = contexto_caput or (_resumo_caput(caput) if caput else "")
    if caput and not contexto_caput:
        corpo_caput = caput if caput.startswith("Art.") else "{} - {}".format(artigo_id, caput)
        chunks.append({"artigo_id": artigo_id, "texto": corpo_caput, "intencao": intencao})
    elif caput and contexto_caput:
        chunks.extend(_explodir(
            {"classe": no.get("classe"), "numero": no.get("numero"), "texto": no.get("texto")},
            artigo_id, intencao, numero_artigo, forcar, id_artigo, contexto_caput,
        ))
    for filho in filhos:
        classe = filho.get("classe") or []
        bruto = filho.get("numero") or []
        numero_filho = str(bruto[0]) if isinstance(bruto, list) and bruto else ""
        forcar_filho = forcar or (
            numero_artigo == "102" and (("inciso" in classe and numero_filho == "3") or "paragrafo" in classe)
        )
        intencao_filho = _intencao_do_filho(numero_artigo, filho, intencao, forcar_filho)
        ident = "{}, {}".format(id_artigo, _rotulo_filho(filho))
        chunks.extend(_explodir(filho, ident, intencao_filho, numero_artigo, forcar_filho, id_artigo, contexto_filhos))
    return chunks
```

A condição de parada é `len(texto) <= 1200 or not filhos`. O filho recebe o caput cortado em 280 caracteres (`_LIMITE_CONTEXTO_CAPUT`, L200) no prefixo `(Contexto: ...)`. O Art. 102, inciso 3 ou qualquer parágrafo dele, força a intenção de controle na chamada recursiva.

```43:52:src/rag/encoder.py
def gerar_embedding(texto: str, convert_to_tensor: bool = True) -> Any:
    if texto is None or not str(texto).strip():
        raise ValueError("Não há texto para vetorizar.")
    return obter_encoder().encode(
        str(texto),
        convert_to_tensor=convert_to_tensor,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
```

Normalização pedida à biblioteca, não escrita à mão:

$$
\hat{v} = \frac{v}{\|v\|_2}, \qquad \|v\|_2 = \sqrt{\sum_{k=1}^{1024} v_k^2}.
$$

`util.cos_sim` no retriever recebe vetores já normalizados. Para \(\|\hat{q}\|_2 = \|\hat{d}_i\|_2 = 1\),

$$
\cos(\hat{q}, \hat{d}_i) = \hat{q} \cdot \hat{d}_i.
$$

O código não reimplementa essa identidade. Ele chama `util.cos_sim(vetor, _EMBEDDINGS)[0]` em `_ranking_denso` L80.

## Bloco 2 — Roteador e soft boost

Hiperparâmetros escritos em `src/roteador/treinar_roteador.py` L50–L56:

```python
LogisticRegression(class_weight="balanced", max_iter=1000, C=1.0, random_state=42)
```

O fonte não passa `solver` nem `multi_class`. Validação: `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` em L123. O joblib só é gravado se o macro F1 out-of-fold for pelo menos 0,60 e nenhuma classe tiver F1 abaixo de 0,45 (L146–L149). O modelo final é reajustado no conjunto inteiro (L150–L151). Asserção: `coef_.shape == (9, 1024)` (L152).

Trava, L65–L87: carrega `PERGUNTAS` de `testes/avaliar_bateria_cega_fase33.py` e, se existir, o CSV de 300. Se alguma pergunta leiga normalizada cair nesse conjunto, `SystemExit`.

`avaliar_intencao`, L53–L81, íntegra no arquivo. O miolo numérico:

```python
probabilidades = _ROTEADOR.predict_proba(vetor)[0]
ordem = np.argsort(probabilidades)[::-1]
prob_top1 = float(probabilidades[ordem[0]])
prob_top2 = float(probabilidades[ordem[1]]) if len(ordem) > 1 else 0.0
margem = prob_top1 - prob_top2
confianca_alta = margem >= limiar_usado  # limiar padrão 0.15
```

O softmax não está neste arquivo. `predict_proba` do scikit-learn devolve a distribuição. A forma que corresponde a uma logística de 9 classes com \(W \in \mathbb{R}^{9 \times 1024}\) e viés \(b \in \mathbb{R}^{9}\), aplicada ao vetor linha \(x = \hat{q}\):

$$
z_c = W_{c,\cdot} x + b_c, \qquad
p_c = \frac{e^{z_c}}{\sum_{k=1}^{9} e^{z_k}}.
$$

$$
m = p_{(1)} - p_{(2)}, \qquad \text{confianca\_alta} \iff m \ge 0{,}15.
$$

`_ranking_denso`, L78–L91:

```python
cossenos = util.cos_sim(vetor, _EMBEDDINGS)[0]
ajustado = cossenos.clone()
if confianca_alta:
    for indice, rotulo in enumerate(_INTENCOES):
        if rotulo == roteamento.get("intencao"):
            ajustado[indice] = ajustado[indice] + boost_intencao
```

`boost_intencao` padrão em `buscar_contexto` L492 é `0.05`.

$$
s'(i) = \cos(\hat{q}, \hat{d}_i) + 0{,}05 \cdot \mathbf{1}[c_i = \hat{c} \land m \ge 0{,}15].
$$

A ordenação usa \(s'\). O valor guardado em `score_cosseno` continua sendo o cosseno sem o bônus (`cossenos`, não `ajustado`).

`limiar_cosseno: float = 0.45` está na assinatura de `buscar_contexto` L490 e é apagado na L512: `del limiar_cosseno`. O docstring L502–L503 diz que o argumento ficou para chamadas antigas e que o freio da lista é `limiar_reranker`.

## Bloco 3 — Composta e multi-query

`detectar_pergunta_composta`, L139–L151, íntegra:

```python
def detectar_pergunta_composta(pergunta: str) -> bool:
    texto = " ".join(str(pergunta or "").split())
    if not texto:
        return False
    baixo = _plano(texto)
    if baixo.count("?") >= 2:
        return True
    if _RE_SEGUNDO_QUESTIONAMENTO.search(baixo):
        return True
    if _RE_DUPLA_DEMANDA.search(baixo) and (baixo.count("?") >= 1 or _RE_INTERROGATIVA.search(baixo)):
        return True
    return len(texto.split()) >= 10 and _sinais(baixo) >= 2
```

`_plano` tira acento e baixa a caixa (L110–L113). `_sinais` (L128–L136) soma ocorrências de `_MARCAS_COMPOSICAO` (`e qual`, `além disso`, `papel do/da`, `também`, `além de`, `ao mesmo tempo`, `bem como`) e mais um ponto se houver `?` duplo, dois ou mais `e|ou|mas`, ou dois ou mais `qual|quais|como`.

Regexes L116–L125:

- segundo questionamento: vírgula, ponto e vírgula ou espaço, depois `e|mas|porem`, depois `qual|quais|como|quando|onde|quem|quanto|quantos|ate quando|em que prazo|existe|ha|pode`;
- dupla demanda: `alem disso`, `tambem quero|gostaria|pode|existe|qual`, `e tambem`, `ao mesmo tempo`, `por outro lado`.

`decompor_consulta` (L246–L261) pede no máximo 3 linhas ao modelo (`num_predict=120`). Se voltar menos de 2 frases, devolve `[]` e o pipeline faz busca única.

`fundir_subconsultas` L555–L652:

- um chunk (índice inteiro) fica com o maior `score_reranker` entre as subconsultas;
- `top_candidatos_brutos` é esse mapa ordenado, cortado em 5;
- para o contexto enviado, cada subconsulta contribui no máximo 3 itens com `status == "APROVADO"`;
- a escolha é round-robin até 8 (`len(escolhidos) >= 8`);
- esses 8 passam por `_montar_pais(..., composta=True)` e `deduplicar_chunks`.

Cada subconsulta, antes da fusão, chama `buscar_contexto` com `anexar_irmaos=False` (`pipeline.py` L434–L441). O padrão de `buscar_contexto` manda 8 candidatos ao reranker (`candidatos_rerank=8`).

## Bloco 4 — ONNX, sigmoide e semáforo

Quantização em `src/rag/otimizar_reranker_onnx.py` L101–L108: `quantize_dynamic`, `weight_type=QuantType.QInt8`, `per_channel=True`, `reduce_range=False`, `extra_options={"WeightSymmetric": True}`. Export ONNX opset 17, eixos dinâmicos de batch e sequência, saída só `logits` (`_Embrulho.forward` devolve `.logits`). O exemplo de export usa `max_length=64`. A janela 512 é decidida depois, em `carregar_onnx_para_producao` L187, se o eixo de sequência não for estático abaixo de 512. `batch_size=4` é o padrão de `reordenar_pares` e de `SessaoOnnx.predict`, não um argumento da quantização.

`_sigmoid` L68–L72:

```python
def _sigmoid(valor: float) -> float:
    if valor >= 0:
        return 1.0 / (1.0 + math.exp(-valor))
    expoente = math.exp(valor)
    return expoente / (1.0 + expoente)
```

$$
\sigma(z) =
\begin{cases}
\frac{1}{1+e^{-z}} & z \ge 0 \\
\frac{e^{z}}{1+e^{z}} & z < 0
\end{cases}
$$

As duas expressões são a mesma função. O ramo \(z < 0\) evita `exp` de um número grande positivo. Não há clamp.

`pontuar_pares` L244–L283: se `modo_escala == "logit_sigmoide_python"`, `predict` é chamado com `activation_fn=torch.nn.Identity()` e cada logit passa por `_sigmoid` uma vez. A ordem de pontuação pode ser por tamanho do texto; a lista devolvida volta à ordem original.

`SessaoOnnx.predict` L107–L135: tokeniza com `truncation=True`, `max_length=self.max_length`, corre `sessao.run`, fica com a primeira coluna do logit. Se `activation_fn` não for `Identity`, aplica essa função. No caminho de produção a sigmoide não entra aqui: entra em `pontuar_pares`.

`modo_pelo_topo`, `pipeline.py` L67–L72:

```python
def modo_pelo_topo(score: float) -> str:
    if score < 0.12:
        return "MODO_CONVERSA_LIVRE"
    if score < 0.25:
        return "MODO_RAG_ZONA_CINZENTA"
    return "MODO_RAG_ALTA_CONFIANCA"
```

$$
\mathrm{modo}(s) =
\begin{cases}
\text{livre} & s < 0{,}12 \\
\text{cinza} & 0{,}12 \le s < 0{,}25 \\
\text{alta} & s \ge 0{,}25
\end{cases}
$$

`_status` no retriever (L323–L328) usa os mesmos cortes com outros nomes: `APROVADO`, `CINZA`, `DESCARTADO`. Quem esvazia os artigos enviados ao modelo é o `if` de `executar_rag` L531–L537, não esse rótulo.

A/B em `benchmarks/resultados_ab_reranker.json`: PyTorch FP32 top 12, média 21,421 s; ONNX INT8 top 8, média 5,313 s. Razão \(21{,}421 / 5{,}313 = 4{,}032\). Os dois cenários registram `recall_5 = 1.0` e `bloqueio["0.25"] = 1.0`. O JSON não traz o inteiro 45. O docstring de `benchmarks/benchmark_latencia_reranker.py` diz que a amostra tem 45 perguntas.

## Bloco 5 — HyDE, anti-cópia, drift, fusão

Trecho que decide a segunda passagem, `pipeline.py` L486–L539. O histórico já foi zerado em L291–L293, então `_continuacao_curta` devolve falso.

```python
if top1 >= 0.25 and not continuacao:
    # tradutor pulado
else:
    consulta_traduzida, hyde_copiou = traduzir_para_juridico(...)
    if consulta_traduzida:
        hyde_cosseno, hyde_reranker = _medir_drift_hyde(...)
        hyde_rejeitado = rejeitar_hyde_por_drift(hyde_cosseno, hyde_reranker)
    if not consulta_traduzida or hyde_rejeitado:
        # segunda busca não corre
    else:
        # busca com a frase reescrita
        if top2 > top1:
            busca = busca_2
            top1 = top2
            passagem = 2
```

A troca exige `top2 > top1`, estrito.

`_medir_drift_hyde` L149–L154:

```python
cosseno = float(torch.dot(vetor_pergunta, vetor_hyde) / (vetor_pergunta.norm() * vetor_hyde.norm()))
return cosseno, float(reordenar_pares(pergunta, [hyde])[0])
```

Aqui o cosseno é calculado com as normas, não assumindo que o encode já normalizou. `gerar_embedding` pede normalização, então o denominador fica 1 se o tensor não foi alterado.

`rejeitar_hyde_por_drift` L154–L156:

```python
return float(reranker) < CORTE_HYDE_RERANKER or float(cosseno) < CORTE_HYDE_COSSENO
```

$$
\mathrm{rejeitar} \iff (s_{\mathrm{rerank}} < 0{,}002) \lor (s_{\cos} < 0{,}52).
$$

`fundir_top1_p1` L83–L120, condição de saída imediata:

```python
if (
    float(top1_p2) >= 0.25
    or float(top1_p2) < 0.12
    or float(top1_p1) < 0.12
    or float(top1_p2) < float(top1_p1)
):
    return artigos, False
```

Depois exige `artigo_id`, texto não vazio, `len(texto) <= 2200` e id ainda ausente. O chunk anexado recebe `origem = "fusao_p1"`.

Anti-cópia, `hyde_copiou_exemplo` L268–L286. Termos: regex `[a-z]{4,}` sobre o texto sem acento e em minúsculas, menos `_STOPWORDS`. Para cada saída de exemplo:

$$
J = \frac{|H \cap E|}{|H \cup E|}, \qquad
C = \frac{|H \cap E|}{|E|}, \qquad
\mathrm{copia} \iff \max(J, C) \ge 0{,}60
$$

e a interseção não é subconjunto dos termos da pergunta (`intersecao <= termos_pergunta` aborta aquele exemplo). Se as duas redações copiarem, `traduzir_para_juridico` devolve `("", True)` e a segunda busca não corre.

`_PROMPT_TRADUTOR` é a string única em L28–L52: reescrita declarativa, sem número de artigo, sem generalizar prazo de produto, infração, pena ou contrato, e competência no molde "compete à União...". Os quatro pares de `_EXEMPLOS_HYDE` L55–L72 são anonimato, confisco, décimo terceiro e atraso de aluguel com troca de fechadura.

## Bloco 6 — Pai, irmãos e geração

`_teto_dinamico` L181–L187:

```python
if composta:
    return min(8, max(top_k, 8))
if topo >= 0.85:
    return min(3, top_k)
return min(5, top_k)
```

`_anexar_irmaos` L190–L245. Só entra em fatia (`_e_fatia`) com texto de no máximo `_TAMANHO_CURTO = 450`. Anda para a esquerda e para a direita enquanto a base do dispositivo (`Art. N` ou `Art. N, § K`) for a mesma e o vizinho também for curto. Orçamento: `_EXTRA_SIMPLES = 700` ou `_EXTRA_COMPOSTA = 1200` (L100–L101, aplicado em L481). Origem do vizinho: `irmao_adjacente`.

`_tentar_pai` L412–L434. Teto do artigo `_TETO_PAI = 2200`. Teto do parágrafo sozinho `_TETO_PARAGRAFO = 1800`. Ordem: parágrafo mais caput curto, se couber em 2200; senão o artigo inteiro, se couber em 2200; senão só o parágrafo, se couber em 1800. Senão `None` e o chunk filho permanece.

`plano_geracao` L128–L165 descarta `composta` e `modo_raciocinio` com `del`. Think só se `usar_think` e `modelo_suporta_think`.

| Modo | think | num_predict | num_ctx | temperature |
|---|---|---:|---:|---:|
| puro | sim | 1200 | 2048 | 0,1 |
| puro | não | 450 | 2048 | 0,1 |
| qualquer RAG | sim | 1200 | 3072, ou 2048 se livre | 0,2, ou 0,5 se livre |
| livre | não | 360 | 2048 | 0,5 |
| alta ou cinza | não | 450 | 3072 | 0,2 |

`NUM_PREDICT_THINK_COMPOSTA = 1600` (L27) não é lido por `plano_geracao`.

`separar_raciocinio` L67–L89 tira, nesta ordem, `<think>...</think>` fechado, `<think>` aberto até o fim, e um `</think>` inicial sem abertura. `estourou_no_pensamento` L96–L98: caracteres não brancos do visível `< 20` e pensamento não vazio. `_com_diretiva_think` L101–L113 acrescenta `\n/no_think` ao último user quando o think está desligado e o modelo suporta think.

`extrair_telemetria` L186–L215:

$$
\mathrm{prefill\_s} = \frac{\texttt{prompt\_eval\_duration}}{10^{9}}, \qquad
\mathrm{decode\_s} = \frac{\texttt{eval\_duration}}{10^{9}}, \qquad
\mathrm{tok/s} = \frac{\texttt{eval\_count}}{\mathrm{decode\_s}}.
$$

Se `usar_think` é falso, a função força `think_s = 0` e `think_chars = 0`. Se é verdadeiro, `think_s` recebe o relógio medido fora dessa função (`think_s_medido`), não um subintervalo de `eval_duration`. A inclusão do think dentro de `eval_duration` é semântica do Ollama usada pelos gráficos (`escrita_util = max(0, decode_s - think_s)`). Esta função não faz essa subtração. Em linhas individuais do benchmark, `think_s` medido pode passar de `decode_s`.

Prompts de `montar_prompt` L264–L359:

- `MODO_LLM_PURO`: `PROMPT_LLM_PURO` (L49), sem fontes.
- `MODO_CONVERSA_LIVRE`: proíbe número de artigo, parágrafo, inciso, alínea e número de lei; permite o nome da lei (CDC, CTB, CLT); até dois parágrafos. O user é só a pergunta.
- `MODO_RAG_ZONA_CINZENTA`: diz que os trechos têm baixa confiança; se não responderem, conversar sem citar artigo. User: `Trechos possivelmente relacionados (baixa confiança):`.
- o `else` é a alta: usar só as fontes, citar no meio da frase, não começar com "Sim" quando a fonte é subconjunto. User: `Fontes:`.

O aviso de conversa livre não está no system. `prefixar_aviso_livre` (L36–L41) cola `AVISO_CONVERSA_LIVRE` no texto já gerado, e o pipeline faz isso antes de `auditar_citacoes` (L623–L625).

## Bloco 7 — Atalho e auditor

`detectar_atalho_trivial` L101–L124. `del historico` na primeira linha: o parâmetro não entra na decisão. Mais de 8 palavras devolve `None`. Termo jurídico (`_RE_JURIDICO`) ou continuação (`_RE_CONTINUACAO`) devolve `None`. Senão casa a frase inteira em saudação, agradecimento, despedida ou meta. A resposta é uma das frases de `_RESPOSTAS`, índice `sum(ord) % len`.

Regexes do auditor, `src/rag/auditor_citacoes.py` L11–L26, e a máquina de status L162–L169, estão íntegras no arquivo. Resumo fiel:

- `_RE_ARTIGO`: ADCT opcional, `Art.` ou `Artigo`, número, ordinal opcional.
- `_chave`: `ADCT Art. N` ou `Art. N`. O ordinal não entra na chave.
- `_janela`: 140 caracteres depois do artigo, ou até o próximo `Art.`.
- `_subdispositivos`: dentro da janela, `§ N`, `parágrafo único`, romano válido, alínea.
- `blob = artigo_id + "\n" + texto` de cada fonte.
- artigo citado cuja chave não está nas fontes vai para `artigos_inventados`.
- subdispositivo cujo marcador não aparece no blob daquele artigo vai para `nao_confirmados`.
- sem citação: `SEM_CITACAO`; artigo inventado: `ALUCINACAO_ARTIGO`; senão subdispositivo falho: `ALERTA_SUBDISPOSITIVO`; senão `FIEL`.
- `citacao_alucinada = bool(artigos_inventados or nao_confirmados)`.

## Bloco 8 — Três casos e a tabela de memória

### Caso 1 — via expressa

Fonte: `benchmarks/resultados_bateria_cega_fase33_drift_check_v4.jsonl`, id `17`. O benchmark de 20 perguntas não grava `margem_roteador`; este JSONL grava.

- Pergunta: usucapião rural, 40 hectares, 5 anos.
- Intenção: Ordem Econômica e Financeira. Margem 0,0899. `soft_boost_aplicado = false` (0,0899 < 0,15).
- `top1_score_bruto_p1 = 0,9942721437179391`. Passagem 2 não corre (`top1_score_bruto_p2 = null`).
- Primeiro artigo da lista: `Art. 191`, cosseno 0,7276086807250977, reranker 0,9942721437179391.
- `modo_resposta = MODO_RAG_ALTA_CONFIANCA`. `fusao_p1_p2_aplicada = false`.

Comparação de geração na suíte de 20, pergunta diferente (Q02, extradição do naturalizado), também passagem 1 e alta (`top1_score_p1 = 0,9687349816564775`, `top1_score_p2 = null`). Fonte: `benchmarks/benchmark_modelos_seminario.json`.

| Modelo | Auditoria | total_s | prefill_s | decode_s | think_s | tok/s | entrada | saída |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| qwen2.5:7b | SEM_CITACAO | 79,870 | 60,607 | 19,139 | 0 | 4,023 | 996 | 77 |
| qwen3:8b | FIEL | 215,745 | 68,995 | 146,623 | 91,669 | 3,383 | 998 | 496 |

Nesta linha do 8B, `think_s` 91,669 é menor que `decode_s` 146,623.

### Caso 2 — resgate

Fonte: o mesmo JSONL da v4, id `02`. Dívida de banco e prisão.

- Margem 0,06398, sem boost, busca global.
- `top1_score_bruto_p1 = 0,1834703481902695` (cinza, abaixo de 0,25, então o HyDE dispara).
- Reescrita: "é vedado ao Estado aplicar prisão por dívida de natureza civil ou trabalhista, salvo em caso de execução penal".
- `hyde_cosseno = 0,6295305490493774` (≥ 0,52). `hyde_reranker = 0,26391038182599563` (≥ 0,002). `hyde_rejeitado_por_drift = false`. `hyde_copiou_exemplo = false`.
- `top1_score_bruto_p2 = 0,6458067362751918` > p1, `passagem = 2`.
- Artigo vencedor: `Art. 5º, LXVII`, cosseno 0,6373100876808167, reranker 0,6458067362751918.
- Modo final: alta. `fusao_p1_p2_aplicada = false`, coerente com o código atual (`top1_p2 >= 0,25` recusa a fusão).

O id `05` do mesmo arquivo tem `fusao_p1_p2_aplicada = true` com `top1_score_bruto_p2 = 0,9208592920969351`. O `fundir_top1_p1` de hoje devolveria falso nesse número. O JSONL é anterior a essa restrição.

### Caso 3 — OOD e estouro

Q19, `benchmarks/benchmark_contexto_congelado_20.json`: notebook comprado há cinco dias. `top1_score_p1 = 0,0011759530797948495`, `top1_score_p2 = 0,002710297684554627`. Os dois ficam abaixo de 0,12. `artigos_recuperados = []`. `modo_rag = MODO_CONVERSA_LIVRE`. A reescrita fala em direito do consumidor e prazo legal.

Geração `qwen3:4b` dessa Q19 em `benchmark_modelos_seminario.json`: `auditoria = SEM_CITACAO`, resposta começa pelo aviso fixo, `think_chars = 3597`, `think_s = 129,655`, `estourou_no_think = false` (a resposta visível passou de 20 caracteres), `num_predict = 1200`, `num_ctx = 2048`, `temperature = 0,1` (o runner do benchmark força 0,1; o `plano_geracao` vivo usaria 0,5 na conversa livre sem think, ou 0,2 com think).

Estouro real do 4B, Q01 do mesmo JSON: `estourou_no_think = true`, `think_chars = 5003`, `think_s = 316,726`, `len(resposta) = 0`, `auditoria = SEM_CITACAO`, `total_s = 380,336`. Há 15 linhas do `qwen3:4b` com `estourou_no_think = true` nesse arquivo.

### Números para decorar

| Fato | Número | Fonte |
|---|---|---|
| ONNX contra FP32 | 5,313 s contra 21,421 s (4,032×) | `benchmarks/resultados_ab_reranker.json` |
| Recall@5 e bloqueio no corte 0,25, nos dois rerankers do A/B | 1,0 e 1,0 | o mesmo JSON |
| 12 inéditas, 1ª passagem | baseline 8, ponte 7 | jsonl `baseline_sem_ponte` e `com_ponte`, chave `recuperou_esperado_p1` |
| 12 inéditas, drift v4 | 11 | `drift_check_v4`, chave `recuperou_esperado_final` |
| Suíte de 20, FIEL nas 18 constitucionais | 4B 2, 7B 10, 8B 15 | `benchmark_modelos_seminario.json` |
| Estouros do 4B nas 20 | 15 | o mesmo arquivo |
| Médias de `total_s` nas 20 | 4B 275,741 s, 7B 80,059 s, 8B 230,367 s | médias das 20 linhas de cada modelo nesse JSON |

## Discrepâncias entre o pedido e o código

- O softmax da logística não é uma linha deste repositório. Está dentro de `predict_proba`.
- O código não nomeia o solver. Não dá para afirmar `lbfgs` a partir do fonte.
- `limiar_cosseno = 0.45` não participa de conta nenhuma.
- `deve_reforcar_apos_fora` não é chamada por `executar_rag`.
- A fusão registrada no id 05 da v4 não cabe na função `fundir_top1_p1` atual.
- `think_s` da telemetria não é calculado como subconjunto de `decode_s`.
- `NUM_PREDICT_THINK_COMPOSTA` não entra no plano.
- O inteiro 45 não está no JSON do A/B. Está no docstring do script da medição.
