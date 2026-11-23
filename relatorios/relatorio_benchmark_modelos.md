# Benchmark final dos três modelos

21 de novembro de 2026, 19:42–23:07. Vinte perguntas, o mesmo contexto RAG congelado, três geradores em sequência. Sessenta respostas, zero erros de rede. Arquivos: `benchmarks/benchmark_contexto_congelado_20.json`, `benchmarks/benchmark_modelos_seminario.json` e `benchmarks/benchmark_modelos.log`.

O contexto foi produzido uma vez com a recuperação da v4. O `qwen3:8b` entrou só no HyDE e na decomposição. Depois o BGE-M3 e o ONNX foram liberados. Cada modelo leu os mesmos `system_prompt` e `user_prompt`. `qwen3:4b` e `qwen3:8b` geraram com `think: true`, 1.200 tokens e temperature 0,1. `qwen2.5:7b` gerou sem a chave `think`, 450 tokens no RAG e 360 na conversa livre.

## Resultado

| Modelo | Total médio | Prefill | Think | Decode | tok/s | FIEL | Alerta | Alucinação | Sem citação | Estouro | Erros |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen3:4b | 276 s | 38 s | 232 s | 237 s | 5,0 | 2 | 0 | 0 | 18 | 15 | 0 |
| qwen2.5:7b | 80 s | 48 s | 0 s | 31 s | 4,0 | 10 | 2 | 0 | 8 | 0 | 0 |
| qwen3:8b | 230 s | 58 s | 104 s | 170 s | 3,1 | 15 | 2 | 1 | 2 | 0 | 0 |

Nas 18 perguntas constitucionais, o `qwen3:8b` ficou FIEL em 15, o `qwen2.5:7b` em 10 e o `qwen3:4b` em 2. Nas duas fora de escopo (Q19 e Q20), os três ficaram sem citação de artigo, que é o comportamento esperado da conversa livre.

O `qwen3:4b` com think ligado esgotou os 1.200 tokens em 15 das 20 perguntas. A resposta visível ficou vazia ou com menos de 40 caracteres úteis (`estourou_no_think`). O pensamento médio foi 232 s. Só Q13 e Q17 produziram resposta FIEL; Q13 ainda atribuiu a doação de imóvel ao município (Art. 156), porque esse artigo estava no contexto congelado junto com o Art. 155.

O `qwen2.5:7b` foi cerca de três vezes mais rápido que o 8B e não estourou nenhuma resposta. Não alucinou artigo. Perdeu citação fiel em Q01, Q02, Q06, Q12, Q16 e Q18, e teve alerta de subdispositivo em Q08 e Q11.

O `qwen3:8b` foi o mais fiel. A alucinação única foi a Q10: o contexto trazia só o Art. 60, e a resposta citou o Art. 5º, que não estava nas fontes, ao falar de pena de morte. Q05 e Q06 ficaram em alerta de subdispositivo.

## Fase A — o contexto compartilhado

Dezesseis das vinte recuperações acharam o artigo esperado. Q19 e Q20 ficaram em conversa livre, com topo abaixo de 0,01.

| ID | Modo | Artigo esperado no contexto | Topo | Retriever |
|---|---|---|---:|---:|
| Q01 | cinza | Art. 5º, XI | 0,159 | 15 s |
| Q02 | alta | Art. 5º, LI | 0,969 | 3 s |
| Q03 | alta | Art. 7º, XXXIII | 0,961 | 56 s |
| Q04 | alta | ADCT, Art. 10, II | 0,793 | 5 s |
| Q05 | alta | Art. 12, § 3º | 0,374 | 4 s |
| Q06 | alta | Art. 14, §§ 1º e 3º | 0,994 | 51 s |
| Q07 | alta | Art. 37, XVI e XI | 0,955 | 54 s |
| Q08 | alta | Art. 41 sem o § 1º | 0,742 | 47 s |
| Q09 | alta | Art. 62, § 3º, sem § 1º e § 7º | 0,986 | 5 s |
| Q10 | alta | Art. 60, sem o § 4º e sem o Art. 5º, XLVII | 0,883 | 5 s |
| Q11 | alta | Art. 150, VI | 0,321 na 2ª passagem | 8 s |
| Q12 | alta | Art. 150, III | 0,993 na 2ª passagem | 8 s |
| Q13 | alta | Art. 155 e também Art. 156 | 0,753 | 4 s |
| Q14 | alta | Art. 183 | 0,962 | 37 s |
| Q15 | alta | Art. 177, V | 0,982 | 3 s |
| Q16 | alta | Art. 199, sem os §§ 1º e 2º | 0,971 | 4 s |
| Q17 | alta | Art. 208, I presente entre outros | 0,951 | 37 s |
| Q18 | alta | Art. 225, § 3º | 0,654 | 3 s |
| Q19 | livre | nenhum | 0,003 | 8 s |
| Q20 | livre | nenhum | 0,006 | 31 s |

Q08, Q09, Q10 e Q16 são furos do contexto, iguais para os três modelos. O juiz externo precisa separar falha de recuperação de falha de geração.

## Caso a caso

| ID | qwen3:4b | qwen2.5:7b | qwen3:8b |
|---|---|---|---|
| Q01 | sem citação, estouro, 380 s | sem citação, 101 s | FIEL, 282 s |
| Q02 | sem citação, estouro, 284 s | sem citação, 80 s | FIEL, 216 s |
| Q03 | sem citação, estouro, 324 s | FIEL, 119 s | FIEL, 248 s |
| Q04 | sem citação, estouro, 274 s | FIEL, 77 s | FIEL, 265 s |
| Q05 | sem citação, estouro, 239 s | FIEL, 37 s | alerta, 194 s |
| Q06 | sem citação, 271 s | sem citação, 58 s | alerta, 188 s |
| Q07 | sem citação, estouro, 368 s | FIEL, 147 s | FIEL, 305 s |
| Q08 | sem citação, estouro, 268 s | alerta, 73 s | FIEL, 165 s |
| Q09 | sem citação, estouro, 292 s | FIEL, 87 s | FIEL, 230 s |
| Q10 | sem citação, estouro, 250 s | FIEL, 68 s | alucinação do Art. 5º, 224 s |
| Q11 | sem citação, estouro, 249 s | alerta, 44 s | FIEL, 109 s |
| Q12 | sem citação, estouro, 272 s | sem citação, 81 s | FIEL, 215 s |
| Q13 | FIEL, 329 s | FIEL, 149 s | FIEL, 397 s |
| Q14 | sem citação, estouro, 237 s | FIEL, 49 s | FIEL, 219 s |
| Q15 | sem citação, estouro, 293 s | FIEL, 86 s | FIEL, 214 s |
| Q16 | sem citação, estouro, 246 s | sem citação, 49 s | FIEL, 195 s |
| Q17 | FIEL, 341 s | FIEL, 141 s | FIEL, 382 s |
| Q18 | sem citação, estouro, 242 s | sem citação, 45 s | FIEL, 168 s |
| Q19 | sem citação, 176 s | sem citação, 71 s | sem citação, 206 s |
| Q20 | sem citação, 181 s | sem citação, 39 s | sem citação, 187 s |

## Leitura para o seminário

O mesmo contexto muda o ranking conforme a métrica. Em fidelidade de citação, `qwen3:8b`. Em tempo de resposta completa, `qwen2.5:7b`, com a metade das constitucionais ainda FIEL e nenhuma alucinação de artigo. O `qwen3:4b` com think ligado não serve como gerador desta pilha: o orçamento de 1.200 tokens se esgota no raciocínio e a resposta some. As respostas brutas e os prompts estão em `benchmarks/benchmark_modelos_seminario.json`, prontos para o juiz externo.
