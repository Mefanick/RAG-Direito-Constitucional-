<div align="center">

# Chat constitucional

Perguntas em linguagem comum, respostas com artigo da Constituição de 1988.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-8000-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Ollama](https://img.shields.io/badge/Ollama-local-000000?logo=ollama&logoColor=white)](https://ollama.com/download)
[![BGE-M3](https://img.shields.io/badge/Hugging%20Face-BGE--M3-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/BAAI/bge-m3)

`python interface.py`

</div>

Chat de recuperação sobre a Carta vigente. A busca usa 1.772 trechos vetorizados com BGE-M3, um roteador de 9 classes e um reranker ONNX INT8. Quem escreve é um Qwen local, no Ollama. Um auditor em Python confere se o artigo citado estava nas fontes.

| | |
|---|---|
| Entrada | `python interface.py` abre a janela, o Ollama na porta 11434 e a API em `http://127.0.0.1:8000` |
| Índice | Já está em `modelos/`. Não baixar de novo |
| Relatórios | `relatorios/` e `benchmarks/` |
| Origem | [`historico/amostra_chatbot_legal.py`](historico/amostra_chatbot_legal.py): 15 frases, TF-IDF e Naive Bayes |

## Índice

- [Subir o chat](#subir-o-chat)
- [Baixar dependências](#baixar-dependências)
- [Arquitetura](#arquitetura-que-se-firmou)
- [Resultado final](#resultado-final)
- [Onde está cada número](#onde-está-cada-número)
- [Linha do tempo](#linha-do-tempo)

## Subir o chat

Na pasta deste arquivo, com Python 3.12, Ollama e o BGE-M3 já no disco:

```powershell
python interface.py
```

## Baixar dependências

| Peça | Para que serve | Onde |
|---|---|---|
| Python 3.12 | API e janela | [python.org](https://www.python.org/downloads/) |
| `requirements.txt` | Torch, sentence-transformers, scikit-learn, ONNX Runtime, pywebview | [PyPI](https://pypi.org) |
| FastAPI e Uvicorn | Servidor em `127.0.0.1:8000`. Ainda não estão no `requirements.txt` | [FastAPI](https://pypi.org/project/fastapi/) · [Uvicorn](https://pypi.org/project/uvicorn/) |
| Ollama | Servidor dos modelos que escrevem | [ollama.com/download](https://ollama.com/download) |
| `qwen3:8b` | Padrão, com think | [ollama.com/library/qwen3](https://ollama.com/library/qwen3:8b) |
| `qwen2.5:7b` | Equilibrado, sem think | [ollama.com/library/qwen2.5](https://ollama.com/library/qwen2.5:7b) |
| `qwen3:4b` | Rápido, com think | [ollama.com/library/qwen3](https://ollama.com/library/qwen3:4b) |
| `BAAI/bge-m3` | Vetor da pergunta. Cai no cache do Hugging Face | [huggingface.co/BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3) |

O índice, o roteador e o ONNX INT8 já viajam em `modelos/`.

Cole isto no PowerShell, na pasta do projeto. O Python 3.12 precisa estar no PATH.

```powershell
python -m pip install -r requirements.txt fastapi uvicorn
winget install --id Ollama.Ollama -e --accept-package-agreements --accept-source-agreements
ollama pull qwen3:8b
ollama pull qwen2.5:7b
ollama pull qwen3:4b
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"
```

> [!TIP]
> Se o `winget` disser que o Ollama já está instalado, pule essa linha. Se `ollama` não for reconhecido, feche o terminal e abra de novo.

<details>
<summary>Comandos separados, se o bloco parar no meio</summary>

```powershell
python -m pip install -r requirements.txt fastapi uvicorn
```

```powershell
winget install --id Ollama.Ollama -e --accept-package-agreements --accept-source-agreements
```

```powershell
ollama pull qwen3:8b
```

```powershell
ollama pull qwen2.5:7b
```

```powershell
ollama pull qwen3:4b
```

```powershell
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"
```

O peso `BAAI/bge-reranker-v2-m3` só é necessário para **regerar** o ONNX. A pasta `modelos/bge_reranker_v2_m3_onnx_int8/` já contém o arquivo de produção.

```powershell
python -m pip install transformers
python -m src.rag.otimizar_reranker_onnx
```

</details>

## Arquitetura que se firmou

| Peça | Estado consolidado nos relatórios |
|---|---|
| Índice | 1.772 chunks da CF/88 vigente, inclusive ADCT, embeddings 1024. Artigos longos abrem por inciso acima de 1.200 caracteres. O Art. 60 cabe inteiro (1.163 caracteres). |
| Roteador | LogisticRegression sobre o mesmo BGE-M3. Evoluiu de 7 para 9 classes. Margem ≥ 0,15 aplica bônus de 0,05 no cosseno. Não há exclusão de capítulo. |
| Busca | Cosseno nos 1.772 chunks, rerank dos 8 primeiros com `bge-reranker-v2-m3` ONNX INT8, janela 512, uma sigmoide. Corte 0,25 (alta), 0,12–0,25 (cinza), abaixo de 0,12 (conversa livre). |
| Geração | Ollama local. Três modos: alta confiança, zona cinzenta e conversa livre. Auditor confere artigo e, quando a resposta desce ao inciso, o marcador. |
| Ponte leiga | Ensaio negativo. 448 chunks enriquecidos ficaram só no arquivo de ablação. O índice ativo voltou a não ter `textos_busca`. |
| HyDE | Segunda passagem só quando o topo da primeira fica abaixo de 0,25. Drift Guard recalibrado para cosseno 0,52 e reranker 0,002. `FORA_CF88` deixou de ser veto. |

## Resultado final

Suíte cega de 20 perguntas, o mesmo contexto para os três modelos. Relatório em [`relatorios/relatorio_benchmark_modelos.md`](relatorios/relatorio_benchmark_modelos.md).

| Modelo | Total médio | FIEL | Alerta | Alucinação | Sem citação | Estouro |
|---|---:|---:|---:|---:|---:|---:|
| qwen3:4b, think ligado | 276 s | 2 | 0 | 0 | 18 | 15 |
| qwen2.5:7b, direto | 80 s | 10 | 2 | 0 | 8 | 0 |
| qwen3:8b, think ligado | 230 s | 15 | 2 | 1 | 2 | 0 |

## Onde está cada número

| O que procurar | Onde |
|---|---|
| Baterias de 17 casos e a parcial de latência | [`relatorios/`](relatorios) e [`benchmarks/`](benchmarks) |
| Contexto congelado das 20 | [`benchmarks/benchmark_contexto_congelado_20.json`](benchmarks/benchmark_contexto_congelado_20.json) |
| 60 respostas | [`benchmarks/benchmark_modelos_seminario.json`](benchmarks/benchmark_modelos_seminario.json) |
| Comparativo escrito | [`relatorios/relatorio_benchmark_modelos.md`](relatorios/relatorio_benchmark_modelos.md) |
| Log da rodada das 23:07 | [`benchmarks/benchmark_modelos.log`](benchmarks/benchmark_modelos.log) |
| Ablação da ponte | [`relatorios/ablacao_ponte_leiga_fase33.md`](relatorios/ablacao_ponte_leiga_fase33.md) |
| Figuras | [`visualizacoes/graficos_seminario/`](visualizacoes/graficos_seminario) e [`visualizacoes/graficos_comparativos_modelos/`](visualizacoes/graficos_comparativos_modelos) |
| Prova de conceito | [`historico/amostra_chatbot_legal.py`](historico/amostra_chatbot_legal.py) |

## Linha do tempo

<details>
<summary>18 a 21 de novembro de 2026</summary>

## 18 de novembro de 2026

### 16:23 — Desempenho depois da injeção da Constituição

Canvas: `relatorio-roteador-hibrido.canvas.tsx`.

A Constituição entrou no treino do roteador. No teste de 26 casos a acurácia subiu de 50% para 61,5% (16/26, antes 13/26). O F1 macro foi de 0,32 para 0,39 e o F1 ponderado de 0,45 para 0,57. Três classes sem exemplos no teste continuaram em zero.

### 17:34 — Auditoria do teste ponta a ponta

Canvas: `relatorio-teste-integracao.canvas.tsx`.

Primeira leitura conjunta de dados, rótulos, roteador SVM, retriever e gerador. O limiar de margem do SVM era 0,5. O teste anti-alucinação ainda não existia: o trace não mostrava se o modelo tinha inventado artigo.

### 17:56 — Bateria depois da refatoração

Canvas: `relatorio-pos-refatoracao.canvas.tsx`.

Quatro consultas medidas por etapa. Cerca de 4 segundos do total não vinham do modelo nem do índice. O relatório descreve o modelo híbrido já em uso nessa altura.

## 19 de novembro de 2026

### 07:41 — Teste cego do roteador

Canvas: `relatorio-desempenho-benchmark.canvas.tsx`.

Roteador por classe, margem de probabilidade com filtro estrito, e se o artigo certo entra no topo. O cosseno separa pergunta constitucional de pergunta de fora. O canvas registra como o modelo foi escolhido.

### 12:31 — BGE-M3, BM25 e reranker

Canvas: `relatorio-mudancas-bge.canvas.tsx`.

Entram embedding denso BGE-M3, BM25 e um reranker. A ablação mostra a busca densa à frente do híbrido BM25+RRF (Recall@5 0,952 contra 0,944, número retomado no canvas de trajeto). O corte de 0,15 do reranker não separava pergunta de fora. Falhas de roteador e de ordem dos chunks continuam.

### 14:24 — Patch da busca densa

Canvas: `relatorio-patch-denso.canvas.tsx`.

Com o modelo quente, a média de quatro controles cai para 12,3 s. Furto (fora de escopo) fica em 10,6 s com lista vazia e LLM parado. Anonimato marca 0,985 no reranker. No corte 0,20, 96,7% das perguntas de fora são bloqueadas. Recall@1 0,933 e Recall@5 1,000.

### 15:42 — Reranker ONNX INT8

Canvas: `relatorio-onnx-int8.canvas.tsx`.

O cross-encoder PyTorch FP32 sai do caminho quente. ONNX INT8 nas 45 consultas: média quente 5,31 s, cerca de 4 vezes mais rápido que o FP32, Recall@5 1,000 igual ao FP32, e 100% de bloqueio fora de escopo no corte 0,25. O MiniLM fica de fora dessa configuração. O card posterior de medições corrige um mal-entendido: 42/45 era o MiniLM, não o ONNX. O ONNX no corte 0,25 é 45/45 (15/15 no top 5 e 30/30 bloqueados).

### 16:10 — Etapa 3, gerador e citações

Canvas: `relatorio-etapa3.canvas.tsx`.

Contrato do gerador e checagem de citação. Nas quatro consultas de integração o furto não chama o LLM (0,00 s de gerador). Os outros três batem no timeout de ligação de 2,02 s. Média das quatro: 10,20 s. Doze testes sem LLM passam. A auditoria das 20 perguntas ainda estava por rodar com o modelo no ar.

### 17:41 — Etapa 3 com o Qwen no ar

Canvas: `relatorio-etapa3-desempenho.canvas.tsx`.

Quinze perguntas constitucionais sem artigo inventado (15/15) e cinco fora de escopo barradas no reranker (5/5). Tempo médio total 51,9 s. Decode em CPU a 1,4 tok/s. O gargalo já é a geração, não a busca.

### 18:45 — 7B enxuto contra o 3B

Canvas: `relatorio-ab-qwen.canvas.tsx`.

`qwen2.5:3b` nas 20 perguntas: média 19,4 s e 5,0 tok/s. `qwen2.5:7b` otimizado: média 61,0 s. As duas rodadas ficam em 15/15 citações fiéis. O 3B ganha a demonstração pela latência, com a mesma fidelidade de citação nessa amostra.

## 20 de novembro de 2026

### 01:06 — Relatório técnico da Fase 2

Canvas: `relatorio-fase2.canvas.tsx`.

Mapa fechado do sistema no ar: 1.772 chunks, BGE-M3 de 1024 dimensões, corte 0,25, interface em `127.0.0.1:8000`. O modelo carregado nesse instante era `qwen2.5:3b` (uvicorn PID 6620, `ollama serve` PID 30088). O Art. 60 não está fatiado. Dois rótulos do índice não recebem o bônus do roteador. Os prompts literais dessa fase ainda pediam `FORA_CF88` ao tradutor e citação integrada no modo de alta confiança.

### 02:07 — Do classificador de 15 frases ao chat

Canvas: `relatorio-trajeto.canvas.tsx`.

Linha do tempo interna, da PoC até a Fase 3.1:

| Etapa | Decisão |
|---|---|
| PoC | 15 frases, TF-IDF, Naive Bayes, 3 classes. A intenção não é a resposta. |
| Corpus | Provas da OAB filtradas para constitucional. As classes passam a ser títulos da Carta. |
| Roteador clássico | TF-IDF + LinearSVC em joblib. Sem probabilidade nativa. |
| Roteador denso | LogisticRegression, 7 classes, coef (7, 1024). Margem ≥ 0,15. Em 270 perguntas constitucionais, 105 casos filtrados com 94,3% de acerto nesse subconjunto. No conjunto inteiro, acurácia 0,741 e F1 macro 0,747. |
| Índice | 1.772 chunks. |
| Busca densa | BM25+RRF perde: Recall@5 0,952 (densa) contra 0,944 (híbrido). |
| Reranker | Recall@1 sobe de 0,870 para 0,930. INT8 a 5,31 s contra 21,42 s do FP32. |
| Confiança baixa | Soft boost 0,05. Corte 0,25. Tributação e ADCT continuam alcançáveis mesmo sem classe própria no roteador. |
| Gerador | Recusa seca dá lugar a citação. 3B: 15/15 fontes, cerca de 19,8 s, contra cerca de 49 s do 7B otimizado. |
| Fase 3.1 | `num_ctx` 4096, think no qwen3, auditor de inciso. Precisão na frente da latência. |

Nesse canvas o roteador ainda é descrito com 7 classes. A expansão para 9 vem no dia seguinte.

### 16:34 — Fase 3.2, latência

Canvas: `relatorio-fase32.canvas.tsx`.

O modelo permanece `qwen3:8b`. Dez fios no Ollama (`num_thread` 10), janela do reranker continua 512, KV cache `q8_0`, flash attention. Atalho social: saudação curta não paga embedding nem LLM. O pensamento do qwen3 liga em pergunta composta e na zona cinzenta, e fica fora do balão. Art. 156, I e II entram na discussão de recuperação tributária.

### 17:49 — O que os testes mediram

Canvas: `relatorio-medicoes.canvas.tsx`.

Números de referência antes da bateria cega de 17:

- ONNX no corte 0,25: 45/45 (15/15 Recall@5 e 30/30 fora de escopo).
- `qwen2.5:3b` na auditoria de 20: 15/15 citações fiéis.
- Decode do `qwen3:8b` com 10 fios: 3,00 tok/s.
- Ponte leiga: só 3 de 1.772 chunks tinham frase gravada.

Ainda não havia taxa de 1ª passagem, status FIEL nem tempo ponta a ponta das inéditas. O roteador de 9 classes (coef 9 × 1024) já estava treinado com 127 questões da OAB e 225 perguntas leigas, sem corte de validação separado. A bateria de 15/17 ainda não tinha JSONL.

### 18:09 — Fase 3.3, correção antes do lote

Canvas: `relatorio-fase33-correcao.canvas.tsx`.

Validação do roteador de 9 classes em 5-fold: acurácia 0,764, macro F1 0,781. Nas 127 da OAB, acurácia 0,646. Nas 225 leigas, 0,831. Quando a margem passa de 0,15 (37,5% dos casos), a acurácia sobe para 97,0%. O modo enxuto da ponte tem 457 chunks. A bateria cega de 17 casos existe como roteiro, ainda sem execução. O card 42/45 deixa de ser atribuído ao ONNX.

### 18:34 — Ponte leiga com qwen3:8b

Canvas: `relatorio-ponte-qwen3.canvas.tsx`.

A ponte existe para acrescentar termos cotidianos ao chunk, sem substituir o texto oficial. O gerador passa a ser `qwen3:8b` com think desligado. No ensaio de cinco chunks, a média quente é 37,1 s. O ETA dos 441 chunks que ainda chamariam o modelo era 272 minutos. Duas das cinco linhas saíram com sentido invertido ou assunto trocado. O lote longo não foi autorizado.

### 18:41 — Polaridade e isolamento do exemplo

Canvas: `relatorio-ponte-polaridade.canvas.tsx`.

Duas linhas aprovadas permanecem. Três são apagadas e geradas de novo, com polaridade explícita e o exemplo isolado para não misturar palavras. Média quente dos dois chunks seguintes: 32,1 s. Nenhum vazamento de cargo comissionado ou de confisco nessas linhas. O cache ainda não está liberado para o lote.

### 18:49 — Descritores curtos

Canvas: `relatorio-ponte-descritores.canvas.tsx`.

Teto da linha sobe de 65 para 90 tokens. Temperature cai de 0,15 para 0,1. Um chunk quente leva 18,3 s. ETA dos 437 restantes: 133 minutos. O cache tem as cinco chaves, mas o índice 985 ainda perde o sujeito (“entre governos”).

### 23:12 — Baseline sem ponte, 17 casos

Canvas: `relatorio-baseline-sem-ponte.canvas.tsx`.

Primeira bateria cega completa no índice limpo. Das 12 inéditas, 8 recuperam o artigo já na 1ª passagem e 8 no contexto final. Nove das 12 são FIEL. Seis usam parent-document. O detector de pergunta composta não disparou nos casos que precisavam dele.

### 23:29 — Estrutura da ponte

Canvas: `relatorio-estrutura-ponte-leiga.canvas.tsx`.

Quatro peças: gerador da frase, filtro de chunk remissivo ou revogado, cache JSONL e aplicador que só reescreve o índice com `--com-ponte`. O modo enxuto percorre 457 chunks. O cache de ensaio tem 5 linhas. `textos_busca` ainda não existe no pkl de produção. A busca em produção continua sendo o texto oficial.

### 23:53 — Blindagem do lote

Canvas: `relatorio-ponte-blindagem.canvas.tsx`.

Dez chunks enxutos não chamam o modelo (piso de tamanho, revogado ou remissão pura). Nenhum dos 457 textos oficiais enxutos passa de 400 tokens (a janela do reranker é 512). O encaixe da ponte no reranker só encurta o prefixo oficial temporário, para o sufixo “Termos cotidianos” caber. Chunk quente desta rodada: 35,1 s. ETA dos 443 que faltam: 259 minutos. O índice 985 ainda não diz “entre governos”.

## 21 de novembro de 2026

### 05:31 — A/B da ponte

Canvas: `relatorio-ab-ponte.canvas.tsx`.

O lote enxuto rodou: 448 chunks com termos cotidianos, 442 quentes em 184 minutos. No índice enriquecido, a 1ª passagem cai de 8/12 para 7/12 e o auditor FIEL cai de 9/12 para 8/12. A ponte não melhorou o placar e tirou um acerto. O experimento fica arquivado. O índice ativo não permanece enriquecido.

### 13:10 — Rollback e correções da consulta

Canvas: `relatorio-rollback-fixes.canvas.tsx`.

O pkl ativo volta a ter 1.772 chunks e nenhuma chave `textos_busca`. Os 448 chunks enriquecidos ficam só no arquivo da ablação. Quatro correções, sem chamada ao Ollama: detector de pergunta composta, trava do tradutor contra falso `FORA_CF88`, conversa livre com 360 tokens e proibição de citar número, métrica estrita por `artigo_id` (não por substring do texto). A porta 8000 fica livre para a validação dos oito casos.

### 14:36 — Oito casos críticos

Canvas: `relatorio-fixes-parcial.canvas.tsx`.

Dos quatro alvos de recuperação, passam o caso 05 e o par 09/10. Os casos 09 e 10 viram pergunta composta, com multi-query e think, e trazem Art. 37 (XI e XVI) e Art. 62. Os casos 13 e 14 continuam em conversa livre, sem número de artigo. Os casos 03, 04 e 12 ainda não recuperam o artigo esperado. O tradutor ainda devolve jargão e, no trabalho, `FORA_CF88`.

### 15:46 — HyDE no estilo da Constituição

Canvas: `relatorio-hyde-parcial.canvas.tsx`.

A segunda passagem deixa de vetar com `FORA_CF88` e reescreve em uma ou duas frases literais, sem número de artigo. Nos cinco casos medidos, 03, 04 e 12 recuperam o artigo e saem FIEL. O caso 13 (consumo) fica em conversa livre. O caso 14 (trânsito) sobe a 0,893, entra em alta confiança e sai da conversa livre: a reescrita virou vedação tributária.

### 15:50 — HyDE, testes curtos e âncora

Canvas: `relatorio-hyde-ancora.canvas.tsx`.

O mesmo resultado dos cinco casos, com a proposta de testar só o subconjunto afetado em vez dos 17, e um prompt-âncora do projeto para o agente. Topo do caso 13 na segunda busca: 0,003. Topo do caso 14: 0,893.

### 16:39 — Drift Guard, varredura só de recuperação

Canvas: `relatorio-drift-guard.canvas.tsx`.

O prompt ganha a regra de não trocar de domínio. Depois da reescrita, o pipeline mede cosseno BGE-M3 e sigmoide do reranker entre a pergunta e a frase. Corte inicial: reranker abaixo de 0,08 ou cosseno abaixo de 0,50 descarta a segunda passagem. A varredura `--so-retriever` das 17 leva 367 s e não gera resposta final. Placar: 10/12 inéditas. O caso 14 é rejeitado (cosseno 0,491, reranker 0,000) e fica livre. O mesmo corte rejeita os casos 03 (reranker 0,049) e 04 (0,006), que na rodada HyDE anterior tinham achado o Art. 150. O caso 05 copia o exemplo de confisco, é rejeitado, e o Art. 155, I permanece pela primeira passagem. O caso 12 recupera o Art. 7º, XIII, sem o XVI no top 8. O caso 02 sobe a alta confiança (0,495).

### 16:40 — Drift Guard v2

Canvas: `relatorio-drift-check-v2.canvas.tsx`.

Entra um quarto exemplo, de aluguel, para preservação de domínio fora da Constituição, a frase “nunca copie os exemplos”, e uma trava local de sobreposição (Jaccard ou cobertura ≥ 0,60). O corte passa a cosseno &lt; 0,52 ou reranker &lt; 0,002. A varredura leva 462 s. A trava anti-cópia não dispara em nenhum dos 17. Placar 11/12. Os casos 03 e 04 voltam (Art. 150, VI a 0,403 e Art. 150, III a 0,597). O caso 05 troca o Art. 155 pelo Art. 150: a reescrita “é vedado cobrar tributos sobre doação” marca 0,348 e apaga a primeira passagem, que já tinha o Art. 155, I a 0,130. Os casos 13 e 14 continuam livres. O portão da bateria final (`fase33_final`) fica reprovado.

### 17:22 — Drift Guard v3

Canvas: `relatorio-drift-check-v3.canvas.tsx`.

A instrução deixa de privilegiar “é vedado” e ganha três moldes (competência, proibição, garantia) mais um quinto exemplo, de emissão de moeda. As reescritas que abrem com “é vedado” caem de 7/8 para 4/8. A varredura leva 568 s. O furo muda do caso 05 para o caso 12: o 05 volta ao Art. 155, I porque a segunda passagem ficou em 0,041, e o 12 cai para conversa livre a 0,054, sem o Art. 7º. Os casos 03 e 04 mantêm o Art. 150, mas descem de alta para cinza (0,179 e 0,148). O caso 04 deixa de ser vedação e repete a pergunta. Portão de novo em 11/12, reprovado.

### 17:45 — Drift Guard v4

Canvas: `relatorio-drift-check-v4.canvas.tsx`.

O prompt volta ao texto enxuto da v2, com os quatro exemplos, mais uma frase: pergunta de competência escreve “compete à…”, nunca “é vedado…”. A fusão protetora guarda o top-1 da primeira passagem quando a segunda vence e a primeira já estava na zona cinzenta. A varredura leva 496 s. Placar ainda 11/12. O furo agora é o caso 03: a frase de competência puxa o Art. 156 a 0,987, no lugar do Art. 150, VI. A primeira passagem estava em 0,006, abaixo de 0,12, e a fusão não tinha o que guardar. O caso 05 recupera o Art. 155 em alta (0,921) e a fusão acrescenta o Art. 147, que era o top-1 da primeira passagem a 0,130. O caso 12 volta à alta (0,494) com o Art. 7º, XIII, ainda sem o XVI. O caso 04 fica em cinza (0,222) com o Art. 150, III. O caso 02 sobe a 0,646. Livres, atalho e regressões (Art. 177 e Art. 191) passam. O índice ativo permanece com 1.772 textos e sem `textos_busca`. O portão `fase33_final` continua reprovado por causa do caso 03. A arquitetura de recuperação é congelada nesse estado.

### 18:27 — Parte 1, latência

Canvas: `relatorio-parte1-velocidade.canvas.tsx`.

O think deixa de ligar sozinho na zona cinzenta e na pergunta composta. Vira interruptor, desmarcado por padrão. Sem think, o RAG pede 450 tokens e a conversa livre 360. Com think, 1.200. O `num_ctx` do RAG cai de 4.096 para 3.072. Conversa livre e chamadas auxiliares usam 2.048. O histórico some do prompt: cada chamada ao Ollama leva só o system e a pergunta atual. A fusão deixa de injetar o top-1 fraco quando a segunda passagem já está em alta confiança, para não repetir o Art. 147 do caso 05.

Três casos medidos com geração, contra a rodada `fase33_fixes_parcial` em que o think estava ligado:

| Caso | Antes | Agora | Decode | Tokens de saída |
|---|---:|---:|---|---|
| 09 | 555 s | 471 s | 251 s → 144 s | 602 → 358 |
| 10 | 472 s | 314 s | 212 s → 54 s | 559 → 138 |
| 01 | sem essa base | 295 s | 51 s | 143 |

O `think_s` dos três ficou em 0. A velocidade de decode continuou entre 2,5 e 2,8 tok/s. O ganho é o raciocínio que deixou de ser escrito. O prefill segue caro: 95 s, 197 s e 165 s. No caso 09 o prompt tinha 6.892 caracteres e 2.070 tokens, dentro dos 3.072. O caso 09 recuperou Art. 37, XI e XVI, com alerta de subdispositivo. O caso 10 ficou FIEL no Art. 62. O caso 01 ficou FIEL no Art. 5º, XI.

</details>

## O que veio depois do último canvas

Estes passos estão nesta conversa e ainda não têm canvas próprio.

- Seletor de três modelos na API e na interface: `qwen3:4b` (rápido, com think), `qwen2.5:7b` (equilibrado, sem chave `think`) e `qwen3:8b` (padrão, com think). Troca de modelo envia `keep_alive: 0` ao anterior. Modo LLM puro pula busca, HyDE e auditor.
- `qwen3:4b` foi baixado (2,5 GB) e o catálogo ao vivo passou a marcá-lo como instalado.
- O template desse modelo abre `<think>` mesmo com `think: false`. Uma consulta de extradição devolveu o raciocínio em inglês no balão (“Okay, let's tackle…”), cortado em “Wait,”, embora `think_chars` tenha sido registrado como 0. O Art. 5º, LI foi recuperado e o auditor marcou FIEL. Total 135 s, prefill 4,6 s, decode 102 s, 4,4 tok/s.
- O benchmark de 20 perguntas para juiz externo rodou de 19:42 a 23:07 (PID 30072). As 60 gerações fecharam sem erro de rede. O relatório comparativo está em `relatorios/relatorio_benchmark_modelos.md`. No mesmo contexto congelado, o `qwen3:8b` com think ficou FIEL em 15 de 20 (média 230 s), o `qwen2.5:7b` sem think em 10 de 20 (média 80 s, nenhuma alucinação de artigo) e o `qwen3:4b` com think em 2 de 20 (média 276 s, 15 estouros de orçamento dentro do raciocínio). A fase A acertou o artigo esperado em 16 das 20; Q08, Q09, Q10 e Q16 ficaram incompletos para os três modelos. Q19 e Q20 permaneceram em conversa livre.

### 23:07 — Bateria final dos três modelos

Relatório: `relatorios/relatorio_benchmark_modelos.md`. Dados: `benchmarks/benchmark_modelos_seminario.json` e `benchmarks/benchmark_contexto_congelado_20.json`.

| Modelo | Total médio | FIEL | Alerta | Alucinação | Sem citação | Estouro |
|---|---:|---:|---:|---:|---:|---:|
| qwen3:4b, think ligado | 276 s | 2 | 0 | 0 | 18 | 15 |
| qwen2.5:7b, direto | 80 s | 10 | 2 | 0 | 8 | 0 |
| qwen3:8b, think ligado | 230 s | 15 | 2 | 1 | 2 | 0 |

## Onde está cada número

| O que procurar | Onde |
|---|---|
| Narrativa visual, na ordem acima | pasta `canvases` citada no início |
| Baterias 17 casos e a parcial de latência | `relatorios/relatorio_bateria_cega_*.md` e `benchmarks/resultados_bateria_cega_*.jsonl` |
| Contexto congelado das 20 | `benchmarks/benchmark_contexto_congelado_20.json` |
| Respostas dos três modelos, 60/60 | `benchmarks/benchmark_modelos_seminario.json` |
| Comparativo da bateria final | `relatorios/relatorio_benchmark_modelos.md` |
| Log da rodada concluída às 23:07 | `benchmarks/benchmark_modelos.log` |
| Ablação da ponte | `relatorios/ablacao_ponte_leiga_fase33.md` e o pkl de ablação, fora do índice ativo |
| Figuras do seminário e comparativos | `visualizacoes/graficos_seminario/` e `visualizacoes/graficos_comparativos_modelos/` |
| Prova de conceito inicial | `historico/amostra_chatbot_legal.py` |
#   R A G - D i r e i t o - C o n s t i t u c i o n a l - 
 
 