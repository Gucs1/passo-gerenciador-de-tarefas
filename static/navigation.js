'use strict';

// As páginas compartilham os dados; cada uma tem endereço e apresentação próprios.
globalThis.PassoPages = (() => {
  const pages = {
    todas: {path: '/tarefas', title: 'Todas as tarefas', eyebrow: 'SUA CABEÇA MERECE UM RESPIRO', heading: 'Menos caos.', accent: 'Mais passo.', description: 'Todas as suas ideias e conquistas, organizadas em um só lugar.', subtitle: 'Seu plano, sem complicação.', emptyTitle: 'Tudo começa com um pequeno passo.', emptyText: 'O que você quer tirar da cabeça hoje? Crie sua primeira tarefa.'},
    pendentes: {path: '/pendentes', title: 'Tarefas pendentes', eyebrow: 'UMA COISA DE CADA VEZ', heading: 'O próximo passo', accent: 'é seu.', description: 'Aqui fica o que ainda está por fazer. Escolha por onde começar.', subtitle: 'Só o que falta fazer. No seu ritmo.', emptyTitle: 'Nenhuma pendência por aqui!', emptyText: 'Você pode respirar ou dar espaço para uma nova ideia.'},
    concluidas: {path: '/concluidas', title: 'Tarefas concluídas', eyebrow: 'CADA PASSO CONTA', heading: 'Olha tudo que', accent: 'você já fez.', description: 'Um espaço para suas conquistas. E para lembrar que você está avançando.', subtitle: 'Seus passos concluídos, todos aqui.', emptyTitle: 'Suas conquistas vão morar aqui.', emptyText: 'Conclua uma tarefa na aba Pendentes para vê-la nesta página.'},
  };
  function resolve(path) { return Object.keys(pages).find(key => pages[key].path === path) || 'todas'; }
  function select(tasks, page, query = '', order = 'recentes') {
    const search = query.trim().toLocaleLowerCase('pt-BR');
    return tasks.filter(task => (page === 'todas' || (page === 'concluidas' ? task.concluida : !task.concluida)) && task.titulo.toLocaleLowerCase('pt-BR').includes(search))
      .sort((a, b) => order === 'titulo' ? a.titulo.localeCompare(b.titulo, 'pt-BR') : order === 'antigas' ? a.id - b.id : b.id - a.id);
  }
  return {pages, resolve, select};
})();
