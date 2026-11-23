# -*- coding: utf-8 -*-
"""Benchmark de 20 perguntas: contexto RAG congelado e depois 3 modelos.

Retoma do disco. Uma falha de geração não derruba o restante.
"""

import argparse
import ctypes
import gc
import json
import os
import re
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path

import requests

_RAIZ = Path(__file__).resolve().parents[1]
_AQUI = Path(__file__).resolve().parent
if str(_RAIZ) not in sys.path:
    sys.path.insert(1, str(_RAIZ))

PERGUNTAS_PATH = _AQUI / "benchmark_perguntas_seminario_20.json"
CONTEXTO_PATH = _AQUI / "benchmark_contexto_congelado_20.json"
RESULTADOS_PATH = _AQUI / "benchmark_modelos_seminario.json"
RELATORIO_PATH = _RAIZ / "relatorios" / "relatorio_benchmark_modelos.md"
OLLAMA_CHAT = "http://127.0.0.1:11434/api/chat"
OLLAMA_GENERATE = "http://127.0.0.1:11434/api/generate"
MODELOS_PADRAO = ("qwen3:4b", "qwen2.5:7b", "qwen3:8b")
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001


def _agora() -> str:
    return datetime.now().strftime("%H:%M:%S")


def _log(mensagem: str) -> None:
    print("[{}] {}".format(_agora(), mensagem), flush=True)


def _gravar(caminho: Path, dados: dict) -> None:
    temporario = caminho.with_suffix(caminho.suffix + ".tmp")
    temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporario, caminho)


def _ler(caminho: Path, vazio: dict) -> dict:
    if not caminho.is_file():
        return vazio
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _log("arquivo {} ilegível ({}), começando vazio".format(caminho.name, exc))
        return vazio


def _norm_id(texto: str) -> str:
    base = unicodedata.normalize("NFKD", str(texto or ""))
    base = "".join(letra for letra in base if not unicodedata.combining(letra))
    base = base.lower().replace("º", "").replace("°", "")
    return " ".join(base.replace("artigo ", "art. ").split())


def _ids_do_chunk(chunk: dict) -> list[str]:
    ids = [str(chunk.get("artigo_id") or "")]
    ids.extend(str(filho) for filho in (chunk.get("child_ids") or []))
    return [item for item in ids if item]


def _bate(esperado: str, candidato: str) -> bool:
    alvo = _norm_id(esperado)
    obtido = _norm_id(candidato)
    return bool(alvo) and (obtido == alvo or obtido.startswith(alvo + " ") or obtido.startswith(alvo + ","))


def _recuperou(caso: dict, modo: str, chunks: list[dict]) -> bool:
    if not caso.get("esperado_na_cf88"):
        return modo == "MODO_CONVERSA_LIVRE"
    esperados = caso.get("artigos_esperados") or []
    obtidos = [ident for chunk in chunks for ident in _ids_do_chunk(chunk)]
    return all(any(_bate(esperado, obtido) for obtido in obtidos) for esperado in esperados)


def _chunk_publico(item: dict) -> dict:
    return {
        "artigo_id": item.get("artigo_id"),
        "texto": item.get("texto") or "",
        "score_reranker": item.get("score_reranker"),
        "score_cosseno": item.get("score_cosseno"),
        "origem": item.get("origem"),
        "child_ids": list(item.get("child_ids") or []),
    }


def _chars_uteis(texto: str) -> int:
    return len(re.sub(r"\s+", "", str(texto or "")))


def _descarregar(modelo: str) -> None:
    try:
        requests.post(OLLAMA_GENERATE, json={"model": modelo, "keep_alive": 0}, timeout=30)
    except requests.exceptions.RequestException as exc:
        _log("não descarregou {}: {}".format(modelo, exc))


def _liberar_recuperacao() -> None:
    import torch

    import src.rag.encoder as encoder
    import src.rag.retriever as retriever

    for modulo, nomes in (
        (encoder, ("_ENCODER", "_RERANKER")),
        (retriever, ("_ENCODER", "_EMBEDDINGS", "_CACHE", "_TEXTOS", "_TEXTOS_BUSCA")),
    ):
        for nome in nomes:
            if hasattr(modulo, nome):
                setattr(modulo, nome, None)
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def _fase_a(perguntas: list[dict], meta: dict) -> list[dict]:
    from src.rag.gerador import montar_prompt
    from src.rag.pipeline import executar_rag

    estado = _ler(CONTEXTO_PATH, {"meta": meta, "perguntas": []})
    prontos = {item["id"]: item for item in estado.get("perguntas") or [] if item.get("id")}
    for caso in perguntas:
        if caso["id"] in prontos:
            _log("fase A {} já congelada".format(caso["id"]))
            continue
        _log("fase A {} recuperando".format(caso["id"]))
        inicio = time.perf_counter()
        trace = executar_rag(
            caso["pergunta"],
            historico=[],
            modelo="qwen3:8b",
            usar_think=False,
            usar_rag=True,
            gerar=False,
        )
        modo = trace.get("modo_resposta") or ""
        chunks = [_chunk_publico(item) for item in (trace.get("artigos_recuperados") or []) if isinstance(item, dict)]
        mensagens = montar_prompt(caso["pergunta"], chunks, modo if modo.startswith("MODO_") else "MODO_CONVERSA_LIVRE")
        registro = {
            "id": caso["id"],
            "area": caso.get("area"),
            "perfil": caso.get("perfil"),
            "esperado_na_cf88": caso.get("esperado_na_cf88"),
            "pergunta": caso["pergunta"],
            "artigos_esperados": caso.get("artigos_esperados") or [],
            "criterios_juiz": caso.get("criterios_juiz"),
            "modo_rag": trace.get("modo_rag") or modo,
            "classe": trace.get("classe_consulta"),
            "top1_score_p1": trace.get("top1_score_bruto_p1"),
            "top1_score_p2": trace.get("top1_score_bruto_p2"),
            "query_traduzida": trace.get("query_traduzida"),
            "artigos_recuperados": [ident for chunk in chunks for ident in _ids_do_chunk(chunk)],
            "recuperou_esperado": _recuperou(caso, modo, chunks),
            "chunks_recuperados": chunks,
            "retriever_s": (trace.get("tempos_s") or {}).get("retriever"),
            "system_prompt": mensagens[0]["content"] if mensagens else "",
            "user_prompt": mensagens[1]["content"] if len(mensagens) > 1 else caso["pergunta"],
        }
        prontos[caso["id"]] = registro
        estado["meta"] = meta
        estado["perguntas"] = [prontos[item["id"]] for item in perguntas if item["id"] in prontos]
        _gravar(CONTEXTO_PATH, estado)
        _log("fase A {} gravada em {:.1f}s | {}".format(caso["id"], time.perf_counter() - inicio, registro["modo_rag"]))
    return [prontos[item["id"]] for item in perguntas]


def _parametros(modelo: str, modo: str) -> dict:
    livre = modo == "MODO_CONVERSA_LIVRE"
    num_ctx = 2048 if livre else 3072
    if modelo.startswith("qwen3:"):
        return {"think": True, "num_predict": 1200, "num_ctx": num_ctx}
    return {"think": None, "num_predict": 360 if livre else 450, "num_ctx": num_ctx}


def _gerar_uma(modelo: str, system_prompt: str, user_prompt: str, modo: str) -> dict:
    from src.rag.auditor_citacoes import auditar_citacoes
    from src.rag.gerador import prefixar_aviso_livre, separar_raciocinio

    ajuste = _parametros(modelo, modo)
    corpo = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": True,
        "keep_alive": "10m",
        "options": {
            "temperature": 0.1,
            "num_predict": ajuste["num_predict"],
            "num_ctx": ajuste["num_ctx"],
            "num_thread": 10,
        },
    }
    if ajuste["think"] is True:
        corpo["think"] = True
    ultimo_erro = None
    for tentativa in (1, 2):
        inicio = time.perf_counter()
        conteudo: list[str] = []
        canal_think: list[str] = []
        primeiro_think = None
        ultimo_think = None
        final = {}
        try:
            resposta = requests.post(OLLAMA_CHAT, json=corpo, timeout=(10, 900), stream=True)
            if resposta.status_code != 200:
                raise requests.exceptions.HTTPError("HTTP {}".format(resposta.status_code))
            for linha in resposta.iter_lines():
                if not linha:
                    continue
                dados = json.loads(linha.decode("utf-8"))
                mensagem = dados.get("message") or {}
                trecho_think = str(mensagem.get("thinking") or "")
                trecho = str(mensagem.get("content") or "")
                agora = time.perf_counter()
                if trecho_think:
                    if primeiro_think is None:
                        primeiro_think = agora
                    ultimo_think = agora
                    canal_think.append(trecho_think)
                if trecho:
                    conteudo.append(trecho)
                if dados.get("done"):
                    final = dados
            break
        except (requests.exceptions.RequestException, json.JSONDecodeError, UnicodeError) as exc:
            ultimo_erro = exc
            if tentativa == 1:
                _log("{} tentativa 1 falhou ({}); nova tentativa em 10s".format(modelo, exc))
                time.sleep(10)
                continue
            raise
    else:
        raise ultimo_erro or RuntimeError("geração sem resposta")

    visivel, interno = separar_raciocinio("".join(conteudo))
    pensamento = "\n\n".join(parte for parte in ("".join(canal_think).strip(), interno or "") if parte)
    if modo == "MODO_CONVERSA_LIVRE":
        visivel = prefixar_aviso_livre(visivel)
    decode_s = float(final.get("eval_duration") or 0) / 1_000_000_000
    tokens_saida = int(final.get("eval_count") or 0)
    think_s = 0.0 if not modelo.startswith("qwen3:") else (
        (ultimo_think - primeiro_think) if primeiro_think is not None and ultimo_think is not None else 0.0
    )
    done_reason = final.get("done_reason")
    estourou = done_reason == "length" and _chars_uteis(visivel) < 40
    return {
        "resposta": visivel,
        "pensamento": pensamento,
        "think_s": think_s,
        "think_chars": len(pensamento),
        "tokens_entrada": final.get("prompt_eval_count"),
        "tokens_saida": tokens_saida,
        "prefill_s": float(final.get("prompt_eval_duration") or 0) / 1_000_000_000,
        "decode_s": decode_s,
        "total_s": time.perf_counter() - inicio,
        "tok_s": (tokens_saida / decode_s) if decode_s > 0 else None,
        "done_reason": done_reason,
        "estourou_no_think": estourou,
        "num_predict": ajuste["num_predict"],
        "num_ctx": ajuste["num_ctx"],
        "temperature": 0.1,
        "auditoria_pronta": visivel,
    }


def _fase_b(contextos: list[dict], modelos: list[str], meta: dict) -> None:
    from src.rag.auditor_citacoes import auditar_citacoes

    estado = _ler(RESULTADOS_PATH, {"meta": meta, "resultados": [], "resumo_modelos": {}})
    feitos = {
        (item.get("id"), item.get("modelo"))
        for item in estado.get("resultados") or []
        if item.get("id") and item.get("modelo") and not item.get("erro")
    }
    for modelo in modelos:
        _log("fase B carregando {}".format(modelo))
        for indice, contexto in enumerate(contextos, start=1):
            par = (contexto["id"], modelo)
            if par in feitos:
                _log("[{}] {}/20 já gravado".format(modelo, contexto["id"]))
                continue
            modo = contexto.get("modo_rag") or ""
            try:
                gerado = _gerar_uma(
                    modelo,
                    contexto.get("system_prompt") or "",
                    contexto.get("user_prompt") or contexto["pergunta"],
                    modo,
                )
                auditoria = auditar_citacoes(gerado.pop("auditoria_pronta"), contexto.get("chunks_recuperados") or [])
                item = {
                    "id": contexto["id"],
                    "modelo": modelo,
                    "area": contexto.get("area"),
                    "perfil": contexto.get("perfil"),
                    "esperado_na_cf88": contexto.get("esperado_na_cf88"),
                    "pergunta": contexto.get("pergunta"),
                    "artigos_esperados": contexto.get("artigos_esperados") or [],
                    "criterios_juiz": contexto.get("criterios_juiz"),
                    "modo_rag": modo,
                    "system_prompt": contexto.get("system_prompt"),
                    "user_prompt": contexto.get("user_prompt"),
                    "erro": None,
                    "auditoria": auditoria.get("status"),
                    "artigos_inventados": auditoria.get("artigos_inventados") or [],
                    **gerado,
                }
                _log(
                    "[{}] {}/20 | total={:.1f}s (prefill={:.1f}s think={:.1f}s decode={:.1f}s) | {} tok/s | {}".format(
                        modelo,
                        contexto["id"],
                        item["total_s"],
                        item["prefill_s"] or 0,
                        item["think_s"] or 0,
                        item["decode_s"] or 0,
                        "{:.1f}".format(item["tok_s"]) if item["tok_s"] else "n/d",
                        item["auditoria"],
                    )
                )
            except Exception as exc:
                item = {
                    "id": contexto["id"],
                    "modelo": modelo,
                    "pergunta": contexto.get("pergunta"),
                    "modo_rag": modo,
                    "erro": str(exc),
                    "resposta": "",
                    "pensamento": "",
                    "auditoria": None,
                    "estourou_no_think": False,
                }
                _log("[{}] {} falhou de novo: {}".format(modelo, contexto["id"], exc))
            anteriores = [
                antigo
                for antigo in estado.get("resultados") or []
                if not (antigo.get("id") == contexto["id"] and antigo.get("modelo") == modelo)
            ]
            anteriores.append(item)
            estado["resultados"] = anteriores
            estado["meta"] = meta
            _gravar(RESULTADOS_PATH, estado)
            feitos.add(par)
        _descarregar(modelo)
        _log("fase B {} descarregado".format(modelo))


def _media(valores: list[float]) -> float | None:
    limpos = [float(valor) for valor in valores if isinstance(valor, (int, float))]
    if not limpos:
        return None
    return sum(limpos) / len(limpos)


def _resumir(estado: dict) -> dict:
    resumo = {}
    for modelo in MODELOS_PADRAO:
        itens = [item for item in estado.get("resultados") or [] if item.get("modelo") == modelo]
        if not itens:
            continue
        resumo[modelo] = {
            "n": len(itens),
            "prefill_s": _media([item.get("prefill_s") for item in itens]),
            "think_s": _media([item.get("think_s") for item in itens]),
            "decode_s": _media([item.get("decode_s") for item in itens]),
            "total_s": _media([item.get("total_s") for item in itens]),
            "tok_s": _media([item.get("tok_s") for item in itens]),
            "fiel": sum(1 for item in itens if item.get("auditoria") == "FIEL"),
            "alerta_subdispositivo": sum(1 for item in itens if item.get("auditoria") == "ALERTA_SUBDISPOSITIVO"),
            "alucinacao_artigo": sum(1 for item in itens if item.get("auditoria") == "ALUCINACAO_ARTIGO"),
            "sem_citacao": sum(1 for item in itens if item.get("auditoria") == "SEM_CITACAO"),
            "estourou_no_think": sum(1 for item in itens if item.get("estourou_no_think")),
            "erros": sum(1 for item in itens if item.get("erro")),
        }
    return resumo


def _relatorio(contextos: list[dict], estado: dict) -> None:
    linhas = [
        "# Benchmark de modelos do seminário",
        "",
        "Gerado em {}.".format(datetime.now().strftime("%d/%m/%Y %H:%M")),
        "",
        "## Fase A — contexto congelado",
        "",
        "| ID | Modo | Recuperou | Retriever (s) |",
        "|---|---|---|---:|",
    ]
    for item in contextos:
        linhas.append(
            "| {} | {} | {} | {} |".format(
                item.get("id"),
                item.get("modo_rag"),
                "sim" if item.get("recuperou_esperado") else "não",
                "{:.1f}".format(item["retriever_s"]) if isinstance(item.get("retriever_s"), (int, float)) else "—",
            )
        )
    linhas.extend(["", "## Fase B — geração", ""])
    resumo = estado.get("resumo_modelos") or {}
    linhas.extend(
        [
            "| Modelo | n | Prefill médio (s) | Think médio (s) | Decode médio (s) | Total médio (s) | tok/s | FIEL | Alerta | Alucinação | Sem citação | Estouro | Erros |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for modelo, dados in resumo.items():
        def n(chave: str) -> str:
            valor = dados.get(chave)
            return "—" if valor is None else "{:.1f}".format(valor)

        linhas.append(
            "| {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
                modelo,
                dados.get("n"),
                n("prefill_s"),
                n("think_s"),
                n("decode_s"),
                n("total_s"),
                n("tok_s"),
                dados.get("fiel"),
                dados.get("alerta_subdispositivo"),
                dados.get("alucinacao_artigo"),
                dados.get("sem_citacao"),
                dados.get("estourou_no_think"),
                dados.get("erros"),
            )
        )
    linhas.append("")
    RELATORIO_PATH.write_text("\n".join(linhas), encoding="utf-8")


def _impedir_suspensao() -> None:
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)


def _permitir_suspensao() -> None:
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--modelos", default=",".join(MODELOS_PADRAO))
    args = parser.parse_args()
    modelos = [item.strip() for item in args.modelos.split(",") if item.strip()]
    desconhecidos = [item for item in modelos if item not in MODELOS_PADRAO]
    if desconhecidos:
        raise SystemExit("Modelo fora do benchmark: {}".format(", ".join(desconhecidos)))
    suite = json.loads(PERGUNTAS_PATH.read_text(encoding="utf-8"))
    perguntas = suite["perguntas"]
    meta = suite.get("meta") or {}
    try:
        _impedir_suspensao()
        _log("suspensão do Windows bloqueada durante o benchmark")
        contextos_salvos = _ler(CONTEXTO_PATH, {"perguntas": []}).get("perguntas") or []
        if len(contextos_salvos) >= len(perguntas) and {item.get("id") for item in contextos_salvos} >= {
            item["id"] for item in perguntas
        }:
            _log("fase A já está completa")
            contextos = [next(item for item in contextos_salvos if item["id"] == caso["id"]) for caso in perguntas]
        else:
            contextos = _fase_a(perguntas, meta)
            _descarregar("qwen3:8b")
            _liberar_recuperacao()
            _log("BGE-M3 e ONNX liberados")
        _fase_b(contextos, modelos, meta)
        estado = _ler(RESULTADOS_PATH, {"meta": meta, "resultados": []})
        estado["resumo_modelos"] = _resumir(estado)
        _gravar(RESULTADOS_PATH, estado)
        _relatorio(contextos, estado)
        _log("benchmark concluído: {} resultados".format(len(estado.get("resultados") or [])))
    finally:
        _permitir_suspensao()
        _log("suspensão do Windows restaurada")


if __name__ == "__main__":
    main()
