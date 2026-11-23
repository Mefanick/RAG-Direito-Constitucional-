# -*- coding: utf-8 -*-
"""Treina o roteador de 9 classes com a OAB e as perguntas leigas.

O CSV de 300 e as 17 perguntas da bateria cega são só uma trava:
se aparecerem no treino, o script para. O joblib anterior é copiado
para *.bak_pre_33 antes da primeira troca.
"""

import importlib.util
import shutil
import unicodedata
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import StratifiedKFold

from src.rag.encoder import obter_encoder

_RAIZ = Path(__file__).resolve().parents[2]
_CSV_OAB = _RAIZ / "datasets" / "oab_treino_limpo.csv"
_CSV_LEIGO = _RAIZ / "dados" / "perguntas_leigas_roteador.csv"
_PKL = _RAIZ / "modelos" / "constituicao_vetorizada.pkl"
_DESTINO = _RAIZ / "modelos" / "roteador_constitucional.joblib"
_CSV_300 = (
    _RAIZ / "datasets" / "dataset_teste_300_perguntas.csv",
    Path(r"c:\Users\nicol\Downloads\dataset_teste_300_perguntas.csv"),
)


def _matriz(textos: list[str]) -> np.ndarray:
    encoder = obter_encoder()
    # As perguntas cabem em poucas centenas de tokens. A janela cheia de
    # 8.192 estoura a RAM quando o lote inclui um artigo longo.
    encoder.max_seq_length = 512
    vetores = encoder.encode(
        textos,
        convert_to_tensor=False,
        normalize_embeddings=True,
        batch_size=8,
        show_progress_bar=True,
    )
    return np.asarray(vetores, dtype=np.float64)


def _classificador() -> LogisticRegression:
    return LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        C=1.0,
        random_state=42,
    )


def _normalizar(texto: str) -> str:
    base = unicodedata.normalize("NFKD", str(texto).strip().lower())
    base = "".join(caractere for caractere in base if not unicodedata.combining(caractere))
    return " ".join(base.replace("?", " ").replace("!", " ").replace(",", " ").split())


def _perguntas_proibidas() -> set[str]:
    spec = importlib.util.spec_from_file_location(
        "bateria_cega_fase33",
        _RAIZ / "testes" / "avaliar_bateria_cega_fase33.py",
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Não achei avaliar_bateria_cega_fase33.py para a trava de vazamento.")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    proibidas = {_normalizar(item["pergunta"]) for item in modulo.PERGUNTAS}
    for caminho in _CSV_300:
        if not caminho.is_file():
            continue
        tabela = pd.read_csv(caminho, encoding="utf-8")
        coluna = "texto" if "texto" in tabela.columns else "pergunta"
        proibidas.update(_normalizar(valor) for valor in tabela[coluna].astype(str))
    return proibidas


def _bloquear_vazamento(perguntas: list[str], proibidas: set[str]) -> None:
    vazadas = [frase for frase in perguntas if _normalizar(frase) in proibidas]
    if vazadas:
        raise SystemExit("Vazamento no treino do roteador:\n" + "\n".join(vazadas))


def main() -> None:
    if not _PKL.is_file():
        raise FileNotFoundError("Índice não encontrado em {}.".format(_PKL))
    cache = torch.load(_PKL, weights_only=False)
    classes_indice = sorted(set(cache["intencoes"]))
    if len(classes_indice) != 9:
        raise SystemExit("O índice não tem 9 intenções: {}".format(classes_indice))
    oab_bruto = pd.read_csv(_CSV_OAB, encoding="utf-8")
    leigo = pd.read_csv(_CSV_LEIGO, encoding="utf-8")
    fora = sorted(set(oab_bruto["intencao"]) - set(classes_indice))
    oab = oab_bruto[oab_bruto["intencao"].isin(classes_indice)]
    print("OAB no CSV: {}. Depois do filtro das 9 classes: {}. Rótulos fora: {}.".format(
        len(oab_bruto), len(oab), fora or "nenhum"
    ))
    if set(leigo["intencao"]) != set(classes_indice):
        raise SystemExit("O CSV leigo não cobre exatamente as 9 classes do índice.")
    contagem = leigo["intencao"].value_counts()
    if (contagem != 25).any() or len(contagem) != 9:
        raise SystemExit("Cada classe leiga precisa de 25 perguntas. Obtido:\n{}".format(contagem))
    hibrido = _RAIZ / "datasets" / "dataset_hibrido_treino.csv"
    if hibrido.is_file():
        extra = len(pd.read_csv(hibrido, encoding="utf-8")) - len(oab_bruto)
        print("dataset_hibrido_treino.csv tem {} linhas além das {} questões da OAB. São trechos de lei, não prova, e ficam de fora.".format(extra, len(oab_bruto)))
    perguntas_leigas = leigo["pergunta"].astype(str).tolist()
    proibidas = _perguntas_proibidas()
    _bloquear_vazamento(perguntas_leigas, proibidas)
    print("Trava de vazamento: {} frases proibidas (bateria cega + CSV de 300). Nenhuma pergunta leiga coincide.".format(len(proibidas)))
    textos = oab["texto"].astype(str).tolist() + perguntas_leigas
    rotulos = oab["intencao"].astype(str).tolist() + leigo["intencao"].astype(str).tolist()
    origem = ["oab"] * len(oab) + ["leigo"] * len(perguntas_leigas)
    print("OAB usada: {}. Leigas: {}. Total: {}.".format(len(oab), len(perguntas_leigas), len(textos)))
    matriz = _matriz(textos)
    rotulos_np = np.asarray(rotulos)
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    previsto = np.empty(len(rotulos), dtype=object)
    margens = np.zeros(len(rotulos))
    for treino_idx, teste_idx in folds.split(matriz, rotulos_np):
        modelo = _classificador()
        modelo.fit(matriz[treino_idx], rotulos_np[treino_idx])
        proba = modelo.predict_proba(matriz[teste_idx])
        ordem = np.argsort(proba, axis=1)[:, ::-1]
        previsto[teste_idx] = modelo.classes_[ordem[:, 0]]
        margens[teste_idx] = proba[np.arange(len(teste_idx)), ordem[:, 0]] - proba[np.arange(len(teste_idx)), ordem[:, 1]]
    acerto = previsto == rotulos_np
    f1_global = float(f1_score(rotulos_np, previsto, average="macro", zero_division=0))
    print("Acurácia out-of-fold: {:.3f}".format(acerto.mean()))
    print("Macro F1 out-of-fold: {:.3f}".format(f1_global))
    for nome in ("oab", "leigo"):
        mascara = np.asarray(origem) == nome
        print("Acurácia {}: {:.3f} (n={})".format(nome, acerto[mascara].mean(), int(mascara.sum())))
    print(classification_report(rotulos_np, previsto, zero_division=0))
    alta = margens >= 0.15
    print("Cobertura margem >= 0,15: {:.3f}".format(alta.mean()))
    if alta.any():
        print("Acurácia na margem >= 0,15: {:.3f}".format(acerto[alta].mean()))
    relatorio = classification_report(rotulos_np, previsto, output_dict=True, zero_division=0)
    piores = [classe for classe in classes_indice if relatorio.get(classe, {}).get("f1-score", 0) < 0.45]
    if f1_global < 0.60 or piores:
        print("Validação insuficiente. Joblib não foi substituído. Classes fracas: {}".format(piores or "macro F1"))
        return
    final = _classificador()
    final.fit(matriz, rotulos)
    if final.coef_.shape != (9, 1024):
        raise SystemExit("coef_ inesperado: {}".format(final.coef_.shape))
    backup = _DESTINO.parent / (_DESTINO.name + ".bak_pre_33")
    if _DESTINO.is_file() and not backup.is_file():
        shutil.copy2(_DESTINO, backup)
        print("Backup: {}".format(backup))
    _DESTINO.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(final, _DESTINO)
    print("Modelo gravado em {}".format(_DESTINO))
    print("Classes: {}".format(", ".join(str(classe) for classe in final.classes_)))
    print("coef_: {}".format(final.coef_.shape))


if __name__ == "__main__":
    main()
