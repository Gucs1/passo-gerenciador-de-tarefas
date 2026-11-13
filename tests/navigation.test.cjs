const test = require('node:test');
const assert = require('node:assert/strict');
require('../static/navigation.js');

const {pages, resolve, select} = globalThis.PassoPages;
const tasks = [
  {id: 1, titulo: 'Estudar Python', concluida: false},
  {id: 2, titulo: 'Criar uma tarefa', concluida: true},
  {id: 3, titulo: 'Praticar Python', concluida: false},
];

test('cada aba tem endereço próprio e pode ser resolvida diretamente', () => {
  assert.equal(new Set(Object.values(pages).map(page => page.path)).size, 3);
  for (const [key, page] of Object.entries(pages)) assert.equal(resolve(page.path), key);
});
test('endereço ausente ou desconhecido volta para a visão geral', () => {
  assert.equal(resolve(''), 'todas');
  assert.equal(resolve('/inexistente'), 'todas');
});
test('pendentes mostra somente tarefas ainda não concluídas', () => {
  assert.deepEqual(select(tasks, 'pendentes').map(t => t.id), [3, 1]);
});
test('concluídas mostra somente tarefas concluídas', () => {
  assert.deepEqual(select(tasks, 'concluidas').map(t => t.id), [2]);
});
test('a busca respeita a aba e ignora maiúsculas e espaços nas pontas', () => {
  assert.deepEqual(select(tasks, 'pendentes', ' PYTHON ').map(t => t.id), [3, 1]);
  assert.deepEqual(select(tasks, 'concluidas', 'Python'), []);
});
test('concluir e reabrir transfere a tarefa entre as páginas', () => {
  const updated = tasks.map(t => t.id === 1 ? {...t, concluida: true} : {...t});
  assert.deepEqual(select(updated, 'pendentes').map(t => t.id), [3]);
  assert.deepEqual(select(updated, 'concluidas').map(t => t.id), [2, 1]);
  updated[0].concluida = false;
  assert.deepEqual(select(updated, 'pendentes').map(t => t.id), [3, 1]);
});
test('ordenação funciona em cada página sem modificar os dados originais', () => {
  const before = JSON.stringify(tasks);
  assert.deepEqual(select(tasks, 'todas', '', 'antigas').map(t => t.id), [1, 2, 3]);
  assert.deepEqual(select(tasks, 'todas', '', 'titulo').map(t => t.id), [2, 1, 3]);
  assert.equal(JSON.stringify(tasks), before);
});
test('cada página tem seu título e sua mensagem de lista vazia', () => {
  assert.equal(new Set(Object.values(pages).map(page => page.title)).size, 3);
  assert.equal(new Set(Object.values(pages).map(page => page.emptyTitle)).size, 3);
  assert.deepEqual(select([], 'pendentes'), []);
  assert.deepEqual(select([], 'concluidas'), []);
});
