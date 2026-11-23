# -*- coding: utf-8 -*-
"""Testes do arranque do LLM que não precisam de um modelo carregado."""

import sys
import unittest
from pathlib import Path
from unittest import mock

_RAIZ = Path(__file__).resolve().parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(1, str(_RAIZ))

from auditoria_ponta_a_ponta import auditar_citacoes
from src.rag.gerador import FRASE_SEM_BASE, montar_prompt, separar_raciocinio
from src.rag import servidor_llm


class EscolhaDeModelo(unittest.TestCase):
    def test_prefere_qwen_sobre_llama(self):
        escolhido = servidor_llm.escolher_modelo(
            ["nomic-embed-text", "llama3.1:8b", "qwen2.5:7b"]
        )
        self.assertEqual(escolhido, "qwen2.5:7b")

    def test_aceita_prefixo_com_etiqueta(self):
        self.assertEqual(servidor_llm.escolher_modelo(["qwen3:8b"]), "qwen3:8b")

    def test_ignora_so_embeddings(self):
        self.assertIsNone(servidor_llm.escolher_modelo(["bge-m3"]))

    def test_le_ids_do_json_openai(self):
        ids = servidor_llm.ids_de_modelos({"data": [{"id": "llama3.1:8b"}, {}]})
        self.assertEqual(ids, ["llama3.1:8b"])


class ArranqueSemRede(unittest.TestCase):
    def setUp(self):
        servidor_llm._ESTADO = None
        servidor_llm.LLM_URL = None
        servidor_llm.LLM_MODEL = None

    def test_servidor_ja_no_ar_configura_url_e_modelo(self):
        payload = {"data": [{"id": "llama3.1:8b"}]}

        def sondar(url, timeout=0.4):
            if "11434" in url:
                return payload
            return None

        with mock.patch.object(servidor_llm, "_pedido", side_effect=sondar):
            estado = servidor_llm.garantir_servidor(forcar=True)

        self.assertEqual(estado["origem"], "ollama")
        self.assertEqual(servidor_llm.LLM_MODEL, "llama3.1:8b")
        self.assertEqual(servidor_llm.LLM_URL, servidor_llm._URL_CHAT_OLLAMA)
        self.assertIsNone(estado["comando"])

    def test_sem_binario_nao_sobe_processo_e_devolve_comando(self):
        with mock.patch.object(servidor_llm, "_pedido", return_value=None), mock.patch.object(
            servidor_llm, "caminho_ollama", return_value=None
        ), mock.patch.object(servidor_llm, "procurar_llamafile", return_value=None), mock.patch.object(
            servidor_llm, "_subir_desacoplado"
        ) as subir:
            estado = servidor_llm.garantir_servidor(forcar=True)

        subir.assert_not_called()
        self.assertIsNone(servidor_llm.LLM_URL)
        self.assertIn("ollama pull qwen2.5:7b", estado["comando"])

    def test_ollama_sem_modelo_nao_faz_pull(self):
        with mock.patch.object(servidor_llm, "_pedido", return_value=None), mock.patch.object(
            servidor_llm, "caminho_ollama", return_value="ollama"
        ), mock.patch.object(servidor_llm, "modelos_ollama_locais", return_value=[]), mock.patch.object(
            servidor_llm, "procurar_llamafile", return_value=None
        ), mock.patch.object(servidor_llm, "_subir_desacoplado") as subir:
            servidor_llm.garantir_servidor(forcar=True)

        subir.assert_not_called()


class PromptSemServidor(unittest.TestCase):
    def test_prompt_exige_a_frase_de_recurso(self):
        mensagens = montar_prompt("Quem pode propor emenda?", ["Art. 60. A Constituição poderá ser emendada."])
        self.assertIn("NUNCA inicie a resposta com 'Sim'", mensagens[0]["content"])
        self.assertIn("Art. 60", mensagens[1]["content"])
        self.assertIn("[FONTE 1 | ? | Relevância: 0.000]", mensagens[1]["content"])

    def test_separa_bloco_think(self):
        visivel, raciocinio = separar_raciocinio("<think>passo interno</think>\nBase Constitucional: Art. 5º, IV")
        self.assertNotIn("<think>", visivel)
        self.assertEqual(raciocinio, "passo interno")
        self.assertIn("Art. 5º, IV", visivel)


class Citacoes(unittest.TestCase):
    def test_artigo_recuperado_nao_e_alucinacao(self):
        auditoria = auditar_citacoes(
            "Base Constitucional: Art. 5º, IV\nResposta: é vedado o anonimato.",
            [{"artigo_id": "Art. 5º, IV"}],
        )
        self.assertFalse(auditoria["citacao_alucinada"])

    def test_artigo_ausente_e_alucinacao(self):
        auditoria = auditar_citacoes(
            "A pena está no Art. 155.",
            [{"artigo_id": "Art. 5º, XLVI"}],
        )
        self.assertTrue(auditoria["citacao_alucinada"])
        self.assertEqual(auditoria["inventadas"], ["Art. 155"])

    def test_adct_nao_confunde_com_o_corpo(self):
        auditoria = auditar_citacoes("Art. 2º", [{"artigo_id": "ADCT, Art. 2º"}])
        self.assertTrue(auditoria["citacao_alucinada"])


if __name__ == "__main__":
    unittest.main()
