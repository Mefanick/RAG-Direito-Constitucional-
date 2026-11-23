# -*- coding: utf-8 -*-
"""Bateria cega da Fase 3.3. Cada pergunta é gravada na hora e pode ser retomada.

Não entra no treino do roteador. O histórico é vazio em todas as chamadas.
"""

import argparse
import json
import os
import re
import sys
import traceback
import unicodedata
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(1, str(_RAIZ))
_BENCH = _RAIZ / "benchmarks"
_REL = _RAIZ / "relatorios"
_JSONL = _BENCH / "resultados_bateria_cega_fase33.jsonl"
_MD = _REL / "relatorio_bateria_cega_fase33.md"

PERGUNTAS = [
    {
        "id": "01",
        "grupo": "LEIGO / EXCECAO",
        "pergunta": "A polícia pode arrombar a porta da minha casa à noite só com ordem do juiz?",
        "constitucional": True,
        "atalho": False,
        "artigos": ["Art. 5"],
        "adct": False,
        "nota": "Art. 5º, XI: ordem judicial só de dia; à noite, flagrante, desastre ou socorro.",
    },
    {
        "id": "02",
        "grupo": "LEIGO / EXCECAO",
        "pergunta": "Se eu dever um empréstimo no banco e não pagar, posso ir preso?",
        "constitucional": True,
        "atalho": False,
        "artigos": ["Art. 5"],
        "adct": False,
        "nota": "Art. 5º, LXVII: vedada a prisão civil por dívida, com as ressalvas do próprio inciso.",
    },
    {
        "id": "03",
        "grupo": "TRIBUTACAO / LEIGO",
        "pergunta": "A prefeitura pode cobrar IPTU de uma igreja do meu bairro?",
        "constitucional": True,
        "atalho": False,
        "artigos": ["Art. 150"],
        "adct": False,
        "nota": "Art. 150, VI, b: imunidade dos templos. Classe Tributação e Orçamento.",
    },
    {
        "id": "04",
        "grupo": "TRIBUTACAO / PRAZO",
        "pergunta": "O governo pode criar um imposto hoje e começar a cobrar na semana que vem?",
        "constitucional": True,
        "atalho": False,
        "artigos": ["Art. 150"],
        "adct": False,
        "nota": "Art. 150, III, b e c: anterioridade anual e nonagesimal, com exceções.",
    },
    {
        "id": "05",
        "grupo": "TRIBUTACAO / COMPETENCIA",
        "pergunta": "Se eu receber um terreno de doação em vida, quem cobra o imposto sobre essa doação: a Prefeitura, o Estado ou a União?",
        "constitucional": True,
        "atalho": False,
        "artigos": ["Art. 155"],
        "adct": False,
        "nota": "Art. 155, I: Estados e Distrito Federal.",
    },
    {
        "id": "06",
        "grupo": "ADCT / LEIGO",
        "pergunta": "Uma funcionária grávida pode ser demitida sem justa causa logo depois de ter o bebê?",
        "constitucional": True,
        "atalho": False,
        "artigos": ["Art. 10"],
        "adct": True,
        "nota": "ADCT, Art. 10, II, b: da confirmação da gravidez até cinco meses após o parto.",
    },
    {
        "id": "07",
        "grupo": "PARENT-DOC / NUMERO",
        "pergunta": "Com quantos anos uma pessoa pode se candidatar a senador ou a presidente da República?",
        "constitucional": True,
        "atalho": False,
        "artigos": ["Art. 14"],
        "adct": False,
        "nota": "Art. 14, § 3º, VI, a: 35 anos.",
    },
    {
        "id": "08",
        "grupo": "PARENT-DOC / INCISOS",
        "pergunta": "Em quais situações um brasileiro nato pode acabar perdendo a nacionalidade brasileira?",
        "constitucional": True,
        "atalho": False,
        "artigos": ["Art. 12"],
        "adct": False,
        "nota": "Art. 12, § 4º, fiel ao texto vigente recuperado, sem inciso inventado.",
    },
    {
        "id": "09",
        "grupo": "COMPOSTA / MULTI-HOP",
        "pergunta": "Um servidor público efetivo pode acumular dois cargos de professor na rede pública, e qual é o limite máximo que ele pode receber de remuneração?",
        "constitucional": True,
        "atalho": False,
        "artigos": ["Art. 37"],
        "adct": False,
        "nota": "Art. 37, XVI, a e Art. 37, XI.",
    },
    {
        "id": "10",
        "grupo": "COMPOSTA / MULTI-HOP",
        "pergunta": "O Presidente da República pode editar medida provisória sobre direito penal, e qual é o prazo máximo de vigência de uma medida provisória antes de perder a eficácia?",
        "constitucional": True,
        "atalho": False,
        "artigos": ["Art. 62"],
        "adct": False,
        "nota": "Art. 62, § 1º, I, b e Art. 62, § 3º.",
    },
    {
        "id": "11",
        "grupo": "ORDEM SOCIAL / LEIGO",
        "pergunta": "Um hospital particular pode cobrar pelo atendimento, ou a saúde no Brasil é proibida para empresas privadas?",
        "constitucional": True,
        "atalho": False,
        "artigos": ["Art. 199"],
        "adct": False,
        "nota": "Art. 199: livre à iniciativa privada; § 2º veda recursos públicos a entidades com fins lucrativos.",
    },
    {
        "id": "12",
        "grupo": "TRABALHO / LEIGO",
        "pergunta": "O patrão pode obrigar alguém a trabalhar 10 horas por dia todos os dias sem pagar nada a mais?",
        "constitucional": True,
        "atalho": False,
        "artigos": ["Art. 7"],
        "adct": False,
        "nota": "Art. 7º, XIII e XVI: 8 horas, 44 semanais e hora extra de pelo menos 50%.",
    },
    {
        "id": "13",
        "grupo": "FORA DE ESCOPO / CDC",
        "pergunta": "Comprei um celular na internet faz 3 dias e me arrependi, a loja é obrigada a devolver meu dinheiro?",
        "constitucional": False,
        "atalho": False,
        "artigos": [],
        "adct": False,
        "nota": "Conversa livre ou zona cinzenta, Código de Defesa do Consumidor, sem artigo inventado da CF/88.",
    },
    {
        "id": "14",
        "grupo": "FORA DE ESCOPO / TRANSITO",
        "pergunta": "Se eu bater no carro de alguém no trânsito sem querer, qual é o valor da multa que eu levo?",
        "constitucional": False,
        "atalho": False,
        "artigos": [],
        "adct": False,
        "nota": "Conversa livre, CTB ou Código Civil, sem artigo inventado da CF/88.",
    },
    {
        "id": "15",
        "grupo": "ATALHO SOCIAL",
        "pergunta": "Boa tarde, tudo bem?",
        "constitucional": False,
        "atalho": True,
        "artigos": [],
        "adct": False,
        "nota": "MODO_ATALHO_SOCIAL em menos de 0,1 s, sem BGE-M3 e sem Ollama.",
    },
    {
        "id": "16",
        "grupo": "REGRESSAO / ESCOPO - MINERACAO",
        "pergunta": "A União detém o monopólio de toda a atividade de mineração no Brasil?",
        "constitucional": True,
        "atalho": False,
        "regressao": True,
        "artigos": ["Art. 177", "Art. 176"],
        "artigos_modo": "qualquer",
        "adct": False,
        "nota": "Não começar com Sim. Restringir a minérios nucleares (Art. 177, V ou § 4º) e ao regime de autorização ou concessão (Art. 176). Sem generalizar.",
    },
    {
        "id": "17",
        "grupo": "REGRESSAO / LIMITE NUMERICO - USUCAPIAO",
        "pergunta": "Quem ocupa e trabalha numa terra rural de 40 hectares por 5 anos sem ser dono de outro imóvel pode adquirir a propriedade por usucapião?",
        "constitucional": True,
        "atalho": False,
        "regressao": True,
        "artigos": ["Art. 191"],
        "adct": False,
        "nota": "Art. 191: até 50 hectares, cinco anos, trabalho da família, moradia, sem outro imóvel. Não misturar o Art. 186.",
    },
]


def normalizar(texto: str) -> str:
    base = unicodedata.normalize("NFKD", str(texto).strip().lower())
    base = "".join(caractere for caractere in base if not unicodedata.combining(caractere))
    return " ".join(base.replace("?", " ").replace("!", " ").replace(",", " ").split())


def _blob(registro: dict) -> str:
    pedacos = []
    for artigo in registro.get("artigos_recuperados") or []:
        pedacos.append(str(artigo.get("artigo_id") or ""))
        for filho in artigo.get("child_ids") or []:
            pedacos.append(str(filho))
    return "\n".join(pedacos)


def _recuperou(caso: dict, registro: dict) -> bool:
    if not caso["artigos"]:
        return False
    blob = _blob(registro)
    achados = []
    for artigo in caso["artigos"]:
        numero = re.search(r"(\d+)", artigo).group(1)
        nucleo = numero + r"(?:º|°)?(?!\d)"
        if caso["adct"]:
            achados.append(re.search(r"ADCT[\s\S]{0,80}Art\.?\s*" + nucleo, blob, re.IGNORECASE) is not None)
        else:
            achados.append(re.search(r"(?<![\d])Art\.?\s*" + nucleo, blob, re.IGNORECASE) is not None)
    if caso.get("artigos_modo") == "qualquer":
        return any(achados)
    return all(achados)


def _fora_ok(registro: dict) -> bool:
    modo = registro.get("modo_resposta")
    auditoria = registro.get("auditoria") or {}
    return modo in ("MODO_CONVERSA_LIVRE", "MODO_RAG_ZONA_CINZENTA", "MODO_ATALHO_SOCIAL") and not auditoria.get(
        "artigos_inventados"
    )


def _caminhos(perfil: str) -> tuple[Path, Path, Path]:
    nome = re.sub(r"[^a-z0-9_]+", "_", perfil.strip().lower()).strip("_")
    if not nome:
        raise SystemExit("Informe um --perfil com letras, números ou _.")
    base = _BENCH / "resultados_bateria_cega_{}".format(nome)
    return base.with_suffix(".jsonl"), _REL / "relatorio_bateria_cega_{}.md".format(nome), base.with_suffix(".erros.log")


def _lidos(caminho: Path) -> dict[str, dict]:
    prontos = {}
    if not caminho.is_file():
        return prontos
    with caminho.open(encoding="utf-8") as ficheiro:
        for linha in ficheiro:
            linha = linha.strip()
            if not linha:
                continue
            item = json.loads(linha)
            prontos[str(item["id"])] = item
    return prontos


def _markdown(registros: list[dict], perfil: str) -> str:
    por_id = {item["id"]: item for item in registros}
    constitucionais = [caso for caso in PERGUNTAS if caso["constitucional"] and not caso.get("regressao")]
    regressoes = [caso for caso in PERGUNTAS if caso.get("regressao")]
    fora = [caso for caso in PERGUNTAS if not caso["constitucional"] and not caso["atalho"]]
    atalho = [caso for caso in PERGUNTAS if caso["atalho"]]

    def item(caso):
        return por_id.get(caso["id"])

    primeira = [
        caso
        for caso in constitucionais
        if item(caso) and item(caso).get("passagem") == 1 and not item(caso).get("consulta_traduzida")
    ]
    recuperados = [caso for caso in constitucionais if item(caso) and _recuperou(caso, item(caso))]
    fieis = [
        caso
        for caso in constitucionais
        if item(caso) and (item(caso).get("auditoria") or {}).get("status") == "FIEL"
    ]
    fora_certos = [caso for caso in fora if item(caso) and _fora_ok(item(caso))]
    atalho_certo = [
        caso
        for caso in atalho
        if item(caso)
        and item(caso).get("modo_resposta") == "MODO_ATALHO_SOCIAL"
        and float((item(caso).get("tempos_s") or {}).get("total") or 9) < 0.1
    ]

    def media(chave, campo=None):
        valores = []
        for caso in PERGUNTAS:
            registro = item(caso) or {}
            if campo:
                valor = (registro.get(campo) or {}).get(chave)
            else:
                valor = registro.get(chave)
            if isinstance(valor, (int, float)):
                valores.append(float(valor))
        if not valores:
            return 0.0
        return sum(valores) / len(valores)

    linhas = [
        "# Bateria cega da Fase 3.3 — {}".format(perfil),
        "",
        "## Resumo executivo",
        "",
        "Perfil {}. Este relatório audita 15 perguntas inéditas e 2 regressões históricas. O histórico de cada chamada fica vazio. As três colunas do placar são independentes.".format(perfil),
        "",
        "| Métrica | Resultado |",
        "| --- | --- |",
        "| Recuperação na 1ª passagem (12 inéditas) | {}/12 |".format(len(primeira)),
        "| Artigo esperado recuperado (12 inéditas) | {}/12 |".format(len(recuperados)),
        "| Auditoria FIEL (12 inéditas) | {}/12 |".format(len(fieis)),
        "| Recuperação na 1ª passagem (2 regressões) | {}/2 |".format(
            sum(1 for caso in regressoes if item(caso) and item(caso).get("passagem") == 1 and _recuperou(caso, item(caso)))
        ),
        "| Auditoria FIEL (2 regressões) | {}/2 |".format(
            sum(1 for caso in regressoes if item(caso) and (item(caso).get("auditoria") or {}).get("status") == "FIEL")
        ),
        "| Fora de escopo sem artigo inventado | {}/2 |".format(len(fora_certos)),
        "| Atalho social abaixo de 0,1 s | {}/1 |".format(len(atalho_certo)),
        "| Retriever médio (s) | {:.2f} |".format(media("retriever", "tempos_s")),
        "| Prefill médio (s) | {:.2f} |".format(media("prefill_s")),
        "| Pensamento médio (s) | {:.2f} |".format(media("tempo_thinking_s")),
        "| Gerador médio (s) | {:.2f} |".format(media("gerador", "tempos_s")),
        "| Total médio (s) | {:.2f} |".format(media("total", "tempos_s")),
        "",
        "## Placar",
        "",
        "| Caso | 1. Artigo na 1ª passagem | 2. Auditor FIEL | 3. Checklist de revisão humana |",
        "| --- | --- | --- | --- |",
    ]
    for caso in PERGUNTAS:
        registro = item(caso) or {}
        auditoria = registro.get("auditoria") or {}
        if caso["atalho"] or not caso["constitucional"]:
            coluna_artigo = "não se aplica"
        else:
            coluna_artigo = "sim" if registro.get("passagem") == 1 and _recuperou(caso, registro) else "não"
        coluna_fiel = "sim" if auditoria.get("status") == "FIEL" else str(auditoria.get("status") or "pendente")
        linhas.append(
            "| {} {} | {} | {} | {} |".format(
                caso["id"],
                caso["grupo"],
                coluna_artigo,
                coluna_fiel,
                caso["nota"].replace("|", "/"),
            )
        )
    linhas.extend(["", "## Resposta integral e checklist", ""])
    for caso in PERGUNTAS:
        registro = item(caso) or {}
        auditoria = registro.get("auditoria") or {}
        tempos = registro.get("tempos_s") or {}
        artigos = registro.get("artigos_recuperados") or []
        pais = []
        for artigo in artigos:
            if artigo.get("origem") == "parent_document":
                pais.append(
                    "{} ({} filhos)".format(artigo.get("artigo_id"), artigo.get("filhos"))
                )
            else:
                pais.append("{} [{}]".format(artigo.get("artigo_id"), artigo.get("origem")))
        rota = registro.get("roteamento") or {}
        linhas.extend(
            [
                "### {} — {}".format(caso["id"], caso["grupo"]),
                "",
                "Pergunta: {}".format(caso["pergunta"]),
                "",
                "Esperado: {}".format(caso["nota"]),
                "",
                "- Intenção: {} (margem {})".format(rota.get("intencao"), rota.get("margem")),
                "- modo_busca: {}".format(registro.get("modo_busca")),
                "- classe: {}".format(registro.get("classe_consulta")),
                "- passagem: {} | tradutor: {} | sub-consultas: {}".format(
                    registro.get("passagem"),
                    registro.get("consulta_traduzida"),
                    registro.get("subconsultas"),
                ),
                "- Modo final: {}".format(registro.get("modo_resposta")),
                "- Entregue ao LLM: {}".format("; ".join(pais) or "(nenhum)"),
                "- Checklist humano: {}".format(caso["nota"]),
                "- Auditoria: {}".format(
                    json.dumps(
                        {
                            "status": auditoria.get("status"),
                            "artigos_citados": auditoria.get("artigos_citados"),
                            "subdispositivos_citados": auditoria.get("subdispositivos_citados"),
                            "artigos_inventados": auditoria.get("artigos_inventados"),
                            "subdispositivos_nao_confirmados": auditoria.get("subdispositivos_nao_confirmados"),
                        },
                        ensure_ascii=False,
                    )
                ),
                "- Tempos (s): retriever {:.2f} | prefill {} | thinking {} | gerador {:.2f} | total {:.2f}".format(
                    float(tempos.get("retriever") or 0),
                    "n/d" if registro.get("prefill_s") is None else "{:.2f}".format(registro["prefill_s"]),
                    "n/d" if registro.get("tempo_thinking_s") is None else "{:.2f}".format(registro["tempo_thinking_s"]),
                    float(tempos.get("gerador") or 0),
                    float(tempos.get("total") or 0),
                ),
                "",
                "Resposta integral:",
                "",
                registro.get("resposta_llm") or "(sem resposta)",
                "",
            ]
        )
    return "\n".join(linhas) + "\n"


def _gravar_md(prontos: dict[str, dict], caminho_md: Path, perfil: str) -> None:
    ordem = [prontos[caso["id"]] for caso in PERGUNTAS if caso["id"] in prontos]
    caminho_md.write_text(_markdown(ordem, perfil), encoding="utf-8")
    print("Relatório: {}".format(caminho_md), flush=True)


def _registrar_erro(caminho: Path, caso: dict, detalhe: str) -> None:
    with caminho.open("a", encoding="utf-8") as ficheiro:
        ficheiro.write("Caso {}\n{}\n\n".format(caso["id"], detalhe))
        ficheiro.flush()
    print("Falha no caso {}. Resultado não gravado. Repita este id isolado.".format(caso["id"]), flush=True)
    print(detalhe, flush=True)


def _registro(caso: dict, trace: dict, perfil: str) -> dict:
    rota = trace.get("roteamento") or {}
    auditoria = trace.get("auditoria") or {}
    artigos = list(trace.get("artigos_recuperados") or [])
    citadas = list(auditoria.get("artigos_citados") or [])
    invalidas = list(auditoria.get("artigos_inventados") or [])
    sub_invalidos = list(auditoria.get("subdispositivos_nao_confirmados") or [])
    validas = [citacao for citacao in citadas if citacao not in invalidas]
    tempos = trace.get("tempos_s") or {}
    parcial = {
        "artigos_recuperados": artigos,
        "passagem": trace.get("passagem"),
    }
    recuperou_final = _recuperou(caso, parcial) if caso["artigos"] else False
    recuperou_p1 = bool(trace.get("passagem") == 1 and recuperou_final)
    return {
        "id": caso["id"],
        "perfil": perfil,
        "categoria": caso["grupo"],
        "grupo": caso["grupo"],
        "pergunta": caso["pergunta"],
        "intencao_prevista": rota.get("intencao"),
        "margem_roteador": rota.get("margem"),
        "soft_boost_aplicado": bool(rota.get("confianca_alta")),
        "modo_busca": trace.get("modo_busca"),
        "acionou_tradutor_2a_passagem": trace.get("passagem") == 2,
        "acionou_multi_query": len(trace.get("subconsultas") or []) >= 2,
        "parent_document_usado": any(item.get("origem") == "parent_document" for item in artigos),
        "artigos_recuperados": artigos,
        "recuperou_esperado_p1": recuperou_p1,
        "recuperou_esperado_final": recuperou_final,
        "modo_final": trace.get("modo_resposta"),
        "think_ativado": bool(trace.get("think")),
        "auditoria_citacoes": {
            "status": auditoria.get("status"),
            "citadas": citadas,
            "validas": validas,
            "invalidas": invalidas + sub_invalidos,
            "detalhes_subdispositivos": {
                "citados": auditoria.get("subdispositivos_citados") or [],
                "nao_confirmados": sub_invalidos,
            },
        },
        "tempos": {
            "retriever_s": tempos.get("retriever"),
            "tradutor_s": tempos.get("tradutor"),
            "prefill_s": trace.get("prefill_s"),
            "think_s": trace.get("think_s") if trace.get("think_s") is not None else trace.get("tempo_thinking_s"),
            "think_chars": trace.get("think_chars"),
            "decode_s": trace.get("eval_s"),
            "total_s": tempos.get("total"),
            "tokens_entrada": trace.get("tokens_prompt"),
            "tokens_saida": trace.get("tokens_resposta"),
            "tok_s": trace.get("tok_s"),
        },
        "resposta_integral": trace.get("resposta_llm") or "",
        "roteamento": rota,
        "classe_consulta": trace.get("classe_consulta"),
        "passagem": trace.get("passagem"),
        "consulta_traduzida": trace.get("consulta_traduzida"),
        "query_traduzida": trace.get("query_traduzida"),
        "top1_score_bruto_p1": trace.get("top1_score_bruto_p1"),
        "top1_score_bruto_p2": trace.get("top1_score_bruto_p2"),
        "hyde_cosseno": trace.get("hyde_cosseno"),
        "hyde_reranker": trace.get("hyde_reranker"),
        "hyde_rejeitado_por_drift": bool(trace.get("hyde_rejeitado_por_drift")),
        "hyde_copiou_exemplo": bool(trace.get("hyde_copiou_exemplo")),
        "fusao_p1_p2_aplicada": bool(trace.get("fusao_p1_p2_aplicada")),
        "usar_think": bool(trace.get("usar_think")),
        "top8_artigo_ids": [
            item.get("artigo_id") for item in (trace.get("top_candidatos_brutos") or [])[:8]
        ],
        "think_chars": trace.get("think_chars"),
        "subconsultas": trace.get("subconsultas"),
        "modo_resposta": trace.get("modo_resposta"),
        "auditoria": auditoria,
        "tempos_s": tempos,
        "prefill_s": trace.get("prefill_s"),
        "eval_s": trace.get("eval_s"),
        "tempo_thinking_s": trace.get("tempo_thinking_s"),
        "tokens_prompt": trace.get("tokens_prompt"),
        "tokens_resposta": trace.get("tokens_resposta"),
        "tok_s": trace.get("tok_s"),
        "resposta_llm": trace.get("resposta_llm") or "",
        "modelo_usado": trace.get("modelo_usado"),
        "erro_llm": trace.get("erro_llm"),
    }


def _linha_acompanhamento(registro: dict, concluidos: int) -> None:
    tempos = registro.get("tempos") or {}
    auditoria = registro.get("auditoria_citacoes") or {}
    print(
        "[{}/17] Caso {} | {:.2f}s | P{} | recuperou={} | {}".format(
            concluidos,
            registro["id"],
            float(tempos.get("total_s") or 0),
            registro.get("passagem"),
            "sim" if registro.get("recuperou_esperado_final") else "não",
            auditoria.get("status"),
        ),
        flush=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--perfil", required=True)
    parser.add_argument("--max-casos", type=int, default=0)
    parser.add_argument("--so-relatorio", action="store_true")
    parser.add_argument("--casos", default="")
    parser.add_argument("--so-retriever", action="store_true")
    parser.add_argument("--usar-think", action="store_true")
    args = parser.parse_args()
    pedido = set()
    for parte in str(args.casos or "").split(","):
        parte = parte.strip()
        if not parte:
            continue
        pedido.add(parte.zfill(2) if parte.isdigit() else parte)
    jsonl, markdown, erros = _caminhos(args.perfil)
    prontos = _lidos(jsonl)
    if args.so_relatorio:
        _gravar_md(prontos, markdown, args.perfil)
        return
    os.environ["LLM_URL"] = "http://127.0.0.1:11434/api/chat"
    os.environ["LLM_MODEL"] = "qwen3:8b"
    os.environ["LLM_NUM_THREAD"] = "10"
    from src.rag.pipeline import executar_rag

    feitos = 0
    with jsonl.open("a", encoding="utf-8") as saida:
        for caso in PERGUNTAS:
            if pedido and caso["id"] not in pedido:
                continue
            if caso["id"] in prontos:
                continue
            if args.max_casos and feitos >= args.max_casos:
                break
            print("Pergunta {}: {}".format(caso["id"], caso["pergunta"]), flush=True)
            try:
                trace = executar_rag(
                    caso["pergunta"],
                    historico=[],
                    usar_think=args.usar_think,
                    gerar=not args.so_retriever,
                )
            except Exception:
                _registrar_erro(erros, caso, traceback.format_exc())
                _gravar_md(prontos, markdown, args.perfil)
                raise SystemExit(1)
            if trace.get("erro_llm") and not args.so_retriever:
                _registrar_erro(erros, caso, str(trace.get("erro_llm")))
                _gravar_md(prontos, markdown, args.perfil)
                raise SystemExit(1)
            modelo = str(trace.get("modelo_usado") or "")
            if (
                not args.so_retriever
                and modelo
                and not modelo.startswith("qwen3:8b")
                and trace.get("modo_resposta") != "MODO_ATALHO_SOCIAL"
            ):
                _registrar_erro(erros, caso, "Modelo inesperado: {}".format(modelo))
                _gravar_md(prontos, markdown, args.perfil)
                raise SystemExit(1)
            registro = _registro(caso, trace, args.perfil)
            saida.write(json.dumps(registro, ensure_ascii=False) + "\n")
            saida.flush()
            prontos[caso["id"]] = registro
            feitos += 1
            _linha_acompanhamento(registro, sum(1 for item in PERGUNTAS if item["id"] in prontos))
    _gravar_md(prontos, markdown, args.perfil)
    print("Concluídos: {}/17".format(sum(1 for item in PERGUNTAS if item["id"] in prontos)), flush=True)


if __name__ == "__main__":
    main()
