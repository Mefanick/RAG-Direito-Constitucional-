# -*- coding: utf-8 -*-
"""Oito figuras do seminário, lidas dos arquivos do repositório. Offline."""

import json
import textwrap
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
SAIDA = AQUI / "graficos_seminario"
DADOS = RAIZ / "benchmarks"
AVISOS = []

AZUL = "#1B365D"
VERDE = "#0F766E"
AMBAR = "#D97706"
VERMELHO = "#DC2626"
CINZA = "#64748B"
FUNDO = "#FFFFFF"
GRADE = "#E2E8F0"
TEXTO = "#0F172A"
SECUNDARIO = "#475569"
REJEICAO = "#FECACA"

CORES_TITULO = {
    "Direitos e Garantias Fundamentais": AZUL,
    "Organização dos Poderes": VERDE,
    "Tributação e Orçamento": AMBAR,
    "Ordem Social": "#0369A1",
    "Organização do Estado": "#7C3AED",
    "Disposições Gerais / ADCT": CINZA,
    "Controle de Constitucionalidade": VERMELHO,
    "Ordem Econômica e Financeira": "#0E7490",
    "Princípios Fundamentais": "#B45309",
}
ORDEM_TITULO = list(CORES_TITULO)

STATUS_COR = {
    "FIEL": VERDE,
    "Alerta": AMBAR,
    "Alucinação": VERMELHO,
    "OOD OK": CINZA,
    "Sem cit.": "#94A3B8",
    "Estouro": "#881337",
}


def estilo():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 14,
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
        "axes.grid": False,
    })


def exigir_readme():
    texto = (RAIZ / "README.md").read_text(encoding="utf-8")
    trechos = ["0,646", "0,764", "0,781", "0,831", "97,0%", "0,952", "0,944", "0,870", "0,930", "45/45"]
    faltando = [t for t in trechos if t not in texto]
    if faltando:
        raise SystemExit("README.md não contém: {}".format(", ".join(faltando)))


def limpar_eixo(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=GRADE, linewidth=0.6)
    ax.set_axisbelow(True)


def rodape(fig, fonte):
    fig.text(0.01, 0.01, fonte, color=SECUNDARIO, fontsize=8, va="bottom")


def margem(fig, bottom, top=0.86, left=0.08, right=0.98, wspace=0.32, hspace=0.28):
    fig.subplots_adjust(left=left, right=right, top=top, bottom=bottom, wspace=wspace, hspace=hspace)


def salvar(fig, nome):
    destinos = {
        "svg": SAIDA / "svg" / "{}.svg".format(nome),
        "pdf": SAIDA / "pdf" / "{}.pdf".format(nome),
        "png_300dpi": SAIDA / "png_300dpi" / "{}.png".format(nome),
    }
    for pasta in destinos.values():
        pasta.parent.mkdir(parents=True, exist_ok=True)
    with warnings.catch_warnings(record=True) as pegos:
        warnings.simplefilter("always")
        fig.savefig(destinos["svg"])
        fig.savefig(destinos["pdf"])
        fig.savefig(destinos["png_300dpi"], dpi=300)
    for aviso in pegos:
        AVISOS.append("{}: {}".format(nome, aviso.message))
    plt.close(fig)


def ler_jsonl(nome):
    caminho = DADOS / nome
    linhas = []
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        if linha.strip():
            linhas.append(json.loads(linha))
    return {item["id"]: item for item in linhas}


def placar(nome, chave):
    dados = ler_jsonl(nome)
    return sum(1 for i in range(1, 13) if dados["{:02d}".format(i)].get(chave))


def pontos_drift():
    pontos = []
    arquivos = [
        ("v1", "resultados_bateria_cega_fase33_drift_check.jsonl"),
        ("v2", "resultados_bateria_cega_fase33_drift_check_v2.jsonl"),
        ("v3", "resultados_bateria_cega_fase33_drift_check_v3.jsonl"),
        ("v4", "resultados_bateria_cega_fase33_drift_check_v4.jsonl"),
    ]
    for versao, nome in arquivos:
        for item in ler_jsonl(nome).values():
            cos = item.get("hyde_cosseno")
            rr = item.get("hyde_reranker")
            if cos is None or rr is None:
                continue
            pontos.append({
                "versao": versao,
                "id": item["id"],
                "cos": float(cos),
                "rr": max(float(rr), 1e-6),
                "rejeitado": float(cos) < 0.52 or float(rr) < 0.002,
            })
    return pontos


def carregar_benchmark():
    contexto = json.loads((DADOS / "benchmark_contexto_congelado_20.json").read_text(encoding="utf-8"))
    modelos = json.loads((DADOS / "benchmark_modelos_seminario.json").read_text(encoding="utf-8"))
    return contexto["perguntas"], modelos["resultados"], modelos.get("resumo_modelos") or {}


def desfecho(item):
    if item.get("id") in ("Q19", "Q20") and item.get("auditoria") == "SEM_CITACAO" and not item.get("estourou_no_think"):
        return "OOD OK"
    if item.get("estourou_no_think"):
        return "Estouro"
    status = item.get("auditoria")
    if status == "FIEL":
        return "FIEL"
    if status == "ALERTA_SUBDISPOSITIVO":
        return "Alerta"
    if status == "ALUCINACAO_ARTIGO":
        return "Alucinação"
    return "Sem cit."


def caixa(ax, x, y, w, h, texto, borda, face="#F8FAFC", fontsize=9):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.4, edgecolor=borda, facecolor=face,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center", fontsize=fontsize, color=TEXTO, linespacing=1.25)


def seta(ax, x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=9,
        linewidth=1.0, color=CINZA, shrinkA=2, shrinkB=2,
    ))


def fig01():
    fig, ax = plt.subplots(figsize=(16, 8.5))
    margem(fig, bottom=0.08, top=0.88, left=0.012, right=0.988, wspace=0.2)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9.2)
    ax.axis("off")
    fig.suptitle("Arquitetura híbrida do chat constitucional", fontsize=16, color=AZUL, fontweight="bold")
    ax.set_title(
        "Fluxo stateless. Borda azul: camada neural. Borda verde: guarda determinística.",
        fontsize=11, color=SECUNDARIO, pad=8,
    )

    def faixa(centro, altura):
        return centro - altura / 2

    h1, h2, h3, h4 = 1.12, 1.22, 1.52, 1.22
    y1, y2, y3, y4 = faixa(7.6, h1), faixa(5.6, h2), faixa(3.4, h3), faixa(1.3, h4)
    caixa(ax, 0.40, y1, 3.15, h1, "Pergunta atual\n(stateless)", AZUL, "#EFF6FF")
    caixa(ax, 4.20, y1, 7.85, h1, "Controles UI\n(4B / 7B / 8B · Think ON/OFF · RAG ou LLM Puro)", CINZA, "#F1F5F9")
    seta(ax, 3.55, 7.6, 4.20, 7.6)

    largura, intervalo = 2.55, 0.50
    xs = [0.40 + i * (largura + intervalo) for i in range(4)]
    etapas = [
        "Atalho social\n(0,0 s)",
        "BGE-M3 1024-d\n+ Roteador 9 classes",
        "Composta / Multi-Query\n+ Cosseno (1.772 chunks)",
        "Reranker ONNX INT8\n(top 8, janela 512)",
    ]
    for x, texto in zip(xs, etapas):
        caixa(ax, x, y2, largura, h2, texto, AZUL, "#EFF6FF")
    for i in range(3):
        seta(ax, xs[i] + largura, 5.6, xs[i + 1], 5.6)
    seta(ax, 1.97, y1, 1.67, y2 + h2)

    caixa(ax, 13.05, y2, 2.50, h2, "LLM Puro\n(Ollama direto)", AZUL, "#EFF6FF")
    caixa(ax, 13.05, y3, 2.50, h3, "Sem base\n/ Sem auditoria", VERDE, "#F0FDFA")
    seta(ax, 12.05, 7.15, 14.30, y2 + h2)
    seta(ax, 14.30, y2, 14.30, y3 + h3)

    largura3, intervalo3 = 3.50, 0.52
    xs3 = [0.40 + i * (largura3 + intervalo3) for i in range(3)]
    decisoes = [
        ("Topo ≥ 0,25\nAlta confiança\n(Parent-Doc)", "#F0FDFA"),
        ("Topo < 0,25\nHyDE + Drift Guard\n(0,52 / 0,002)\n+ fusão na cinza", "#FFFBEB"),
        ("Topo < 0,12\nConversa livre\n(aviso fixo, zero artigos)", "#FEF2F2"),
    ]
    for x, (texto, face) in zip(xs3, decisoes):
        caixa(ax, x, y3, largura3, h3, texto, VERDE, face)
    reranker_x = xs[3] + largura / 2
    for x in xs3:
        seta(ax, reranker_x, y2, x + largura3 / 2, y3 + h3)
    seta(ax, xs3[1] + largura3, y3 + h3 - 0.08, xs[3] + 0.25, y2 + 0.08)

    largura4, intervalo4 = 3.50, 0.52
    xs4 = [0.40 + i * (largura4 + intervalo4) for i in range(3)]
    finais = [
        ("Gerador Ollama\n(flash_attention, KV q8_0,\nnum_ctx 3072/2048)", AZUL, "#EFF6FF"),
        ("Auditor determinístico\n(artigo + inciso/parágrafo)", VERDE, "#F0FDFA"),
        ("Resposta auditada\n+ telemetria", AZUL, "#EFF6FF"),
    ]
    for x, (texto, borda, face) in zip(xs4, finais):
        caixa(ax, x, y4, largura4, h4, texto, borda, face)
    for x in xs3:
        seta(ax, x + largura3 / 2, y3, xs4[0] + largura4 / 2, y4 + h4)
    seta(ax, xs4[0] + largura4, 1.3, xs4[1], 1.3)
    seta(ax, xs4[1] + largura4, 1.3, xs4[2], 1.3)
    rodape(fig, "Fonte: arquitetura descrita em README.md e src/rag (diagrama; sem medida nova).")
    salvar(fig, "fig01_arquitetura_hibrida")


def projetar(embeddings):
    try:
        import umap
        with warnings.catch_warnings(record=True) as pegos:
            warnings.simplefilter("always")
            modelo = umap.UMAP(
                n_neighbors=18, min_dist=0.15, metric="cosine", random_state=42,
                n_jobs=1, compatibility_layout=True,
            )
            xy = modelo.fit_transform(embeddings)
        for aviso in pegos:
            AVISOS.append("Fig. 02: {}".format(aviso.message))
        return xy, "UMAP (n_neighbors=18, min_dist=0,15, cosseno, random_state=42)"
    except Exception as exc:
        AVISOS.append("UMAP indisponível ({}). Projeção t-SNE.".format(exc))
        from sklearn.manifold import TSNE
        xy = TSNE(n_components=2, metric="cosine", random_state=42, init="random", perplexity=30).fit_transform(embeddings)
        return xy, "projeção t-SNE (métrica cosseno, random_state=42); UMAP não foi usado"


def fig02():
    pacote = torch.load(RAIZ / "modelos" / "constituicao_vetorizada.pkl", weights_only=False)
    if "textos_busca" in pacote:
        raise SystemExit("O índice não está limpo: textos_busca presente.")
    vetores = np.asarray(pacote["embeddings"], dtype=np.float32)
    rotulos = list(pacote["intencoes"])
    if vetores.shape != (1772, 1024) or len(rotulos) != 1772:
        raise SystemExit("Forma inesperada do índice: {}".format(vetores.shape))
    xy, nome = projetar(vetores)
    fig, ax = plt.subplots(figsize=(12, 8.5), constrained_layout=True)
    fig.suptitle("Mapa semântico da Constituição de 1988", fontsize=16, color=AZUL, fontweight="bold")
    ax.set_title("N = 1.772 chunks | Embeddings BGE-M3 (1024-dim) | Índice limpo, sem textos_busca | {}".format(nome), fontsize=10.5, color=SECUNDARIO)
    for rotulo in ORDEM_TITULO:
        mascara = np.array([item == rotulo for item in rotulos])
        if not mascara.any():
            continue
        ax.scatter(xy[mascara, 0], xy[mascara, 1], s=16, alpha=0.72, c=CORES_TITULO[rotulo], label="{} ({})".format(rotulo, int(mascara.sum())), linewidths=0)
        if rotulo in (
            "Direitos e Garantias Fundamentais",
            "Organização dos Poderes",
            "Tributação e Orçamento",
            "Ordem Social",
            "Disposições Gerais / ADCT",
        ):
            centro = xy[mascara].mean(axis=0)
            ax.annotate(
                rotulo.split(" / ")[0],
                centro, fontsize=8, color=TEXTO, ha="center",
                bbox={"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.85},
            )
    ax.legend(frameon=False, fontsize=8, loc="best")
    ax.set_xlabel("Componente 1")
    ax.set_ylabel("Componente 2")
    limpar_eixo(ax)
    ax.grid(True, color=GRADE, linewidth=0.5)
    rodape(fig, "Fonte: modelos/constituicao_vetorizada.pkl · campo intencoes e embeddings.")
    salvar(fig, "fig02_mapa_semantico_cf88")
    return nome, int(vetores.shape[0])


def fig03():
    ab = json.loads((DADOS / "resultados_ab_reranker.json").read_text(encoding="utf-8"))
    por_nome = {item["cenario"]: item for item in ab}
    fp32 = por_nome["A PyTorch FP32 top12"]
    onnx = por_nome["B ONNX INT8 top8"]
    fig, eixos = plt.subplots(1, 2, figsize=(13, 5.8))
    margem(fig, bottom=0.14, top=0.86, left=0.22, right=0.97, wspace=0.28)
    fig.suptitle("Roteador, busca densa e reranker", fontsize=16, color=AZUL, fontweight="bold")
    ax = eixos[0]
    rotulos = [
        "OAB, 127 questões",
        "Geral, 5-fold",
        "Macro F1, 5-fold",
        "Leigas, 225 questões",
        "Margem ≥ 0,15\n(37,5% dos casos)",
    ]
    valores = [64.6, 76.4, 78.1, 83.1, 97.0]
    cores = [CINZA, AZUL, AZUL, VERDE, VERDE]
    y = np.arange(len(rotulos))
    ax.barh(y, valores, color=cores, height=0.62)
    ax.set_yticks(y, rotulos)
    ax.set_xlim(0, 110)
    ax.set_xlabel("Percentual")
    ax.set_title("Roteador de 9 classes", fontsize=12, color=TEXTO)
    for i, valor in enumerate(valores):
        ax.text(valor + 1.2, i, "{:.1f}%".format(valor).replace(".", ","), va="center", fontsize=9, color=TEXTO)
    ax.text(
        0.98, 0.05,
        "Busca densa BGE-M3\nRecall@5 = 95,2%\nBM25 + RRF = 94,4%",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=9,
        bbox={"boxstyle": "round", "fc": "white", "ec": GRADE},
    )
    limpar_eixo(ax)

    ax = eixos[1]
    nomes = ["PyTorch FP32", "ONNX INT8"]
    tempos = [fp32["media_s"], onnx["media_s"]]
    barras = ax.bar(nomes, tempos, color=[CINZA, AZUL], width=0.55)
    ax.set_ylabel("Latência quente média (s)")
    ax.set_title("Reranker nas 45 consultas", fontsize=12, color=TEXTO)
    for barra, tempo in zip(barras, tempos):
        ax.text(barra.get_x() + barra.get_width() / 2, tempo + 0.4, "{:.2f} s".format(tempo).replace(".", ","), ha="center", fontsize=10)
    ax.set_ylim(0, 26)
    ax.set_xlim(-0.55, 1.55)
    fator = fp32["media_s"] / onnx["media_s"]
    ax.text(
        1, 13.5,
        "ONNX {:,.1f}× mais rápido\nCorte 0,25: 15/15 Recall@5\ne 30/30 OOD\nRecall@1 densa 87,0% → {:.1f}%".format(
            fator, onnx["recall_1"] * 100
        ).replace(".", ","),
        ha="center", va="center", fontsize=8,
        bbox={"boxstyle": "round,pad=0.35", "fc": "#F0FDFA", "ec": VERDE},
    )
    limpar_eixo(ax)
    rodape(fig, "Fonte: README.md (roteador e Recall@5 densa/BM25; Recall@1 87,0% da busca densa) e resultados_ab_reranker.json (latência e Recall@1 do reranker).")
    salvar(fig, "fig03_evolucao_retriever_onnx")


def fig04():
    series = [
        ("Baseline\n1ª passagem", placar("resultados_bateria_cega_baseline_sem_ponte.jsonl", "recuperou_esperado_p1"), CINZA),
        ("Ponte leiga\n1ª passagem", placar("resultados_bateria_cega_com_ponte.jsonl", "recuperou_esperado_p1"), VERMELHO),
        ("Drift v1\n0,50 / 0,08", placar("resultados_bateria_cega_fase33_drift_check.jsonl", "recuperou_esperado_final"), AMBAR),
        ("Drift v2", placar("resultados_bateria_cega_fase33_drift_check_v2.jsonl", "recuperou_esperado_final"), AZUL),
        ("Drift v3", placar("resultados_bateria_cega_fase33_drift_check_v3.jsonl", "recuperou_esperado_final"), AZUL),
        ("Drift v4\ncongelado", placar("resultados_bateria_cega_fase33_drift_check_v4.jsonl", "recuperou_esperado_final"), VERDE),
    ]
    fig, eixos = plt.subplots(1, 2, figsize=(13.5, 6.2))
    margem(fig, bottom=0.22, top=0.86, left=0.09, right=0.98, wspace=0.28)
    fig.suptitle("Ablação da recuperação e Drift Guard", fontsize=16, color=AZUL, fontweight="bold")
    ax = eixos[0]
    xs = np.arange(len(series))
    barras = ax.bar(xs, [item[1] for item in series], color=[item[2] for item in series], width=0.72)
    ax.set_xticks(xs)
    ax.set_xticklabels([item[0] for item in series], fontsize=10)
    plt.setp(ax.get_xticklabels(), rotation=22, ha="right", rotation_mode="anchor")
    ax.set_ylim(0, 14)
    ax.set_ylabel("Inéditas com o artigo esperado (de 12)")
    ax.set_title("Trajetória das 12 inéditas", fontsize=12)
    for barra, item in zip(barras, series):
        ax.text(barra.get_x() + barra.get_width() / 2, item[1] + 0.15, "{}/12".format(item[1]), ha="center", fontsize=9)
    ax.annotate(
        "Ensaio negativo —\nrollback",
        xy=(0.78, series[1][1]),
        xytext=(0.05, 9.45),
        ha="left",
        va="bottom",
        arrowprops={"arrowstyle": "->", "color": VERMELHO, "shrinkB": 2},
        color=VERMELHO,
        fontsize=8,
        bbox={"boxstyle": "round,pad=0.3", "fc": "white", "ec": VERMELHO},
    )
    ax.text(
        5, 12.45,
        "v4 congelada:\n2/2 OOD livres\n2/2 regressões ok",
        ha="center", va="bottom", fontsize=8,
        bbox={"boxstyle": "round", "fc": "#F0FDFA", "ec": VERDE},
    )
    limpar_eixo(ax)

    ax = eixos[1]
    pontos = pontos_drift()
    cores_v = {"v1": CINZA, "v2": AMBAR, "v3": "#0369A1", "v4": AZUL}
    for versao, cor in cores_v.items():
        grupo = [p for p in pontos if p["versao"] == versao]
        ax.scatter([p["cos"] for p in grupo], [p["rr"] for p in grupo], s=28, alpha=0.8, c=cor, label=versao, zorder=3)
    ax.axvline(0.52, color=VERMELHO, ls="--", lw=1)
    ax.axhline(0.002, color=VERMELHO, ls="--", lw=1)
    ax.axvspan(0.35, 0.52, color=REJEICAO, alpha=0.35, zorder=0)
    ax.set_yscale("symlog", linthresh=0.001)
    ax.set_xlim(0.35, 1.02)
    ax.set_xlabel("Cosseno BGE-M3 (pergunta × HyDE)")
    ax.set_ylabel("Reranker ONNX (pergunta × HyDE)")
    ax.set_title("Cortes calibrados: 0,52 e 0,002", fontsize=12)
    for alvo_id, alvo_v, texto in (("14", "v1", "#14 v1  0,491 / 0,000"), ("05", "v1", "#05 v1  0,527 / 0,001")):
        alvo = next(p for p in pontos if p["id"] == alvo_id and p["versao"] == alvo_v)
        if alvo_id == "05":
            ax.annotate(
                texto,
                xy=(alvo["cos"], alvo["rr"]),
                xytext=(alvo["cos"] + 0.012, 0.00095),
                ha="left",
                va="top",
                fontsize=8,
                color=VERMELHO,
                bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "none", "pad": 1},
            )
        else:
            ax.annotate(texto, (alvo["cos"], alvo["rr"]), textcoords="offset points", xytext=(8, 8), fontsize=8, color=VERMELHO)
    ax.legend(frameon=False, title="Varredura")
    limpar_eixo(ax)
    ax.grid(True, color=GRADE, linewidth=0.5)
    rodape(fig, "Fonte: resultados_bateria_cega_baseline_sem_ponte.jsonl, com_ponte.jsonl e fase33_drift_check*.jsonl.")
    salvar(fig, "fig04_ablacao_fase33_e_drift_guard")


def fig05():
    fixes = ler_jsonl("resultados_bateria_cega_fase33_fixes_parcial.jsonl")
    rapido = ler_jsonl("resultados_bateria_cega_parte1_rapido_check.jsonl")
    _, resultados, resumo = carregar_benchmark()
    fig, eixos = plt.subplots(1, 2, figsize=(13.5, 6.2))
    margem(fig, bottom=0.15, top=0.86, left=0.07, right=0.98, wspace=0.28)
    fig.suptitle("Anatomia da latência na CPU", fontsize=16, color=AZUL, fontweight="bold")
    ax = eixos[0]
    casos = ["09", "10"]
    x = np.arange(len(casos))
    antes = [fixes[c]["tempos"]["total_s"] for c in casos]
    depois = [rapido[c]["tempos"]["total_s"] for c in casos]
    dec_a = [fixes[c]["tempos"]["decode_s"] for c in casos]
    dec_d = [rapido[c]["tempos"]["decode_s"] for c in casos]
    largura = 0.18
    ax.bar(x - 1.5 * largura, antes, largura, color=CINZA, label="Total, think ligado")
    ax.bar(x - 0.5 * largura, depois, largura, color=AZUL, label="Total, think desligado")
    ax.bar(x + 0.5 * largura, dec_a, largura, color="#94A3B8", label="Decode, think ligado")
    ax.bar(x + 1.5 * largura, dec_d, largura, color=VERDE, label="Decode, think desligado")
    ax.set_xticks(x, ["Caso 09", "Caso 10"])
    ax.set_ylabel("Segundos")
    ax.set_title("Parte 1: think automático removido", fontsize=12)
    queda = (dec_a[1] - dec_d[1]) / dec_a[1] * 100
    ax.annotate(
        "decode do caso 10: −{:.0f}%".format(queda),
        xy=(1 + 1.5 * largura, dec_d[1]),
        xytext=(1.72, 360),
        ha="left",
        va="center",
        arrowprops={"arrowstyle": "->", "color": VERDE},
        fontsize=8,
        color=TEXTO,
        bbox={"boxstyle": "round,pad=0.3", "fc": "white", "ec": GRADE},
    )
    ax.set_xlim(-0.55, 2.85)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    limpar_eixo(ax)

    ax = eixos[1]
    ordem = ["qwen3:4b", "qwen3:8b", "qwen2.5:7b"]
    rotulos = ["qwen3:4b + think", "qwen3:8b + think", "qwen2.5:7b direto"]
    pre, think, escrita, totais, toks = [], [], [], [], []
    for modelo in ordem:
        grupo = [item for item in resultados if item["modelo"] == modelo]
        p = float(np.mean([item["prefill_s"] for item in grupo]))
        t = float(np.mean([item["think_s"] or 0 for item in grupo]))
        d = float(np.mean([item["decode_s"] for item in grupo]))
        pre.append(p)
        think.append(t)
        escrita.append(max(0.0, d - t))
        totais.append(float(np.mean([item["total_s"] for item in grupo])))
        toks.append(float(np.mean([item["tok_s"] for item in grupo])))
    y = np.arange(len(ordem))
    ax.barh(y, pre, color=AZUL, label="Prefill")
    ax.barh(y, think, left=pre, color=AMBAR, label="Raciocínio")
    esquerda = np.array(pre) + np.array(think)
    ax.barh(y, escrita, left=esquerda, color=VERDE, label="Escrita útil (decode − think)")
    ax.set_yticks(y, rotulos)
    ax.set_xlabel("Segundos médios nas 20 perguntas")
    ax.set_title("Benchmark final, i5-1235U", fontsize=12)
    for i, (total, tok) in enumerate(zip(totais, toks)):
        ax.text(pre[i] + think[i] + escrita[i] + 4, i, "{:.0f} s · {:.1f} tok/s".format(total, tok).replace(".", ","), va="center", fontsize=8)
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    ax.set_xlim(0, 390)
    limpar_eixo(ax)
    rodape(fig, "Fonte: resultados_bateria_cega_fase33_fixes_parcial.jsonl, parte1_rapido_check.jsonl e benchmark_modelos_seminario.json. Escrita útil = max(0, decode_s − think_s).")
    salvar(fig, "fig05_latencia_cpu_anatomia")


def fig06():
    _, resultados, _ = carregar_benchmark()
    fig, eixos = plt.subplots(1, 2, figsize=(14, 6.2))
    margem(fig, bottom=0.20, top=0.86, left=0.08, right=0.98, wspace=0.28)
    fig.suptitle("Velocidade, fidelidade e desfechos", fontsize=16, color=AZUL, fontweight="bold")
    ax = eixos[0]
    modelos = ["qwen3:4b", "qwen2.5:7b", "qwen3:8b"]
    cores = {"qwen3:4b": AMBAR, "qwen2.5:7b": VERDE, "qwen3:8b": AZUL}
    for modelo in modelos:
        grupo = [item for item in resultados if item["modelo"] == modelo and item["id"] not in ("Q19", "Q20")]
        tempo = float(np.mean([item["total_s"] for item in grupo]))
        fiel = sum(1 for item in grupo if item.get("auditoria") == "FIEL")
        taxa = 100 * fiel / len(grupo)
        ax.scatter([tempo], [taxa], s=160, color=cores[modelo], zorder=3)
        ax.annotate(
            "{}\n{}/18 = {:.1f}%\n{:.0f} s".format(modelo, fiel, taxa, tempo).replace(".", ","),
            (tempo, taxa), textcoords="offset points", xytext=(10, 8), fontsize=8,
        )
    ax.set_xlabel("Tempo médio total nas 18 constitucionais (s)")
    ax.set_ylabel("Taxa FIEL (%)")
    ax.set_xlim(0, 420)
    ax.set_ylim(0, 100)
    ax.annotate("← mais rápido", xy=(40, 8), fontsize=9, color=SECUNDARIO)
    ax.set_title("Fronteira nas 18 perguntas constitucionais", fontsize=12)
    limpar_eixo(ax)
    ax.grid(True, color=GRADE, linewidth=0.5)

    ax = eixos[1]
    classes = ["FIEL", "Alerta", "Alucinação", "OOD OK", "Sem cit.", "Estouro"]
    contagens = []
    for modelo in modelos:
        grupo = [item for item in resultados if item["modelo"] == modelo]
        contagens.append([sum(1 for item in grupo if desfecho(item) == classe) for classe in classes])
    matriz = np.array(contagens, dtype=float)
    totais = matriz.sum(axis=1, keepdims=True)
    percentual = matriz / totais * 100
    esquerda = np.zeros(len(modelos))
    y = np.arange(len(modelos))
    for j, classe in enumerate(classes):
        ax.barh(y, percentual[:, j], left=esquerda, color=STATUS_COR[classe], label=classe, height=0.62)
        for i, valor in enumerate(matriz[:, j]):
            if valor >= 1:
                ax.text(esquerda[i] + percentual[i, j] / 2, i, str(int(valor)), ha="center", va="center", color="white", fontsize=8)
        esquerda += percentual[:, j]
    ax.set_yticks(y, modelos)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Participação nas 20 perguntas (%)")
    ax.set_title("60 gerações", fontsize=12)
    ax.legend(frameon=False, fontsize=8, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    limpar_eixo(ax)
    ax.grid(False)
    rodape(fig, "Fonte: benchmark_modelos_seminario.json. OOD OK = Q19 e Q20 com SEM_CITACAO e sem estouro.")
    salvar(fig, "fig06_benchmark_pareto_e_desfechos")


def fig07():
    contextos, resultados, _ = carregar_benchmark()
    modelos = ["qwen3:4b", "qwen2.5:7b", "qwen3:8b"]
    ids = [item["id"] for item in contextos]
    furos = {"Q08", "Q09", "Q10", "Q16"}
    rotulos = []
    for item in contextos:
        marca = "*" if item["id"] in furos else ""
        area = item.get("area") or ""
        curto = area.split("—")[0].strip()
        if len(curto) > 28:
            curto = curto[:26] + "…"
        rotulos.append("{}{}  {}".format(item["id"], marca, curto))
    grade = np.zeros((20, 3))
    textos = [[""] * 3 for _ in range(20)]
    indice_status = {nome: i for i, nome in enumerate(["FIEL", "Alerta", "Alucinação", "OOD OK", "Sem cit.", "Estouro"])}
    mapa = {(item["id"], item["modelo"]): item for item in resultados}
    for i, qid in enumerate(ids):
        for j, modelo in enumerate(modelos):
            item = mapa[(qid, modelo)]
            classe = desfecho(item)
            grade[i, j] = indice_status[classe]
            textos[i][j] = "{}\n{:.0f} s".format(classe, item["total_s"])
    from matplotlib.colors import ListedColormap
    cmap = ListedColormap([STATUS_COR[nome] for nome in indice_status])
    fig, eixos = plt.subplots(1, 2, figsize=(14, 8.5), gridspec_kw={"width_ratios": [1.85, 1]})
    margem(fig, bottom=0.11, top=0.90, left=0.20, right=0.98, wspace=0.42)
    fig.suptitle("Vinte casos no mesmo contexto", fontsize=16, color=AZUL, fontweight="bold")
    ax = eixos[0]
    ax.imshow(grade, cmap=cmap, vmin=-0.5, vmax=5.5, aspect="auto")
    ax.set_xticks(range(3), ["4B + think", "2.5:7B direto", "8B + think"])
    ax.set_yticks(range(20), rotulos)
    ax.tick_params(axis="y", labelsize=8)
    for i in range(20):
        for j in range(3):
            ax.text(j, i, textos[i][j], ha="center", va="center", color="white", fontsize=7)
    ax.set_title("Auditoria e tempo", fontsize=12)
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax = eixos[1]
    scores = []
    for item in contextos:
        p1 = item.get("top1_score_p1") or 0
        p2 = item.get("top1_score_p2")
        scores.append(float(p2) if p2 is not None and float(p2) >= float(p1) else float(p1))
    y = np.arange(20)
    ax.barh(y, scores[::-1], color=[AZUL if s >= 0.25 else AMBAR if s >= 0.12 else CINZA for s in scores[::-1]], height=0.72)
    ax.axvline(0.12, color=CINZA, ls="--", lw=1)
    ax.axvline(0.25, color=VERDE, ls="--", lw=1)
    ax.set_yticks(y, rotulos[::-1])
    ax.tick_params(axis="y", labelsize=8)
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("Topo do reranker que decidiu o modo")
    ax.set_title("Separação Q01–Q20", fontsize=12, pad=16)
    ax.text(0.12, 18.8, "0,12", color=CINZA, fontsize=8, ha="center", va="bottom", bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.9})
    ax.text(0.25, 18.8, "0,25", color=VERDE, fontsize=8, ha="center", va="bottom", bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.9})
    limpar_eixo(ax)
    rodape(
        fig,
        "* Contexto da Fase A incompleto: Q08, Q09, Q10 e Q16. Separação OOD: Q19 = 0,003 e Q20 = 0,006.\n"
        "Fonte: benchmark_contexto_congelado_20.json e benchmark_modelos_seminario.json.",
    )
    salvar(fig, "fig07_matriz_20_casos_e_separacao_ood")


def _trecho(texto, largura, linhas):
    bruto = " ".join(str(texto or "").split())
    if not bruto:
        return "(resposta visível vazia)"
    cheio = textwrap.fill(bruto, width=largura)
    partes = cheio.splitlines()
    if len(partes) > linhas:
        partes = partes[:linhas]
        partes[-1] = partes[-1].rstrip(".") + "…"
    return "\n".join(partes)


def fig08():
    contextos, resultados, _ = carregar_benchmark()
    por_id = {item["id"]: item for item in contextos}
    mapa = {(item["id"], item["modelo"]): item for item in resultados}
    c1 = mapa[("Q02", "qwen3:8b")]
    c2 = mapa[("Q19", "qwen2.5:7b")]
    c3 = mapa[("Q01", "qwen3:4b")]
    ctx1 = por_id["Q02"]
    ctx2 = por_id["Q19"]
    fig, ax = plt.subplots(figsize=(14, 6.5), constrained_layout=True)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.suptitle("Três respostas reais do mesmo experimento", fontsize=16, color=AZUL, fontweight="bold")
    cartoes = [
        (0.02, VERDE, "Alta precisão · qwen3:8b + think",
         "Q02  {}\nArtigo no contexto: Art. 5º, LI".format(_trecho(ctx1["pergunta"], 42, 2)),
         _trecho(c1["resposta"], 46, 7),
         "FIEL   {:.0f} s   prefill {:.0f} s   {:.1f} tok/s".format(c1["total_s"], c1["prefill_s"], c1["tok_s"])),
        (0.35, CINZA, "Fora de escopo · qwen2.5:7b",
         "Q19  topo {:.3f} < 0,12\n{}".format(
             max(ctx2.get("top1_score_p2") or 0, ctx2.get("top1_score_p1") or 0),
             _trecho(ctx2["pergunta"], 42, 2),
         ),
         _trecho(c2["resposta"], 46, 7),
         "CONVERSA LIVRE   {:.0f} s".format(c2["total_s"])),
        (0.68, VERMELHO, "Limite · qwen3:4b + think",
         "Q01  estourou_no_think = verdadeiro\nthink {:.0f} s · resposta visível ausente".format(c3["think_s"] or 0),
         "Pensamento (não mostrado como resposta):\n" + _trecho(c3.get("pensamento"), 46, 6),
         "resposta com {:.0f} caracteres   total {:.0f} s".format(len(c3.get("resposta") or ""), c3["total_s"])),
    ]
    for x, cor, titulo, cabeca, corpo, rod in cartoes:
        ax.add_patch(FancyBboxPatch(
            (x, 0.08), 0.30, 0.82,
            boxstyle="round,pad=0.008,rounding_size=0.015",
            linewidth=1.6, edgecolor=cor, facecolor="#F8FAFC",
        ))
        ax.text(x + 0.015, 0.82, titulo, fontsize=10, color=cor, fontweight="bold", va="top")
        ax.text(x + 0.015, 0.74, cabeca, fontsize=8, color=TEXTO, va="top")
        ax.text(x + 0.015, 0.58, corpo, fontsize=7.5, color=TEXTO, va="top")
        ax.text(x + 0.015, 0.12, rod, fontsize=8, color=SECUNDARIO, va="bottom")
    rodape(fig, "Fonte: benchmark_modelos_seminario.json e benchmark_contexto_congelado_20.json. Trechos literais, só cortados no fim da caixa.")
    salvar(fig, "fig08_cartoes_comparativos_respostas")


LEGENDAS = [
    ("fig01_arquitetura_hibrida", "Arquitetura híbrida", "Fluxo stateless, com o ramo LLM puro separado do RAG constitucional e os cortes 0,25, 0,12 e do Drift Guard."),
    ("fig02_mapa_semantico_cf88", "Mapa semântico da CF/88", "1.772 embeddings BGE-M3 coloridos pela intenção gravada no índice limpo."),
    ("fig03_evolucao_retriever_onnx", "Roteador e reranker", "Acurácia do roteador de 9 classes e a troca do reranker PyTorch pelo ONNX INT8."),
    ("fig04_ablacao_fase33_e_drift_guard", "Ablação e Drift Guard", "Placar das 12 inéditas e o plano cosseno × reranker das reescritas HyDE."),
    ("fig05_latencia_cpu_anatomia", "Anatomia da latência", "Queda do decode ao desligar o think automático e a composição prefill, raciocínio e escrita no benchmark."),
    ("fig06_benchmark_pareto_e_desfechos", "Fronteira e desfechos", "Tempo contra taxa FIEL nas 18 constitucionais e a distribuição das 60 gerações."),
    ("fig07_matriz_20_casos_e_separacao_ood", "Matriz dos 20 casos", "Status por modelo e o topo do reranker que separa Q19 e Q20."),
    ("fig08_cartoes_comparativos_respostas", "Três respostas reais", "Q02 no 8B, Q19 no 7B e o estouro de raciocínio do 4B em Q01."),
]


def galeria():
    import base64
    blocos = []
    for nome, titulo, legenda in LEGENDAS:
        png = (SAIDA / "png_300dpi" / "{}.png".format(nome)).read_bytes()
        embutido = base64.b64encode(png).decode("ascii")
        blocos.append(
            "<article><h2>{titulo}</h2><p>{legenda}</p>"
            "<img src=\"data:image/png;base64,{embutido}\" alt=\"{titulo}\">"
            "<p><a href=\"svg/{nome}.svg\">SVG</a> · <a href=\"pdf/{nome}.pdf\">PDF</a> · <a href=\"png_300dpi/{nome}.png\">PNG 300 DPI</a></p></article>".format(
                titulo=titulo, legenda=legenda, nome=nome, embutido=embutido,
            )
        )
    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Galeria do seminário</title>
<style>
body {{ font-family: "Segoe UI", sans-serif; margin: 32px; color: #0F172A; background: #fff; }}
article {{ margin: 0 0 48px; }}
img {{ width: 100%; height: auto; border: 1px solid #E2E8F0; }}
a {{ color: #1B365D; }}
</style>
</head>
<body>
<h1>Figuras do seminário</h1>
{corpo}
</body>
</html>
""".format(corpo="\n".join(blocos))
    (SAIDA / "preview_galeria.html").write_text(html, encoding="utf-8")


def auditar(projecao, n_chunks):
    from PIL import Image
    print("Projeção da Fig. 02: {} | chunks plotados: {}".format(projecao, n_chunks))
    faltas = []
    for nome, _, _ in LEGENDAS:
        for pasta, ext in (("svg", "svg"), ("pdf", "pdf"), ("png_300dpi", "png")):
            caminho = SAIDA / pasta / "{}.{}".format(nome, ext)
            tamanho = caminho.stat().st_size if caminho.is_file() else 0
            if tamanho <= 10_000:
                faltas.append("{} ({} bytes)".format(caminho, tamanho))
            else:
                extra = ""
                if ext == "png":
                    with Image.open(caminho) as img:
                        dpi = img.info.get("dpi")
                        extra = " {}x{} dpi={}".format(img.size[0], img.size[1], dpi)
                print("{:8} {:>10} bytes{}".format(ext, tamanho, extra), caminho.name)
    galeria_path = SAIDA / "preview_galeria.html"
    if galeria_path.stat().st_size <= 10_000:
        faltas.append(str(galeria_path))
    if AVISOS:
        print("Avisos Matplotlib/UMAP:")
        for aviso in AVISOS:
            print(" -", aviso)
    else:
        print("Nenhum aviso de fonte ou layout.")
    if faltas:
        raise SystemExit("Arquivos pequenos ou ausentes: {}".format(faltas))
    print("Galeria:", galeria_path)


def main():
    estilo()
    exigir_readme()
    for pasta in ("svg", "pdf", "png_300dpi"):
        (SAIDA / pasta).mkdir(parents=True, exist_ok=True)
    fig01()
    projecao, n_chunks = fig02()
    fig03()
    fig04()
    fig05()
    fig06()
    fig07()
    fig08()
    galeria()
    auditar(projecao, n_chunks)


if __name__ == "__main__":
    main()
