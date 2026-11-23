# -*- coding: utf-8 -*-
"""Checagens do tradutor HyDE e do aviso da conversa livre, sem Ollama."""

import sys
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(1, str(_RAIZ))

from src.rag.auditor_citacoes import auditar_citacoes
from src.rag.gerador import prefixar_aviso_livre
from src.rag.tradutor_consulta import (
    CORTE_HYDE_COSSENO,
    CORTE_HYDE_RERANKER,
    _EXEMPLOS_HYDE,
    _PROMPT_TRADUTOR,
    hyde_copiou_exemplo,
    limpar_saida_tradutor,
    rejeitar_hyde_por_drift,
)


def testar_limpador() -> None:
    bruto = (
        '<think>vou citar o artigo</think> "Art. 150 é vedado instituir impostos sobre templos de qualquer culto"'
    )
    limpo = limpar_saida_tradutor(bruto)
    if "<think>" in limpo or "Art." in limpo or limpo.startswith('"'):
        raise SystemExit("limpador não removeu think, aspas ou artigo: {}".format(limpo))
    if "é vedado instituir impostos sobre templos de qualquer culto" not in limpo:
        raise SystemExit("a frase normativa foi perdida: {}".format(limpo))
    if limpar_saida_tradutor("FORA_CF88"):
        raise SystemExit("FORA_CF88 sozinho deveria virar consulta vazia")
    if "?" in limpar_saida_tradutor("compete ao ente instituir a regra?"):
        raise SystemExit("a interrogação final deveria ser removida")


def testar_pipeline_sem_veto() -> None:
    texto = (_RAIZ / "src" / "rag" / "pipeline.py").read_text(encoding="utf-8")
    if "consulta_traduzida == FORA" in texto or "deve_reforcar_apos_fora" in texto:
        raise SystemExit("o pipeline ainda aborta ou reforça por FORA_CF88")


def testar_aviso() -> None:
    resposta = prefixar_aviso_livre("A loja pode ter de devolver o valor, conforme o Código de Defesa do Consumidor.")
    if not resposta.startswith("Aviso: este tema não foi localizado na base constitucional carregada (CF/88)."):
        raise SystemExit("o aviso fixo não foi colocado no início")
    repetido = prefixar_aviso_livre(resposta)
    if repetido.count("Aviso: este tema não foi localizado") != 1:
        raise SystemExit("o aviso foi duplicado")
    auditoria = auditar_citacoes(resposta, [])
    if auditoria.get("status") != "SEM_CITACAO" or auditoria.get("artigos_inventados"):
        raise SystemExit("o aviso disparou o auditor: {}".format(auditoria))


def testar_copia() -> None:
    if len(_EXEMPLOS_HYDE) != 4:
        raise SystemExit("a trava anti-cópia precisa cobrir os 4 exemplos da v2, achou {}".format(len(_EXEMPLOS_HYDE)))
    if any("moeda" in saida for _, saida in _EXEMPLOS_HYDE):
        raise SystemExit("o quinto exemplo de emissão de moeda deveria ter saído")
    if "Pergunta de competência ou atribuição" in _PROMPT_TRADUTOR:
        raise SystemExit("a tabela de moldes da v3 ainda está no prompt")
    if "quem cobra" not in _PROMPT_TRADUTOR or "nunca 'é vedado...'" not in _PROMPT_TRADUTOR:
        raise SystemExit("falta a linha curta de competência")
    copiada = "é vedado à União, aos Estados, ao Distrito Federal e aos Municípios utilizar tributo com efeito de confisco"
    if not hyde_copiou_exemplo("quem recebe um bem por liberalidade paga qual imposto?", copiada):
        raise SystemExit("a cópia do exemplo de confisco deveria ser bloqueada")
    aluguel = "atraso no pagamento de aluguel residencial e retomada de imóvel pelo locador em contrato de locação"
    if not hyde_copiou_exemplo("o sindicato pode marcar a assembleia no domingo?", aluguel):
        raise SystemExit("a cópia do exemplo de aluguel deveria ser bloqueada")
    legitima = "são direitos dos trabalhadores urbanos e rurais a duração do trabalho normal não superior a oito horas diárias"
    if hyde_copiou_exemplo("o empregado pode ter jornada maior sem adicional?", legitima):
        raise SystemExit("reescrita de jornada não deveria ser tratada como cópia do exemplo")
    if "Nunca copie nem reutilize frases dos exemplos" not in _PROMPT_TRADUTOR:
        raise SystemExit("falta a instrução anti-cópia")


def testar_fusao() -> None:
    from src.rag.pipeline import fundir_top1_p1, modo_pelo_topo

    p1 = {"artigo_id": "Art. X", "texto": "texto literal da primeira passagem", "score_reranker": 0.130}
    alta, aplicada_alta = fundir_top1_p1(
        [{"artigo_id": "Art. Y", "texto": "texto da segunda passagem", "score_reranker": 0.348}],
        p1,
        0.130,
        0.348,
    )
    if aplicada_alta or [item["artigo_id"] for item in alta] != ["Art. Y"]:
        raise SystemExit("alta confiança não deveria receber o chunk fraco da P1")
    cinza, aplicada = fundir_top1_p1(
        [{"artigo_id": "Art. Y", "texto": "texto da segunda passagem", "score_reranker": 0.20}],
        p1,
        0.130,
        0.20,
    )
    if not aplicada or [item["artigo_id"] for item in cinza] != ["Art. Y", "Art. X"]:
        raise SystemExit("a zona cinzenta deveria preservar Art. X: {}".format([item["artigo_id"] for item in cinza]))
    if modo_pelo_topo(0.348) != "MODO_RAG_ALTA_CONFIANCA":
        raise SystemExit("0,348 deveria permanecer em alta confiança")
    repetido, aplicada_repetida = fundir_top1_p1(
        [{"artigo_id": "Art. Y", "texto": "y"}, dict(p1)],
        p1,
        0.130,
        0.20,
    )
    if aplicada_repetida or [item["artigo_id"] for item in repetido].count("Art. X") != 1:
        raise SystemExit("Art. X já presente na P2 não deveria ser duplicado")
    ood, aplicada_ood = fundir_top1_p1(
        [{"artigo_id": "Art. Y", "texto": "y"}],
        {"artigo_id": "Art. X", "texto": "x"},
        0.002,
        0.095,
    )
    if aplicada_ood or any(item["artigo_id"] == "Art. X" for item in ood):
        raise SystemExit("abaixo de 0,12 a P1 não deveria ser preservada")
    if modo_pelo_topo(0.095) != "MODO_CONVERSA_LIVRE":
        raise SystemExit("0,095 deveria ficar em conversa livre")


def testar_cortes() -> None:
    if CORTE_HYDE_COSSENO != 0.52 or CORTE_HYDE_RERANKER != 0.002:
        raise SystemExit("os cortes do drift foram alterados")


def testar_drift() -> None:
    if rejeitar_hyde_por_drift(0.581, 0.049) or rejeitar_hyde_por_drift(0.546, 0.006):
        raise SystemExit("traduções legítimas com reranker baixo deveriam passar")
    if not rejeitar_hyde_por_drift(0.491, 0.000) or not rejeitar_hyde_por_drift(0.527, 0.001):
        raise SystemExit("os desvios medidos deveriam ser rejeitados")


def main() -> None:
    testar_limpador()
    testar_pipeline_sem_veto()
    testar_aviso()
    testar_copia()
    testar_cortes()
    testar_drift()
    testar_fusao()
    print("ok hyde, pipeline, aviso e drift")


if __name__ == "__main__":
    main()
