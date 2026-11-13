import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from armazenamento import DadosInvalidos, carregar, salvar
from main import executar
from tarefas import cadastrar, concluir, excluir


class GerenciadorTests(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        self.caminho = Path(self.pasta.name) / "tarefas.json"

    def menu(self, entradas):
        saida = io.StringIO()
        with patch("builtins.input", side_effect=entradas), contextlib.redirect_stdout(saida):
            retorno = executar(self.caminho)
        return retorno, saida.getvalue()

    def test_cadastro_e_titulos_repetidos(self):
        tarefas = cadastrar([], "Estudar Python")
        tarefas = cadastrar(tarefas, "Estudar Python")
        self.assertEqual([t["id"] for t in tarefas], [1, 2])
        self.assertTrue(all(not t["concluida"] for t in tarefas))

    def test_titulo_vazio_recusado_sem_gravar(self):
        for titulo in ("", "   "):
            with self.subTest(titulo=titulo):
                _, saida = self.menu(["1", titulo, "4"])
                self.assertIn("título não pode ficar vazio", saida)
                self.assertFalse(self.caminho.exists())

    def test_listagem_vazia(self):
        _, saida = self.menu(["2", "4"])
        self.assertIn("Nenhuma tarefa cadastrada", saida)

    def test_fluxo_completo_e_persistencia_imediata(self):
        def entrada(texto):
            valor = next(entradas)
            if valor == "2":
                tarefas = carregar(self.caminho)
                self.assertEqual(len(tarefas), 2)
                self.assertTrue(tarefas[0]["concluida"])
                self.assertFalse(tarefas[1]["concluida"])
            return valor

        entradas = iter(["1", "Estudar Python", "1", "Praticar", "3", "1", "2", "4"])
        saida = io.StringIO()
        with patch("builtins.input", side_effect=entrada), contextlib.redirect_stdout(saida):
            self.assertEqual(executar(self.caminho), 0)
        self.assertIn("1 | Estudar Python | Concluída", saida.getvalue())
        self.assertIn("2 | Praticar | Pendente", saida.getvalue())
        _, reabertura = self.menu(["1", "Revisar", "2", "4"])
        self.assertIn("1 | Estudar Python | Concluída", reabertura)
        self.assertIn("3 | Revisar | Pendente", reabertura)

    def test_conclusoes_invalidas_preservam_arquivo(self):
        tarefas = concluir(cadastrar([], "Estudar"), 1)
        salvar(self.caminho, tarefas)
        original = self.caminho.read_bytes()
        _, saida = self.menu(["3", "99", "3", "1", "4"])
        self.assertIn("Não existe tarefa", saida)
        self.assertIn("já está concluída", saida)
        self.assertEqual(self.caminho.read_bytes(), original)

    def test_excluir_preserva_lista_original(self):
        tarefas = cadastrar(cadastrar([], "Primeira"), "Segunda")
        restantes = excluir(tarefas, 1)
        self.assertEqual(len(tarefas), 2)
        self.assertEqual(restantes, [tarefas[1]])
        with self.assertRaisesRegex(ValueError, "Não existe tarefa"):
            excluir(tarefas, 99)

    def test_exclusao_confirmada_persiste_e_preserva_outras_tarefas(self):
        for concluida in (False, True):
            with self.subTest(concluida=concluida):
                tarefas = cadastrar(cadastrar([], "Excluir"), "Preservar")
                if concluida:
                    tarefas = concluir(tarefas, 1)
                salvar(self.caminho, tarefas)
                entradas = iter(["5", "1", "s", "2", "4"])
                def entrada(texto):
                    valor = next(entradas)
                    if "[s/N]" in texto:
                        self.assertIn("Excluir", texto)
                    if valor == "2":
                        self.assertEqual(carregar(self.caminho), [tarefas[1]])
                    return valor
                _, saida = self.menu(entrada)
                self.assertIn("Tarefa excluída.", saida)
                self.assertNotIn("1 | Excluir", saida)
                _, reabertura = self.menu(["2", "4"])
                self.assertNotIn("1 | Excluir", reabertura)
                self.assertIn("2 | Preservar | Pendente", reabertura)

    def test_cancelar_exclusao_preserva_arquivo(self):
        salvar(self.caminho, cadastrar([], "Preservar"))
        original = self.caminho.read_bytes()
        for resposta in ("", "n", "talvez"):
            with self.subTest(resposta=resposta):
                _, saida = self.menu(["5", "1", resposta, "2", "4"])
                self.assertIn("Exclusão cancelada.", saida)
                self.assertIn("1 | Preservar | Pendente", saida)
                self.assertEqual(self.caminho.read_bytes(), original)

    def test_exclusao_inexistente_nao_pede_confirmacao(self):
        salvar(self.caminho, cadastrar([], "Preservar"))
        original = self.caminho.read_bytes()
        _, saida = self.menu(["5", "99", "4"])
        self.assertIn("Não existe tarefa", saida)
        self.assertEqual(self.caminho.read_bytes(), original)

    def test_excluir_ultima_tarefa_e_reabrir(self):
        salvar(self.caminho, cadastrar([], "Excluir"))
        self.menu(["5", "1", " S ", "4"])
        self.assertEqual(carregar(self.caminho), [])
        _, saida = self.menu(["2", "4"])
        self.assertIn("Nenhuma tarefa cadastrada", saida)

    def test_falha_ao_salvar_exclusao_preserva_tarefa(self):
        salvar(self.caminho, cadastrar([], "Preservar"))
        original = self.caminho.read_bytes()
        with patch("armazenamento.os.replace", side_effect=OSError("Falha simulada")):
            _, saida = self.menu(["5", "1", "s", "2", "4"])
        self.assertIn("Não foi possível salvar", saida)
        self.assertNotIn("Tarefa excluída.", saida)
        self.assertIn("1 | Preservar | Pendente", saida)
        self.assertEqual(self.caminho.read_bytes(), original)

    def test_identificador_nao_numerico_na_exclusao(self):
        _, saida = self.menu(["5", "abc", "4"])
        self.assertIn("Informe um número inteiro", saida)
        self.assertFalse(self.caminho.exists())

    def test_arquivo_ausente(self):
        self.assertEqual(carregar(self.caminho), [])

    def test_json_danificado_preservado_e_programa_encerrado(self):
        for conteudo in (b"{invalido", b"{}", b'[{}]', b'\xff'):
            with self.subTest(conteudo=conteudo):
                self.caminho.write_bytes(conteudo)
                retorno, saida = self.menu([])
                self.assertEqual(retorno, 1)
                self.assertIn("sem alterar o arquivo", saida)
                self.assertEqual(self.caminho.read_bytes(), conteudo)

    def test_identificadores_duplicados_recusados(self):
        tarefas = cadastrar([], "Estudar")
        salvar(self.caminho, tarefas + tarefas)
        with self.assertRaises(DadosInvalidos):
            carregar(self.caminho)

    def test_entrada_invalida_permite_continuar(self):
        _, saida = self.menu(["x", "3", "abc", "2", "4"])
        self.assertIn("Opção inválida", saida)
        self.assertIn("Informe um número inteiro", saida)
        self.assertIn("Nenhuma tarefa cadastrada", saida)

    def test_falha_de_gravacao_preserva_estado_e_arquivo(self):
        salvar(self.caminho, cadastrar([], "Original"))
        original = self.caminho.read_bytes()
        with patch("armazenamento.os.replace", side_effect=OSError("Falha simulada")):
            _, saida = self.menu(["1", "Nova", "2", "4"])
        self.assertIn("Não foi possível salvar", saida)
        self.assertNotIn("2 | Nova", saida)
        self.assertEqual(self.caminho.read_bytes(), original)
        self.assertEqual(list(Path(self.pasta.name).glob("*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
