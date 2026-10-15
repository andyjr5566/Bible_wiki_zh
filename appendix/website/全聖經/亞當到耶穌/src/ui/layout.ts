import { hierarchy, tree } from 'd3-hierarchy';
import { branchRoots, buildGraph, firstReference, isPlacementNode } from '../data/model';
import type { GenealogyData, Person } from '../data/types';

export const MAIN_NODE_W = 96;
export const MAIN_NODE_H = 48;
export const SIDE_NODE_W = 96;
export const SIDE_NODE_H = 46;
export const ROW_H = 82;
export const COLUMN_W = 320;
const SIDE_GAP_X = 24;
const SIDE_LEVEL_GAP_X = 52;
const SIDE_ROW_STEP = 82;
const ROW_TREE_PADDING = 20;

export interface LayoutNode {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  rectX: number;
  rectWidth: number;
  rectHeight: number;
  sideRoot?: string;
  mainline: boolean;
  collapsed?: boolean;
  expandedRoot?: boolean;
  descendantCount?: number;
  segment?: string;
  groupLabel?: string;
  groupKey?: string;
  groupMembers?: string[];
  groupLine?: string;
  groupParentId?: string;
  syntheticParent?: string;
}

export interface LayoutEdge {
  from: string;
  to: string;
  kind: 'parent' | 'mother' | 'descends' | 'list' | 'member' | 'kin';
  line: string;
  key: string;
}

export interface CanvasLayout {
  nodes: LayoutNode[];
  groups: LayoutNode[];
  edges: LayoutEdge[];
  regions: Array<{ id: string; title: string; x0: number; y0: number; x1: number; y1: number }>;
  segments: Array<{ title: string; y0: number; y1: number; line: string; labelX: number }>;
  bounds: { x: number; y: number; width: number; height: number };
  durationMs: number;
}

interface BranchDatum {
  person: Person | null;
  rootId?: string;
  groupKey?: string;
  groupLabel?: string;
  groupMembers?: string[];
  groupLine?: string;
  groupParentId?: string;
  children: BranchDatum[];
}

interface BranchPlacement {
  person: Person | null;
  id: string;
  rootId: string;
  depth: number;
  vertical: number;
  collapsed: boolean;
  expandedRoot: boolean;
  descendantCount: number;
  groupLabel?: string;
  groupKey?: string;
  groupMembers?: string[];
  groupLine?: string;
  groupParentId?: string;
  inGroup?: boolean;
  metrics: NodeMetrics;
}

interface NodeMetrics {
  width: number;
  height: number;
  rectX: number;
  rectWidth: number;
  rectHeight: number;
}

interface BranchForest {
  parentId: string;
  /** 第一層往外多推的距離（避開分岔處往下走的主線） */
  pushOut?: number;
  direction: -1 | 1;
  roots: string[];
  placements: BranchPlacement[];
  height: number;
  levelWidths: Map<number, number>;
  groupKey?: string;
  grouped?: boolean;
}

const lineColorKey = (person: Person): string => {
  const lines = person.lines ?? [];
  return lines.includes('common') ? 'common' : lines.includes('馬太') ? '馬太' : lines.includes('路加') ? '路加' : 'common';
};

function textWidth(text: string, fontSize: number): number {
  return Array.from(text).reduce((width, char) => width + (/[\u0000-\u00ff]/.test(char) ? fontSize * 0.58 : fontSize), 0);
}

function markText(person: Person): string {
  return (person.marks ?? []).map((item) => item.label).filter(Boolean).join('／');
}

function nodeMetrics(person: Person, mainline: boolean, control = false): NodeMetrics {
  const minWidth = mainline ? MAIN_NODE_W : SIDE_NODE_W;
  const rectHeight = mainline ? MAIN_NODE_H : SIDE_NODE_H;
  const subtitle = person.qualifier || firstReference(person) || '';
  const mark = markText(person);
  const labelWidth = Math.max(textWidth(person.name, 15), textWidth(subtitle, 11));
  const badgeWidth = mark ? textWidth(mark, 10) + 18 : 0;
  const rectWidth = Math.max(minWidth, Math.ceil(labelWidth + 28), Math.ceil(badgeWidth));
  const extraWidth = control ? 24 : 0;
  return {
    width: rectWidth + extraWidth,
    height: rectHeight + (mark ? 20 : 0),
    rectX: -((rectWidth + extraWidth) / 2),
    rectWidth,
    rectHeight,
  };
}

// 名單牌子與區域：標題較長，下面一行是經節範圍
function plaqueMetrics(person: Person, control: boolean): NodeMetrics {
  const rectWidth = Math.max(SIDE_NODE_W + 24, Math.ceil(Math.max(textWidth(person.name, 14), textWidth(person.qualifier ?? '', 11)) + 36));
  const rectHeight = person.kind === 'region' ? 54 : 48;
  const extraWidth = control ? 24 : 0;
  return { width: rectWidth + extraWidth, height: rectHeight, rectX: -((rectWidth + extraWidth) / 2), rectWidth, rectHeight };
}

function groupNodeMetrics(label: string): NodeMetrics {
  const rectWidth = Math.max(104, Math.ceil(textWidth(label, 12) + 28));
  const rectHeight = 34;
  return { width: rectWidth, height: rectHeight, rectX: -rectWidth / 2, rectWidth, rectHeight };
}

function countDesc(id: string, children: Map<string, string[]>): number {
  let total = 0;
  const seen = new Set([id]);
  const stack = [...(children.get(id) ?? [])];
  while (stack.length) {
    const next = stack.pop()!;
    if (seen.has(next)) continue;
    seen.add(next);
    total += 1;
    stack.push(...(children.get(next) ?? []));
  }
  return total;
}

function buildForests(
  data: GenealogyData,
  graph: ReturnType<typeof buildGraph>,
  mainIds: Set<string>,
  expanded: Set<string>,
): BranchForest[] {
  // 每位主線人物左右各一片旁支；真正的子女超過三位時收成一個「N 位子女」，
  // 大圖安置掛上來的（母親、妻子、名單牌子、區域）另外排在子女後面，不算進子女數。
  const groups = new Map<string, { parentId: string; direction: -1 | 1; roots: string[]; extras: string[] }>();
  const rootOwner = new Set<string>();
  const rootCounts = new Map<string, number>();
  const clearColumn = new Set<string>();
  for (const { parentId, rootId } of branchRoots(data, graph)) {
    if (rootOwner.has(rootId)) continue;
    const rootPerson = graph.byId.get(rootId);
    const parent = graph.byId.get(parentId);
    if (!rootPerson || !parent) continue;
    rootOwner.add(rootId);
    const placement = graph.placed.get(rootId);
    const route = lineColorKey(rootPerson) !== 'common' ? lineColorKey(rootPerson) : lineColorKey(parent);
    const outward: -1 | 1 = route === '馬太' ? -1 : 1;
    // 母親、妻子放在另一側；只有共同主線（畫面中央）那段的另一側是空的，馬太、路加兩欄往中間放會撞到對面那一欄
    const direction: -1 | 1 = placement?.side === 'opposite' && lineColorKey(parent) === 'common' ? (-outward as -1 | 1) : outward;
    const key = `${parentId}\u0000${direction}`;
    const group = groups.get(key) ?? { parentId, direction, roots: [], extras: [] };
    // 主線在這裡分成馬太、路加兩欄時（大衛），左邊有馬太線往下走：放在左邊的母親、妻子要整組推到線外面
    if (direction === -1 && (graph.children.get(parentId) ?? []).some((id) => graph.spineIds.has(id) && lineColorKey(graph.byId.get(id)!) === '馬太')) {
      clearColumn.add(key);
    }
    if (placement) group.extras.push(rootId);
    else {
      group.roots.push(rootId);
      rootCounts.set(parentId, (rootCounts.get(parentId) ?? 0) + 1);
    }
    groups.set(key, group);
  }

  const globallyAssigned = new Set<string>();
  const forests: BranchForest[] = [];
  for (const group of groups.values()) {
    const localAssigned = new Set<string>();
    const allRoots = [...group.roots, ...group.extras];
    const descendantCount = new Map(allRoots.map((id) => [id, countDesc(id, graph.children)]));
    const grouped = (rootCounts.get(group.parentId) ?? 0) > 3 && group.roots.length > 1;
    const groupKey = `siblings:${group.parentId}:${group.direction}`;
    const groupOpen = grouped && (expanded.has(groupKey) || group.roots.every((id) => expanded.has(id)));
    const makeBranch = (id: string, rootId: string, includeChildren: boolean): BranchDatum | null => {
      if (mainIds.has(id) || globallyAssigned.has(id) || localAssigned.has(id)) return null;
      const person = graph.byId.get(id);
      if (!person) return null;
      localAssigned.add(id);
      // 名單牌子和區域各自展開收合：上一層打開了，牌子底下的人還是要再點牌子才出來
      const open = isPlacementNode(person) ? expanded.has(id) : includeChildren;
      const children = open
        ? (graph.children.get(id) ?? []).map((childId) => makeBranch(childId, rootId, true)).filter((item): item is BranchDatum => Boolean(item))
        : [];
      return { person, rootId, children };
    };
    const members = groupOpen
      ? group.roots.map((rootId) => makeBranch(rootId, rootId, expanded.has(rootId))).filter((item): item is BranchDatum => Boolean(item))
      : [];
    const firstRoot = graph.byId.get(group.roots[0] ?? group.extras[0]!);
    const parentPerson = graph.byId.get(group.parentId)!;
    const line = firstRoot && lineColorKey(firstRoot) !== 'common' ? lineColorKey(firstRoot) : lineColorKey(parentPerson);
    const extraData = group.extras.map((rootId) => makeBranch(rootId, rootId, expanded.has(rootId))).filter((item): item is BranchDatum => Boolean(item));
    const rootData = grouped
      ? [{ person: null, rootId: group.parentId, groupKey, groupLabel: groupOpen ? `收合 ${group.roots.length} 位子女 −` : `${group.roots.length} 位子女 ＋`,
        groupMembers: group.roots, groupLine: line, groupParentId: group.parentId, children: members }, ...extraData]
      : [...group.roots.map((rootId) => makeBranch(rootId, rootId, expanded.has(rootId))).filter((item): item is BranchDatum => Boolean(item)), ...extraData];
    for (const id of localAssigned) globallyAssigned.add(id);
    if (!rootData.length) continue;
    const datum: BranchDatum = { person: null, children: rootData };
    const root = hierarchy(datum, (item) => item.children);
    const laidOut = tree<BranchDatum>().nodeSize([SIDE_ROW_STEP, 1])(root);
    const visible = laidOut.descendants().filter((item) => item.data.person || item.data.groupLabel);
    const metricsOf = (item: typeof visible[number]) => item.data.groupLabel
      ? groupNodeMetrics(item.data.groupLabel)
      : isPlacementNode(item.data.person) ? plaqueMetrics(item.data.person!, true)
        : nodeMetrics(item.data.person!, false, item.data.rootId === item.data.person!.id && expanded.has(item.data.rootId));
    const top = Math.min(...visible.map((item) => {
      return item.x - metricsOf(item).height / 2;
    }));
    const bottom = Math.max(...visible.map((item) => {
      return item.x + metricsOf(item).height / 2;
    }));
    const center = (top + bottom) / 2;
    const levelWidths = new Map<number, number>();
    const placements = visible.map((item): BranchPlacement => {
      if (item.data.groupLabel && item.data.groupKey) {
        const metrics = groupNodeMetrics(item.data.groupLabel);
        levelWidths.set(item.depth, Math.max(levelWidths.get(item.depth) ?? 0, metrics.width));
        return {
          person: null, id: item.data.groupKey, rootId: group.parentId, depth: item.depth, vertical: item.x - center,
          collapsed: !groupOpen, expandedRoot: groupOpen, descendantCount: group.roots.length,
          groupLabel: item.data.groupLabel, groupKey: item.data.groupKey, groupMembers: item.data.groupMembers,
          groupLine: item.data.groupLine, groupParentId: item.data.groupParentId, metrics,
        };
      }
      const person = item.data.person!;
      const rootId = item.data.rootId!;
      const isRoot = rootId === person.id;
      // 旁支的根和名單牌子、區域都可以單獨展開收合
      const toggles = isRoot || isPlacementNode(person);
      const count = toggles ? (descendantCount.get(person.id) ?? countDesc(person.id, graph.children)) : 0;
      const isOpen = toggles && count > 0 && expanded.has(person.id);
      const hasControl = toggles && (isOpen || count > 0);
      const metrics = isPlacementNode(person) ? plaqueMetrics(person, hasControl) : nodeMetrics(person, false, hasControl);
      levelWidths.set(item.depth, Math.max(levelWidths.get(item.depth) ?? 0, metrics.width));
      return {
        person,
        id: person.id,
        rootId,
        depth: item.depth,
        vertical: item.x - center,
        collapsed: toggles && !isOpen && count > 0,
        expandedRoot: isOpen,
        descendantCount: count,
        inGroup: Boolean(item.parent?.data.groupKey),
        metrics,
      };
    });
    forests.push({
      parentId: group.parentId,
      direction: group.direction,
      roots: group.roots,
      placements,
      height: bottom - top + ROW_TREE_PADDING,
      levelWidths,
      ...(grouped ? { groupKey } : {}),
      grouped,
      pushOut: clearColumn.has(`${group.parentId}\u0000${group.direction}`) ? COLUMN_W / 2 + 48 : 0,
    });
  }
  return forests;
}

function buildEdges(data: GenealogyData, graph: ReturnType<typeof buildGraph>, visibleIds: Set<string>, nodesById: Map<string, LayoutNode>): LayoutEdge[] {
  const result: LayoutEdge[] = [];
  const seen = new Set<string>();
  const witnessLines = new Map((data.witnesses ?? []).map((witness) => [witness.id, witness.line ?? 'common']));
  const add = (from: string, to: string, kind: LayoutEdge['kind'], line: string) => {
    const key = `${from}\u0000${to}\u0000${kind}\u0000${line}`;
    if (seen.has(key) || !visibleIds.has(from) || !visibleIds.has(to)) return;
    seen.add(key);
    result.push({ from, to, kind, line, key });
  };
  for (const person of data.persons) {
    const line = lineColorKey(person);
    for (const parent of person.parents ?? []) {
      const childNode = nodesById.get(person.id);
      const groupingNode = childNode?.syntheticParent ? nodesById.get(childNode.syntheticParent) : undefined;
      if (groupingNode?.groupParentId === parent.id) continue;
      const kind = /母|mother/i.test(`${parent.role ?? ''} ${parent.type ?? ''}`) ? 'mother' : 'parent';
      // 母親放在父親的另一側時（例如大衛的妻子在左、兒子在右），母子線會橫越父親和主線，
      // 和夫妻線、子女線糾在一起；這種就不畫，母親照樣列在人物卡上，讀經時墨線也會畫出來
      if (kind === 'mother') {
        const mother = nodesById.get(parent.id);
        const child = nodesById.get(person.id);
        const via = graph.treeParent.get(person.id);
        const father = via ? nodesById.get(via) : undefined;
        if (mother && child && father && (mother.x - father.x) * (child.x - father.x) < 0) continue;
      }
      const source = String(parent.witness ?? parent.source ?? '');
      const relationLine = String(parent.line ?? witnessLines.get(source) ?? '');
      const refLine = /^太/.test(parent.ref ?? '') ? '馬太' : /^路/.test(parent.ref ?? '') ? '路加' : '';
      const edgeLine = ['common', '馬太', '路加'].includes(relationLine) ? relationLine : refLine || line;
      add(parent.id, person.id, kind, edgeLine);
    }
    for (const ancestor of person.descends ?? []) add(ancestor.id, person.id, 'descends', line);
  }
  for (const node of nodesById.values()) {
    if (node.groupParentId && node.groupKey) add(node.groupParentId, node.id, 'parent', node.groupLine ?? 'common');
    if (node.syntheticParent) {
      const person = data.persons.find((candidate) => candidate.id === node.id);
      if (person) add(node.syntheticParent, node.id, 'parent', lineColorKey(person));
    }
  }
  // 大圖安置：名單牌子用點線掛在支派底下，牌子到各家用細線；區域不畫連到主線的線；
  // 靠妻子、兄弟姊妹、親屬掛上來的一家，畫出那條經文關係
  const lineOf = (id: string) => { const person = graph.byId.get(id); return person ? lineColorKey(person) : 'common'; };
  for (const node of data.placements?.nodes ?? []) {
    if (node.kind === 'list') add(node.under, node.id, 'list', lineOf(node.under));
  }
  for (const item of data.placements?.items ?? []) {
    const under = graph.byId.get(item.under);
    if (under && (under.kind === 'list' || under.kind === 'family')) add(item.under, item.root, 'member', lineOf(item.root));
    if (item.via && ['spouse', 'sibling', 'kin'].includes(item.via.kind)) add(item.via.to, item.via.from, 'kin', lineOf(item.via.from));
  }
  return result;
}

/** 展開的區域畫一個框，把區域裡各家框在一起。 */
function regionFrames(graph: ReturnType<typeof buildGraph>, nodesById: Map<string, LayoutNode>): CanvasLayout['regions'] {
  const frames: CanvasLayout['regions'] = [];
  for (const node of nodesById.values()) {
    const person = graph.byId.get(node.id);
    if (person?.kind !== 'region' || !node.expandedRoot) continue;
    const inside: LayoutNode[] = [node];
    const stack = [...(graph.children.get(node.id) ?? [])];
    while (stack.length) {
      const id = stack.pop()!;
      const child = nodesById.get(id);
      if (!child) continue;
      inside.push(child);
      stack.push(...(graph.children.get(id) ?? []));
    }
    const pad = 22;
    frames.push({
      id: node.id, title: person.name,
      x0: Math.min(...inside.map((item) => item.x - item.width / 2)) - pad,
      y0: Math.min(...inside.map((item) => item.y - item.height / 2)) - pad,
      x1: Math.max(...inside.map((item) => item.x + item.width / 2)) + pad,
      y1: Math.max(...inside.map((item) => item.y + item.height / 2)) + pad,
    });
  }
  return frames;
}

function routeX(id: string, line: string, sharedIds: Set<string>): number {
  if (sharedIds.has(id)) return 0;
  return line === '馬太' ? -COLUMN_W : line === '路加' ? COLUMN_W : 0;
}

function positionSpine(
  data: GenealogyData,
  graph: ReturnType<typeof buildGraph>,
  expanded: Set<string>,
): { nodes: Map<string, LayoutNode>; segments: Array<{ title: string; y0: number; y1: number; line: string; labelX: number }>; mainIds: Set<string> } {
  const nodes = new Map<string, LayoutNode>();
  const mainRoutes = Object.values(data.spine.lines ?? {});
  const mainIds = new Set(mainRoutes.flat());
  const sharedIds = new Set(mainRoutes.length > 1
    ? mainRoutes.slice(1).reduce((shared, route) => new Set([...shared].filter((id) => route.includes(id))), new Set(mainRoutes[0] ?? []))
    : []);
  const forests = buildForests(data, graph, graph.spineIds, expanded);
  const forestByParent = new Map<string, BranchForest[]>();
  for (const forest of forests) forestByParent.set(forest.parentId, [...(forestByParent.get(forest.parentId) ?? []), forest]);
  const mainMetrics = new Map<string, NodeMetrics>();
  for (const id of mainIds) {
    const person = graph.byId.get(id);
    if (person) mainMetrics.set(id, nodeMetrics(person, true));
  }
  const rowHeight = (id: string) => Math.max(
    ROW_H,
    mainMetrics.get(id)?.height ?? MAIN_NODE_H,
    ...((forestByParent.get(id) ?? []).map((forest) => forest.height + ROW_TREE_PADDING)),
  );
  const rowStep = (from: string, to: string) => Math.max(ROW_H, rowHeight(from), rowHeight(to));
  const segments: Array<{ title: string; y0: number; y1: number; line: string; labelX: number }> = [];
  let cursorY = 0;
  let previousEnds = new Set<string>();
  for (const segment of data.spine.segments ?? []) {
    const routes = Object.entries(segment.lines ?? {}).filter(([, route]) => route.length);
    const spans = routes.map(([, route]) => route.slice(0, -1).reduce((height, parentId, index) => height + rowStep(parentId, route[index + 1]!), 0));
    const targetSpan = Math.max(0, ...spans);
    const knownStarts = routes.map(([, route]) => nodes.get(route[0]!)?.y).filter((y): y is number => y !== undefined);
    let segmentStart = Math.max(cursorY, ...knownStarts);
    if (!knownStarts.length && previousEnds.size) {
      const starts = routes.map(([, route]) => route[0]!);
      const transitions = [...previousEnds].flatMap((parentId) => starts
        .filter((id) => (graph.children.get(parentId) ?? []).includes(id))
        .map((id) => rowStep(parentId, id)));
      segmentStart = cursorY + Math.max(ROW_H, ...transitions);
    }
    for (let routeIndex = 0; routeIndex < routes.length; routeIndex += 1) {
      const [line, route] = routes[routeIndex]!;
      const span = spans[routeIndex] ?? 0;
      const extraStep = route.length > 1 ? (targetSpan - span) / (route.length - 1) : 0;
      let y = nodes.get(route[0]!)?.y ?? segmentStart;
      const startPerson = graph.byId.get(route[0]!);
      const startMetric = mainMetrics.get(route[0]!);
      if (startPerson && startMetric && !nodes.has(startPerson.id)) {
        nodes.set(startPerson.id, {
          id: startPerson.id,
          x: routeX(startPerson.id, line, sharedIds), y,
          ...startMetric, mainline: true, segment: segment.title,
        });
      }
      for (let i = 1; i < route.length; i += 1) {
        const id = route[i]!;
        y += rowStep(route[i - 1]!, id) + extraStep;
        if (nodes.has(id)) continue;
        const person = graph.byId.get(id);
        const metrics = mainMetrics.get(id);
        if (!person || !metrics) continue;
        nodes.set(id, { id, x: routeX(id, line, sharedIds), y, ...metrics, mainline: true, segment: segment.title });
      }
    }
    const endY = segmentStart + targetSpan;
    for (const [line, route] of routes) {
      segments.push({ title: segment.title, y0: segmentStart, y1: Math.max(endY, segmentStart + ROW_H), line,
        labelX: routeX(route[0]!, line, sharedIds) - 120 });
    }
    cursorY = endY;
    previousEnds = new Set(routes.map(([, route]) => route.at(-1)!).filter(Boolean));
  }

  // Route arrays remain authoritative for partial segment fixtures.
  for (const [line, route] of Object.entries(data.spine.lines ?? {})) {
    for (let i = 0; i < route.length; i += 1) {
      const id = route[i]!;
      if (nodes.has(id)) continue;
      const person = graph.byId.get(id);
      const metrics = mainMetrics.get(id);
      if (!person || !metrics) continue;
      nodes.set(id, { id, x: routeX(id, line, sharedIds), y: i * ROW_H, ...metrics, mainline: true });
    }
  }

  for (const forest of forests) {
    const parent = nodes.get(forest.parentId);
    if (!parent) continue;
    const depthOffsets = new Map<number, number>();
    let previousDepth = 0;
    let previousWidth = parent.width;
    for (const depth of [...forest.levelWidths.keys()].sort((a, b) => a - b)) {
      const width = forest.levelWidths.get(depth)!;
      const offset = depth === 1
        ? parent.width / 2 + SIDE_GAP_X + width / 2 + (forest.pushOut ?? 0)
        : (depthOffsets.get(previousDepth) ?? 0) + previousWidth / 2 + SIDE_LEVEL_GAP_X + width / 2;
      depthOffsets.set(depth, offset);
      previousDepth = depth;
      previousWidth = width;
    }
    for (const branch of forest.placements) {
      const xOffset = depthOffsets.get(branch.depth);
      if (xOffset === undefined) continue;
      const { metrics } = branch;
      nodes.set(branch.id, {
        id: branch.id,
        x: parent.x + forest.direction * xOffset,
        y: parent.y + branch.vertical,
        ...metrics,
        sideRoot: branch.rootId,
        mainline: false,
        collapsed: branch.collapsed,
        expandedRoot: branch.expandedRoot,
        descendantCount: branch.descendantCount,
        segment: parent.segment,
        ...(branch.groupLabel ? {
          groupLabel: branch.groupLabel, groupKey: branch.groupKey, groupMembers: branch.groupMembers,
          groupLine: branch.groupLine, groupParentId: branch.groupParentId,
        } : {}),
        ...(forest.grouped && branch.inGroup && forest.groupKey ? { syntheticParent: forest.groupKey } : {}),
      });
    }
  }
  return { nodes, segments, mainIds };
}

export function computeLayout(data: GenealogyData, expanded = new Set<string>()): CanvasLayout {
  const started = performance.now();
  const graph = buildGraph(data);
  const { nodes: nodeMap, segments } = positionSpine(data, graph, expanded);
  const allNodes = [...nodeMap.values()];
  const nodes = allNodes.filter((node) => !node.groupLabel);
  const groups = allNodes.filter((node) => Boolean(node.groupLabel));
  const edges = buildEdges(data, graph, new Set(nodeMap.keys()), nodeMap);
  const regions = regionFrames(graph, nodeMap);
  const minX = Math.min(0, ...allNodes.map((node) => node.x - node.width / 2)) - 80;
  const maxX = Math.max(0, ...allNodes.map((node) => node.x + node.width / 2)) + 80;
  const minY = Math.min(0, ...allNodes.map((node) => node.y - node.height / 2)) - 80;
  const maxY = Math.max(0, ...allNodes.map((node) => node.y + node.height / 2)) + 80;
  return {
    nodes,
    groups,
    edges,
    regions,
    segments,
    bounds: { x: minX, y: minY, width: maxX - minX, height: maxY - minY },
    durationMs: performance.now() - started,
  };
}
