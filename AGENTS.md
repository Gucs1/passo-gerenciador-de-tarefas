# Orientações para o agente

## Objetivo e contexto
Este projeto é um gerenciador de tarefas em Python, com interfaces de terminal e web local, e armazenamento em JSON. Seu objetivo educacional é ensinar harness engineering a um iniciante. Leia README.md antes de propor alterações.

## Como colaborar
- Explique as decisões em português simples, conectando cada mudança ao motivo dela.
- Antes de editar, apresente o comportamento solicitado, os arquivos afetados e como verificar o resultado.
- Trabalhe somente na etapa autorizada. Ao terminar, explique o resultado e espere aprovação explícita para iniciar a próxima.
- Se faltar uma decisão que mude o comportamento do programa, pergunte antes de implementá-la.

## Escopo e ferramentas
- Use Python e sua biblioteca padrão. Não instale dependências sem justificar a necessidade e obter aprovação.
- A versão web moderna e responsiva foi autorizada. Mantenha o servidor apenas em 127.0.0.1, usando a biblioteca padrão do Python e HTML/CSS/JavaScript locais. Login, banco de dados, serviços externos, publicação e Docker não fazem parte desta etapa.
- Preserve a compatibilidade do JSON e da interface de terminal. Não leia dados pessoais para testes ou demonstrações. Use apenas uma interface por vez para gravar no arquivo; o bloqueio da web coordena somente requisições no mesmo processo.
- Valide entradas no servidor, preserve a proteção por token das mutações e exiba títulos no navegador como texto, nunca como HTML.
- Para mudanças na interface web, execute também node --check static/app.js quando Node estiver disponível e confira a interface em larguras de computador e celular quando o navegador permitir. Informe qualquer bloqueio de verificação visual.
- Para mudanças nas abas, execute também node --check static/navigation.js e node --test tests/navigation.test.cjs, quando Node estiver disponível. Preserve os links diretos e a navegação por Voltar/Avançar.
- Inspecione os arquivos e comandos disponíveis antes de usá-los; não invente resultados.

## Dados e validação
- Preserve dados existentes. Um JSON inválido deve gerar um aviso e encerramento, sem sobrescrever o arquivo.
- Use arquivos e diretórios temporários nos testes; não use tarefas reais para validar mudanças.
- Ao implementar comportamento, cubra os critérios correspondentes do README.md com testes automáticos usando unittest.
- Ao corrigir um bug, identifique o critério violado e use ou crie um teste que reproduza o problema. Confirme que ele falha pelo motivo esperado antes da correção e passa depois; se não conseguir reproduzir, informe essa limitação.
- Faça experimentos que introduzem falhas somente em cópias temporárias do código, sem copiar dados pessoais. Uma falha proposital deve ser relatada como parte do experimento, não como defeito do projeto original.
- Execute os testes a partir da raiz: python -m unittest discover -s tests -v.
- Informe o que foi executado, o resultado observado e o que não foi verificado. Nunca declare testes que não rodaram.
- Atualize a documentação se uma mudança de comportamento for aprovada.

## Etapa atual
A versão web, a revisão visual e a correção para páginas HTML separadas em /tarefas, /pendentes e /concluidas foram autorizadas e implementadas. Não substitua os links normais por simples alterações de tema ou rotas com #. Preserve a direção visual descrita no README e relate o bloqueio de revisão visual quando ainda se aplicar. Novas funcionalidades, publicação ou serviços externos exigem autorização.
