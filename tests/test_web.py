import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from armazenamento import carregar, salvar
from tarefas import cadastrar
from web import Servidor


class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.TemporaryDirectory()
        cls.caminho = Path(cls.pasta.name) / 'tarefas.json'
        cls.servidor = Servidor(('127.0.0.1', 0), cls.caminho)
        cls.thread = threading.Thread(target=cls.servidor.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()
        cls.thread.join()
        cls.pasta.cleanup()

    def setUp(self):
        salvar(self.caminho, [])

    def requisicao(self, dados=None, token=True, path='/api/tarefas', host=None):
        conexao = http.client.HTTPConnection('127.0.0.1', self.servidor.server_port, timeout=5)
        headers = {}
        if host:
            headers['Host'] = host
        if token:
            headers['X-Task-Token'] = self.servidor.token
        body = json.dumps(dados) if dados is not None else None
        conexao.request('POST' if dados is not None else 'GET', path, body, headers)
        resposta = conexao.getresponse()
        status, conteudo = resposta.status, resposta.read()
        conexao.close()
        return status, json.loads(conteudo) if path == '/api/tarefas' else conteudo

    def test_criar_editar_concluir_reabrir_excluir(self):
        status, resultado = self.requisicao({'acao': 'cadastrar', 'titulo': 'Estudar'})
        self.assertEqual(status, 200)
        identificador = resultado['tarefas'][0]['id']
        for dados in (
            {'acao': 'editar', 'id': identificador, 'titulo': 'Praticar'},
            {'acao': 'situacao', 'id': identificador, 'concluida': True},
            {'acao': 'situacao', 'id': identificador, 'concluida': False},
        ):
            status, resultado = self.requisicao(dados)
            self.assertEqual(status, 200)
        self.assertEqual(carregar(self.caminho), [{'id': identificador, 'titulo': 'Praticar', 'concluida': False}])
        self.assertEqual(self.requisicao({'acao': 'excluir', 'id': identificador})[0], 200)
        self.assertEqual(carregar(self.caminho), [])

    def test_titulos_invalidos_e_payloads_preservam_dados(self):
        salvar(self.caminho, cadastrar([], 'Preservar'))
        original = self.caminho.read_bytes()
        for dados in (
            {'acao': 'cadastrar', 'titulo': '   '},
            {'acao': 'editar', 'id': 1, 'titulo': ''},
            {'acao': 'cadastrar', 'titulo': 123},
            {'acao': 'cadastrar', 'titulo': 'a' * 301},
            {'acao': 'situacao', 'id': 1, 'concluida': 'sim'},
            {'acao': 'excluir', 'id': True},
            {'acao': 'desconhecida'},
            [],
        ):
            with self.subTest(dados=dados):
                self.assertEqual(self.requisicao(dados)[0], 400)
                self.assertEqual(self.caminho.read_bytes(), original)

    def test_csrf_e_host_invalido_bloqueados(self):
        dados = {'acao': 'cadastrar', 'titulo': 'Não criar'}
        self.assertEqual(self.requisicao(dados, token=False)[0], 403)
        self.assertEqual(self.requisicao(dados, host='exemplo.com')[0], 403)
        self.assertEqual(self.requisicao(host='exemplo.com')[0], 403)
        self.assertEqual(carregar(self.caminho), [])

    def test_tarefa_inexistente(self):
        for acao in ('editar', 'situacao', 'excluir'):
            self.assertEqual(self.requisicao({'acao': acao, 'id': 99, 'titulo': 'Teste', 'concluida': True})[0], 404)

    def test_json_danificado_preservado(self):
        self.caminho.write_bytes(b'{invalido')
        self.assertEqual(self.requisicao()[0], 500)
        self.assertEqual(self.requisicao({'acao': 'cadastrar', 'titulo': 'Teste'})[0], 500)
        self.assertEqual(self.caminho.read_bytes(), b'{invalido')

    def test_falha_de_gravacao_preserva_dados(self):
        original = self.caminho.read_bytes()
        with patch('armazenamento.os.replace', side_effect=OSError('Falha simulada')):
            self.assertEqual(self.requisicao({'acao': 'cadastrar', 'titulo': 'Teste'})[0], 500)
        self.assertEqual(self.caminho.read_bytes(), original)

    def test_arquivos_publicos_sem_acesso_ao_json(self):
        for caminho in ('/tarefas', '/pendentes', '/concluidas', '/app.js', '/navigation.js', '/style.css', '/favicon.svg'):
            self.assertEqual(self.requisicao(path=caminho)[0], 200)
        for caminho in ('/tarefas.json', '/../tarefas.json', '/web.py'):
            self.assertEqual(self.requisicao(path=caminho)[0], 404)

    def test_raiz_redireciona_para_pagina_de_tarefas(self):
        conexao = http.client.HTTPConnection('127.0.0.1', self.servidor.server_port, timeout=5)
        conexao.request('GET', '/')
        resposta = conexao.getresponse()
        self.assertEqual(resposta.status, 302)
        self.assertEqual(resposta.getheader('Location'), '/tarefas')
        resposta.read()
        conexao.close()

    def test_paginas_sao_documentos_distintos_com_links_reais(self):
        documentos = {}
        for caminho, pagina in (('/tarefas', 'todas'), ('/pendentes', 'pendentes'), ('/concluidas', 'concluidas')):
            status, corpo = self.requisicao(path=caminho)
            self.assertEqual(status, 200)
            html = corpo.decode('utf-8')
            documentos[caminho] = html
            self.assertIn(f'data-page="{pagina}"', html)
            self.assertIn(f'aria-current="page" data-filter="{pagina}"', html)
            for destino in ('/tarefas', '/pendentes', '/concluidas'):
                self.assertIn(f'href="{destino}"', html)
            self.assertNotIn('href="#/', html)
            self.assertNotIn('<!-- PAGE_CONTENT -->', html)
            self.assertNotIn('<!-- TASK_PANEL -->', html)
        self.assertEqual(len(set(documentos.values())), 3)
        self.assertIn('class="hero-art"', documentos['/tarefas'])
        self.assertNotIn('class="hero-art"', documentos['/pendentes'])
        self.assertNotIn('class="stats"', documentos['/concluidas'])
        self.assertIn('SUA LISTA DE AÇÃO', documentos['/pendentes'])
        self.assertIn('SEU ESPAÇO DE CONQUISTAS', documentos['/concluidas'])

    def test_criacoes_concorrentes_preservadas(self):
        resultados = []
        def criar(indice):
            resultados.append(self.requisicao({'acao': 'cadastrar', 'titulo': f'Tarefa {indice}'})[0])
        threads = [threading.Thread(target=criar, args=(i,)) for i in range(6)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(resultados, [200] * 6)
        tarefas = carregar(self.caminho)
        self.assertEqual(len(tarefas), 6)
        self.assertEqual(len({t['id'] for t in tarefas}), 6)
