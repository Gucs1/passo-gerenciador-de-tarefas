'use strict';
const $ = (selector) => document.querySelector(selector);
const state = {tasks: [], token: '', filter: 'todas', view: 'list', editing: null, deleting: null, busy: false, ready: false, loading: false};
let toastTimer;
function toast(message) { $('#toast').textContent = message; $('#toast').classList.add('show'); clearTimeout(toastTimer); toastTimer = setTimeout(() => $('#toast').classList.remove('show'), 3500); }
function banner(message = '') { $('#error-banner').hidden = !message; $('#error-banner span').textContent = message; }
function preference(key, value) { try { if (value === undefined) return localStorage.getItem(key); localStorage.setItem(key, value); } catch (_) {} }
async function request(data) {
  const options = data ? {method: 'POST', headers: {'Content-Type': 'application/json', 'X-Task-Token': state.token}, body: JSON.stringify(data)} : {};
  const response = await fetch('/api/tarefas', options);
  let result;
  try { result = await response.json(); } catch (_) { throw new Error('O servidor não respondeu como esperado. Tente novamente.'); }
  if (!response.ok) throw new Error(result.erro || 'Não foi possível completar a ação.');
  return result;
}
async function load() {
  if (state.busy || state.loading) return;
  state.loading = true; $('#refresh').disabled = true; $('#refresh').classList.add('refreshing');
  $('#task-content').setAttribute('aria-busy', 'true'); saveStatus('Atualizando tarefas…', true);
  try { const result = await request(); state.tasks = result.tarefas; state.token = result.token; state.ready = true; banner(); render(); saveStatus('Tudo atualizado'); }
  catch (error) { banner(error.message || 'Não foi possível conectar. Verifique se o programa está aberto.'); saveStatus('Atualização não confirmada'); if (!state.ready) { $('#task-content').replaceChildren(); $('#footer-count').textContent = 'Não foi possível carregar as tarefas.'; } }
  finally { state.loading = false; $('#refresh').disabled = false; $('#refresh').classList.remove('refreshing'); $('#task-content').setAttribute('aria-busy', 'false'); }
}
function saveStatus(message, saving = false) { $('#save-status').textContent = message; $('#save-status').classList.toggle('saving', saving); }
async function mutate(data, message) {
  if (state.busy || state.loading || !state.ready) return false;
  const focused = document.activeElement;
  const focusId = focused.closest('.task-row')?.dataset.id;
  const focusClass = focused.classList.contains('task-check') ? 'task-check' : null;
  state.busy = true; setBusy(true); saveStatus('Salvando seu passo…', true);
  try {
    const result = await request(data); state.tasks = result.tarefas; banner(); render(); toast(message); saveStatus('Alterações salvas');
    if (data.acao === 'situacao' && data.concluida) document.querySelector(`.task-row[data-id="${data.id}"]`)?.classList.add('just-completed');
    return true;
  }
  catch (error) { banner(error.message || 'Falha de conexão. A alteração não foi confirmada.'); saveStatus('Alteração não confirmada'); return false; }
  finally {
    state.busy = false; setBusy(false);
    if (focusId && focusClass && !document.querySelector('dialog[open]')) (document.querySelector(`.task-row[data-id="${focusId}"] .${focusClass}`) || $('#new-task')).focus({preventScroll: true});
  }
}
function setBusy(value) { document.querySelectorAll('#task-content button, #save-task, #confirm-delete, #refresh').forEach(button => { button.disabled = value; }); }
function filtered() {
  return PassoPages.select(state.tasks, state.filter, $('#search').value, $('#sort').value);
}
function openEditor(task = null) {
  if (!state.ready || state.loading || state.busy) { toast('Aguarde as tarefas carregarem antes de continuar.'); return; }
  state.editing = task?.id ?? null;
  $('#editor-title').textContent = task ? 'Um novo jeito de dizer.' : 'O que vamos fazer?';
  $('#task-title').value = task?.titulo ?? '';
  $('#save-task').textContent = task ? 'Salvar alterações ↗' : 'Criar tarefa ↗';
  $('#form-error').textContent = ''; updateCount(); $('#editor').showModal(); $('#task-title').focus();
}
function updateCount() { $('#char-count').textContent = `${$('#task-title').value.length}/300`; }
function taskRow(task) {
  const row = $('#task-template').content.firstElementChild.cloneNode(true);
  row.dataset.id = task.id;
  row.classList.toggle('completed', task.concluida);
  const check = row.querySelector('.task-check');
  check.textContent = task.concluida ? '✓' : '';
  check.setAttribute('aria-label', `${task.concluida ? 'Reabrir' : 'Concluir'}: ${task.titulo}`);
  check.setAttribute('aria-pressed', String(task.concluida));
  check.addEventListener('click', () => mutate({acao: 'situacao', id: task.id, concluida: !task.concluida}, task.concluida ? 'Tarefa reaberta. Um novo começo.' : 'Mais um passo dado. Tarefa concluída!'));
  const title = row.querySelector('.task-title'); title.textContent = task.titulo; title.title = 'Editar tarefa'; title.addEventListener('click', () => openEditor(task));
  row.querySelector('.task-id').textContent = `TAREFA ${String(task.id).padStart(3, '0')}`;
  const badge = row.querySelector('.badge'); badge.textContent = task.concluida ? 'Concluída' : 'Pendente'; badge.classList.toggle('done', task.concluida);
  row.querySelector('.edit-button').addEventListener('click', () => openEditor(task));
  row.querySelector('.delete-button').addEventListener('click', () => { state.deleting = task.id; $('#delete-title').textContent = task.titulo; $('#delete-error').textContent = ''; $('#delete-dialog').showModal(); });
  return row;
}
function emptyView() {
  const empty = document.createElement('div'); empty.className = 'empty';
  const hasSearch = Boolean($('#search').value.trim());
  const page = PassoPages.pages[state.filter];
  const icon = document.createElement('div'); icon.className = 'empty-symbol'; icon.textContent = hasSearch ? '⌕' : state.filter === 'concluidas' ? '✓' : '✦';
  const title = document.createElement('h3'); title.textContent = hasSearch ? 'Nenhum resultado nesta aba.' : page.emptyTitle;
  const text = document.createElement('p'); text.textContent = hasSearch ? 'Experimente outro termo para buscar nas tarefas desta página.' : page.emptyText;
  const button = document.createElement('button'); button.className = hasSearch || state.filter === 'concluidas' ? 'secondary' : 'primary'; button.textContent = hasSearch ? 'Limpar busca' : state.filter === 'concluidas' ? 'Ver tarefas pendentes' : '＋ Criar uma tarefa';
  button.addEventListener('click', () => { if (hasSearch) { $('#search').value = ''; render(); } else if (state.filter === 'concluidas') setFilter('pendentes'); else openEditor(); });
  empty.append(icon, title, text, button); return empty;
}
function render() {
  const total = state.tasks.length, done = state.tasks.filter(t => t.concluida).length, pending = total - done;
  const percent = total ? Math.round(done / total * 100) : 0;
  if ($('#total')) $('#total').textContent = total;
  if ($('#pending')) $('#pending').textContent = pending;
  if ($('#done')) $('#done').textContent = done;
  $('#nav-total').textContent = total; $('#nav-pending').textContent = pending; $('#nav-done').textContent = done;
  $('#tab-total').textContent = total; $('#tab-pending').textContent = pending; $('#tab-done').textContent = done;
  if ($('#percent')) $('#percent').firstChild.textContent = percent;
  if ($('#progress')) $('#progress').value = percent;
  if ($('#progress-label')) $('#progress-label').textContent = !total ? 'Vamos começar?' : percent === 100 ? 'Você chegou lá! ✦' : `${done} de ${total} concluídas`;
  if ($('#page-task-count')) { const count = state.filter === 'concluidas' ? done : pending; $('#page-task-count').textContent = `${count} ${count === 1 ? 'tarefa' : 'tarefas'}`; }
  const tasks = filtered(); $('#visible-count').textContent = tasks.length;
  $('#footer-count').textContent = `${tasks.length} ${tasks.length === 1 ? 'tarefa' : 'tarefas'} nesta visualização`;
  const content = $('#task-content'); content.replaceChildren();
  if (!tasks.length) content.append(emptyView());
  else if (state.view === 'list') tasks.forEach(t => content.append(taskRow(t)));
  else {
    const board = document.createElement('div'); board.className = 'board';
    const situations = state.filter === 'todas' ? [false, true] : [state.filter === 'concluidas'];
    board.classList.toggle('single-column', situations.length === 1);
    for (const completed of situations) {
      const column = document.createElement('section'); column.className = 'board-column';
      const subset = tasks.filter(t => t.concluida === completed);
      const heading = document.createElement('div'); heading.className = 'column-heading';
      const dot = document.createElement('i'); const label = document.createElement('strong'); label.textContent = completed ? 'Concluídas' : 'Pendentes';
      const count = document.createElement('span'); count.textContent = subset.length; heading.append(dot, label, count); column.append(heading);
      subset.forEach(t => column.append(taskRow(t)));
      if (!subset.length) { const text = document.createElement('p'); text.className = 'column-empty'; text.textContent = 'Nenhuma tarefa nesta coluna.'; column.append(text); }
      board.append(column);
    }
    content.append(board);
  }
  setBusy(state.busy);
}
function setFilter(filter) {
  const page = PassoPages.pages[filter];
  if (page && location.pathname !== page.path) location.assign(page.path);
}
function applyRoute() {
  const filter = PassoPages.resolve(location.pathname);
  const page = PassoPages.pages[filter];
  state.filter = filter;
  try {
    const preferences = JSON.parse(sessionStorage.getItem('passo-page-' + filter) || '{}');
    if (typeof preferences.query === 'string') $('#search').value = preferences.query;
    if (['recentes', 'antigas', 'titulo'].includes(preferences.sort)) $('#sort').value = preferences.sort;
    if (['list', 'board'].includes(preferences.view)) state.view = preferences.view;
  } catch (_) {}
  document.body.dataset.page = filter;
  document.title = `${page.title} — Passo`;
  document.querySelectorAll('[data-filter]').forEach(control => {
    const selected = control.dataset.filter === filter;
    control.classList.toggle(control.classList.contains('nav-item') ? 'active' : 'selected', selected);
    if (control.tagName === 'A') { if (selected) control.setAttribute('aria-current', 'page'); else control.removeAttribute('aria-current'); }
    else control.setAttribute('aria-pressed', String(selected));
  });
  $('#list-title').firstChild.textContent = page.title + ' '; $('#breadcrumb-title').textContent = page.title; $('#list-subtitle').textContent = page.subtitle;
  const heading = document.querySelector('h1'); heading.id = 'page-title'; $('#conteudo').setAttribute('aria-labelledby', 'page-title');
  updateView();
  if (state.ready) render();
}
window.addEventListener('pagehide', () => {
  try { sessionStorage.setItem('passo-page-' + state.filter, JSON.stringify({query: $('#search').value, sort: $('#sort').value, view: state.view})); } catch (_) {}
});
window.addEventListener('pageshow', event => { if (event.persisted) load(); });
document.querySelectorAll('button[data-filter]').forEach(button => button.addEventListener('click', () => setFilter(button.dataset.filter)));
$('#search').addEventListener('input', render); $('#sort').addEventListener('change', render);
$('#new-task').addEventListener('click', () => openEditor()); $('#quick-add').addEventListener('click', () => openEditor());
$('#task-title').addEventListener('input', updateCount);
$('#task-form').addEventListener('submit', async event => {
  event.preventDefault(); const title = $('#task-title').value.trim();
  if (!title) { $('#form-error').textContent = 'Escreva um título. Espaços não contam.'; $('#task-title').focus(); return; }
  const editing = state.editing !== null;
  const success = await mutate({acao: editing ? 'editar' : 'cadastrar', id: state.editing, titulo: title}, editing ? 'Tarefa atualizada.' : 'Tarefa criada. Você já deu o primeiro passo!');
  if (success) { $('#editor').close(); if (!editing && state.filter === 'concluidas') setFilter('pendentes'); } else $('#form-error').textContent = 'Não foi possível salvar. Confira o aviso na página.';
});
$('#confirm-delete').addEventListener('click', async () => { if (await mutate({acao: 'excluir', id: state.deleting}, 'Tarefa excluída. Espaço para o que importa.')) $('#delete-dialog').close(); else $('#delete-error').textContent = 'Não foi possível confirmar a exclusão. Feche esta janela e confira o aviso na página.'; });
document.querySelectorAll('[data-close]').forEach(button => button.addEventListener('click', () => { if (!state.busy) document.getElementById(button.dataset.close).close(); }));
document.querySelectorAll('dialog').forEach(dialog => dialog.addEventListener('cancel', event => { if (state.busy) event.preventDefault(); }));
for (const [id, view] of [['list-view', 'list'], ['board-view', 'board']]) $( '#' + id).addEventListener('click', () => { state.view = view; preference('passo-view', view); updateView(); render(); });
function updateView() { $('#list-view').classList.toggle('selected', state.view === 'list'); $('#board-view').classList.toggle('selected', state.view === 'board'); $('#list-view').setAttribute('aria-pressed', String(state.view === 'list')); $('#board-view').setAttribute('aria-pressed', String(state.view === 'board')); }
function updateTheme() { $('#theme span').textContent = document.body.classList.contains('dark') ? 'Modo claro' : 'Modo escuro'; $('#theme').setAttribute('aria-label', $('#theme span').textContent); }
$('#theme').addEventListener('click', () => { document.body.classList.toggle('dark'); preference('passo-theme', document.body.classList.contains('dark') ? 'dark' : 'light'); updateTheme(); });
$('#help').addEventListener('click', () => $('#help-dialog').showModal()); $('#retry').addEventListener('click', load);
$('#refresh').addEventListener('click', load);
document.querySelector('.skip').addEventListener('click', event => { event.preventDefault(); $('#conteudo').setAttribute('tabindex', '-1'); $('#conteudo').focus(); });
$('#export').addEventListener('click', () => {
  if (!state.ready) { toast('Carregue as tarefas antes de exportar.'); return; }
  const url = URL.createObjectURL(new Blob([JSON.stringify(state.tasks, null, 2)], {type: 'application/json'}));
  const link = document.createElement('a'); link.href = url; link.download = 'minhas-tarefas.json'; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); toast('Sua cópia de tarefas está pronta.');
});
document.addEventListener('keydown', event => {
  if (event.ctrlKey || event.metaKey || event.altKey || ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName) || document.querySelector('dialog[open]')) return;
  if (event.key.toLowerCase() === 'n') { event.preventDefault(); openEditor(); }
  if (event.key === '/') { event.preventDefault(); $('#search').focus(); }
  if (event.key === '?') { event.preventDefault(); $('#help-dialog').showModal(); }
});
$('#today').textContent = new Intl.DateTimeFormat('pt-BR', {day: 'numeric', month: 'long', year: 'numeric'}).format(new Date());
if (preference('passo-theme') === 'dark') document.body.classList.add('dark'); updateTheme();
document.querySelectorAll('.nav-item').forEach(button => { button.setAttribute('aria-label', PassoPages.pages[button.dataset.filter].title); });
$('#help').setAttribute('aria-label', 'Atalhos de teclado');
for (const [id, heading] of [['editor', 'editor-title'], ['delete-dialog', 'delete-heading'], ['help-dialog', 'help-heading']]) {
  const dialog = $('#' + id); const title = dialog.querySelector('h2'); title.id = heading; dialog.setAttribute('aria-labelledby', heading);
  dialog.addEventListener('close', () => { if (!document.querySelector('dialog[open]') && !document.activeElement.closest('.task-row')) $('#new-task').focus({preventScroll: true}); });
}
$('#task-title').setAttribute('aria-describedby', 'form-error char-count');
state.view = preference('passo-view') === 'board' ? 'board' : 'list';
if (location.hash.startsWith('#/')) location.replace(PassoPages.pages[PassoPages.resolve(location.hash.slice(1))].path);
else { applyRoute(); load(); }
