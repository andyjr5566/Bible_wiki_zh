import './styles.css';
import { DATA, VERSES, buildGraph, makeSyntheticData, pathToFirstAncestor } from './data/model';
import type { GenealogyData, GenealogyNote, Person } from './data/types';
import { createAges } from './ui/ages';
import { createCanvas, type CanvasApi } from './ui/canvas';
import { createCompare } from './ui/compare';
import { createPersonCard, type PersonCard } from './ui/card';
import { button, h } from './ui/dom';
import { createNTFamilies } from './ui/ntfamilies';
import { createNotes } from './ui/notes';
import { createToolbar, type LineFilter, type PageId } from './ui/toolbar';
import { createTour } from './ui/tour';
import { createUnconnectedFamilies } from './ui/unconnected';

const synthetic = import.meta.env.DEV && new URLSearchParams(location.search).get('synthetic') === '1';
const data: GenealogyData = synthetic ? makeSyntheticData() : DATA;
const graph = buildGraph(data);
let line: LineFilter = 'both';
let page: PageId = 'tree';

const app = document.querySelector<HTMLElement>('#app');
if (!app) throw new Error('Missing #app root');
const verseLayer = h('div', { className: 'ag-modal-layer', hidden: true });

const openVerse = (ref: string) => {
  const verse = VERSES[ref];
  const dialog = h('section', { className: 'ag-verse-dialog', role: 'dialog', 'aria-modal': 'true', 'aria-labelledby': 'ag-verse-title' },
    h('div', { className: 'ag-dialog-head' }, h('div', {}, h('p', { className: 'ag-eyebrow' }, '經文全文'), h('h2', { id: 'ag-verse-title' }, ref)),
      button('關閉', () => { verseLayer.hidden = true; verseLayer.replaceChildren(); }, 'ag-card-close')),
    verse ? h('p', { className: 'ag-verse-text' }, verse) : h('p', { className: 'ag-empty-state' }, '這節經文尚未收錄在目前的 verses.json。'));
  verseLayer.hidden = false;
  verseLayer.replaceChildren(h('div', { className: 'ag-dialog-scrim' }, dialog));
};

let canvas: CanvasApi;
let card: PersonCard;
const selectPerson = (person: Person | null) => {
  if (!person) {
    card.show(null);
    canvas.select(null);
    if (location.hash.startsWith('#p=')) history.replaceState(null, '', `${location.pathname}${location.search}`);
    return;
  }
  page = 'tree';
  applyPage();
  const focusId = focusIdForPerson(person);
  canvas.select(focusId);
  if (focusId) canvas.focusPerson(focusId, true);
  card.show(person);
  history.replaceState(null, '', `${location.pathname}${location.search}#p=${encodeURIComponent(person.id)}`);
};

canvas = createCanvas(data, selectPerson, openNote);
card = createPersonCard(data, {
  select: (id) => { const person = graph.byId.get(id); if (person) selectPerson(person); },
  verse: openVerse,
  trace: traceToAdam,
  family: openPersonFamily,
  note: openNote,
});

const treePage = h('section', { className: 'ag-workspace ag-page-view', 'data-page': 'tree' },
  h('div', { className: 'ag-canvas-wrap' }, canvas.el,
    h('div', { className: 'ag-canvas-legend-panel' },
      h('div', { className: 'ag-legend' },
        h('span', {}, h('i', { className: 'ag-dot ag-dot-common' }), '共同主線'),
        h('span', {}, h('i', { className: 'ag-dot ag-dot-matthew' }), '馬太'),
        h('span', {}, h('i', { className: 'ag-dot ag-dot-luke' }), '路加'),
        h('span', {}, h('i', { className: 'ag-dot ag-dot-side' }), '旁支')),
      h('div', { className: 'ag-canvas-hint' }, '拖曳移動畫布　·　Ctrl＋滾輪縮放　·　觸控可平移與雙指縮放'))),
  card.el);
const comparePage = createCompare(data, (id) => {
  const person = graph.byId.get(id);
  if (person) selectPerson(person);
});
const agesPage = createAges(data, VERSES, (id) => {
  const person = graph.byId.get(id);
  if (person) selectPerson(person);
}, openVerse);
const notesPage = createNotes(data, VERSES, (id) => {
  const person = graph.byId.get(id);
  if (person) selectPerson(person);
}, openVerse);
const familiesPage = createNTFamilies(data, (id) => {
  const person = graph.byId.get(id);
  if (person) selectPerson(person);
}, (id) => {
  const person = graph.byId.get(id);
  if (person) selectPerson(person);
});
const unconnectedFamiliesPage = createUnconnectedFamilies(data, (id) => {
  const person = graph.byId.get(id);
  if (person) selectPerson(person);
}, (id) => {
  const person = graph.byId.get(id);
  if (person) selectPerson(person);
});
const pageNodes = new Map<PageId, HTMLElement>([
  ['tree', treePage], ['compare', comparePage], ['ages', agesPage], ['notes', notesPage], ['families', familiesPage], ['unconnected', unconnectedFamiliesPage.el],
]);

function focusPageTarget(container: HTMLElement, selector: string, value: string) {
  const target = [...container.querySelectorAll<HTMLElement>(selector)].find((element) => element.dataset.familyCardId === value);
  if (!target) return;
  container.scrollTo({ top: container.scrollTop + target.getBoundingClientRect().top - container.getBoundingClientRect().top - 20, behavior: 'smooth' });
}

function openPersonFamily(id: string) {
  if (unconnectedFamiliesPage.hasPerson(id)) {
    page = 'unconnected';
    applyPage();
    unconnectedFamiliesPage.focusPerson(id);
    return;
  }
  const family = (data.ntFamilies ?? []).find((item) => item.members?.includes(id) || item.roots?.includes(id));
  if (family) {
    page = 'families';
    applyPage();
    focusPageTarget(familiesPage, '[data-family-card-id]', family.id);
    return;
  }
  page = 'unconnected';
  applyPage();
}

function chooseSearchPerson(person: Person) {
  if (unconnectedFamiliesPage.hasPerson(person.id)) {
    page = 'unconnected';
    applyPage();
    unconnectedFamiliesPage.focusPerson(person.id);
    return;
  }
  selectPerson(person);
}

function focusIdForPerson(person: Person): string | null {
  canvas.expandFor(person.id);
  if (canvas.layoutNow().nodes.some((node) => node.id === person.id)) return person.id;

  const childThroughMother = data.persons.find((candidate) =>
    candidate.parents?.some((parent) => parent.id === person.id && parent.role === '母') ||
    candidate.mother_name === person.name || candidate.mother_name === person.id);
  const childId = childThroughMother?.id ?? graph.children.get(person.id)?.[0];
  if (childId) {
    canvas.expandFor(childId);
    return childId;
  }

  const spouseId = person.spouses?.[0]?.id;
  if (spouseId) {
    canvas.expandFor(spouseId);
    return spouseId;
  }
  return null;
}

function applyPage() {
  for (const [id, element] of pageNodes) element.hidden = id !== page;
  toolbar?.setState();
}

const toolbar = createToolbar(data, {
  selectPerson: chooseSearchPerson,
  setPage(id) { page = id; applyPage(); },
  setLine(value) { line = value; canvas.setLine(value); },
  restartTour() { page = 'tree'; applyPage(); tour.start(); },
  zoom: (factor) => canvas.zoom(factor),
  fit: () => canvas.fitSpine(true),
  getLine: () => line,
  getPage: () => page,
});
const tour = createTour(data, canvas, openVerse);
const main = h('main', { className: 'ag-main' });
for (const element of pageNodes.values()) main.append(element);
const footer = h('footer', { className: 'ag-footer' },
  h('span', {}, '家譜依資料中的經文記載呈現。'),
  h('span', {}, synthetic ? '合成壓力測試資料' : `${data.persons.length.toLocaleString()} 位人物`));
app.replaceChildren(toolbar.el, main, footer, tour.el, verseLayer);
applyPage();

function applyDeepLink() {
  const hash = location.hash.slice(1);
  if (hash.startsWith('p=')) {
    let id = '';
    try { id = decodeURIComponent(hash.slice(2)); } catch { return; }
    const person = graph.byId.get(id);
    if (!person) return;
    tour.stop(false);
    selectPerson(person);
    return;
  }
  if (hash.startsWith('family=')) {
    let id = '';
    try { id = decodeURIComponent(hash.slice('family='.length)); } catch { return; }
    if (!id) return;
    tour.stop(false);
    page = 'tree';
    applyPage();
    canvas.expandFamily(id);
  }
}

window.addEventListener('hashchange', applyDeepLink);
requestAnimationFrame(() => {
  if (!location.hash && window.matchMedia('(max-width: 520px)').matches) {
    const first = Object.values(data.spine.lines)[0]?.[0];
    if (first) canvas.focusPerson(first, false);
  }
  requestAnimationFrame(applyDeepLink);
});

function traceToAdam(id: string) {
  const person = graph.byId.get(id);
  if (!person) return;
  const route = pathToFirstAncestor(id, data, graph);
  if (!route) {
    canvas.expandFor(id);
    canvas.setTrace([], []);
    const unattached = data.unattached?.includes(id) ?? false;
    const message = !person.parents?.length && !unattached
      ? '經文沒有記載他的父母。'
      : '經文沒有記載他和主線的關係。';
    card.setTraceMessage(message, false, unattached);
    const focusId = focusIdForPerson(person);
    if (focusId) canvas.focusPerson(focusId, true);
    return;
  }
  const drawingEdges = route.edges.map((edge) => ({
    from: edge.to,
    to: edge.from,
    kind: edge.kind,
  }));
  canvas.setTrace(route.ids, drawingEdges);
  canvas.expandPath(route.ids);
  card.setTraceMessage('', route.hasUnknownGenerations);
  canvas.focusIds(route.ids, true);
}

function openNote(noteId: string) {
  const note = data.notes.find((item) => item.id === noteId);
  if (!note) return;
  const dialog = noteDialog(note);
  verseLayer.hidden = false;
  verseLayer.replaceChildren(h('div', { className: 'ag-dialog-scrim' }, dialog));
}

function noteDialog(note: GenealogyNote): HTMLElement {
  const dialog = h('section', { className: 'ag-note-dialog', role: 'dialog', 'aria-modal': 'true', 'aria-labelledby': 'ag-note-dialog-title' },
    h('div', { className: 'ag-dialog-head' }, h('div', {}, h('p', { className: 'ag-eyebrow' }, '經文不同的地方'), h('h2', { id: 'ag-note-dialog-title' }, note.title)),
      button('關閉', () => { verseLayer.hidden = true; verseLayer.replaceChildren(); }, 'ag-card-close')));
  for (const item of note.scripture ?? []) {
    const text = item.quote ?? VERSES[item.ref] ?? '經文全文尚未收錄。';
    dialog.append(h('blockquote', {}, h('p', {}, `「${text}」`), button(item.ref, () => openVerse(item.ref), 'ag-text-button')));
  }
  if (note.text) dialog.append(h('p', { className: 'ag-note-text' }, note.text));
  for (const view of note.views ?? []) {
    dialog.append(h('section', { className: 'ag-view-card' },
      view.source ? h('h3', {}, String(view.source)) : null,
      view.quote ? h('blockquote', {}, `「${String(view.quote)}」`) : null,
      view.translation ? h('p', {}, String(view.translation)) : null,
      view.paraphrase ? h('p', {}, String(view.paraphrase)) : null,
      view.url ? h('a', { href: String(view.url), target: '_blank', rel: 'noopener noreferrer' }, '查看來源網址') : null));
  }
  const attached = h('div', { className: 'ag-chip-list' });
  for (const id of note.attach ?? []) {
    const person = graph.byId.get(id);
    if (!person) continue;
    attached.append(button(person.name, () => {
      verseLayer.hidden = true;
      verseLayer.replaceChildren();
      selectPerson(person);
    }, 'ag-person-link'));
  }
  if (attached.childElementCount) dialog.append(h('p', {}, '相關人物'), attached);
  return dialog;
}
