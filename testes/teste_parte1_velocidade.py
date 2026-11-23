# -*- coding: utf-8 -*-
"""Parte 1: think manual, stateless e fusão só na zona cinzenta. Sem Ollama."""

import sys
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(1, str(_RAIZ))

from src.api.server import Pedido, historico_efetivo
from src.rag.gerador import (
    NUM_CTX,
    NUM_CTX_AUX,
    NUM_CTX_LIVRE,
    NUM_PREDICT_LIVRE,
    NUM_PREDICT_RAG_SEM_THINK,
    NUM_PREDICT_THINK_SIMPLES,
    extrair_telemetria,
    montar_prompt,
    plano_geracao,
)
from src.rag.tradutor_consulta import CORTE_HYDE_COSSENO, CORTE_HYDE_RERANKER


def testar_think() -> None:
    cinza = plano_geracao("MODO_RAG_ZONA_CINZENTA", True, "qwen3:8b", "auto", usar_think=False)
    composta = plano_geracao("MODO_RAG_ALTA_CONFIANCA", True, "qwen3:8b", usar_think=False)
    if cinza["think"] or composta["think"]:
        raise SystemExit("think padrão ligou sozinho: {} {}".format(cinza, composta))
    if cinza["num_predict"] != NUM_PREDICT_RAG_SEM_THINK or NUM_PREDICT_RAG_SEM_THINK != 450:
        raise SystemExit("RAG sem think deveria prever 450 tokens")
    if cinza["num_ctx"] != 3072:
        raise SystemExit("num_ctx do RAG deveria ser 3072")
    livre = plano_geracao("MODO_CONVERSA_LIVRE", False, "qwen3:8b", usar_think=False)
    if livre["num_predict"] != NUM_PREDICT_LIVRE or livre["num_ctx"] != NUM_CTX_LIVRE:
        raise SystemExit("conversa livre deveria usar 360 tokens e num_ctx 2048")
    ligado = plano_geracao("MODO_RAG_ZONA_CINZENTA", True, "qwen3:8b", usar_think=True)
    if not ligado["think"] or ligado["num_predict"] != NUM_PREDICT_THINK_SIMPLES:
        raise SystemExit("usar_think=True deveria ir ao gerador com think e 1200 tokens")
    texto = (_RAIZ / "src" / "rag" / "gerador.py").read_text(encoding="utf-8")
    if 'think = bool(composta) or modo == "MODO_RAG_ZONA_CINZENTA"' in texto:
        raise SystemExit("o acionamento automático de think ainda está no gerador")


def testar_stateless() -> None:
    historico = [
        {"role": "user", "content": "turno antigo do usuario"},
        {"role": "assistant", "content": "turno antigo do assistente"},
    ]
    mensagens = montar_prompt("pergunta atual isolada", [], "MODO_RAG_ALTA_CONFIANCA", historico)
    if [item["role"] for item in mensagens] != ["system", "user"]:
        raise SystemExit("o payload deveria ter só system e o turno atual: {}".format(mensagens))
    if "turno antigo" in mensagens[-1]["content"] or "pergunta atual isolada" not in mensagens[-1]["content"]:
        raise SystemExit("a pergunta atual se misturou com o histórico")
    pedido = Pedido(pergunta="oi", historico=[{"role": "user", "content": "turno antigo do usuario"}])
    if historico_efetivo(pedido):
        raise SystemExit("a API ainda encaminha o histórico")


def testar_telemetria() -> None:
    bruto = {
        "prompt_eval_count": 100,
        "eval_count": 50,
        "prompt_eval_duration": 2_000_000_000,
        "eval_duration": 4_000_000_000,
    }
    frio = extrair_telemetria(bruto, usar_think=False, think_s_medido=3.5, think_chars_brutos=80)
    if frio["tokens_entrada"] != 100 or frio["tokens_saida"] != 50:
        raise SystemExit("contagem de tokens incorreta: {}".format(frio))
    if frio["prefill_s"] != 2.0 or frio["decode_s"] != 4.0 or frio["tok_s"] != 12.5:
        raise SystemExit("tempos do Ollama incorretos: {}".format(frio))
    if frio["think_s"] != 0.0 or frio["think_chars"] != 0:
        raise SystemExit("think desligado deveria zerar o raciocínio")
    quente = extrair_telemetria(bruto, usar_think=True, think_s_medido=1.5, think_chars_brutos=40)
    if quente["think_s"] != 1.5 or quente["think_chars"] != 40:
        raise SystemExit("think ligado deveria separar o raciocínio: {}".format(quente))


def testar_folga_contexto() -> None:
    if NUM_CTX != 3072 or NUM_CTX_AUX != 2048:
        raise SystemExit("contextos auxiliares ou do RAG mudaram")
    if CORTE_HYDE_COSSENO != 0.52 or CORTE_HYDE_RERANKER != 0.002:
        raise SystemExit("os cortes do drift foram alterados")
    mensagens = montar_prompt(
        "pergunta",
        [{"artigo_id": "Art. 1", "texto": "a" * 2200, "score_reranker": 0.9}],
    )
    chars = sum(len(item["content"]) for item in mensagens)
    if chars >= NUM_CTX * 2:
        raise SystemExit("um pai de 2200 caracteres não cabe com folga em 3072: {} chars".format(chars))


def testar_fusao() -> None:
    from src.rag.pipeline import fundir_top1_p1

    p1 = {"artigo_id": "Art. X", "texto": "literal", "score_reranker": 0.130}
    alta, aplicada_alta = fundir_top1_p1(
        [{"artigo_id": "Art. Y", "texto": "forte", "score_reranker": 0.348}],
        p1,
        0.130,
        0.348,
    )
    if aplicada_alta or [item["artigo_id"] for item in alta] != ["Art. Y"]:
        raise SystemExit("P2 em alta confiança não deveria receber Art. X")
    cinza, aplicada = fundir_top1_p1(
        [{"artigo_id": "Art. Y", "texto": "cinza", "score_reranker": 0.20}],
        p1,
        0.130,
        0.20,
    )
    if not aplicada or [item["artigo_id"] for item in cinza] != ["Art. Y", "Art. X"]:
        raise SystemExit("P2 cinzenta deveria preservar o top-1 da P1")
    ood, aplicada_ood = fundir_top1_p1(
        [{"artigo_id": "Art. Y", "texto": "y"}],
        p1,
        0.002,
        0.095,
    )
    if aplicada_ood or any(item["artigo_id"] == "Art. X" for item in ood):
        raise SystemExit("abaixo de 0,12 a P1 não entra")


def main() -> None:
    testar_think()
    testar_stateless()
    testar_telemetria()
    testar_folga_contexto()
    testar_fusao()
    print("ok parte1 velocidade")


if __name__ == "__main__":
    main()
