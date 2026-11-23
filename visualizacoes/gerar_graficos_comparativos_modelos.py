# -*- coding: utf-8 -*-
"""Comparativos novos entre modelos. Não redesenha figuras já existentes.

Já cobertos em gerar_graficos_seminario.py e por isso omitidos aqui:
- barras empilhadas Prefill + Think + Escrita (fig05, painel B);
- desfechos 100% empilhados das 60 gerações (fig06, painel B);
- latência FP32 versus ONNX sozinha (fig03, painel B).
"""

import base64
import json
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import FancyBboxPatch

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
SAIDA = AQUI / "graficos_comparativos_modelos"
DADOS = RAIZ / "benchmarks"
AVISOS = []

AZUL = "#1B365D"
VERDE = "#0F766E"
AMBAR = "#D97706"
VERMELHO = "#DC2626"
CINZA = "#64748B"
AZUL_CLARO = "#3B82F6"
FUNDO = "#FFFFFF"
GRADE = "#E2E8F0"
TEXTO = "#0F172A"
SECUNDARIO = "#475569"

MODELOS = ["qwen3:4b", "qwen2.5:7b", "qwen3:8b"]
COR = {"qwen3:4b": AMBAR, "qwen2.5:7b": VERDE, "qwen3:8b": AZUL}
ROTULO = {
    "qwen3:4b": "qwen3:4b + think",
    "qwen2.5:7b": "qwen2.5:7b direto",
    "qwen3:8b": "qwen3:8b + think",
}
FUROS = {"Q08", "Q09", "Q10", "Q16"}
PESOS = {
    "fidelidade": 0.35,
    "anti_alucinacao": 0.20,
    "estabilidade": 0.15,
    "velocidade": 0.15,
    "throughput": 0.05,
    "eficiencia_escrita": 0.10,
}
AREAS = [
    ("Direitos individuais", {"Q01", "Q02"}),
    ("Trabalho", {"Q03", "Q04"}),
    ("Nacionalidade e voto", {"Q05", "Q06"}),
    ("Administração pública", {"Q07", "Q08"}),
    ("Poderes", {"Q09", "Q10"}),
    ("Tributário", {"Q11", "Q12", "Q13"}),
    ("Ordem econômica", {"Q14", "Q15"}),
    ("Ordem social", {"Q16", "Q17", "Q18"}),
    ("Fora de escopo", {"Q19", "Q20"}),
]


def estilo():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 13.5,
        "axes.labelsize": 10.5,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "text.color": TEXTO,
        "axes.labelcolor": TEXTO,
        "axes.edgecolor": "#CBD5E1",
        "xtick.color": SECUNDARIO,
        "ytick.color": SECUNDARIO,
        "figure.facecolor": FUNDO,
        "axes.facecolor": FUNDO,
        "savefig.facecolor": FUNDO,
    })


def limpar(ax, grade_y=True):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if grade_y:
        ax.grid(axis="y", color=GRADE, linewidth=0.6)
        ax.set_axisbelow(True)


def rodape(fig, texto):
    fig.supxlabel(texto, fontsize=8, color=SECUNDARIO, x=0.01, ha="left")


def salvar(fig, nome):
    for pasta, ext, extra in (
        ("svg", "svg", {}),
        ("pdf", "pdf", {}),
        ("png_300dpi", "png", {"dpi": 300}),
    ):
        destino = SAIDA / pasta
        destino.mkdir(parents=True, exist_ok=True)
        with warnings.catch_warnings(record=True) as pegos:
            warnings.simplefilter("always")
            fig.savefig(destino / "{}.{}".format(nome, ext), **extra)
        for aviso in pegos:
            AVISOS.append("{}: {}".format(nome, aviso.message))
    plt.close(fig)


def carregar():
    contexto = json.loads((DADOS / "benchmark_contexto_congelado_20.json").read_text(encoding="utf-8"))
    bench = json.loads((DADOS / "benchmark_modelos_seminario.json").read_text(encoding="utf-8"))
    ctx = {item["id"]: item for item in contexto["perguntas"]}
    linhas = []
    for item in bench["resultados"]:
        base = ctx[item["id"]]
        p1 = float(base.get("top1_score_p1") or 0)
        p2 = base.get("top1_score_p2")
        topo = float(p2) if p2 is not None and float(p2) >= p1 else p1
        decode = float(item.get("decode_s") or 0)
        think = float(item.get("think_s") or 0)
        linhas.append({
            "id": item["id"],
            "modelo": item["modelo"],
            "usar_think": item["modelo"].startswith("qwen3:"),
            "auditoria": item.get("auditoria"),
            "estourou": bool(item.get("estourou_no_think")),
            "total_s": float(item.get("total_s") or 0),
            "prefill_s": float(item.get("prefill_s") or 0),
            "think_s": think,
            "decode_s": decode,
            "escrita_util_s": max(0.0, decode - think),
            "tok_s": float(item["tok_s"]) if item.get("tok_s") is not None else np.nan,
            "tokens_entrada": float(item["tokens_entrada"]) if item.get("tokens_entrada") is not None else np.nan,
            "tokens_saida": float(item["tokens_saida"]) if item.get("tokens_saida") is not None else np.nan,
            "constitucional": item["id"] not in ("Q19", "Q20"),
            "limpa": item["id"] not in FUROS and item["id"] not in ("Q19", "Q20"),
            "ood": item["id"] in ("Q19", "Q20"),
            "classe": base.get("classe"),
            "top1": topo,
            "area_grupo": next(nome for nome, ids in AREAS if item["id"] in ids),
        })
    return pd.DataFrame(linhas), ctx


def indices(df):
    medias_total = df.groupby("modelo")["total_s"].mean()
    medias_tok = df.groupby("modelo")["tok_s"].mean()
    menor_total = float(medias_total.min())
    maior_tok = float(medias_tok.max())
    linhas = []
    for modelo in MODELOS:
        grupo = df[df["modelo"] == modelo]
        c18 = grupo[grupo["constitucional"]]
        c14 = grupo[grupo["limpa"]]
        ood = grupo[grupo["ood"]]
        fiel_18 = int((c18["auditoria"] == "FIEL").sum())
        fiel_14 = int((c14["auditoria"] == "FIEL").sum())
        aluc = int((grupo["auditoria"] == "ALUCINACAO_ARTIGO").sum())
        alerta = int((grupo["auditoria"] == "ALERTA_SUBDISPOSITIVO").sum())
        sem = int((grupo["auditoria"] == "SEM_CITACAO").sum())
        estouro = int(grupo["estourou"].sum())
        ood_ok = int(((ood["auditoria"] == "SEM_CITACAO") & ~ood["estourou"]).sum())
        totais = grupo["total_s"].to_numpy()
        i_fid = 100 * fiel_18 / len(c18)
        i_anti = (1 - aluc / len(grupo)) * 100
        i_est = (1 - estouro / len(grupo)) * 100
        i_vel = (menor_total / float(totais.mean())) * 100
        i_thr = (float(grupo["tok_s"].mean()) / maior_tok) * 100
        i_eff = (float(grupo["escrita_util_s"].mean()) / float(grupo["decode_s"].mean())) * 100
        score = (
            PESOS["fidelidade"] * i_fid
            + PESOS["anti_alucinacao"] * i_anti
            + PESOS["estabilidade"] * i_est
            + PESOS["velocidade"] * i_vel
            + PESOS["throughput"] * i_thr
            + PESOS["eficiencia_escrita"] * i_eff
        )
        linhas.append({
            "modelo": modelo,
            "usar_think": bool(grupo["usar_think"].iloc[0]),
            "n_total": int(len(grupo)),
            "fiel_18": fiel_18,
            "taxa_fiel_18_pct": i_fid,
            "fiel_14_limpas": fiel_14,
            "taxa_fiel_14_pct": 100 * fiel_14 / len(c14),
            "alerta_n": alerta,
            "alucinacao_n": aluc,
            "sem_citacao_n": sem,
            "estouro_n": estouro,
            "ood_ok_2": ood_ok,
            "total_s_media": float(totais.mean()),
            "total_s_mediana_p50": float(np.percentile(totais, 50)),
            "total_s_p90": float(np.percentile(totais, 90)),
            "total_s_p95": float(np.percentile(totais, 95)),
            "total_s_min": float(totais.min()),
            "total_s_max": float(totais.max()),
            "total_s_desvio": float(totais.std(ddof=0)),
            "prefill_s_media": float(grupo["prefill_s"].mean()),
            "think_s_media": float(grupo["think_s"].mean()),
            "escrita_util_s_media": float(grupo["escrita_util_s"].mean()),
            "decode_s_media": float(grupo["decode_s"].mean()),
            "tok_s_media": float(grupo["tok_s"].mean()),
            "tokens_entrada_media": float(grupo["tokens_entrada"].mean()),
            "tokens_saida_media": float(grupo["tokens_saida"].mean()),
            "razao_think_sobre_decode_pct": 100 * float(grupo["think_s"].mean()) / float(grupo["decode_s"].mean()),
            "I_fidelidade": i_fid,
            "I_anti_alucinacao": i_anti,
            "I_estabilidade": i_est,
            "I_velocidade": i_vel,
            "I_throughput": i_thr,
            "I_eficiencia_escrita": i_eff,
            "score_composto_0_100": score,
        })
    tabela = pd.DataFrame(linhas)
    soma = tabela["prefill_s_media"] + tabela["think_s_media"] + tabela["escrita_util_s_media"]
    desvio = (soma - tabela["total_s_media"]).abs()
    if float(desvio.max()) > 8:
        raise SystemExit("prefill + think + escrita não fecha com o total: {}".format(desvio.tolist()))
    return tabela


def parte1():
    def ler(nome):
        linhas = []
        for linha in (DADOS / nome).read_text(encoding="utf-8").splitlines():
            if linha.strip():
                linhas.append(json.loads(linha))
        return {item["id"]: item for item in linhas}

    dados = ler("resultados_bateria_cega_parte1_rapido_check.jsonl")
    casos = ["01", "09", "10"]
    totais = [dados[i]["tempos"]["total_s"] for i in casos]
    toks = [dados[i]["tok_s"] for i in casos]
    fieis = sum(1 for i in casos if (dados[i].get("auditoria_citacoes") or {}).get("status") == "FIEL")
    return {
        "total_s": float(np.mean(totais)),
        "tok_s": float(np.mean(toks)),
        "fiel": fieis,
        "n": len(casos),
    }


def exigir_readme():
    texto = (RAIZ / "README.md").read_text(encoding="utf-8")
    for trecho in ("19,4", "5,0 tok/s", "61,0", "15/15", "0,741", "0,747", "94,3%", "0,764", "0,781", "0,646", "0,831", "97,0%", "0,952", "0,944", "42/45", "5,31", "21,42"):
        if trecho not in texto:
            raise SystemExit("README.md não contém {}".format(trecho))


def comp01(tabela):
    eixos_nome = ["Fidelidade", "Anti-alucinação", "Estabilidade", "Velocidade", "Throughput", "Eficiência\nde escrita"]
    colunas = ["I_fidelidade", "I_anti_alucinacao", "I_estabilidade", "I_velocidade", "I_throughput", "I_eficiencia_escrita"]
    angulos = np.linspace(0, 2 * np.pi, len(colunas), endpoint=False)
    angulos = np.concatenate([angulos, angulos[:1]])
    fig = plt.figure(figsize=(13.5, 7.2), layout="constrained")
    ax = fig.add_subplot(1, 2, 1, projection="polar")
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angulos[:-1]), eixos_nome, fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.tick_params(colors=SECUNDARIO)
    ax.spines["polar"].set_color(GRADE)
    ax.grid(color=GRADE)
    for _, linha in tabela.iterrows():
        valores = linha[colunas].to_numpy(dtype=float)
        valores = np.concatenate([valores, valores[:1]])
        ax.plot(angulos, valores, color=COR[linha["modelo"]], lw=2, label=ROTULO[linha["modelo"]])
        ax.fill(angulos, valores, color=COR[linha["modelo"]], alpha=0.18)
    ax.set_title("Seis índices normalizados", fontsize=13.5, color=TEXTO, pad=18)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.16), fontsize=9)

    ax2 = fig.add_subplot(1, 2, 2)
    componentes = [
        ("I_fidelidade", PESOS["fidelidade"], AZUL, "Fidelidade 35%"),
        ("I_anti_alucinacao", PESOS["anti_alucinacao"], VERDE, "Anti-alucinação 20%"),
        ("I_estabilidade", PESOS["estabilidade"], AMBAR, "Estabilidade 15%"),
        ("I_velocidade", PESOS["velocidade"], CINZA, "Velocidade 15%"),
        ("I_throughput", PESOS["throughput"], AZUL_CLARO, "Throughput 5%"),
        ("I_eficiencia_escrita", PESOS["eficiencia_escrita"], "#0E7490", "Escrita útil 10%"),
    ]
    y = np.arange(len(MODELOS))
    esquerda = np.zeros(len(MODELOS))
    for coluna, peso, cor, nome in componentes:
        fatia = tabela[coluna].to_numpy() * peso
        ax2.barh(y, fatia, left=esquerda, color=cor, label=nome, height=0.62)
        esquerda += fatia
    ax2.set_yticks(y, [ROTULO[m] for m in MODELOS])
    for i, score in enumerate(tabela["score_composto_0_100"]):
        ax2.text(score + 1, i, "{:.1f}".format(score).replace(".", ","), va="center", fontsize=10, color=TEXTO)
    ax2.set_xlim(0, 112)
    ax2.set_xlabel("Pontos no score composto (0–100)")
    ax2.set_title("Score composto", fontsize=13.5)
    ax2.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.42, -0.18), ncol=2)
    limpar = ax2
    limpar.spines["top"].set_visible(False)
    limpar.spines["right"].set_visible(False)
    limpar.grid(axis="x", color=GRADE, linewidth=0.6)
    fig.suptitle("Índices normalizados e score composto", fontsize=16, color=AZUL, fontweight="bold")
    rodape(fig, "Pesos: fidelidade 35%, anti-alucinação 20%, estabilidade 15%, velocidade 15%, throughput 5%, eficiência de escrita 10%. Fonte: benchmark_modelos_seminario.json.")
    salvar(fig, "comp01_radar_e_score_global")


def comp02(df):
    fig, eixos = plt.subplots(1, 2, figsize=(13.5, 5.8), constrained_layout=True)
    fig.suptitle("Distribuição da latência nas 20 perguntas", fontsize=16, color=AZUL, fontweight="bold")
    ax = eixos[0]
    plotavel = df.copy()
    plotavel["rotulo"] = plotavel["modelo"].map(ROTULO)
    ordem = [ROTULO[m] for m in MODELOS]
    sns.boxplot(
        data=plotavel, x="rotulo", y="total_s", order=ordem, hue="rotulo",
        palette=[COR[m] for m in MODELOS], legend=False, ax=ax, width=0.45,
        showmeans=True, meanprops={"marker": "D", "markerfacecolor": "white", "markeredgecolor": TEXTO, "markersize": 7},
        flierprops={"marker": ""},
    )
    sns.stripplot(data=plotavel, x="rotulo", y="total_s", order=ordem, color=TEXTO, size=3.5, alpha=0.45, ax=ax, jitter=0.12)
    for i, modelo in enumerate(MODELOS):
        serie = df.loc[df["modelo"] == modelo, "total_s"]
        p90 = float(np.percentile(serie, 90))
        ax.hlines(p90, i - 0.28, i + 0.28, colors=VERMELHO, linestyles="--", linewidth=1)
        ax.text(i, p90 + 8, "P90 {:.0f} s".format(p90), ha="center", fontsize=8, color=VERMELHO)
    ax.set_xlabel("")
    ax.set_ylabel("Tempo total (s)")
    ax.set_title("Vinte tempos, média e P90", fontsize=13.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=GRADE, linewidth=0.6)

    ax = eixos[1]
    for modelo in MODELOS:
        serie = np.sort(df.loc[df["modelo"] == modelo, "total_s"].to_numpy())
        y = np.arange(1, len(serie) + 1) / len(serie) * 100
        ax.step(serie, y, where="post", color=COR[modelo], lw=2, label=ROTULO[modelo])
    for marca, texto in ((60, "60 s"), (120, "120 s"), (240, "240 s")):
        ax.axvline(marca, color=GRADE, ls="--", lw=1)
        ax.text(marca + 4, 8, texto, fontsize=8, color=SECUNDARIO, rotation=90)
    ax.set_xlim(0, 420)
    ax.set_ylim(0, 105)
    ax.set_xlabel("Tempo limite (s)")
    ax.set_ylabel("Perguntas respondidas até esse tempo (%)")
    ax.set_title("Curva acumulada", fontsize=13.5)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(color=GRADE, linewidth=0.6)
    rodape(fig, "Fonte: benchmark_modelos_seminario.json. Losango branco = média. Linha vermelha tracejada = P90.")
    salvar(fig, "comp02_distribuicao_latencia_percentis")


def comp03(tabela):
    fig, eixos = plt.subplots(1, 2, figsize=(13.5, 5.8), constrained_layout=True)
    fig.suptitle("Paradoxo do throughput e da escrita útil", fontsize=16, color=AZUL, fontweight="bold")
    ax = eixos[0]
    x = np.arange(len(MODELOS))
    toks = tabela["tok_s_media"].to_numpy()
    estouros = tabela["estouro_n"].to_numpy()
    barras = ax.bar(x - 0.18, toks, 0.36, color=[COR[m] for m in MODELOS], label="tok/s médio")
    ax2 = ax.twinx()
    ax2.bar(x + 0.18, estouros, 0.36, color=VERMELHO, alpha=0.85, label="Estouros")
    ax2.spines["top"].set_visible(False)
    ax.set_xticks(x, [ROTULO[m] for m in MODELOS])
    ax.set_ylabel("tok/s médio")
    ax2.set_ylabel("Estouros em 20 perguntas")
    ax.set_title("Mais tok/s não significa mais resposta", fontsize=13.5)
    for barra, valor in zip(barras, toks):
        ax.text(barra.get_x() + barra.get_width() / 2, valor + 0.08, "{:.1f}".format(valor).replace(".", ","), ha="center", fontsize=9)
    for i, valor in enumerate(estouros):
        ax2.text(i + 0.18, valor + 0.3, "{:.0f}".format(valor), ha="center", fontsize=9, color=VERMELHO)
    ax.spines["top"].set_visible(False)
    ax.grid(axis="y", color=GRADE, linewidth=0.6)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, frameon=False, fontsize=8, loc="upper right")

    ax = eixos[1]
    largura = 0.34
    ax.bar(x - largura / 2, tabela["decode_s_media"], largura, color=CINZA, label="Decode (já inclui o think)")
    ax.bar(x + largura / 2, tabela["escrita_util_s_media"], largura, color=VERDE, label="Escrita útil")
    ax.set_xticks(x, [ROTULO[m] for m in MODELOS])
    ax.set_ylabel("Segundos médios")
    ax.set_title("Quanto do decode virou texto", fontsize=13.5)
    for i, (dec, esc) in enumerate(zip(tabela["decode_s_media"], tabela["escrita_util_s_media"])):
        ax.text(i + largura / 2, esc + 3, "{:.0f}%".format(100 * esc / dec), ha="center", fontsize=8, color=VERDE)
    ax.legend(frameon=False, fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=GRADE, linewidth=0.6)
    rodape(fig, "Fonte: benchmark_modelos_seminario.json. Escrita útil = max(0, decode_s − think_s). O empilhado de tempo já está em fig05.")
    salvar(fig, "comp03_decomposicao_tempo_e_eficiencia_tokens")


def comp04(tabela):
    fig, eixos = plt.subplots(1, 2, figsize=(14, 6.0), constrained_layout=True)
    fig.suptitle("Fidelidade bruta, fidelidade com contexto completo e falhas", fontsize=16, color=AZUL, fontweight="bold")
    ax = eixos[0]
    x = np.arange(len(MODELOS))
    largura = 0.34
    ax.bar(x - largura / 2, tabela["taxa_fiel_18_pct"], largura, color=AZUL, label="18 constitucionais")
    ax.bar(x + largura / 2, tabela["taxa_fiel_14_pct"], largura, color=VERDE, label="14 com contexto completo")
    ax.set_xticks(x, [ROTULO[m] for m in MODELOS])
    ax.set_ylabel("Taxa FIEL (%)")
    ax.set_ylim(0, 110)
    ax.set_title("Gerador isolado dos quatro furos de contexto", fontsize=13.5)
    for i, (a, b, n18, n14) in enumerate(zip(tabela["taxa_fiel_18_pct"], tabela["taxa_fiel_14_pct"], tabela["fiel_18"], tabela["fiel_14_limpas"])):
        ax.text(i - largura / 2, a + 1.5, "{}/18".format(int(n18)), ha="center", fontsize=8)
        ax.text(i + largura / 2, b + 1.5, "{}/14".format(int(n14)), ha="center", fontsize=8)
    ax.legend(frameon=False, fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=GRADE, linewidth=0.6)

    ax = eixos[1]
    falhas = ["alerta_n", "alucinacao_n", "estouro_n"]
    nomes = ["Alerta", "Alucinação", "Estouro no think"]
    cores = [AMBAR, VERMELHO, "#7F1D1D"]
    largura = 0.22
    for j, (coluna, nome, cor) in enumerate(zip(falhas, nomes, cores)):
        vals = tabela[coluna].to_numpy()
        ax.bar(x + (j - 1) * largura, vals, largura, color=cor, label=nome)
        for i, valor in enumerate(vals):
            ax.text(i + (j - 1) * largura, valor + 0.15, str(int(valor)), ha="center", fontsize=8)
    ax.set_xticks(x, [ROTULO[m] for m in MODELOS])
    ax.set_ylabel("Contagem em 20 perguntas")
    ax.set_title("Falhas, sem repetir o empilhado geral", fontsize=13.5)
    ax.legend(frameon=False, fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=GRADE, linewidth=0.6)
    rodape(fig, "Fonte: benchmark_modelos_seminario.json e benchmark_contexto_congelado_20.json. As 14 excluem Q08, Q09, Q10 e Q16.")
    salvar(fig, "comp04_precisao_bruta_ajustada_e_falhas")


def comp05(df):
    fig, eixos = plt.subplots(1, 2, figsize=(14, 6.5), constrained_layout=True)
    fig.suptitle("Desempenho por área e por tipo de pergunta", fontsize=16, color=AZUL, fontweight="bold")
    ax = eixos[0]
    matriz = []
    anot = []
    for nome, ids in AREAS:
        linha = []
        notas = []
        for modelo in MODELOS:
            grupo = df[(df["modelo"] == modelo) & (df["area_grupo"] == nome)]
            if nome == "Fora de escopo":
                ok = int(((grupo["auditoria"] == "SEM_CITACAO") & ~grupo["estourou"]).sum())
                taxa = 100 * ok / len(grupo)
                notas.append("{:.0f}%\n{}/{}".format(taxa, ok, len(grupo)))
            else:
                ok = int((grupo["auditoria"] == "FIEL").sum())
                taxa = 100 * ok / len(grupo)
                notas.append("{:.0f}%\n{}/{}".format(taxa, ok, len(grupo)))
            linha.append(taxa)
        matriz.append(linha)
        anot.append(notas)
    grade = np.array(matriz)
    im = ax.imshow(grade, cmap="YlGnBu", vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(3), ["4B", "7B", "8B"])
    ax.set_yticks(range(len(AREAS)), [nome for nome, _ in AREAS])
    for i in range(grade.shape[0]):
        for j in range(grade.shape[1]):
            ax.text(j, i, anot[i][j], ha="center", va="center", fontsize=8, color="white" if grade[i, j] >= 60 else TEXTO)
    ax.set_title("FIEL por área; fora de escopo = livre correto", fontsize=13.5)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04).set_label("%")

    ax = eixos[1]
    tipos = ["Simples", "Composta", "Fora de escopo"]

    def tipo(linha):
        if linha["ood"]:
            return "Fora de escopo"
        if linha["classe"] == "COMPOSTA":
            return "Composta"
        return "Simples"

    df = df.copy()
    df["tipo"] = df.apply(tipo, axis=1)
    x = np.arange(len(tipos))
    largura = 0.24
    for j, modelo in enumerate(MODELOS):
        medias = []
        for nome in tipos:
            serie = df[(df["modelo"] == modelo) & (df["tipo"] == nome)]["total_s"]
            medias.append(float(serie.mean()) if len(serie) else 0)
        ax.bar(x + (j - 1) * largura, medias, largura, color=COR[modelo], label=ROTULO[modelo])
        for i, valor in enumerate(medias):
            ax.text(i + (j - 1) * largura, valor + 4, "{:.0f}".format(valor), ha="center", fontsize=7.5)
    ax.set_xticks(x, tipos)
    ax.set_ylabel("Latência média (s)")
    ax.set_title("Simples, composta e fora de escopo", fontsize=13.5)
    ax.legend(frameon=False, fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=GRADE, linewidth=0.6)
    rodape(fig, "Fonte: benchmark_modelos_seminario.json. Composta = classe COMPOSTA no contexto congelado.")
    salvar(fig, "comp05_desempenho_por_area_e_perfil")


def comp06(df):
    fig, eixos = plt.subplots(1, 2, figsize=(14, 5.8), constrained_layout=True)
    fig.suptitle("Custo do prefill e relação com o score do retriever", fontsize=16, color=AZUL, fontweight="bold")
    ax = eixos[0]
    for modelo in MODELOS:
        grupo = df[df["modelo"] == modelo].dropna(subset=["tokens_entrada", "prefill_s"])
        x = grupo["tokens_entrada"].to_numpy()
        y = grupo["prefill_s"].to_numpy()
        ax.scatter(x, y, s=28, alpha=0.75, color=COR[modelo], label=ROTULO[modelo])
        coef = np.polyfit(x, y, 1)
        xs = np.linspace(x.min(), x.max(), 50)
        previsto = np.polyval(coef, x)
        ss_res = float(np.sum((y - previsto) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        r2 = 1 - ss_res / ss_tot if ss_tot else 0
        ax.plot(xs, np.polyval(coef, xs), color=COR[modelo], lw=1.4)
        taxa = float(np.mean(x / np.maximum(y, 1e-6)))
        ax.text(0.02, 0.96 - 0.08 * MODELOS.index(modelo), "{}  R²={:.2f}  {:.0f} tok/s de prefill".format(modelo, r2, taxa), transform=ax.transAxes, fontsize=8, color=COR[modelo])
    ax.set_xlabel("Tokens de entrada")
    ax.set_ylabel("Prefill (s)")
    ax.set_ylim(bottom=0)
    ax.set_title("Leitura do prompt na CPU", fontsize=13.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(color=GRADE, linewidth=0.6)

    ax = eixos[1]
    for modelo in MODELOS:
        grupo = df[df["modelo"] == modelo]
        for _, linha in grupo.iterrows():
            if linha["estourou"] or linha["auditoria"] == "ALUCINACAO_ARTIGO":
                marca = "X"
            elif linha["ood"]:
                marca = "D"
            elif linha["auditoria"] == "FIEL":
                marca = "o"
            else:
                marca = "s"
            ax.scatter(linha["top1"], linha["total_s"], c=COR[modelo], marker=marca, s=36, alpha=0.8)
    ax.axvline(0.12, color=CINZA, ls="--", lw=1)
    ax.axvline(0.25, color=VERDE, ls="--", lw=1)
    ax.set_xlabel("Topo do reranker que decidiu o modo")
    ax.set_ylabel("Tempo total (s)")
    ax.set_title("Círculo FIEL, X falha, losango OOD, quadrado outro", fontsize=13.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(color=GRADE, linewidth=0.6)
    rodape(fig, "Fonte: benchmark_modelos_seminario.json e benchmark_contexto_congelado_20.json. Reta por np.polyfit de grau 1.")
    salvar(fig, "comp06_correlacao_contexto_score_latencia")


def comp07(p1, tabela):
    readme = (RAIZ / "README.md").read_text(encoding="utf-8")
    exigir = ("19,4 s", "5,0 tok/s", "61,0 s", "15/15")
    if not all(t in readme for t in exigir):
        raise SystemExit("Números da Fase 2 não estão no README.")
    pontos = [
        ("qwen2.5:3b\nFase 2, n=20", 19.4, 100.0, 5.0, CINZA),
        ("qwen2.5:7b otimizado\nFase 2, n=20", 61.0, 100.0, None, CINZA),
        ("qwen3:8b sem think\nParte 1, n=3", p1["total_s"], 100 * p1["fiel"] / p1["n"], p1["tok_s"], AZUL_CLARO),
        ("qwen2.5:7b direto\nFase 3.3, n=20", float(tabela.loc[tabela["modelo"] == "qwen2.5:7b", "total_s_media"].iloc[0]), float(tabela.loc[tabela["modelo"] == "qwen2.5:7b", "taxa_fiel_18_pct"].iloc[0]), float(tabela.loc[tabela["modelo"] == "qwen2.5:7b", "tok_s_media"].iloc[0]), VERDE),
        ("qwen3:8b + think\nFase 3.3, n=20", float(tabela.loc[tabela["modelo"] == "qwen3:8b", "total_s_media"].iloc[0]), float(tabela.loc[tabela["modelo"] == "qwen3:8b", "taxa_fiel_18_pct"].iloc[0]), float(tabela.loc[tabela["modelo"] == "qwen3:8b", "tok_s_media"].iloc[0]), AZUL),
        ("qwen3:4b + think\nFase 3.3, n=20", float(tabela.loc[tabela["modelo"] == "qwen3:4b", "total_s_media"].iloc[0]), float(tabela.loc[tabela["modelo"] == "qwen3:4b", "taxa_fiel_18_pct"].iloc[0]), float(tabela.loc[tabela["modelo"] == "qwen3:4b", "tok_s_media"].iloc[0]), AMBAR),
    ]
    fig, ax = plt.subplots(figsize=(13.5, 6.4), constrained_layout=True)
    fig.suptitle("Todos os geradores já medidos", fontsize=16, color=AZUL, fontweight="bold")
    ax.set_title("Fase 2: 15 perguntas diretas, 15/15 fiéis. Fase 3.3: 18 constitucionais da suíte cega. Parte 1: só os casos 01, 09 e 10.", fontsize=10.5, color=SECUNDARIO)
    deslocamentos = {
        "qwen2.5:3b\nFase 2, n=20": (10, 8),
        "qwen2.5:7b otimizado\nFase 2, n=20": (10, -28),
        "qwen3:8b sem think\nParte 1, n=3": (-118, 10),
    }
    for nome, tempo, taxa, tok, cor in pontos:
        tamanho = 180 if tok is None else 80 + tok * 70
        ax.scatter([tempo], [taxa], s=tamanho, color=cor, alpha=0.9, zorder=3, edgecolors="white", linewidths=0.6)
        ax.annotate(nome, (tempo, taxa), textcoords="offset points", xytext=deslocamentos.get(nome, (8, 8)), fontsize=8)
    ax.set_xlabel("Latência média (s)")
    ax.set_ylabel("Taxa FIEL da suíte indicada (%)")
    ax.set_xlim(0, 460)
    ax.set_ylim(0, 118)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(color=GRADE, linewidth=0.6)
    rodape(fig, "Fonte: README.md (Fase 2: 19,4 s, 5,0 tok/s e 61,0 s, 15/15) e os JSON/JSONL da Parte 1 e da Fase 3.3. O 7B da Fase 2 não tem tok/s publicado; a bolha não codifica velocidade.")
    salvar(fig, "comp07_evolucao_historica_llms")


def comp08():
    exigir_readme()
    ab = json.loads((DADOS / "resultados_ab_reranker.json").read_text(encoding="utf-8"))
    por_nome = {item["cenario"]: item for item in ab}
    fig, eixos = plt.subplots(1, 2, figsize=(14, 5.8), constrained_layout=True)
    fig.suptitle("Roteadores e buscadores, fora da geração", fontsize=16, color=AZUL, fontweight="bold")
    ax = eixos[0]
    metricas = ["Acurácia geral", "Macro F1", "Margem ≥ 0,15"]
    sete = [74.1, 74.7, 94.3]
    nove = [76.4, 78.1, 97.0]
    x = np.arange(len(metricas))
    ax.bar(x - 0.18, sete, 0.36, color=CINZA, label="7 classes, 270 perguntas")
    ax.bar(x + 0.18, nove, 0.36, color=AZUL, label="9 classes, 5-fold")
    for i, (a, b) in enumerate(zip(sete, nove)):
        ax.text(i - 0.18, a + 1, "{:.1f}".format(a).replace(".", ","), ha="center", fontsize=8)
        ax.text(i + 0.18, b + 1, "{:.1f}".format(b).replace(".", ","), ha="center", fontsize=8)
    ax.set_xticks(x, metricas)
    ax.set_ylim(0, 128)
    ax.set_ylabel("Percentual")
    ax.set_title("7 classes contra 9 classes", fontsize=13.5)
    ax.text(
        0.02, 0.96,
        "9 classes também: OAB 64,6% e leigas 83,1%",
        transform=ax.transAxes, ha="left", va="top", fontsize=8, color=TEXTO,
        bbox={"boxstyle": "round,pad=0.3", "fc": "white", "ec": GRADE},
    )
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=GRADE, linewidth=0.6)

    ax = eixos[1]
    nomes = ["BM25+RRF\nRecall@5", "BGE-M3 denso\nRecall@5", "MiniLM\n45 consultas", "FP32\n45 consultas", "ONNX INT8\n45 consultas"]
    valores = [94.4, 95.2, 42 / 45 * 100, 100, 100]
    cores = [CINZA, AZUL_CLARO, CINZA, CINZA, VERDE]
    barras = ax.bar(nomes, valores, color=cores, width=0.68)
    for barra, valor in zip(barras, valores):
        ax.text(barra.get_x() + barra.get_width() / 2, valor + 1, "{:.1f}%".format(valor).replace(".", ","), ha="center", fontsize=8)
    fp32 = por_nome["A PyTorch FP32 top12"]["media_s"]
    onnx = por_nome["B ONNX INT8 top8"]["media_s"]
    ax.set_ylim(0, 138)
    ax.set_ylabel("Percentual de acerto da métrica do rótulo")
    ax.set_title("Busca e reranker", fontsize=13.5)
    ax.text(
        0.5, 0.93,
        "FP32 {} s → ONNX {} s ({}×). MiniLM = 42/45.\nLatência do MiniLM não está no repositório.".format(
            "{:.2f}".format(fp32).replace(".", ","),
            "{:.2f}".format(onnx).replace(".", ","),
            "{:.1f}".format(fp32 / onnx).replace(".", ","),
        ),
        transform=ax.transAxes, ha="center", va="top", fontsize=8, color=SECUNDARIO,
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=GRADE, linewidth=0.6)
    rodape(fig, "Fonte: README.md (7 classes, 9 classes, Recall@5, 42/45) e resultados_ab_reranker.json (tempos FP32 e ONNX).")
    salvar(fig, "comp08_comparativo_modelos_recuperacao_e_roteamento")


LEGENDAS = [
    ("comp01_radar_e_score_global", "Radar e score composto", "Seis índices de 0 a 100 e a soma ponderada dos três geradores da suíte de 20."),
    ("comp02_distribuicao_latencia_percentis", "Percentis e curva acumulada", "Os 20 tempos de cada modelo, com média, P90 e a fração respondida até 60, 120 e 240 s."),
    ("comp03_decomposicao_tempo_e_eficiencia_tokens", "Throughput contra escrita útil", "O 4B é o mais rápido em tok/s e o que menos converte o decode em resposta."),
    ("comp04_precisao_bruta_ajustada_e_falhas", "Fidelidade bruta e ajustada", "18 constitucionais contra as 14 em que o contexto da fase A estava completo."),
    ("comp05_desempenho_por_area_e_perfil", "Área e tipo de pergunta", "Taxa por domínio e latência de pergunta simples, composta e fora de escopo."),
    ("comp06_correlacao_contexto_score_latencia", "Prefill e score do retriever", "Reta de prefill por tokens de entrada e os 60 pontos no corte 0,12 e 0,25."),
    ("comp07_evolucao_historica_llms", "Geradores de todas as fases", "Fase 2, Parte 1 e a suíte congelada, com a amostra escrita em cada bolha."),
    ("comp08_comparativo_modelos_recuperacao_e_roteamento", "Roteadores e buscadores", "Sete contra nove classes, busca densa contra BM25 e os três rerankers."),
]


def galeria(tabela):
    cabeca = "".join("<th>{}</th>".format(col) for col in ("modelo", "taxa_fiel_18_pct", "taxa_fiel_14_pct", "total_s_mediana_p50", "total_s_p90", "total_s_p95", "score_composto_0_100"))
    corpo = []
    for _, linha in tabela.iterrows():
        corpo.append("<tr><td>{}</td><td>{:.1f}</td><td>{:.1f}</td><td>{:.1f}</td><td>{:.1f}</td><td>{:.1f}</td><td>{:.1f}</td></tr>".format(
            linha["modelo"], linha["taxa_fiel_18_pct"], linha["taxa_fiel_14_pct"], linha["total_s_mediana_p50"], linha["total_s_p90"], linha["total_s_p95"], linha["score_composto_0_100"],
        ))
    artigos = []
    for nome, titulo, legenda in LEGENDAS:
        png = (SAIDA / "png_300dpi" / "{}.png".format(nome)).read_bytes()
        emb = base64.b64encode(png).decode("ascii")
        artigos.append(
            "<article><h2>{}</h2><p>{}</p><img src=\"data:image/png;base64,{}\" alt=\"{}\">"
            "<p><a href=\"svg/{}.svg\">SVG</a> · <a href=\"pdf/{}.pdf\">PDF</a> · <a href=\"png_300dpi/{}.png\">PNG</a></p></article>".format(
                titulo, legenda, emb, titulo, nome, nome, nome,
            )
        )
    html = (
        "<!DOCTYPE html><html lang=\"pt-BR\"><head><meta charset=\"utf-8\"><title>Comparativo de modelos</title>"
        "<style>body{{font-family:Segoe UI,sans-serif;margin:32px;color:#0F172A}} table{{border-collapse:collapse;margin:16px 0 32px}}"
        "td,th{{border:1px solid #E2E8F0;padding:6px 10px}} img{{width:100%;height:auto;border:1px solid #E2E8F0}} a{{color:#1B365D}}</style>"
        "</head><body><h1>Comparativo de modelos</h1><table><tr>{}</tr>{}</table>{}</body></html>"
    ).format(cabeca, "".join(corpo), "".join(artigos))
    (SAIDA / "preview_comparativo_modelos.html").write_text(html, encoding="utf-8")


def auditar():
    from PIL import Image
    faltas = []
    for nome, _, _ in LEGENDAS:
        for pasta, ext in (("svg", "svg"), ("pdf", "pdf"), ("png_300dpi", "png")):
            caminho = SAIDA / pasta / "{}.{}".format(nome, ext)
            tamanho = caminho.stat().st_size if caminho.is_file() else 0
            extra = ""
            if ext == "png" and caminho.is_file():
                with Image.open(caminho) as img:
                    extra = " {}x{} dpi={}".format(*img.size, img.info.get("dpi"))
            print("{:8} {:>10}{}".format(ext, tamanho, extra), caminho.name)
            if tamanho <= 10_000:
                faltas.append(str(caminho))
    html = SAIDA / "preview_comparativo_modelos.html"
    csv = SAIDA / "resumo_indices_comparativos.csv"
    print("csv", csv.stat().st_size, "html", html.stat().st_size)
    if csv.stat().st_size <= 100 or html.stat().st_size <= 10_000:
        faltas.append("csv ou html pequeno")
    if AVISOS:
        print("Avisos:")
        for aviso in AVISOS:
            print(" -", aviso)
    else:
        print("Nenhum aviso de fonte ou layout.")
    if faltas:
        raise SystemExit(faltas)


def main():
    estilo()
    df, _ = carregar()
    if len(df) != 60:
        raise SystemExit("Esperava 60 gerações, veio {}".format(len(df)))
    tabela = indices(df)
    SAIDA.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(SAIDA / "resumo_indices_comparativos.csv", index=False, float_format="%.6f")
    comp01(tabela)
    comp02(df)
    comp03(tabela)
    comp04(tabela)
    comp05(df)
    comp06(df)
    comp07(parte1(), tabela)
    comp08()
    galeria(tabela)
    print(tabela[["modelo", "taxa_fiel_18_pct", "taxa_fiel_14_pct", "total_s_mediana_p50", "total_s_p90", "total_s_p95", "score_composto_0_100"]].to_string(index=False))
    auditar()


if __name__ == "__main__":
    main()
