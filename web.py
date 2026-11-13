"""Aplicação web local, sem dependências externas. Execute python web.py."""

import argparse
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import threading

from armazenamento import DadosInvalidos, carregar, salvar
from tarefas import cadastrar, excluir


RAIZ = Path(__file__).resolve().parent
PAGINAS = {
    "/tarefas": ("tarefas", "todas", "Todas as tarefas"),
    "/pendentes": ("pendentes", "pendentes", "Tarefas pendentes"),
    "/concluidas": ("concluidas", "concluidas", "Tarefas concluídas"),
}


def renderizar_pagina(caminho):
    arquivo, pagina, titulo = PAGINAS[caminho]
    layout = (RAIZ / "static/index.html").read_text(encoding="utf-8")
    conteudo = (RAIZ / "pages" / f"{arquivo}.html").read_text(encoding="utf-8")
    painel = (RAIZ / "pages/painel.html").read_text(encoding="utf-8")
    conteudo = conteudo.replace("<!-- TASK_PANEL -->", painel)
    html = layout.replace("<!-- PAGE_CONTENT -->", conteudo)
    html = html.replace("{{page}}", pagina).replace("{{title}}", titulo)
    # O destaque correto já vem no HTML, antes de carregar o JavaScript.
    for chave in ("todas", "pendentes", "concluidas"):
        html = html.replace(f'class="nav-item active" data-filter="{chave}"', f'class="nav-item" data-filter="{chave}"')
    html = html.replace(' aria-current="page"', '')
    html = html.replace(f'class="nav-item" data-filter="{pagina}"', f'class="nav-item active" aria-current="page" data-filter="{pagina}"')
    return html.encode("utf-8")


class Servidor(ThreadingHTTPServer):
    def __init__(self, endereco, caminho):
        self.caminho = Path(caminho)
        self.trava = threading.Lock()
        self.token = secrets.token_urlsafe(32)
        super().__init__(endereco, partial(Atendimento, directory=str(RAIZ / "static")))


class Atendimento(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        super().end_headers()

    def json(self, conteudo, status=200):
        corpo = json.dumps(conteudo, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def host_valido(self):
        esperado = f"127.0.0.1:{self.server.server_port}"
        return self.headers.get("Host") == esperado

    def do_GET(self):
        if not self.host_valido():
            self.json({"erro": "Endereço não permitido."}, 403)
            return
        if self.path in ("/", "/index.html"):
            self.send_response(302)
            self.send_header("Location", "/tarefas")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if self.path in PAGINAS:
            corpo = renderizar_pagina(self.path)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)
            return
        if self.path == "/api/tarefas":
            try:
                with self.server.trava:
                    tarefas = carregar(self.server.caminho)
                self.json({"tarefas": tarefas, "token": self.server.token})
            except (DadosInvalidos, OSError):
                self.json({"erro": "Não foi possível ler as tarefas. O arquivo foi preservado."}, 500)
            return
        if self.path not in ("/app.js", "/navigation.js", "/style.css", "/favicon.svg"):
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        super().do_GET()

    def do_POST(self):
        if not self.host_valido() or self.headers.get("X-Task-Token") != self.server.token:
            self.json({"erro": "Acesso não permitido. Atualize a página."}, 403)
            return
        if self.path != "/api/tarefas":
            self.json({"erro": "Rota não encontrada."}, 404)
            return
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            if not 0 < tamanho <= 16384:
                self.json({"erro": "Requisição muito grande ou vazia."}, 400)
                return
            dados = json.loads(self.rfile.read(tamanho))
            if not isinstance(dados, dict):
                raise ValueError("Dados inválidos.")
            with self.server.trava:
                tarefas = carregar(self.server.caminho)
                acao = dados.get("acao")
                if acao in ("cadastrar", "editar"):
                    titulo = dados.get("titulo")
                    if not isinstance(titulo, str) or not titulo.strip():
                        raise ValueError("Escreva um título para a tarefa.")
                    if len(titulo.strip()) > 300:
                        raise ValueError("Use até 300 caracteres no título.")
                if acao == "cadastrar":
                    novas = cadastrar(tarefas, titulo)
                elif acao in ("editar", "situacao", "excluir"):
                    identificador = dados.get("id")
                    if type(identificador) is not int or identificador <= 0:
                        raise ValueError("Identificador inválido.")
                    tarefa = next((t for t in tarefas if t["id"] == identificador), None)
                    if tarefa is None:
                        self.json({"erro": "Essa tarefa não existe mais. Atualize a lista."}, 404)
                        return
                    if acao == "excluir":
                        novas = excluir(tarefas, identificador)
                    else:
                        if acao == "situacao" and type(dados.get("concluida")) is not bool:
                            raise ValueError("Situação inválida.")
                        campo = {"titulo": titulo.strip()} if acao == "editar" else {"concluida": dados["concluida"]}
                        novas = [{**t, **campo} if t["id"] == identificador else dict(t) for t in tarefas]
                else:
                    raise ValueError("Ação inválida.")
                salvar(self.server.caminho, novas)
            self.json({"tarefas": novas})
        except DadosInvalidos:
            self.json({"erro": "O arquivo de tarefas está danificado e foi preservado."}, 500)
        except (ValueError, UnicodeDecodeError):
            self.json({"erro": "Dados inválidos. Verifique o título e a ação solicitada."}, 400)
        except OSError:
            self.json({"erro": "Não foi possível salvar. Seus dados anteriores foram preservados."}, 500)


if __name__ == "__main__":
    argumentos = argparse.ArgumentParser(description="Gerenciador web local")
    argumentos.add_argument("--port", type=int, default=8765)
    argumentos.add_argument("--dados", type=Path, default=RAIZ / "tarefas.json")
    opcoes = argumentos.parse_args()
    with Servidor(("127.0.0.1", opcoes.port), opcoes.dados) as servidor:
        print(f"Gerenciador disponível em http://127.0.0.1:{servidor.server_port}", flush=True)
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor encerrado.")
