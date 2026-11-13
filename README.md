# Passo — Gerenciador de tarefas

**Menos caos. Mais passo.**

Um gerenciador de tarefas com interface web e versão de terminal, desenvolvido em Python, HTML, CSS e JavaScript. Organize ideias, acompanhe pendências e consulte o que já foi concluído, com os dados salvos localmente em JSON.

O Passo também é um projeto de aprendizado em **harness engineering**: estruturar as instruções, o contexto, as ferramentas e as verificações que orientam o trabalho de um agente de IA. O desenvolvimento foi realizado com apoio do Codex, com decisões de escopo e revisões conduzidas pelo autor do projeto.

> Aplicação educacional de uso local. Não exige instalar bibliotecas Python, usar Docker ou preparar uma etapa de compilação do frontend.

## Funcionalidades

### Organização de tarefas

- Criar tarefas e editar seus títulos pela web.
- Marcar como concluída ou reabrir uma tarefa pela web.
- Excluir com confirmação, preservando as demais tarefas.
- Buscar pelo título e ordenar por identificador ou ordem alfabética.
- Alternar entre visualizações em lista e quadro.
- Consultar contadores e percentual de conclusão no painel geral.
- Exportar uma cópia das tarefas em JSON.

### Experiência de uso

- Páginas separadas para todas as tarefas, pendentes e concluídas.
- Layout adaptável a diferentes larguras de tela.
- Modos claro e escuro, com preferência salva no navegador.
- Mensagens de carregamento, salvamento, sucesso e erro.
- Atalhos de teclado e indicação de foco.
- Animações que respeitam a preferência por movimento reduzido.

### Persistência e validação

- Dados mantidos após fechar e abrir o programa.
- Títulos vazios ou compostos apenas por espaços são recusados.
- Validação de entradas também no servidor web.
- Leitura validada do arquivo JSON.
- Gravação em arquivo temporário antes de substituir o anterior.
- Arquivo danificado preservado, com mensagem de erro.

## Tecnologias

| Camada | Tecnologia | Responsabilidade |
| --- | --- | --- |
| Servidor | Python · `http.server` | Entregar as páginas e atender às operações de tarefas |
| Interface | HTML, CSS e JavaScript | Navegação, aparência e interações |
| Persistência | JSON · `pathlib` · `tempfile` | Ler, validar e salvar as tarefas |
| Testes Python | `unittest` · `unittest.mock` | Verificar regras, terminal, HTTP e falhas de gravação |
| Testes JavaScript | `node:test` · `node:assert` | Verificar endereços, seleção, busca e ordenação |

A aplicação usa a biblioteca padrão do Python e JavaScript sem frameworks. Node.js é opcional e serve apenas para executar as verificações de JavaScript.

## Como executar

### Requisitos

- Python **3.10 ou superior** disponível no terminal.
- Um navegador atualizado para a interface web.

Baixe o ZIP ou clone este repositório. Abra o terminal na pasta que contém `web.py`.

### Interface web

```bash
python web.py
```

Acesse **[http://127.0.0.1:8765/tarefas](http://127.0.0.1:8765/tarefas)**.

No Windows, também é possível dar dois cliques em `iniciar_web.bat`. Se o comando `python` não estiver disponível, tente `py web.py`. Para encerrar o servidor, pressione `Ctrl + C` no terminal em que ele está rodando.

O programa não é iniciado pelo duplo clique em `index.html`: as páginas precisam do servidor Python para carregar e salvar tarefas.

### Versão de terminal

```bash
python main.py
```

O menu permite cadastrar, listar, concluir e excluir tarefas. Edição, reabertura, busca e visualizações pertencem à interface web.

**Use apenas uma interface por vez para editar o mesmo arquivo de dados.** O terminal e a web compartilham o JSON, mas não coordenam gravações entre processos separados.

### Porta ou arquivo de dados alternativos

```bash
python web.py --port 8766 --dados tarefas-de-teste.json
```

Esse comando usa outro arquivo e outra porta. Caso informe um caminho com pastas, elas precisam existir. Use dados fictícios em testes e demonstrações.

## Páginas e navegação

| Página | Endereço | Conteúdo |
| --- | --- | --- |
| Todas as tarefas | `/tarefas` | Visão geral, indicadores e tarefas de ambas as situações |
| Pendentes | `/pendentes` | Lista de ação com o que ainda falta fazer |
| Concluídas | `/concluidas` | Tarefas finalizadas, com opção de reabertura |

Cada ícone do menu abre um documento HTML próprio entregue pelo servidor. Os links podem ser acessados diretamente, e a navegação usa os recursos normais de Voltar, Avançar e recarregar do navegador.

Busca, ordenação e modo de visualização são lembrados por página durante a sessão da aba, quando o armazenamento da sessão estiver disponível. Não há sincronização automática entre abas: use **Atualizar tarefas** para buscar os dados mais recentes.

### Atalhos

| Tecla | Ação |
| --- | --- |
| `N` | Abrir o cadastro de tarefa |
| `/` | Focar o campo de busca |
| `?` | Exibir os atalhos |
| `Esc` | Fechar uma janela, quando não houver uma operação em andamento |

Os atalhos de abertura são ignorados enquanto o usuário digita em campos ou está com uma janela aberta.

## Estrutura do projeto

```text
.
├── AGENTS.md                  # Orientações para o agente de IA
├── README.md                  # Apresentação, uso e regras do projeto
├── tarefas.py                 # Regras usadas pelo terminal e pelo servidor
├── armazenamento.py           # Leitura, validação e gravação do JSON
├── main.py                    # Interface de terminal
├── web.py                     # Servidor HTTP e operações da interface web
├── iniciar_web.bat            # Inicialização da versão web no Windows
├── pages/
│   ├── tarefas.html           # Conteúdo da visão geral
│   ├── pendentes.html         # Conteúdo da página de pendências
│   ├── concluidas.html        # Conteúdo da página de conquistas
│   └── painel.html            # Controles compartilhados das listas
├── static/
│   ├── index.html             # Layout compartilhado e janelas de interação
│   ├── style.css              # Aparência, temas e adaptação de layout
│   ├── app.js                 # Interações e comunicação com o servidor
│   ├── navigation.js          # Configuração das páginas e seleção de tarefas
│   └── favicon.svg            # Identidade visual
└── tests/
    ├── test_gerenciador.py     # Regras, terminal e persistência
    ├── test_web.py            # Operações HTTP e documentos das páginas
    └── navigation.test.cjs    # Lógica de navegação e seleção
```

O arquivo `tarefas.json` é criado na raiz do projeto no primeiro cadastro. Ele está no `.gitignore` para manter as tarefas pessoais fora do versionamento.

## Regras e critérios de aceitação

| Situação | Comportamento esperado |
| --- | --- |
| Cadastrar uma tarefa válida | Criar com identificador próprio e situação pendente |
| Informar título vazio ou apenas espaços | Recusar sem salvar a tarefa |
| Cadastrar títulos iguais | Permitir, diferenciando pelo identificador |
| Criar ou editar pela web | Aceitar de 1 a 300 caracteres no título após remover espaços nas pontas |
| Consultar uma lista vazia | Exibir uma mensagem apropriada à página |
| Concluir uma tarefa | Alterar somente a tarefa escolhida e salvar |
| Concluir novamente pelo terminal | Avisar que a tarefa já está concluída |
| Reabrir pela web | Retornar a tarefa para pendente |
| Informar um identificador inexistente | Avisar sem alterar as outras tarefas |
| Cancelar uma exclusão | Preservar os dados |
| Confirmar uma exclusão | Remover somente a tarefa escolhida e salvar |
| Excluir a última tarefa | Persistir a lista vazia e permitir reabrir o programa |
| Fechar e reabrir | Recuperar identificadores, títulos e situações das tarefas existentes |
| Iniciar sem arquivo JSON | Começar com uma lista vazia |
| Encontrar JSON inválido | Avisar e preservar o arquivo; no terminal, encerrar a execução |
| Falhar uma gravação | Informar o erro e manter os dados anteriores |
| Abrir Pendentes ou Concluídas | Entregar uma página própria e mostrar somente a situação correspondente |

No terminal, a exclusão é confirmada com `s`, ignorando maiúsculas e espaços nas pontas. Na web, exige o botão **Sim, excluir**. A exclusão permite remover tarefas pendentes ou concluídas.

## Testes

Execute os comandos a partir da raiz do projeto.

**Python:**

```bash
python -m unittest discover -s tests -v
```

**JavaScript — opcional, com Node.js compatível com `node --test`:**

```bash
node --check static/app.js
node --check static/navigation.js
node --test tests/navigation.test.cjs
```

Na última validação, em **13/11/2026**, passaram **27 testes Python e 8 testes JavaScript**. As verificações de sintaxe JavaScript também passaram. Os testes usam dados fictícios e arquivos temporários, sem acessar as tarefas pessoais.

A suíte verifica regras, persistência, operações HTTP, páginas distintas, proteção das mutações por token, entradas inválidas e falhas simuladas de gravação. A revisão visual automatizada e as interações reais do navegador ainda estão pendentes; os testes de lógica não substituem essa conferência.

## Harness engineering na prática

O aprendizado deste projeto vai além da implementação de uma lista de tarefas. A proposta é tornar o trabalho com IA mais claro, limitado ao escopo e verificável.

| Parte do processo | Aplicação no projeto |
| --- | --- |
| Contexto | Objetivo, estrutura e regras descritos no README |
| Instruções | `AGENTS.md` define como colaborar, preservar dados e validar mudanças |
| Escopo | Etapas autorizadas pelo usuário antes de implementar |
| Ferramentas | Leitura de arquivos, edição e execução de verificações |
| Evidências | Testes executados e resultados relatados com suas limitações |
| Melhoria contínua | Ajustes nas instruções a partir dos problemas observados |

### Um experimento de regressão

Em uma cópia temporária do projeto, removemos a validação que elimina espaços antes de conferir se o título está vazio. O teste de título composto apenas por espaços falhou. Ao restaurar a regra, ele voltou a passar.

O código original foi preservado. O teste já existente demonstrou que detectava aquela regressão, e o `AGENTS.md` recebeu orientações para reproduzir bugs antes de corrigi-los e realizar experimentos somente em cópias sem dados pessoais.

A lição: **um pedido claro define o resultado; uma instrução orienta a execução; um teste fornece evidência sobre o comportamento verificado.**

## Escopo e limitações

- Aplicação pessoal e local, sem autenticação ou isolamento entre usuários.
- Servidor vinculado somente a `127.0.0.1`, sem preparação para exposição pública.
- O layout se adapta a janelas estreitas, mas o servidor local não fica acessível ao celular pela rede.
- Persistência em JSON, sem banco de dados ou sincronização em nuvem.
- Requisições no mesmo servidor são coordenadas; processos independentes não compartilham esse bloqueio.
- Exportação cria uma cópia dos dados carregados; a interface não possui importação.
- Mantenha backup dos dados importantes. A gravação por substituição não substitui uma política de backup.

---

**Passo:** um projeto para organizar tarefas e aprender a construir software com contexto, critérios e verificação.
