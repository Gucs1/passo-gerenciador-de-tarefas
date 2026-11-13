"""Regras das tarefas, sem leitura de arquivos ou interação com o terminal."""


def cadastrar(tarefas, titulo):
    titulo = titulo.strip()
    if not titulo:
        raise ValueError("O título não pode ficar vazio.")
    identificador = max((tarefa["id"] for tarefa in tarefas), default=0) + 1
    tarefa = {"id": identificador, "titulo": titulo, "concluida": False}
    return tarefas + [tarefa]


def concluir(tarefas, identificador):
    for tarefa in tarefas:
        if tarefa["id"] == identificador:
            if tarefa["concluida"]:
                raise ValueError("Essa tarefa já está concluída.")
            return [
                {**item, "concluida": True} if item["id"] == identificador
                else dict(item)
                for item in tarefas
            ]
    raise ValueError("Não existe tarefa com esse número.")


def excluir(tarefas, identificador):
    if not any(tarefa["id"] == identificador for tarefa in tarefas):
        raise ValueError("Não existe tarefa com esse número.")
    return [dict(tarefa) for tarefa in tarefas if tarefa["id"] != identificador]
