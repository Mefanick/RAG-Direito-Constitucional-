# -*- coding: utf-8 -*-
"""O raciocínio do qwen3 não pode aparecer na resposta. Sem Ollama."""

import sys
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(1, str(_RAIZ))

from src.rag.gerador import _corpo_ollama, _com_diretiva_think, separar_raciocinio, estourou_no_pensamento


def testar_payload_4b() -> None:
    mensagens = _com_diretiva_think(
        [{"role": "user", "content": "Qual é a regra?"}],
        "qwen3:4b",
        False,
    )
    corpo = _corpo_ollama("qwen3:4b", mensagens, False, 0.2, 450, 3072, False)
    if corpo.get("think") is not False:
        raise SystemExit("qwen3:4b com usar_think=False deveria enviar think false: {}".format(corpo))
    if not corpo["messages"][-1]["content"].endswith("/no_think"):
        raise SystemExit("faltou /no_think no turno do usuário")
    ligado = _corpo_ollama("qwen3:8b", [{"role": "user", "content": "oi"}], False, 0.2, 1200, 3072, True)
    if ligado.get("think") is not True:
        raise SystemExit("qwen3:8b com think ligado deveria enviar think true")
    sem = _corpo_ollama("qwen2.5:7b", [{"role": "user", "content": "oi"}], False, 0.2, 450, 2048, False)
    if "think" in sem:
        raise SystemExit("qwen2.5:7b não recebe a chave think")


def testar_thinking_nao_vira_resposta() -> None:
    visivel, _ = separar_raciocinio("")
    pensamento = "Okay, let's tackle this question"
    if visivel:
        raise SystemExit("content vazio não pode ganhar texto")
    if not estourou_no_pensamento(visivel, pensamento):
        raise SystemExit("content vazio com thinking deveria marcar estouro")
    if pensamento in visivel:
        raise SystemExit("o thinking vazou para a resposta")


def testar_tags() -> None:
    visivel, pensamento = separar_raciocinio("<think>ok</think>Resposta real sobre a extradição.")
    if visivel != "Resposta real sobre a extradição." or pensamento != "ok":
        raise SystemExit("bloco fechado não foi separado: {} / {}".format(visivel, pensamento))
    if "ok" in visivel:
        raise SystemExit("o miolo do think ficou na resposta")
    cortado, miolo = separar_raciocinio("<think>raciocinio truncado sem fechar")
    if cortado or "truncado" not in (miolo or ""):
        raise SystemExit("tag aberta deveria sair da resposta: {} / {}".format(cortado, miolo))
    prefixo, interno = separar_raciocinio("Okay, let's tackle\n</think>\nO Brasil não extradita o nato.")
    if "Okay" in prefixo or not prefixo.endswith("nato."):
        raise SystemExit("o fechamento solto deveria sair: {}".format(prefixo))
    if "Okay" not in (interno or ""):
        raise SystemExit("o prefixo deveria ir para o pensamento")


def main() -> None:
    testar_payload_4b()
    testar_thinking_nao_vira_resposta()
    testar_tags()
    print("ok vazamento think")


if __name__ == "__main__":
    main()
