# -*- coding: utf-8 -*-
"""Uma pergunta real no qwen3:4b, sem think."""

import json
import sys
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(1, str(_RAIZ))

from src.rag.pipeline import executar_rag

PERGUNTA = (
    "Se um brasileiro naturalizado cometer um crime comum lá fora, "
    "o Brasil pode autorizar a extradição dele, ou ele tem a mesma proteção "
    "que um brasileiro nato?"
)


def main() -> None:
    trace = executar_rag(PERGUNTA, modelo="qwen3:4b", usar_think=False, usar_rag=True)
    auditoria = trace.get("auditoria") or {}
    tempos = trace.get("tempos_s") or {}
    resumo = {
        "modelo": trace.get("modelo_usado"),
        "usar_think": trace.get("usar_think"),
        "think_chars": trace.get("think_chars"),
        "think_s": trace.get("think_s"),
        "raciocinio_vazio": not (trace.get("raciocinio_llm") or "").strip(),
        "estourou_no_think": trace.get("estourou_no_think"),
        "modo": trace.get("modo_resposta"),
        "auditoria": auditoria.get("status"),
        "prefill_s": trace.get("prefill_s"),
        "decode_s": trace.get("eval_s"),
        "tok_s": trace.get("tok_s"),
        "total_s": tempos.get("total"),
        "artigos": [item.get("artigo_id") for item in (trace.get("artigos_recuperados") or [])],
        "resposta": trace.get("resposta_llm") or "",
    }
    print(json.dumps(resumo, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
