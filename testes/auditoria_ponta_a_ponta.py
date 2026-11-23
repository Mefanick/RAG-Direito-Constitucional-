# -*- coding: utf-8 -*-
"""Auditoria da Etapa 3: citações do LLM contra os artigos recuperados.

Vinte perguntas do CSV de 300. Se o servidor local não responder,
o script avisa como subi-lo e termina sem percorrer a amostra.
"""

import os
import re
import sys
from pathlib import Path

import pandas as pd

_RAIZ = Path(__file__).resolve().parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(1, str(_RAIZ))

from src.rag.auditor_citacoes import auditar_citacoes, extrair_artigos
from src.rag.gerador import FRASE_SEM_BASE
from src.rag.servidor_llm import COMANDO_MANUAL, garantir_servidor

_CSV = Path(r"c:\Users\nicol\Downloads\dataset_teste_300_perguntas.csv")
_RELATORIO = _RAIZ / "relatorios" / "auditoria_etapa3_respostas.md"
_CLASSES = (
    "Princípios Fundamentais",
    "Direitos e Garantias Fundamentais",
    "Organização do Estado",
    "Organização dos Poderes",
    "Controle de Constitucionalidade",
    "Ordem Econômica e Financeira",
    "Ordem Social",
)
def _modelos_url(url_chat: str) -> str:
    if "/chat/completions" in url_chat:
        return url_chat.replace("/chat/completions", "/models")
    return url_chat.rstrip("/") + "/v1/models"


def servidor_no_ar() -> tuple[bool, str]:
    """Confere /v1/models. Não baixa modelo."""
    estado = garantir_servidor()
    url = os.getenv("LLM_URL", "")
    if not url:
        return False, (
            "Nenhum servidor LLM respondeu em 127.0.0.1:11434 (Ollama) "
            "nem em 127.0.0.1:8080 (Llamafile).\n"
            "Para subir o Ollama:\n{}\n"
            "Para um Llamafile já presente no projecto ou em Transferências, "
            "volte a correr este script: ele usa --server --nobrowser em 127.0.0.1:8080."
        ).format(COMANDO_MANUAL)
    from src.rag.servidor_llm import _pedido

    if _pedido(_modelos_url(url), timeout=2.0) is None:
        return False, "LLM_URL={} não respondeu em /v1/models.\n{}".format(url, COMANDO_MANUAL)
    return True, "{} | {}".format(estado.get("origem"), os.getenv("LLM_MODEL", ""))


def _amostra(tabela: pd.DataFrame) -> list[dict]:
    constitucional = tabela.loc[tabela["intencao_esperada"].astype(str) != "Fora de Escopo"].copy()
    fora = tabela.loc[tabela["intencao_esperada"].astype(str) == "Fora de Escopo"].copy()
    escolhidas: list[dict] = []
    usadas = set()

    def acrescentar(linha: pd.Series) -> None:
        ident = int(linha["id"])
        if ident in usadas:
            return
        usadas.add(ident)
        escolhidas.append(linha.to_dict())

    for marca in ("anonimato", "monopólio de mineração", "culto"):
        for _, linha in constitucional.iterrows():
            if marca in str(linha["texto"]).lower():
                acrescentar(linha)
                break
    presentes = {str(item["intencao_esperada"]) for item in escolhidas}
    for classe in _CLASSES:
        if classe in presentes:
            continue
        bloco = constitucional.loc[constitucional["intencao_esperada"].astype(str) == classe]
        if not bloco.empty:
            acrescentar(bloco.iloc[0])
    for _, linha in constitucional.iterrows():
        if len([item for item in escolhidas if str(item["intencao_esperada"]) != "Fora de Escopo"]) >= 15:
            break
        acrescentar(linha)

    oos: list[dict] = []
    for marca in ("furto qualificado", "maria da penha"):
        for _, linha in fora.iterrows():
            if marca in str(linha["texto"]).lower() and int(linha["id"]) not in {int(item["id"]) for item in oos}:
                oos.append(linha.to_dict())
                break
    for _, linha in fora.iterrows():
        if len(oos) >= 5:
            break
        if int(linha["id"]) not in {int(item["id"]) for item in oos}:
            oos.append(linha.to_dict())
    return escolhidas[:15] + oos[:5]


def _recusa(trace: dict) -> str:
    resposta = str(trace.get("resposta_llm") or "").strip()
    if not trace.get("artigos_recuperados") and resposta == FRASE_SEM_BASE and not trace.get("erro_llm"):
        return "reranker"
    if FRASE_SEM_BASE in resposta and not trace.get("erro_llm"):
        return "llm"
    return "nao_recusou"


def _cita_referencia(resposta: str, referencia: str) -> bool:
    esperados = extrair_artigos(str(referencia))
    if not esperados:
        return False
    citados = set(extrair_artigos(resposta))
    return any(item in citados for item in esperados)


def _linha_md(rotulo: str, valor: str) -> str:
    return "**{}:** {}\n".format(rotulo, valor)


def _casos_criticos(registros: list[dict]) -> dict[str, str]:
    saida = {"mineracao": "não encontrada", "adi": "não encontrada", "usucapiao": "não encontrada"}
    for item in registros:
        texto = str(item["linha"]["texto"]).lower()
        resposta = str(item["trace"]["resposta_llm"] or "")
        baixo = resposta.lower()
        ids = " | ".join(str(artigo.get("artigo_id", "")) for artigo in item["trace"]["artigos_recuperados"])
        if "monopólio de mineração" in texto:
            restringe = any(
                marca in baixo
                for marca in (
                    "não autoriz",
                    "nao autoriz",
                    "apenas",
                    "somente",
                    "restrit",
                    "não se estende",
                    "nao se estende",
                    "específic",
                    "especific",
                )
            )
            afirma_sim = bool(re.search(r"\bsim\b", baixo))
            saida["mineracao"] = (
                "restringiu ao nuclear"
                if "nuclear" in baixo and restringe and not (afirma_sim and "em geral" in baixo)
                else "alargou ou não restringiu"
            )
        if "mesa da câmara" in texto or "mesa da camara" in texto:
            fontes_ii = bool(re.search(r"103\s*,\s*II(?!I)", ids))
            fontes_iii = bool(re.search(r"103\s*,\s*III", ids))
            resp_ii = bool(re.search(r"103\s*,\s*II(?!I)", resposta))
            resp_iii = bool(re.search(r"103\s*,\s*III", resposta))
            saida["adi"] = (
                "II e III nas fontes e na resposta"
                if fontes_ii and fontes_iii and resp_ii and resp_iii
                else "fontes II={} III={} | resposta II={} III={}".format(fontes_ii, fontes_iii, resp_ii, resp_iii)
            )
        if "usucapião" in texto or "usucapiao" in texto:
            hectares = (
                "cinquenta hectares" in baixo
                or "cinqüenta hectares" in baixo
                or "50 hectares" in baixo
            )
            anos = "cinco anos" in baixo or "5 anos" in baixo
            faltas = []
            if not hectares:
                faltas.append("cinquenta hectares")
            if not anos:
                faltas.append("cinco anos")
            saida["usucapiao"] = "hectares e cinco anos" if not faltas else "faltou {}".format(" e ".join(faltas))
    return saida


def _metricas(registros: list[dict]) -> dict:
    fora = [item for item in registros if str(item["linha"]["intencao_esperada"]) == "Fora de Escopo"]
    dentro = [item for item in registros if str(item["linha"]["intencao_esperada"]) != "Fora de Escopo"]
    respondidas = [item for item in dentro if item["trace"]["tempos_s"]["gerador"] > 0 and not item["trace"].get("erro_llm")]
    recusas = sum(item["recusa"] != "nao_recusou" for item in fora)
    fieis = sum(not item["auditoria"]["citacao_alucinada"] for item in dentro)
    tokens = []
    segundos = []
    ttfts = []
    for item in respondidas:
        if item["trace"].get("tokens_resposta"):
            tokens.append(item["trace"]["tokens_resposta"])
            segundos.append(item["trace"]["tempos_s"]["gerador"])
        if item["trace"].get("ttft_s") is not None:
            ttfts.append(item["trace"]["ttft_s"])
    pior = max((item["trace"]["tempos_s"]["gerador"] for item in respondidas), default=0.0)
    return {
        "total_20": sum(item["trace"]["tempos_s"]["total"] for item in registros) / len(registros),
        "retriever_20": sum(item["trace"]["tempos_s"]["retriever"] for item in registros) / len(registros),
        "gerador_15": sum(item["trace"]["tempos_s"]["gerador"] for item in respondidas) / (len(respondidas) or 1),
        "pior": pior,
        "ttft": sum(ttfts) / len(ttfts) if ttfts else None,
        "tok_s": sum(tokens) / sum(segundos) if tokens and segundos else None,
        "fidelidade": "{}/{}".format(fieis, len(dentro)),
        "bloqueio": "{}/{}".format(recusas, len(fora)),
        "casos": _casos_criticos(registros),
        "fora": fora,
        "dentro": dentro,
        "fieis": fieis,
        "recusas": recusas,
    }


def _escrever(caminho: Path, aviso: str, registros: list[dict], resumo: dict) -> None:
    partes = ["# Auditoria da Etapa 3 v2\n", "\nServidor: {}\n".format(aviso)]
    partes.append("\nTempo total médio (20): {:.2f} s.\n".format(resumo["total_20"]))
    partes.append("Tempo gerador médio (respondidas): {:.2f} s.\n".format(resumo["gerador_15"]))
    partes.append("Pior caso do gerador: {:.2f} s.\n".format(resumo["pior"]))
    partes.append("TTFT médio: {}.\n".format("indisponível" if resumo["ttft"] is None else "{:.2f} s".format(resumo["ttft"])))
    partes.append(
        "Tokens/s: {}.\n".format("indisponível" if resumo["tok_s"] is None else "{:.1f}".format(resumo["tok_s"]))
    )
    partes.append("Fidelidade: {}. Bloqueio: {}.\n".format(resumo["fidelidade"], resumo["bloqueio"]))
    casos = resumo["casos"]
    partes.append("Mineração: {}.\n".format(casos["mineracao"]))
    partes.append("ADI das Mesas: {}.\n".format(casos["adi"]))
    partes.append("Usucapião rural: {}.\n".format(casos["usucapiao"]))
    for item in registros:
        linha = item["linha"]
        trace = item["trace"]
        auditoria = item["auditoria"]
        artigos = [
            "{}. {} ({:.3f}, {})".format(
                posicao,
                artigo.get("artigo_id"),
                float(artigo.get("score_reranker") or 0.0),
                artigo.get("origem", "reranker"),
            )
            for posicao, artigo in enumerate(trace["artigos_recuperados"], start=1)
        ]
        estado = "alucinada: {}".format(", ".join(auditoria["inventadas"])) if auditoria["citacao_alucinada"] else "fiel"
        tempos = trace["tempos_s"]
        partes.append("\n## {}\n".format(linha["texto"]))
        partes.append(_linha_md("Classe", str(linha["intencao_esperada"])))
        partes.append(_linha_md("Artigo de referência", str(linha["artigo_referencia"])))
        partes.append(_linha_md("Artigos recuperados", "; ".join(artigos) if artigos else "(nenhum)"))
        partes.append(_linha_md("Resposta do LLM", trace["resposta_llm"] or "(vazia)"))
        if trace.get("erro_llm"):
            partes.append(_linha_md("Erro", str(trace["erro_llm"])))
        partes.append(_linha_md("Checagem de citação", estado))
        if str(linha["intencao_esperada"]) == "Fora de Escopo":
            partes.append(_linha_md("Recusa", item["recusa"]))
        ttft = trace.get("ttft_s")
        partes.append(
            _linha_md(
                "Tempos",
                "retriever {:.2f} s | gerador {:.2f} s | total {:.2f} s | ttft {}".format(
                    tempos["retriever"],
                    tempos["gerador"],
                    tempos["total"],
                    "n/d" if ttft is None else "{:.2f} s".format(ttft),
                ),
            )
        )
    caminho.write_text("".join(partes), encoding="utf-8")


def _rodar(modelo: str, caminho: Path, amostra: list[dict]) -> dict:
    os.environ["LLM_URL"] = "http://127.0.0.1:11434/v1/chat/completions"
    os.environ["LLM_MODEL"] = modelo
    from src.rag.pipeline import executar_rag

    print("\n=== {} ===".format(modelo), flush=True)
    registros = []
    for indice, linha in enumerate(amostra, start=1):
        print("{}/{} {}".format(indice, len(amostra), str(linha["texto"])[:80]), flush=True)
        trace = executar_rag(str(linha["texto"]), stream=True)
        auditoria = auditar_citacoes(trace["resposta_llm"], trace["artigos_recuperados"])
        registros.append({"linha": linha, "trace": trace, "auditoria": auditoria, "recusa": _recusa(trace)})
    resumo = _metricas(registros)
    _escrever(caminho, "ollama | {}".format(modelo), registros, resumo)
    print("Fidelidade {} | bloqueio {} | gerador-15 {:.2f} s | pior {:.2f} s".format(
        resumo["fidelidade"], resumo["bloqueio"], resumo["gerador_15"], resumo["pior"]
    ), flush=True)
    print("Mineração: {}".format(resumo["casos"]["mineracao"]), flush=True)
    print("ADI: {}".format(resumo["casos"]["adi"]), flush=True)
    print("Usucapião: {}".format(resumo["casos"]["usucapiao"]), flush=True)
    print("Relatório: {}".format(caminho), flush=True)
    return resumo


def _garantir_qwen3b() -> None:
    from src.rag.servidor_llm import caminho_ollama, modelos_ollama_locais

    exe = caminho_ollama()
    if not exe:
        raise RuntimeError("Ollama não encontrado para baixar qwen2.5:3b.")
    if "qwen2.5:3b" in modelos_ollama_locais(exe):
        print("qwen2.5:3b já está no Ollama.", flush=True)
        return
    print("A baixar qwen2.5:3b.", flush=True)
    import subprocess

    subprocess.run([exe, "pull", "qwen2.5:3b"], check=True)


def _imprimir_comparativo(otimizado: dict, leve: dict) -> None:
    baseline = {
        "total_20": 51.95,
        "gerador_15": 55.71,
        "pior": 114.81,
        "ttft": None,
        "tok_s": 1.4,
        "fidelidade": "15/15",
        "bloqueio": "5/5",
        "casos": {
            "mineracao": "alargou para a mineração em geral",
            "adi": "só a Câmara; Senado fora do top 5",
            "usucapiao": "faltou cinquenta hectares",
        },
    }
    linhas = [
        ("Baseline 7b sem tuning", baseline),
        ("qwen2.5:7b otimizado", otimizado),
        ("qwen2.5:3b otimizado", leve),
    ]

    def celula_tempo(valor):
        return "n/d" if valor is None else "{:.2f}".format(valor)

    print()
    print(
        "{:<24} {:>10} {:>12} {:>10} {:>8} {:>8} {:>8} {:>8}".format(
            "Rodada", "total 20", "gerador 15", "pior", "ttft", "tok/s", "fiel", "bloqueio"
        )
    )
    for nome, item in linhas:
        print(
            "{:<24} {:>10} {:>12} {:>10} {:>8} {:>8} {:>8} {:>8}".format(
                nome,
                celula_tempo(item["total_20"]),
                celula_tempo(item["gerador_15"]),
                celula_tempo(item["pior"]),
                celula_tempo(item["ttft"]),
                celula_tempo(item["tok_s"]),
                item["fidelidade"],
                item["bloqueio"],
            )
        )
    print()
    print("{:<24} {:<32} {:<40} {:<28}".format("Rodada", "Mineração", "ADI das Mesas", "Usucapião"))
    for nome, item in linhas:
        print(
            "{:<24} {:<32} {:<40} {:<28}".format(
                nome, item["casos"]["mineracao"], item["casos"]["adi"], item["casos"]["usucapiao"]
            )
        )


def main() -> None:
    ok, aviso = servidor_no_ar()
    if not ok:
        print(aviso)
        return
    print("Servidor: {}".format(aviso), flush=True)
    tabela = pd.read_csv(_CSV, encoding="utf-8")
    amostra = _amostra(tabela)
    otimizado = _rodar("qwen2.5:7b", _RAIZ / "relatorios" / "auditoria_etapa3_v2_qwen7b.md", amostra)
    _garantir_qwen3b()
    leve = _rodar("qwen2.5:3b", _RAIZ / "relatorios" / "auditoria_etapa3_v2_qwen3b.md", amostra)
    _imprimir_comparativo(otimizado, leve)
    comparativo = _RAIZ / "relatorios" / "auditoria_etapa3_v2_comparativo.md"
    comparativo.write_text(
        "\n".join(
            [
                "# Comparativo Etapa 3 v2",
                "",
                "| Rodada | Total 20 (s) | Gerador 15 (s) | Pior (s) | TTFT (s) | tok/s | Fidelidade | Bloqueio |",
                "|---|---:|---:|---:|---:|---:|---|---|",
                "| 7b sem tuning | 51.95 | 55.71 | 114.81 | n/d | 1.4 | 15/15 | 5/5 |",
                "| 7b otimizado | {:.2f} | {:.2f} | {:.2f} | {} | {} | {} | {} |".format(
                    otimizado["total_20"],
                    otimizado["gerador_15"],
                    otimizado["pior"],
                    "n/d" if otimizado["ttft"] is None else "{:.2f}".format(otimizado["ttft"]),
                    "n/d" if otimizado["tok_s"] is None else "{:.1f}".format(otimizado["tok_s"]),
                    otimizado["fidelidade"],
                    otimizado["bloqueio"],
                ),
                "| 3b otimizado | {:.2f} | {:.2f} | {:.2f} | {} | {} | {} | {} |".format(
                    leve["total_20"],
                    leve["gerador_15"],
                    leve["pior"],
                    "n/d" if leve["ttft"] is None else "{:.2f}".format(leve["ttft"]),
                    "n/d" if leve["tok_s"] is None else "{:.1f}".format(leve["tok_s"]),
                    leve["fidelidade"],
                    leve["bloqueio"],
                ),
                "",
                "Mineração 7b otimizado: {}.".format(otimizado["casos"]["mineracao"]),
                "ADI 7b otimizado: {}.".format(otimizado["casos"]["adi"]),
                "Usucapião 7b otimizado: {}.".format(otimizado["casos"]["usucapiao"]),
                "Mineração 3b otimizado: {}.".format(leve["casos"]["mineracao"]),
                "ADI 3b otimizado: {}.".format(leve["casos"]["adi"]),
                "Usucapião 3b otimizado: {}.".format(leve["casos"]["usucapiao"]),
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("Comparativo: {}".format(comparativo), flush=True)


if __name__ == "__main__":
    main()
