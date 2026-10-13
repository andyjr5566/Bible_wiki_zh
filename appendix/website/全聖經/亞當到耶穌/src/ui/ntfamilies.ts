import { hierarchy, tree } from 'd3-hierarchy';
import type { Family, GenealogyData, Person } from '../data/types';
import { buildGraph } from '../data/model';
import { h, svgEl } from './dom';

interface FamilyTreeNode { person: Person; children: FamilyTreeNode[] }

export function createNTFamilies(data: GenealogyData, onPerson: (id: string) => void, onTree: (id: string) => void): HTMLElement {
  const root = h('section', { className: 'ag-page ag-families-page' },
    h('div', { className: 'ag-page-heading' }, h('div', {}, h('p', { className: 'ag-eyebrow' }, '新約中的家族'), h('h1', {}, '新約家族')),
      h('p', {}, '每張小圖只展開資料明列的親屬關係。連得上主線的人可回到家譜樹查看。')));
  const families = data.ntFamilies ?? [];
  if (!families.length) {
    root.append(h('div', { className: 'ag-empty-state' }, h('strong', {}, '新約家族資料尚未加入'), h('p', {}, '這份測試資料沒有 ntFamilies 項目。')));
    return root;
  }
  const graph = buildGraph(data);
  for (const family of families) root.append(createFamilyCard(data, family, onPerson, onTree, graph));
  return root;
}

export function createFamilyCard(
  data: GenealogyData,
  family: Family,
  onPerson: (id: string) => void,
  onTree: (id: string) => void,
  graph = buildGraph(data),
): HTMLElement {
  const members = familyMembers(family, graph);
  const memberIds = new Set(members.keys());
  const children = parentChildren(data);
  const rootIds = (family.roots?.length ? family.roots : [...memberIds].filter((id) => {
    const person = graph.byId.get(id)!;
    return !(person.parents ?? []).some((parent) => memberIds.has(parent.id));
  })).filter((id) => memberIds.has(id));
  const trees = rootIds.map((id) => buildFamilyTree(id, members, children)).filter((node): node is FamilyTreeNode => Boolean(node));
  const svg = svgEl('svg', { class: 'ag-family-svg', role: 'img', 'aria-label': `${family.title}家族圖` });
  const edgeLayer = svgEl('g', { class: 'ag-family-edges' });
  const nodeLayer = svgEl('g', { class: 'ag-family-nodes' });
  let offsetY = 16;
  let viewWidth = 880;
  for (const familyRoot of trees) {
    const hRoot = hierarchy(familyRoot, (node) => node.children);
    const laid = tree<typeof familyRoot>().nodeSize([48, 170])(hRoot);
    const nodes = laid.descendants();
    const minX = Math.min(...nodes.map((node) => node.x));
    const maxX = Math.max(...nodes.map((node) => node.x));
    const maxY = Math.max(...nodes.map((node) => node.y));
    const localHeight = Math.max(48, maxX - minX + 48);
    viewWidth = Math.max(viewWidth, maxY + 250);
    for (const node of laid.links()) {
      const sourceY = offsetY + node.source.x - minX;
      const targetY = offsetY + node.target.x - minX;
      edgeLayer.append(svgEl('path', {
        class: 'ag-family-edge',
        d: `M${node.source.y + 170} ${sourceY} C${node.source.y + 210} ${sourceY}, ${node.target.y + 130} ${targetY}, ${node.target.y + 130} ${targetY}`,
      }));
    }
    for (const node of nodes) {
      const person = node.data.person;
      const group = svgEl('g', { class: 'ag-family-node', transform: `translate(${node.y + 110} ${offsetY + node.x - minX})`, tabindex: '0', role: 'button', 'aria-label': person.name });
      group.append(svgEl('rect', { x: -65, y: -17, width: 130, height: 34, rx: 7 }));
      const label = svgEl('text', { 'text-anchor': 'middle', 'dominant-baseline': 'central' }); label.textContent = person.name;
      group.append(label);
      group.addEventListener('click', () => onPerson(person.id));
      group.addEventListener('keydown', (event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); onPerson(person.id); } });
      nodeLayer.append(group);
    }
    offsetY += localHeight + 28;
  }
  svg.setAttribute('viewBox', `0 0 ${viewWidth} ${Math.max(180, offsetY)}`);
  svg.append(edgeLayer, nodeLayer);
  const card = h('article', { className: 'ag-family-card', 'data-family-card-id': family.id },
    h('header', {}, h('div', {}, h('p', { className: 'ag-eyebrow' }, `${members.size} 位人物`), h('h2', {}, family.title)),
      family.imported ? h('span', { className: 'ag-family-imported' }, '歷代志上族譜頁') : null,
      family.intro ? h('p', {}, family.intro) : null),
    svg);
  const mainline = [...members.values()].filter((person) => graph.spineIds.has(person.id));
  if (mainline.length) {
    const shortcuts = h('div', { className: 'ag-chip-list' }, ...mainline.map((person) => {
      const action = h('button', { className: 'ag-person-link', type: 'button' }, `在家譜樹上看：${person.name}`);
      action.addEventListener('click', () => onTree(person.id));
      return action;
    }));
    card.append(shortcuts);
  }
  return card;
}

function familyMembers(family: Family, graph: ReturnType<typeof buildGraph>): Map<string, Person> {
  if (family.members) {
    return new Map(family.members.map((id) => graph.byId.get(id)).filter((person): person is Person => Boolean(person)).map((person) => [person.id, person]));
  }
  const members = new Map<string, Person>();
  const queue = [...(family.roots ?? [])];
  const limit = Math.max(1, Math.min(120, Number(family.count ?? 60)));
  while (queue.length && members.size < limit) {
    const id = queue.shift()!;
    if (members.has(id)) continue;
    const person = graph.byId.get(id);
    if (!person) continue;
    members.set(id, person);
    queue.push(...(graph.children.get(id) ?? []));
  }
  return members;
}

function parentChildren(data: GenealogyData): Map<string, string[]> {
  const children = new Map<string, string[]>();
  for (const person of data.persons) {
    for (const parent of person.parents ?? []) {
      const childIds = children.get(parent.id) ?? [];
      if (!childIds.includes(person.id)) childIds.push(person.id);
      children.set(parent.id, childIds);
    }
  }
  return children;
}

function buildFamilyTree(id: string, members: Map<string, Person>, childrenByParent: Map<string, string[]>, visited = new Set<string>()): FamilyTreeNode | null {
  const person = members.get(id);
  if (!person || visited.has(id)) return null;
  visited.add(id);
  const children = (childrenByParent.get(id) ?? []).filter((child) => members.has(child))
    .map((child) => buildFamilyTree(child, members, childrenByParent, visited)).filter((node): node is FamilyTreeNode => Boolean(node));
  return { person, children };
}
