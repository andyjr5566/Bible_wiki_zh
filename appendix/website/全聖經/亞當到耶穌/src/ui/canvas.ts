import type { GenealogyData, Person } from '../data/types';
import { branchRoots, buildGraph, firstReference } from '../data/model';
import { computeLayout, type CanvasLayout, type LayoutNode } from './layout';
import { svgEl } from './dom';

export type CanvasLine = 'both' | '馬太' | '路加';

export interface CanvasApi {
  el: SVGSVGElement;
  focusPerson(id: string, animate?: boolean): void;
  focusIds(ids: string[], animate?: boolean): void;
  focusTourIds(ids: string[], avoid: HTMLElement | null, animate?: boolean): Promise<boolean>;
  fitSpine(animate?: boolean): void;
  fitAll(animate?: boolean): void;
  zoom(factor: number): void;
  select(id: string | null): void;
  setTourHighlights(ids: string[], currentId: string | null, edges: Array<[string, string]>): void;
  clearTourHighlights(): void;
  setLine(line: CanvasLine): void;
  setTrace(ids: string[], edges: Array<{ from: string; to: string; kind: string }>): void;
  expandFor(id: string): void;
  expandPath(ids: string[]): void;
  expandFamily(id: string): void;
  expandAll(): void;
  layoutNow(): CanvasLayout;
}

interface ViewBox { x: number; y: number; width: number; height: number }
interface Pointer { x: number; y: number }

const COLORS: Record<string, string> = { common: 'var(--ag-ink)', '馬太': 'var(--ag-matthew)', '路加': 'var(--ag-luke)' };

export function createCanvas(data: GenealogyData, onSelect: (person: Person) => void, onNote: (noteId: string) => void): CanvasApi {
  const svg = svgEl('svg', {
    class: 'ag-canvas', role: 'application', 'aria-label': '可縮放的家譜畫布', tabindex: '0',
    preserveAspectRatio: 'xMidYMid meet',
  });
  const scene = svgEl('g', { class: 'ag-scene' });
  const segmentLayer = svgEl('g', { class: 'ag-segment-layer' });
  const edgeLayer = svgEl('g', { class: 'ag-edge-layer' });
  const overviewLayer = svgEl('g', { class: 'ag-overview-layer' });
  const nodeLayer = svgEl('g', { class: 'ag-node-layer' });
  scene.append(segmentLayer, edgeLayer, overviewLayer, nodeLayer);
  svg.append(scene);
  const graph = buildGraph(data);
  const expanded = new Set<string>();
  let layout = computeLayout(data, expanded);
  const allLayoutNodes = () => [...layout.nodes, ...layout.groups];
  let currentBox: ViewBox = { x: -500, y: -300, width: 1000, height: 600 };
  let currentLine: CanvasLine = 'both';
  let selected: string | null = null;
  let tourHighlightIds = new Set<string>();
  let tourCurrentId: string | null = null;
  let tourEdgeKeys = new Set<string>();
  let traceIds = new Set<string>();
  let traceEdges = new Set<string>();
  let nodeEls = new Map<string, SVGGElement>();
  let edgeEls = new Map<string, SVGPathElement>();
  let dragStart: Pointer | null = null;
  let dragBox: ViewBox | null = null;
  let didDrag = false;
  const pointers = new Map<number, Pointer>();
  let pinchStart: { distance: number; box: ViewBox; center: Pointer } | null = null;
  let cullTimer = 0;
  let animationFrame = 0;
  let layoutAnimationFrame = 0;
  let animationDone: (() => void) | null = null;

  const nodeFor = (id: string) => layout.nodes.find((node) => node.id === id);
  const lineFor = (person: Person) => person.lines?.includes('common') ? 'common' : person.lines?.includes('馬太') ? '馬太' : person.lines?.includes('路加') ? '路加' : 'common';
  const lineOpacity = (key: string) => currentLine === 'both' || key === 'common' || key === currentLine ? 1 : 0;
  const worldPoint = (clientX: number, clientY: number): Pointer => {
    const rect = svg.getBoundingClientRect();
    return {
      x: currentBox.x + ((clientX - rect.left) / Math.max(1, rect.width)) * currentBox.width,
      y: currentBox.y + ((clientY - rect.top) / Math.max(1, rect.height)) * currentBox.height,
    };
  };

  const setViewBox = (box: ViewBox) => {
    currentBox = { ...box };
    svg.setAttribute('viewBox', `${box.x} ${box.y} ${box.width} ${box.height}`);
    window.clearTimeout(cullTimer);
    cullTimer = window.setTimeout(cullToViewport, 140);
  };
  const fitRect = (x0: number, y0: number, x1: number, y1: number, animate = false, padding = 90, lockAspect = true) => {
    const rect = svg.getBoundingClientRect();
    const aspect = Math.max(0.45, rect.width / Math.max(1, rect.height));
    let width = Math.max(160, x1 - x0 + padding * 2);
    let height = Math.max(160, y1 - y0 + padding * 2);
    if (lockAspect) {
      if (width / height > aspect) height = width / aspect;
      else width = height * aspect;
    }
    const target: ViewBox = { x: (x0 + x1) / 2 - width / 2, y: (y0 + y1) / 2 - height / 2, width, height };
    animateToBox(target, animate);
  };
  const finishAnimation = () => {
    const done = animationDone;
    animationDone = null;
    done?.();
  };
  const animateToBox = (target: ViewBox, animate: boolean): Promise<void> => new Promise((resolve) => {
    if (!animate || document.documentElement.dataset.motion === 'off') {
      cancelAnimationFrame(animationFrame);
      finishAnimation();
      setViewBox(target);
      resolve();
      return;
    }
    cancelAnimationFrame(animationFrame);
    finishAnimation();
    animationDone = resolve;
    const from = { ...currentBox };
    const start = performance.now();
    const duration = 720;
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - (1 - t) ** 3;
      setViewBox({
        x: from.x + (target.x - from.x) * eased,
        y: from.y + (target.y - from.y) * eased,
        width: from.width + (target.width - from.width) * eased,
        height: from.height + (target.height - from.height) * eased,
      });
      if (t < 1) animationFrame = requestAnimationFrame(tick);
      else finishAnimation();
    };
    animationFrame = requestAnimationFrame(tick);
  });

  function cullToViewport() {
    const marginX = currentBox.width * 0.12;
    const marginY = currentBox.height * 0.12;
    const zoomLevel = Math.max(1, svg.clientHeight || window.innerHeight) / Math.max(1, currentBox.height);
    const overview = zoomLevel < 0.6;
    nodeLayer.classList.toggle('ag-side-mini', zoomLevel < 0.45);
    nodeLayer.classList.toggle('ag-spine-mini', overview);
    for (const [id, element] of nodeEls) {
      const label = element.querySelector<SVGTextElement>('.ag-node-label');
      const rect = element.querySelector<SVGRectElement>(':scope > rect');
      const dot = element.querySelector<SVGCircleElement>('.ag-node-dot');
      const node = nodeFor(id);
      if (!label || !rect || !node) continue;
      const emphasized = tourHighlightIds.has(id);
      label.style.display = emphasized ? 'block' : '';
      label.style.fontSize = emphasized ? `${13 / zoomLevel}px` : '';
      if (dot) dot.style.display = emphasized ? 'none' : '';
      rect.style.display = emphasized ? 'block' : '';
      if (emphasized) {
        const labelWidth = label.getComputedTextLength();
        const width = Math.max(node.rectWidth, labelWidth + 24 / zoomLevel);
        const height = Math.max(node.rectHeight, 22 / zoomLevel);
        rect.setAttribute('x', String(node.rectX + (node.rectWidth - width) / 2));
        rect.setAttribute('y', String(-height / 2));
        rect.setAttribute('width', String(width));
        rect.setAttribute('height', String(height));
      } else {
        rect.setAttribute('x', String(node.rectX));
        rect.setAttribute('y', String(-node.height / 2));
        rect.setAttribute('width', String(node.rectWidth));
        rect.setAttribute('height', String(node.rectHeight));
      }
    }
    segmentLayer.classList.toggle('ag-segment-overview', overview);
    segmentLayer.style.display = overview ? '' : 'none';
    overviewLayer.style.display = 'none';
    const visible = new Set<string>();
    for (const node of allLayoutNodes()) {
      const shown = node.x + node.width / 2 >= currentBox.x - marginX && node.x - node.width / 2 <= currentBox.x + currentBox.width + marginX &&
        node.y + node.height / 2 >= currentBox.y - marginY && node.y - node.height / 2 <= currentBox.y + currentBox.height + marginY;
      if (shown) visible.add(node.id);
      const el = nodeEls.get(node.id);
      if (el) el.style.display = shown ? '' : 'none';
    }
    for (const edge of layout.edges) {
      const shown = visible.has(edge.from) && visible.has(edge.to);
      const el = edgeEls.get(edge.key);
      if (el) el.style.display = shown ? '' : 'none';
    }
  }

  const nodeSubtitle = (person: Person) => person.qualifier || firstReference(person) ||
    Object.entries(person.gen ?? {}).map(([line, generation]) => `${line} ${generation}代`).join('／') || person.id;
  const renderNode = (node: LayoutNode) => {
    if (node.groupLabel && node.groupKey) {
      const group = svgEl('g', {
        class: `ag-node ag-node-group ag-node-group-${node.groupLine ?? 'common'}${node.expandedRoot ? ' ag-node-group-expanded' : ''}`,
        transform: `translate(${node.x} ${node.y})`, 'data-group-key': node.groupKey,
        role: 'button', tabindex: '0', 'aria-label': node.groupLabel,
      });
      group.style.opacity = String(lineOpacity(node.groupLine ?? 'common'));
      group.append(svgEl('rect', { x: node.rectX, y: -node.rectHeight / 2, width: node.rectWidth, height: node.rectHeight, rx: 17 }));
      const label = svgEl('text', { class: 'ag-child-group-label', 'text-anchor': 'middle', 'dominant-baseline': 'central' });
      label.textContent = node.groupLabel;
      group.append(label);
      const toggle = (event: Event) => {
        event.stopPropagation();
        if (expanded.has(node.groupKey!)) {
          expanded.delete(node.groupKey!);
          for (const id of node.groupMembers ?? []) expanded.delete(id);
        } else {
          expanded.add(node.groupKey!);
          for (const id of node.groupMembers ?? []) expanded.add(id);
        }
        refresh(true);
        requestAnimationFrame(() => focusIds(node.groupMembers?.length ? node.groupMembers : [node.groupParentId ?? ''], true));
      };
      group.addEventListener('click', toggle);
      group.addEventListener('keydown', (event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); toggle(event); } });
      return group;
    }
    const person = graph.byId.get(node.id);
    if (!person) return null;
    const group = svgEl('g', {
      class: `ag-node${node.mainline ? ' ag-node-main' : ' ag-node-side'} ag-node-route-${lineFor(person)}${node.collapsed ? ' ag-node-collapsed' : ''}`,
      transform: `translate(${node.x} ${node.y})`,
      'data-id': node.id,
      role: 'button', tabindex: '0',
      'aria-label': `${person.name}${node.collapsed ? `，展開 ${node.descendantCount ?? 0} 位後代` : ''}`,
    });
    group.style.opacity = String(lineOpacity(lineFor(person)));
    const top = -node.height / 2;
    const rect = svgEl('rect', { x: node.rectX, y: top, width: node.rectWidth, height: node.rectHeight, rx: node.mainline ? 8 : 6 });
    const textX = node.rectX + node.rectWidth / 2;
    const primary = svgEl('text', { class: 'ag-node-label', 'text-anchor': 'middle', 'dominant-baseline': 'middle', x: textX, y: top + 16 });
    primary.textContent = person.name;
    const secondary = svgEl('text', { class: 'ag-node-subtitle', 'text-anchor': 'middle', 'dominant-baseline': 'middle', x: textX, y: top + node.rectHeight - 8 });
    secondary.textContent = nodeSubtitle(person);
    const dot = svgEl('circle', { class: 'ag-node-dot', cx: 0, cy: 0, r: 3.2 });
    group.append(rect, dot, primary, secondary);
    if (person.marks?.length) {
      const label = person.marks.map((item) => item.label).filter(Boolean).join('／');
      const capsuleWidth = Math.min(node.rectWidth, Math.max(42, Array.from(label).length * 10 + 16));
      const capsuleY = top + node.rectHeight + 2;
      const capsule = svgEl('g', { class: 'ag-node-mark' });
      capsule.append(svgEl('rect', { x: -capsuleWidth / 2, y: capsuleY, width: capsuleWidth, height: 16, rx: 8 }));
      const mark = svgEl('text', { x: 0, y: capsuleY + 8, 'text-anchor': 'middle', 'dominant-baseline': 'middle' });
      mark.textContent = label;
      capsule.append(mark);
      group.append(capsule);
    }
    if (node.collapsed) {
      const badge = svgEl('g', { class: 'ag-descendant-badge', transform: `translate(${node.rectX + node.rectWidth + 12} ${top + 12})` });
      badge.append(svgEl('circle', { r: 11 }), (() => {
        const count = svgEl('text', { 'text-anchor': 'middle', 'dominant-baseline': 'central' });
        count.textContent = `+${node.descendantCount ?? 0}`;
        return count;
      })());
      group.append(badge);
    }
    if (person.notes?.length) {
      const note = svgEl('g', { class: 'ag-node-note', transform: `translate(${node.rectX + node.rectWidth - 3} ${top + node.rectHeight - 2})`, tabindex: '0', role: 'button', 'aria-label': '查看經文差異說明' });
      note.append(svgEl('circle', { r: 10 }), (() => {
        const text = svgEl('text', { 'text-anchor': 'middle', 'dominant-baseline': 'central' }); text.textContent = '※'; return text;
      })());
      note.addEventListener('click', (event) => { event.stopPropagation(); onNote(person.notes![0]!); });
      group.append(note);
    }
    if (node.expandedRoot) {
      const collapse = svgEl('g', { class: 'ag-collapse-badge', transform: `translate(${node.rectX + node.rectWidth + 12} ${top + 12})`, tabindex: '0', role: 'button', 'aria-label': '收合旁支' });
      collapse.append(svgEl('circle', { r: 10 }), (() => {
        const label = svgEl('text', { 'text-anchor': 'middle', 'dominant-baseline': 'central' }); label.textContent = '−'; return label;
      })());
      const collapseTree = (event: Event) => { event.stopPropagation(); expanded.delete(node.id); refresh(true); };
      collapse.addEventListener('click', collapseTree);
      collapse.addEventListener('keydown', (event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); collapseTree(event); } });
      group.append(collapse);
    }
    if (traceIds.has(node.id)) group.classList.add('ag-trace-node');
    if (tourHighlightIds.has(node.id)) group.classList.add('ag-node-tour-lit');
    if (tourCurrentId === node.id) group.classList.add('ag-node-tour-current');
    if (selected === node.id) group.classList.add('ag-node-selected');
    group.addEventListener('click', (event) => {
      event.stopPropagation();
      if (didDrag) return;
      if (node.collapsed) {
        expanded.add(node.id);
        refresh(true);
        requestAnimationFrame(() => focusIds([person.id, ...(graph.children.get(person.id) ?? [])], true));
      } else onSelect(person);
    });
    group.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); onSelect(person); }
    });
    return group;
  };

  const edgePath = (a: LayoutNode, b: LayoutNode) => {
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    if (Math.abs(dx) < 1) {
      const direction = Math.sign(dy || 1);
      const startY = a.y + direction * a.height / 2;
      const endY = b.y - direction * b.height / 2;
      return `M${a.x} ${startY} V${endY}`;
    }
    const direction = Math.sign(dx);
    const startX = a.x + direction * a.width / 2;
    const endX = b.x - direction * b.width / 2;
    const midX = (startX + endX) / 2;
    if (endX * direction < startX * direction) return `M${a.x + direction * a.width / 2} ${a.y} L${b.x - direction * b.width / 2} ${b.y}`;
    return `M${startX} ${a.y} H${midX} V${b.y} H${endX}`;
  };

  function refresh(animate = false) {
    const previousLayout = layout;
    const previousNodeEls = nodeEls;
    const previousEdgeEls = edgeEls;
    const previousNodes = new Map([...previousLayout.nodes, ...previousLayout.groups].map((node) => [node.id, node]));
    cancelAnimationFrame(layoutAnimationFrame);
    layout = computeLayout(data, expanded);
    nodeEls = new Map();
    edgeEls = new Map();
    segmentLayer.replaceChildren();
    edgeLayer.replaceChildren();
    nodeLayer.replaceChildren();
    for (const segment of layout.segments) {
      const text = svgEl('text', { class: `ag-segment-title ag-segment-${segment.line}`, x: segment.labelX, y: (segment.y0 + segment.y1) / 2, 'text-anchor': 'end' });
      text.textContent = segment.title;
      text.style.opacity = String(lineOpacity(segment.line));
      segmentLayer.append(text);
    }
    const nodesById = new Map(allLayoutNodes().map((node) => [node.id, node]));
    for (const edge of layout.edges) {
      const a = nodesById.get(edge.from);
      const b = nodesById.get(edge.to);
      if (!a || !b) continue;
      const path = svgEl('path', {
        class: `ag-edge ag-edge-${edge.kind}${traceEdges.has(`${edge.from}>${edge.to}>${edge.kind}`) ? ' ag-edge-traced' : ''}${tourEdgeKeys.has(edge.key) ? ' ag-edge-tour-lit' : ''}`,
        d: edgePath(a, b),
        stroke: COLORS[edge.line] ?? COLORS.common,
        'stroke-width': tourEdgeKeys.has(edge.key) ? 4 : edge.kind === 'mother' ? 1.1 : edge.kind === 'descends' ? 1.4 : 1.7,
      });
      path.style.opacity = String(lineOpacity(edge.line));
      edgeLayer.append(path);
      edgeEls.set(edge.key, path);
    }
    for (const node of allLayoutNodes()) {
      const rendered = renderNode(node);
      if (rendered) {
        nodeLayer.append(rendered);
        nodeEls.set(node.id, rendered);
      }
    }
    // 動畫只聽頁面上的「動畫」開關，不跟作業系統的「減少動態」設定（使用者的決定）
    const shouldAnimate = animate && document.documentElement.dataset.motion !== 'off';
    if (shouldAnimate) {
      const oldIds = new Set(previousNodeEls.keys());
      for (const [id, oldNode] of previousNodeEls) {
        if (nodeEls.has(id)) continue;
        oldIds.delete(id);
        oldNode.classList.add('ag-node-leaving');
        oldNode.style.transition = 'opacity 250ms ease';
        oldNode.style.pointerEvents = 'none';
        nodeLayer.append(oldNode);
        requestAnimationFrame(() => { oldNode.style.opacity = '0'; });
        window.setTimeout(() => oldNode.remove(), 270);
      }
      for (const oldPath of previousEdgeEls.values()) {
        oldPath.classList.add('ag-edge-leaving');
        oldPath.style.transition = 'opacity 250ms ease';
        edgeLayer.insertBefore(oldPath, edgeLayer.firstChild);
        requestAnimationFrame(() => { oldPath.style.opacity = '0'; });
        window.setTimeout(() => oldPath.remove(), 270);
      }
      const startPositions = new Map<string, { x: number; y: number }>();
      for (const node of allLayoutNodes()) {
        const old = previousNodes.get(node.id);
        if (old) startPositions.set(node.id, { x: old.x, y: old.y });
        else if (node.sideRoot) {
          const root = previousNodes.get(node.sideRoot);
          const rootPerson = graph.byId.get(node.sideRoot);
          const parent = rootPerson?.parents?.map((relation) => previousNodes.get(relation.id)).find(Boolean);
          const origin = root ?? parent;
          if (origin) startPositions.set(node.id, { x: origin.x, y: origin.y });
        }
      }
      for (const node of allLayoutNodes()) {
        const start = startPositions.get(node.id);
        const element = nodeEls.get(node.id);
        if (start && element) element.setAttribute('transform', `translate(${start.x} ${start.y})`);
      }
      const start = performance.now();
      const duration = 250;
      const tick = (now: number) => {
        const t = Math.min(1, (now - start) / duration);
        const eased = t * t * (3 - 2 * t);
        const currentNodes = new Map<string, LayoutNode>();
        for (const node of allLayoutNodes()) {
          const origin = startPositions.get(node.id) ?? node;
          const current = { ...node, x: origin.x + (node.x - origin.x) * eased, y: origin.y + (node.y - origin.y) * eased };
          currentNodes.set(node.id, current);
          nodeEls.get(node.id)?.setAttribute('transform', `translate(${current.x} ${current.y})`);
        }
        for (const edge of layout.edges) {
          const a = currentNodes.get(edge.from);
          const b = currentNodes.get(edge.to);
          const element = edgeEls.get(edge.key);
          if (a && b && element) element.setAttribute('d', edgePath(a, b));
        }
        if (t < 1) layoutAnimationFrame = requestAnimationFrame(tick);
        else cullToViewport();
      };
      layoutAnimationFrame = requestAnimationFrame(tick);
    }
    cullToViewport();
  }

  const fitSpine = (animate = false) => {
    const main = layout.nodes.filter((node) => node.mainline);
    if (!main.length) return;
    const x0 = Math.min(...main.map((node) => node.x - node.width / 2));
    const x1 = Math.max(...main.map((node) => node.x + node.width / 2));
    const rect = svg.getBoundingClientRect();
    const height = Math.max(1, rect.height) / (11 / 15);
    const width = Math.max(1, rect.width) / (11 / 15);
    const centerX = (x0 + x1) / 2;
    const centerY = currentBox.y + currentBox.height / 2;
    animateToBox({ x: centerX - width / 2, y: centerY - height / 2, width, height }, animate);
  };
  const focusIds = (ids: string[], animate = true) => {
    const nodes = ids.map(nodeFor).filter((node): node is LayoutNode => Boolean(node));
    if (!nodes.length) return;
    fitRect(Math.min(...nodes.map((node) => node.x - node.width / 2)), Math.min(...nodes.map((node) => node.y - node.height / 2)),
      Math.max(...nodes.map((node) => node.x + node.width / 2)), Math.max(...nodes.map((node) => node.y + node.height / 2)), animate, 180);
  };
  const focusTourIds = (ids: string[], avoid: HTMLElement | null, animate = true): Promise<boolean> => {
    const nodes = ids.map(nodeFor).filter((node): node is LayoutNode => Boolean(node));
    if (!nodes.length) return Promise.resolve(false);
    const bounds = {
      left: Math.min(...nodes.map((node) => node.x - node.width / 2)),
      right: Math.max(...nodes.map((node) => node.x + node.width / 2)),
      top: Math.min(...nodes.map((node) => node.y - node.height / 2)),
      bottom: Math.max(...nodes.map((node) => node.y + node.height / 2)),
    };
    const canvasRect = svg.getBoundingClientRect();
    const gap = 22;
    let areas = [{ left: canvasRect.left + 8, top: canvasRect.top + 8, right: canvasRect.right - 8, bottom: canvasRect.bottom - 8 }];
    const cover = avoid?.getBoundingClientRect();
    if (cover && cover.left < canvasRect.right && cover.right > canvasRect.left && cover.top < canvasRect.bottom && cover.bottom > canvasRect.top) {
      const candidates = [
        { left: canvasRect.left + 8, top: canvasRect.top + 8, right: canvasRect.right - 8, bottom: Math.min(canvasRect.bottom - 8, cover.top - gap) },
        { left: Math.max(canvasRect.left + 8, cover.right + gap), top: canvasRect.top + 8, right: canvasRect.right - 8, bottom: canvasRect.bottom - 8 },
        { left: canvasRect.left + 8, top: canvasRect.top + 8, right: Math.min(canvasRect.right - 8, cover.left - gap), bottom: canvasRect.bottom - 8 },
        { left: canvasRect.left + 8, top: Math.max(canvasRect.top + 8, cover.bottom + gap), right: canvasRect.right - 8, bottom: canvasRect.bottom - 8 },
      ].filter((area) => area.right - area.left > 100 && area.bottom - area.top > 100);
      if (candidates.length) areas = candidates;
    }
    const padding = 20;
    const maxLabelWidth = Math.max(...nodes.map((node) => {
      const person = graph.byId.get(node.id);
      return person ? [...person.name].reduce((sum, char) => sum + (char.codePointAt(0)! > 0x2e80 ? 13 : 7.5), 0) + 24 : 0;
    }));
    const requiredUnits = (area: typeof areas[number]) => Math.max(
      (bounds.right - bounds.left + padding * 2) / Math.max(1, area.right - area.left - maxLabelWidth),
      (bounds.bottom - bounds.top + padding * 2) / Math.max(1, area.bottom - area.top - 22),
    );
    const area = areas.reduce((best, candidate) => requiredUnits(candidate) < requiredUnits(best) ? candidate : best);
    // Tour labels stay at 13 screen pixels; 0.2x is the smallest permitted camera scale.
    const unitsPerPixel = Math.max(0.2, Math.min(5, requiredUnits(area)));
    const viewWidth = Math.max(1, canvasRect.width) * unitsPerPixel;
    const viewHeight = Math.max(1, canvasRect.height) * unitsPerPixel;
    const centerX = (bounds.left + bounds.right) / 2;
    const centerY = (bounds.top + bounds.bottom) / 2;
    const areaCenterX = (area.left + area.right) / 2;
    const areaCenterY = (area.top + area.bottom) / 2;
    const target = {
      x: centerX - ((areaCenterX - canvasRect.left) / Math.max(1, canvasRect.width)) * viewWidth,
      y: centerY - ((areaCenterY - canvasRect.top) / Math.max(1, canvasRect.height)) * viewHeight,
      width: viewWidth,
      height: viewHeight,
    };
    let screenBounds = {
      left: canvasRect.left + ((bounds.left - target.x) / viewWidth) * canvasRect.width,
      right: canvasRect.left + ((bounds.right - target.x) / viewWidth) * canvasRect.width,
      top: canvasRect.top + ((bounds.top - target.y) / viewHeight) * canvasRect.height,
      bottom: canvasRect.top + ((bounds.bottom - target.y) / viewHeight) * canvasRect.height,
    };
    if (cover && cover.bottom >= canvasRect.bottom - 1 && cover.top > canvasRect.top) {
      const blockedBottoms = nodes.map((node) => {
        const left = canvasRect.left + ((node.x - node.width / 2 - target.x) / viewWidth) * canvasRect.width;
        const right = canvasRect.left + ((node.x + node.width / 2 - target.x) / viewWidth) * canvasRect.width;
        const top = canvasRect.top + ((node.y - node.height / 2 - target.y) / viewHeight) * canvasRect.height;
        return { left, right, top, bottom: top + (node.height / viewHeight) * canvasRect.height };
      }).filter((rect) => rect.left < cover.right && rect.right > cover.left && rect.top < cover.bottom && rect.bottom > cover.top);
      const shiftUp = Math.max(0, ...blockedBottoms.map((rect) => rect.bottom - (cover.top - gap)));
      if (shiftUp > 0) {
        target.y += shiftUp * unitsPerPixel;
        screenBounds = { ...screenBounds, top: screenBounds.top - shiftUp, bottom: screenBounds.bottom - shiftUp };
      }
    }
    const fitsVisibleArea = screenBounds.left >= area.left - 1 && screenBounds.right <= area.right + 1 &&
      screenBounds.top >= area.top - 1 && screenBounds.bottom <= area.bottom + 1;
    return animateToBox(target, animate).then(() => fitsVisibleArea);
  };

  const api: CanvasApi = {
    el: svg,
    focusTourIds,
    focusPerson(id, animate = true) {
      const node = nodeFor(id);
      if (!node) return;
      if (window.matchMedia('(max-width: 520px)').matches) {
        const rect = svg.getBoundingClientRect();
        const height = Math.max(220, rect.height * 15 / 14);
        const width = height * Math.max(0.45, rect.width / Math.max(1, rect.height));
        animateToBox({ x: node.x - width / 2, y: node.y - height / 2, width, height }, animate);
      } else focusIds([id], animate);
    },
    focusIds,
    fitSpine,
    fitAll(animate = true) {
      const bounds = layout.bounds;
      fitRect(bounds.x, bounds.y, bounds.x + bounds.width, bounds.y + bounds.height, animate, 130);
    },
    zoom(factor) {
      const x = currentBox.x + currentBox.width / 2;
      const y = currentBox.y + currentBox.height / 2;
      const ratio = Math.max(0.12, Math.min(4.5, 1 / factor));
      setViewBox({ x: x - currentBox.width * ratio / 2, y: y - currentBox.height * ratio / 2, width: currentBox.width * ratio, height: currentBox.height * ratio });
    },
    select(id) { selected = id; refresh(); },
    setTourHighlights(ids, currentId, edges) {
      tourHighlightIds = new Set(ids);
      tourCurrentId = currentId;
      const adjacency = new Map<string, Array<{ id: string; key: string }>>();
      for (const edge of layout.edges) {
        adjacency.set(edge.from, [...(adjacency.get(edge.from) ?? []), { id: edge.to, key: edge.key }]);
        adjacency.set(edge.to, [...(adjacency.get(edge.to) ?? []), { id: edge.from, key: edge.key }]);
      }
      tourEdgeKeys = new Set();
      for (const [from, to] of edges) {
        const parents = new Map<string, { id: string; key: string } | null>([[from, null]]);
        const queue = [from];
        while (queue.length && !parents.has(to)) {
          const current = queue.shift()!;
          for (const next of adjacency.get(current) ?? []) {
            if (parents.has(next.id)) continue;
            parents.set(next.id, { id: current, key: next.key });
            queue.push(next.id);
          }
        }
        let current = to;
        while (parents.has(current) && current !== from) {
          const step = parents.get(current);
          if (!step) break;
          tourEdgeKeys.add(step.key);
          current = step.id;
        }
      }
      refresh();
    },
    clearTourHighlights() {
      tourHighlightIds.clear();
      tourCurrentId = null;
      tourEdgeKeys.clear();
      refresh();
    },
    setLine(line) { currentLine = line; refresh(); },
    setTrace(ids, edges) {
      traceIds = new Set(ids);
      traceEdges = new Set(edges.map((edge) => `${edge.from}>${edge.to}>${edge.kind}`));
      refresh();
    },
    expandFor(id) {
      let current = id;
      const visited = new Set<string>();
      while (!visited.has(current)) {
        visited.add(current);
        const group = layout.groups.find((node) => node.groupKey && node.groupMembers?.includes(current));
        if (group?.groupKey) {
          expanded.add(group.groupKey);
          expanded.add(current);
        }
        if (layout.nodes.some((node) => node.id === current && node.collapsed)) expanded.add(current);
        const person = graph.byId.get(current);
        const parent = person?.parents?.find((item) => graph.spineIds.has(item.id)) ?? person?.parents?.[0] ?? person?.descends?.[0];
        if (!parent) break;
        current = parent.id;
      }
      refresh(true);
    },
    expandPath(ids) {
      const pathIds = new Set(ids);
      for (const startId of ids) {
        let current = startId;
        const visited = new Set<string>();
        while (!visited.has(current)) {
          visited.add(current);
          const group = layout.groups.find((node) => node.groupKey && node.groupMembers?.includes(current));
          if (group?.groupKey) {
            expanded.add(group.groupKey);
            expanded.add(current);
          }
          if (layout.nodes.some((node) => node.id === current && node.collapsed)) expanded.add(current);
          const person = graph.byId.get(current);
          const relation = [...(person?.parents ?? []), ...(person?.descends ?? [])].find((item) => pathIds.has(item.id));
          if (!relation) break;
          current = relation.id;
        }
      }
      refresh(true);
    },
    expandFamily(id) {
      const family = [...(data.families ?? []), ...(data.ntFamilies ?? [])].find((item) => item.id === id);
      const targets = family?.roots ?? family?.members ?? (graph.byId.has(id) ? [id] : []);
      const directRoots = new Set(branchRoots(data, graph).map(({ rootId }) => rootId));
      const focus = new Set<string>();
      for (const target of targets) {
        focus.add(target);
        if (directRoots.has(target)) expanded.add(target);
        else {
          const children = branchRoots(data, graph).filter((item) => item.parentId === target);
          for (const child of children) { expanded.add(child.rootId); focus.add(child.rootId); }
          if (!children.length && graph.byId.has(target)) {
            let current = target;
            const visited = new Set<string>();
            while (!visited.has(current)) {
              visited.add(current);
              if (layout.nodes.some((node) => node.id === current && node.collapsed)) expanded.add(current);
              const parent = graph.byId.get(current)?.parents?.[0];
              if (!parent) break;
              current = parent.id;
            }
          }
        }
      }
      refresh(true);
      focusIds([...focus], true);
    },
    expandAll() {
      const roots = branchRoots(data, graph);
      const counts = new Map<string, number>();
      for (const { parentId, rootId } of roots) {
        expanded.add(rootId);
        counts.set(parentId, (counts.get(parentId) ?? 0) + 1);
      }
      for (const [parentId, count] of counts) {
        if (count <= 3) continue;
        for (const direction of [-1, 1] as const) expanded.add(`siblings:${parentId}:${direction}`);
      }
      refresh(true);
    },
    layoutNow() { return layout; },
  };

  svg.addEventListener('wheel', (event) => {
    event.preventDefault();
    const focus = worldPoint(event.clientX, event.clientY);
    const factor = Math.max(0.72, Math.min(1.4, Math.exp(-event.deltaY * 0.0015)));
    const ratio = 1 / factor;
    setViewBox({
      x: focus.x - (focus.x - currentBox.x) * ratio,
      y: focus.y - (focus.y - currentBox.y) * ratio,
      width: currentBox.width * ratio,
      height: currentBox.height * ratio,
    });
  }, { passive: false });
  svg.addEventListener('pointerdown', (event) => {
    pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    if (pointers.size === 1) {
      dragStart = { x: event.clientX, y: event.clientY };
      dragBox = { ...currentBox };
      didDrag = false;
    } else if (pointers.size === 2) {
      const [a, b] = [...pointers.values()];
      if (a && b) pinchStart = { distance: Math.hypot(a.x - b.x, a.y - b.y), box: { ...currentBox }, center: { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 } };
    }
  });
  svg.addEventListener('pointermove', (event) => {
    if (!pointers.has(event.pointerId)) return;
    pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    if (pointers.size >= 2 && pinchStart) {
      const [a, b] = [...pointers.values()];
      if (!a || !b) return;
      const distance = Math.hypot(a.x - b.x, a.y - b.y);
      const scale = pinchStart.distance / Math.max(10, distance);
      const rect = svg.getBoundingClientRect();
      const focusX = pinchStart.box.x + ((pinchStart.center.x - rect.left) / Math.max(1, rect.width)) * pinchStart.box.width;
      const focusY = pinchStart.box.y + ((pinchStart.center.y - rect.top) / Math.max(1, rect.height)) * pinchStart.box.height;
      const width = Math.max(150, Math.min(pinchStart.box.width * scale, layout.bounds.width * 2));
      const height = pinchStart.box.height * width / pinchStart.box.width;
      const r = width / pinchStart.box.width;
      setViewBox({ x: focusX - (focusX - pinchStart.box.x) * r, y: focusY - (focusY - pinchStart.box.y) * r, width, height });
      didDrag = true;
      return;
    }
    if (dragStart && dragBox && pointers.size === 1) {
      const dx = event.clientX - dragStart.x;
      const dy = event.clientY - dragStart.y;
      if (Math.abs(dx) + Math.abs(dy) > 4) didDrag = true;
      if (!didDrag) return;
      const rect = svg.getBoundingClientRect();
      setViewBox({ x: dragBox.x - dx / Math.max(1, rect.width) * dragBox.width, y: dragBox.y - dy / Math.max(1, rect.height) * dragBox.height, width: dragBox.width, height: dragBox.height });
    }
  });
  const endPointer = (event: PointerEvent) => {
    pointers.delete(event.pointerId);
    if (pointers.size < 2) pinchStart = null;
    if (!pointers.size) { dragStart = null; dragBox = null; window.setTimeout(() => { didDrag = false; }, 0); }
  };
  svg.addEventListener('pointerup', endPointer);
  svg.addEventListener('pointercancel', endPointer);
  svg.addEventListener('dblclick', () => fitSpine(true));
  svg.addEventListener('keydown', (event) => {
    if (event.key === '+' || event.key === '=') api.zoom(1.2);
    if (event.key === '-') api.zoom(0.84);
  });

  refresh();
  requestAnimationFrame(() => fitSpine(false));
  const resize = new ResizeObserver(() => { if (!currentBox.width) fitSpine(false); });
  resize.observe(svg);
  return api;
}
