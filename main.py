"""Menu do gerenciador: execute com python main.py."""

from pathlib import Path

from armazenamento import DadosInvalidos, carregar, salvar
from tarefas import cadastrar, concluir, excluir


ARQUIVO_DADOS = Path(__file__).resolve().parent / "tarefas.json"


def executar(caminho=ARQUIVO_DADOS):
    try:
        tarefas = carregar(caminho)
    except (DadosInvalidos, OSError) as erro:
        print(f"Não foi possível abrir as tarefas: {erro}")
        print("O programa foi encerrado sem alterar o arquivo.")
        return 1

    while True:
        print("\n1. Cadastrar tarefa\n2. Listar tarefas\n3. Concluir tarefa\n4. Sair\n5. Excluir tarefa")
        try:
            opcao = input("Escolha uma opção: ").strip()
            if opcao == "4":
                print("Até a próxima!")
                return 0
            if opcao == "2":
                if not tarefas:
                    print("Nenhuma tarefa cadastrada.")
                for tarefa in tarefas:
                    situacao = "Concluída" if tarefa["concluida"] else "Pendente"
                    print(f"{tarefa['id']} | {tarefa['titulo']} | {situacao}")
                continue
            if opcao == "1":
                novas = cadastrar(tarefas, input("Título: "))
            elif opcao in ("3", "5"):
                numero = input("Número da tarefa: ").strip()
                try:
                    identificador = int(numero)
                except ValueError:
                    print("Informe um número inteiro para identificar a tarefa.")
                    continue
                if opcao == "3":
                    novas = concluir(tarefas, identificador)
                else:
                    novas = excluir(tarefas, identificador)
                    tarefa = next(item for item in tarefas if item["id"] == identificador)
                    confirmacao = input(
                        f"Excluir a tarefa {identificador} — {tarefa['titulo']}? [s/N]: "
                    ).strip().lower()
                    if confirmacao != "s":
                        print("Exclusão cancelada.")
                        continue
            else:
                print("Opção inválida. Escolha de 1 a 5.")
                continue
            salvar(caminho, novas)
            tarefas = novas
            mensagens = {
                "1": "Tarefa cadastrada.",
                "3": "Tarefa concluída.",
                "5": "Tarefa excluída.",
            }
            print(mensagens[opcao])
        except ValueError as erro:
            print(erro)
        except OSError as erro:
            print(f"Não foi possível salvar a alteração: {erro}")
        except (EOFError, KeyboardInterrupt):
            print("\nPrograma encerrado.")
            return 0


if __name__ == "__main__":
    raise SystemExit(executar())
