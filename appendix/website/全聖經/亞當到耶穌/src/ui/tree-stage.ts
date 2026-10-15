import type { GenealogyData, ReadingData } from '../data/types';
import type { PersonGraph } from '../data/model';
import type { CanvasApi, ReadingMarks } from './canvas';
import { svgEl } from './dom';
import { type ReadingStage, type StageMarks } from './stage';

/** 縮影上主線的顏色 class（顏色在 reading.css） */
const LINE_CLASS: Record<string, string> = { '馬太': 'is-matthew', '路加': 'is-luke' };

/**
 * 家譜樹的讀經舞台：包住現有的畫布（CanvasApi），把讀經程式給的標記轉成畫布認得的樣子。
 * 職位圖才有的 id（rid、role: 開頭）一律在這裡丟掉。
 */
export function createTreeStage(
  canvas: CanvasApi,
  data: GenealogyData,
  graph: PersonGraph,
  wrap: HTMLElement,
  reading?: ReadingData,
): ReadingStage {
  const onTree = (id: string) => !id.startsWith('role:') && graph.byId.has(id);

  // 圖上有哪些節點：版面重算過（打開了旁支）才重建
  let knownLayout: ReturnType<CanvasApi['layoutNow']> | null = null;
  let nodeIds = new Set<string>();
  function nodes() {
    const layout = canvas.layoutNow();
    if (layout !== knownLayout) {
      knownLayout = layout;
      nodeIds = new Set([...layout.nodes, ...layout.groups].map((node) => node.id));
    }
    return layout;
  }

  // 縮影的取景：主線所有節點的外框。locate 用同一個取景，小紅點才對得上縮影
  let frame: { x: number; y: number; width: number; height: number } | null = null;
  function spineBounds() {
    const layout = nodes();
    const spine = new Set(Object.values(data.spine.lines).flat());
    const list = layout.nodes.filter((node) => spine.has(node.id));
    const use = list.length ? list : layout.nodes;
    if (!use.length) return { x: 0, y: 0, width: 1, height: 1 };
    let x0 = Infinity; let y0 = Infinity; let x1 = -Infinity; let y1 = -Infinity;
    for (const node of use) {
      x0 = Math.min(x0, node.x - node.rectWidth / 2);
      x1 = Math.max(x1, node.x + node.rectWidth / 2);
      y0 = Math.min(y0, node.y - node.height / 2);
      y1 = Math.max(y1, node.y + node.height / 2);
    }
    // 旁支會往主線兩側伸出去：左右多留一些邊，旁支上的人才不會全擠在縮影的邊線上
    const width = Math.max(1, x1 - x0);
    const height = Math.max(1, y1 - y0);
    const padX = Math.max(width * 0.8, 600);
    const padY = height * 0.02;
    return { x: x0 - padX, y: y0 - padY, width: width + padX * 2, height: height + padY * 2 };
  }
  const clamp01 = (value: number) => Math.max(0, Math.min(1, value));

  /** 讀到、已讀過的歸回連結指到的樹上祖先：讀過就留著淡淡的亮 */
  const linkedAncestors = (links: Set<number>): string[] => {
    const ids: string[] = [];
    for (const index of links) {
      for (const target of reading?.links[index]?.to ?? []) if (target.tree && onTree(target.tree)) ids.push(target.tree);
    }
    return ids;
  };

  return {
    id: 'tree',
    el: wrap,
    ready: () => Promise.resolve(),
    setReading(on) { canvas.setReading(on); },
    setMarks(marks: StageMarks) {
      const lit = new Set([...marks.lit].filter(onTree));
      const trail = new Set([...marks.trail, ...linkedAncestors(marks.links)].filter((id) => onTree(id) && !lit.has(id)));
      const next: ReadingMarks = {
        lit,
        trail,
        current: marks.current && onTree(marks.current) ? marks.current : null,
        seals: marks.seals.filter((seal) => onTree(seal.id)),
        ink: marks.ink.filter((line) => onTree(line.from) && onTree(line.to)),
        fresh: marks.fresh,
      };
      canvas.setReadingMarks(next);
    },
    reveal(ids) {
      const wanted = ids.filter(onTree);
      if (wanted.length) canvas.expandMany(wanted);
    },
    async flyTo(target, animate) {
      if (!onTree(target)) return;
      await canvas.flyTo(target, animate);
    },
    has(target) {
      if (!onTree(target)) return false;
      nodes();
      return nodeIds.has(target);
    },
    onUserCamera(listener) { canvas.onUserCamera(listener); },
    locate(target) {
      if (!onTree(target)) return null;
      nodes();
      if (!nodeIds.has(target)) return null;
      const node = [...canvas.layoutNow().nodes, ...canvas.layoutNow().groups].find((item) => item.id === target);
      if (!node) return null;
      const box = frame ?? spineBounds();
      return { x: clamp01((node.x - box.x) / box.width), y: clamp01((node.y - box.y) / box.height) };
    },
    miniature() {
      const layout = nodes();
      frame = spineBounds();
      const box = frame;
      const position = new Map(layout.nodes.map((node) => [node.id, node]));
      // 座標換成 0–1，整張小圖拉到容器大小；只是主線的形狀，不求精細
      const svg = svgEl('svg', { class: 'ag-rd-mini-svg', viewBox: '0 0 1 1', preserveAspectRatio: 'none', 'aria-hidden': 'true', focusable: 'false' });
      for (const [name, ids] of Object.entries(data.spine.lines)) {
        const points = ids.map((id) => position.get(id)).filter((node): node is NonNullable<typeof node> => Boolean(node));
        if (points.length < 2) continue;
        const d = points.map((node, index) => `${index ? 'L' : 'M'}${clamp01((node.x - box.x) / box.width).toFixed(4)} ${clamp01((node.y - box.y) / box.height).toFixed(4)}`).join('');
        svg.append(svgEl('path', { class: `ag-rd-mini-line ${LINE_CLASS[name] ?? ''}`.trim(), d }));
      }
      return svg;
    },
    saveView() { return canvas.getExpanded(); },
    restoreView(saved) { if (saved instanceof Set) canvas.setExpanded(saved as Set<string>); },
  };
}
