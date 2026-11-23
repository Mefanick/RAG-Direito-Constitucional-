# Ablação da Ponte Leiga — Fase 3.3

Registro objetivo do experimento de expansão de documento offline. Os números abaixo saem dos arquivos preservados, não de uma nova execução.

## Hipótese inicial

A busca densa compara a pergunta do cidadão com embeddings BAAI/bge-m3 do texto oficial da Constituição de 1988. A hipótese foi reduzir o abismo lexical com Document Expansion offline: uma linha de termos cotidianos por chunk, gravada à parte e concatenada só em `textos_busca`. O campo `textos` permaneceria a redação oficial entregue ao gerador, ao auditor e à interface. Sem fine-tuning e sem chamada extra de modelo no tempo da consulta.

## Evolução do gerador

1. `qwen2.5:3b` com prompt que pedia perguntas. O ensaio de três chunks produziu pergunta artificial, alucinação de regra no Art. 2º e vazamento de número de artigo. Essas três linhas foram apagadas do cache antes do lote.
2. `qwen2.5:3b` com pós-filtro que exigia uma palavra de quatro letras presente no chunk. O filtro cortou perguntas, e também cortou o sinônimo que não está escrito na lei. A linha restante era cópia do juridiquês.
3. `qwen3:8b` com `think` desligado e sem trava lexical. Os termos populares passaram a aparecer. O Art. 150, VI inverteu a imunidade de templos. O ADCT Art. 10, II leu «comissão» como cargo em comissão por contaminação do exemplo few-shot do Art. 37, II.
4. `qwen3:8b`, temperature 0,15, lista proporcional de 4 a 12 termos curtos, proteção da janela de 512 tokens do reranker ONNX, `texto_hash` de 12 hexadecimais e piso de 55 caracteres para chunk remissivo. O lote longo usou esta versão.

## Custo do lote

Modo enxuto: 457 chunks (arts. 5º–17, 145–162, 170–191, 196–214 e ADCT Art. 10). Desses, 447 receberam texto de ponte e 10 foram gravados vazios (cabeçalho curto, revogado ou remissão pura). O Art. 2º está fora do enxuto e já tinha ponte aprovada. O índice reconstruído ficou com 448 chunks em que `textos_busca` difere de `textos`.

Não houve linha em `modelos/ponte_leiga_erros.log`. Um chunk frio levou 122,06 s. A média dos 442 chunks seguintes foi 24,72 s. A soma da geração é 184 min de CPU.

## A/B com código congelado

A comparação usa só o `artigo_id` do chunk recuperado. Menção de outro artigo dentro do texto não conta. Fonte: `benchmarks/resultados_bateria_cega_baseline_sem_ponte.jsonl` e `benchmarks/resultados_bateria_cega_com_ponte.jsonl`.

| Métrica nas 12 inéditas | Sem ponte | Com ponte |
| --- | ---: | ---: |
| Artigo na 1ª passagem | 8/12 | 7/12 |
| Artigo no contexto final | 8/12 | 7/12 |
| Auditor com status FIEL | 9/12 | 8/12 |

Os casos 13 e 14 permaneceram em conversa livre, abaixo do corte 0,25 do reranker. Os casos 16 e 17 continuaram recuperando o artigo esperado. Não houve regressão de recuperação nessas duas regressões históricas.

## Causas

A diluição semântica em chunk curto derrubou o caso 02. No baseline, o Art. 5º, LXVII entrou na zona cinzenta com score 0,183 e a auditoria foi FIEL. Com a ponte, o mesmo caso caiu para conversa livre, sem chunk, o que implica topo abaixo de 0,12.

O sequestro por termo largo derrubou o caso 03. A ponte do Art. 156, II continha «imposto sobre imóveis». A busca sobre imunidade de templos, cujo dispositivo é o Art. 150, VI, passou a receber o Art. 156. O auditor ficou FIEL a esse chunk errado.

O teto do `qwen3:8b` com `think` desligado ficou entre dois objetivos que se atrapalham: não inventar regra e produzir vocabulário popular que não está no texto. Nas iterações anteriores, afrouxar o filtro inventou polaridade; apertar o filtro copiou o juridiquês.

## Decisão

O índice ativo `modelos/constituicao_vetorizada.pkl` volta à cópia `modelos/constituicao_vetorizada.pkl.bak_pre_33`, que não tem `textos_busca`. O índice enriquecido fica arquivado e não é apagado. O trabalho seguinte é do lado da consulta: detector de pergunta composta, tradutor da segunda passagem e regras da conversa livre.

## Artefatos preservados

- `modelos/constituicao_vetorizada.pkl.ab_com_ponte`
- `modelos/constituicao_vetorizada.pkl.bak_pre_33`
- `modelos/ponte_leiga_cache.jsonl`
- `modelos/ponte_leiga_run.log`
- `benchmarks/resultados_bateria_cega_baseline_sem_ponte.jsonl`
- `relatorios/relatorio_bateria_cega_baseline_sem_ponte.md`
- `benchmarks/resultados_bateria_cega_com_ponte.jsonl`
- `relatorios/relatorio_bateria_cega_com_ponte.md`
