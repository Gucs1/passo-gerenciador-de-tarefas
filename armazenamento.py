"""Leitura validada e gravação do arquivo JSON."""

import json
import os
from pathlib import Path
import tempfile


class DadosInvalidos(ValueError):
    """O arquivo não representa uma lista válida de tarefas."""


def carregar(caminho):
    try:
        with Path(caminho).open(encoding="utf-8") as arquivo:
            tarefas = json.load(arquivo)
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, UnicodeDecodeError) as erro:
        raise DadosInvalidos("O arquivo de tarefas está danificado.") from erro

    if not isinstance(tarefas, list):
        raise DadosInvalidos("O arquivo deve conter uma lista de tarefas.")
    identificadores = set()
    for tarefa in tarefas:
        if (
            not isinstance(tarefa, dict)
            or set(tarefa) != {"id", "titulo", "concluida"}
            or type(tarefa["id"]) is not int
            or tarefa["id"] <= 0
            or tarefa["id"] in identificadores
            or not isinstance(tarefa["titulo"], str)
            or not tarefa["titulo"].strip()
            or type(tarefa["concluida"]) is not bool
        ):
            raise DadosInvalidos("O arquivo contém uma tarefa inválida.")
        identificadores.add(tarefa["id"])
    return tarefas


def salvar(caminho, tarefas):
    caminho = Path(caminho)
    temporario = None
    try:
        # Só substitui o arquivo anterior depois de escrever o novo por completo.
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=caminho.parent,
            prefix=".tarefas-", suffix=".tmp", delete=False,
        ) as arquivo:
            temporario = Path(arquivo.name)
            json.dump(tarefas, arquivo, ensure_ascii=False, indent=2)
            arquivo.write("\n")
        os.replace(temporario, caminho)
    finally:
        if temporario is not None:
            temporario.unlink(missing_ok=True)
