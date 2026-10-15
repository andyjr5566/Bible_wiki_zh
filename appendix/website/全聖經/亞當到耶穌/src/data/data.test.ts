import { describe, expect, it } from 'vitest';
import { DATA, READING, VERSES, branchRoots, expandVerseRefs, lookupVerses, buildGraph, makeSyntheticData, pathToFirstAncestor, searchNameForms, searchPeople } from './model';
import type { GenealogyData } from './types';
import { computeLayout } from '../ui/layout';

/** 全部展開：每位主線人物的旁支、「N 位子女」、「某某所生」底下各個孩子、名單牌子和區域都打開。 */
function everythingOpen(data: GenealogyData): Set<string> {
  const graph = buildGraph(data);
  const open = new Set<string>(branchRoots(data, graph).map((item) => item.rootId));
  for (const id of graph.byId.keys()) open.add(id);
  for (const id of graph.spineIds) for (const direction of [-1, 1]) open.add(`siblings:${id}:${direction}`);
  for (const node of data.placements?.nodes ?? []) open.add(node.id);
  return open;
}

function allReferenceKeys(data: GenealogyData): string[] {
  const refs: string[] = [];
  const add = (ref?: string) => { if (ref) refs.push(...expandVerseRefs(ref)); };
  for (const person of data.persons) {
    for (const name of person.names ?? []) add(name.ref);
    for (const relation of [...(person.parents ?? []), ...(person.spouses ?? []), ...(person.siblings ?? []), ...(person.kin ?? []), ...(person.descends ?? [])]) add(relation.ref);
    for (const candidate of person.maybeSame ?? []) for (const ref of candidate.refs) add(ref);
  }
  for (const witness of data.witnesses) add(witness.ref);
  for (const age of data.ages.people) for (const ref of age.refs ?? []) add(ref);
  for (const note of data.notes) for (const entry of note.scripture ?? []) add(entry.ref);
  for (const stop of data.tour) for (const ref of (Array.isArray(stop.refs) ? stop.refs : [stop.refs])) add(ref);
  return refs;
}

function firstNamed(data: GenealogyData, name: string) {
  return data.persons.find((person) => person.name === name || person.id === name);
}

function findOverlaps(nodes: ReturnType<typeof computeLayout>['nodes']): string[] {
  const sorted = [...nodes].sort((a, b) => (a.x - a.width / 2) - (b.x - b.width / 2));
  const active: typeof sorted = [];
  const overlaps: string[] = [];
  for (const node of sorted) {
    const left = node.x - node.width / 2;
    for (let i = active.length - 1; i >= 0; i -= 1) if (active[i]!.x + active[i]!.width / 2 <= left) active.splice(i, 1);
    const top = node.y - node.height / 2;
    const bottom = node.y + node.height / 2;
    for (const other of active) {
      if (top < other.y + other.height / 2 && bottom > other.y - other.height / 2) overlaps.push(`${node.id} × ${other.id}`);
    }
    active.push(node);
  }
  return overlaps;
}

describe('家譜資料閘門', () => {
  it('每個人物在大圖上都有自己的節點（全部展開時）', () => {
    const layout = computeLayout(DATA, everythingOpen(DATA));
    const ids = new Set(layout.nodes.map((node) => node.id));
    const missing = DATA.persons.filter((person) => !ids.has(person.id)).map((person) => person.id);
    expect(missing).toEqual([]);
    for (const node of DATA.placements?.nodes ?? []) expect(ids.has(node.id), node.id).toBe(true);
  });

  it('全部展開時節點框不重疊', () => {
    const layout = computeLayout(DATA, everythingOpen(DATA));
    expect(findOverlaps(layout.nodes).slice(0, 5)).toEqual([]);
  });

  it('經文記載的母親：孩子在圖上時，不是掛在母親（或「某某所生」）底下，就是有母子線或「母親：某某」', () => {
    const graph = buildGraph(DATA);
    const layout = computeLayout(DATA, everythingOpen(DATA));
    const ids = new Set(layout.nodes.map((node) => node.id));
    const mothers = new Set(layout.edges.filter((edge) => edge.kind === 'mother').map((edge) => `${edge.from}|${edge.to}`));
    const tags = new Set(layout.farLinks.filter((item) => item.label === '母親').map((item) => `${item.other}|${item.id}`));
    const missing: string[] = [];
    for (const person of DATA.persons) {
      if (!ids.has(person.id)) continue;
      for (const parent of person.parents ?? []) {
        if (parent.role !== '母' || !graph.byId.has(parent.id)) continue;
        const tree = graph.treeParent.get(person.id);
        const underMother = tree === parent.id || graph.bornOf.get(tree ?? '') === parent.id;
        if (!underMother && !mothers.has(`${parent.id}|${person.id}`) && !tags.has(`${parent.id}|${person.id}`)) missing.push(`${parent.id} → ${person.id}`);
      }
    }
    expect(missing).toEqual([]);
    // 以實瑪利掛在夏甲底下；流便在「利亞所生」底下；猶大（主線）頭上標「母親：利亞」
    expect(graph.treeParent.get('以實瑪利')).toBe('夏甲');
    expect(graph.bornOf.get(graph.treeParent.get('流便') ?? '')).toBe('利亞');
    expect(tags.has('利亞|猶大')).toBe(true);
    // 母親底下看得到他生的每一個孩子，主線上的也是（代上3:5 拔示巴生示米亞、朔罷、拿單、所羅門）
    const bathsheba = graph.treeParent.get('朔罷')!;
    const shown = (graph.children.get(bathsheba) ?? []).map((id) => graph.childRefs.get(id) ?? id);
    expect(shown).toEqual(['示米亞#大衛', '朔罷', '拿單', '所羅門']);
    for (const [card, mother] of graph.bornOf) {
      const father = graph.treeParent.get(card)!;
      const recorded = DATA.persons.filter((person) => person.parents?.some((r) => r.id === mother && r.role === '母') && person.parents?.some((r) => r.id === father));
      const under = new Set((graph.children.get(card) ?? []).map((id) => graph.childRefs.get(id) ?? id));
      expect(recorded.filter((person) => !under.has(person.id)).map((person) => person.id), card).toEqual([]);
    }
    // 分身卡不是人物；父母本來就排在同一處的（西庇太一家），不放分身卡，免得同一位母親在旁邊出現兩次
    expect(DATA.persons.some((person) => graph.bornOf.has(person.id))).toBe(false);
    for (const [card, mother] of graph.bornOf) {
      const father = graph.treeParent.get(card)!;
      expect(graph.treeParent.get(mother) === graph.treeParent.get(father) && graph.treeParent.has(father), card).toBe(false);
    }
  });

  it('經文記載的夫妻：兩人都在圖上時，不是有夫妻線，就是名字上方標出配偶', () => {
    const graph = buildGraph(DATA);
    const layout = computeLayout(DATA, everythingOpen(DATA));
    const linked = new Set(layout.edges.flatMap((edge) => [`${edge.from}|${edge.to}`, `${edge.to}|${edge.from}`]));
    const chips = new Set(layout.farLinks.map((item) => `${item.id}|${item.other}`));
    const ids = new Set(layout.nodes.map((node) => node.id));
    const missing: string[] = [];
    for (const person of DATA.persons) {
      for (const spouse of person.spouses ?? []) {
        if (spouse.id === person.id || !ids.has(person.id) || !ids.has(spouse.id)) continue;
        const key = `${person.id}|${spouse.id}`;
        // 丈夫旁邊有妻子的分身卡（以色列旁邊的利亞）也算標出來了
        const card = graph.bornOf.has(`所生:${person.id}:${spouse.id}`) || graph.bornOf.has(`所生:${spouse.id}:${person.id}`);
        const tagged = (chips.has(key) || card) && (chips.has(`${spouse.id}|${person.id}`) || card);
        if (!linked.has(key) && !tagged) missing.push(key);
      }
    }
    expect(missing).toEqual([]);
    // 撒拉就在亞伯拉罕旁邊，線上標「妻子」
    const sarah = layout.edges.find((edge) => edge.kind === 'kin' && [edge.from, edge.to].includes('撒拉') && [edge.from, edge.to].includes('亞伯拉罕'));
    expect(sarah?.label).toBe('妻子');
  });

  it('名單牌子掛在圖上的人底下，區域在主線人物旁邊而且不畫連到主線的線', () => {
    const graph = buildGraph(DATA);
    const layout = computeLayout(DATA, everythingOpen(DATA));
    const placements = DATA.placements!;
    expect(placements.nodes.filter((node) => node.kind === 'list').length).toBeGreaterThan(10);
    for (const node of placements.nodes) {
      expect(graph.byId.has(node.under), `${node.id} → ${node.under}`).toBe(true);
      if (node.kind === 'region') {
        expect(graph.spineIds.has(node.under), node.id).toBe(true);
        expect(layout.edges.some((edge) => edge.to === node.id), `${node.id} 不該有線`).toBe(false);
      }
      if (node.kind === 'list') expect(layout.edges.some((edge) => edge.from === node.under && edge.to === node.id && edge.kind === 'list'), node.id).toBe(true);
    }
    // 新約家族頁的每一位都在大圖上
    const ids = new Set(layout.nodes.map((node) => node.id));
    for (const family of DATA.ntFamilies) for (const member of family.members ?? []) expect(ids.has(member), member).toBe(true);
  });

  it('人物搜尋只比對姓名和別名，並優先顯示主線候選', () => {
    const results = searchPeople('約瑟', DATA);
    expect(results.length).toBeGreaterThan(0);
    expect(results.every((person) => searchNameForms(person, '約瑟').length > 0)).toBe(true);
    const exactNames = results.filter((person) => searchNameForms(person, '約瑟').some((name) => name === '約瑟'));
    const spineIds = buildGraph(DATA).spineIds;
    expect(exactNames.filter((person) => spineIds.has(person.id)).length).toBeGreaterThan(0);
    const idOnlyMatches = DATA.persons.filter((person) => person.id.includes('約瑟') && !searchNameForms(person, '約瑟').length);
    expect(results.some((person) => idOnlyMatches.some((candidate) => candidate.id === person.id))).toBe(false);
    const rank = (person: (typeof results)[number]) => Math.max(0, ...searchNameForms(person, '約瑟').map((name) =>
      name === '約瑟' ? 3 : name.startsWith('約瑟') ? 2 : 1));
    for (let index = 1; index < results.length; index += 1) {
      const previous = results[index - 1]!;
      const current = results[index]!;
      expect(rank(previous)).toBeGreaterThanOrEqual(rank(current));
      if (rank(previous) === rank(current) && !spineIds.has(previous.id)) expect(spineIds.has(current.id)).toBe(false);
    }
  });

  it('兩條主線都有有效起點，路線人物都存在於資料中', () => {
    const routes = Object.values(DATA.spine.lines);
    expect(routes.length).toBeGreaterThanOrEqual(2);
    expect(routes[0]?.[0]).toBeTruthy();
    for (const route of routes) {
      expect(route.length).toBeGreaterThan(0);
      expect(route[0]).toBe(routes[0]?.[0]);
      expect(route.every((id) => DATA.persons.some((person) => person.id === id))).toBe(true);
    }
  });

  it('兩條主線從亞當經父子或 link 連續到耶穌', () => {
    const adam = firstNamed(DATA, '亞當')!;
    const jesus = firstNamed(DATA, '耶穌')!;
    const routes = Object.values(DATA.spine.lines);
    for (const route of routes) {
      expect(route[0]).toBe(adam.id);
      expect(route.at(-1)).toBe(jesus.id);
      for (let index = 1; index < route.length; index += 1) {
        const parent = route[index - 1]!;
        const child = DATA.persons.find((person) => person.id === route[index]);
        const connected = child?.parents?.some((item) => item.id === parent) || child?.descends?.some((item) => item.id === parent) ||
          DATA.persons.find((person) => person.id === parent)?.kin?.some((item) => item.id === route[index]);
        expect(connected, `${parent} → ${route[index]}`).toBe(true);
      }
    }
  });

  it('施洗約翰追溯到亞當時保留以利沙伯通往亞倫的後裔關係', () => {
    const john = DATA.persons.find((person) => person.id.includes('施洗'))!;
    const elizabeth = DATA.persons.find((person) => person.name === '以利沙伯')!;
    const aaron = DATA.persons.find((person) => person.name === '亞倫')!;
    const route = pathToFirstAncestor(john.id, DATA, buildGraph(DATA));
    expect(route?.ids).toContain(elizabeth.id);
    expect(route?.ids).toContain(aaron.id);
    expect(route?.edges).toContainEqual({ from: elizabeth.id, to: aaron.id, kind: 'descends' });
  });

  it('每筆 parents、kin 關係都指向存在的人物', () => {
    const ids = new Set(DATA.persons.map((person) => person.id));
    for (const person of DATA.persons) {
      for (const relation of [...(person.parents ?? []), ...(person.kin ?? [])]) expect(ids.has(relation.id), `${person.id} → ${relation.id}`).toBe(true);
    }
  });

  it('可能同一人的候選都能連到人物，引用經節都存在', () => {
    const ids = new Set(DATA.persons.map((person) => person.id));
    for (const person of DATA.persons) {
      for (const candidate of person.maybeSame ?? []) {
        expect(ids.has(candidate.id), `${person.id} ≈ ${candidate.id}`).toBe(true);
        expect(candidate.refs.length).toBeGreaterThan(0);
        for (const ref of candidate.refs) expect(VERSES[ref], `${person.id}: ${ref}`).toBeTruthy();
      }
    }
  });

  it('每個導覽焦點與經節都存在於匯出資料', () => {
    const ids = new Set(DATA.persons.map((person) => person.id));
    for (const stop of DATA.tour) {
      for (const focus of stop.focus) expect(ids.has(focus), `${stop.id}: ${focus}`).toBe(true);
      const refs = Array.isArray(stop.refs) ? stop.refs : [stop.refs];
      for (const ref of refs.flatMap((value) => expandVerseRefs(value))) {
        expect(VERSES[ref], `${stop.id}: ${ref}`).toBeTruthy();
      }
    }
  });

  it('每站導覽序列都只用主線人物，且每個人都有版面節點', () => {
    const graph = buildGraph(DATA);
    const layout = computeLayout(DATA);
    const layoutIds = new Set(layout.nodes.map((node) => node.id));
    for (const stop of DATA.tour) {
      expect(stop.sequence?.length, `${stop.id}: sequence`).toBeGreaterThan(0);
      for (const id of stop.sequence ?? []) {
        expect(graph.spineIds.has(id), `${stop.id}: ${id} should be on the spine`).toBe(true);
        expect(layoutIds.has(id), `${stop.id}: ${id} should have a layout node`).toBe(true);
      }
    }
  });

  it('所有人物、見證、年歲、註記與導覽引用都能在 verses.json 找到', () => {
    for (const ref of allReferenceKeys(DATA)) expect(VERSES[ref], ref).toBeTruthy();
  });

  it('資訊卡上每一個經文標籤（含範圍、逗號、跨章）都查得到全文', () => {
    const refs = new Set<string>();
    const add = (ref?: string) => { if (ref) refs.add(ref); };
    for (const person of DATA.persons) {
      for (const name of person.names ?? []) add(name.ref);
      for (const relation of [...(person.parents ?? []), ...(person.spouses ?? []), ...(person.siblings ?? []), ...(person.kin ?? []), ...(person.descends ?? [])]) add(relation.ref);
    }
    for (const witness of DATA.witnesses) add(witness.ref);
    for (const note of DATA.notes) for (const entry of note.scripture ?? []) add(entry.ref);
    expect(refs.size).toBeGreaterThan(500);
    for (const ref of refs) {
      const lines = lookupVerses(ref);
      expect(lines.length, ref).toBeGreaterThan(0);
      expect(lines.filter((line) => !line.text).map((line) => line.key), ref).toEqual([]);
    }
  });

  it('名字字義：主線人物幾乎都有原文，經文說明的引句真的在經文裡', () => {
    const spine = new Set(Object.values(DATA.spine.lines).flat());
    const withOrig = [...spine].filter((id) => DATA.persons.find((person) => person.id === id)?.nameMeaning?.orig);
    expect(withOrig.length / spine.size).toBeGreaterThan(0.9);
    let withMeaning = 0;
    for (const person of DATA.persons) {
      const info = person.nameMeaning;
      if (!info) continue;
      if (info.meaningEn) { withMeaning += 1; expect(info.meaningZh, person.id).toBeTruthy(); }
      for (const item of info.scripture) {
        const text = lookupVerses(item.ref).map((line) => line.text ?? '').join('');
        expect(text.includes(item.quote), `${person.id} ${item.ref}`).toBe(true);
      }
    }
    expect(withMeaning).toBeGreaterThan(1000);
    expect(DATA.persons.find((person) => person.id === '塞特')?.nameMeaning?.meaningZh).toBe('補償');
  });

  it('經文範圍展開：同章、逗號、跨章', () => {
    const verses = { '創1:30': 'a', '創1:31': 'b', '創2:1': 'c', '創2:2': 'd', '創3:5': 'e' };
    expect(expandVerseRefs('創1:30-31', verses)).toEqual(['創1:30', '創1:31']);
    expect(expandVerseRefs('創1:30-2:2', verses)).toEqual(['創1:30', '創1:31', '創2:1', '創2:2']);
    expect(expandVerseRefs('創1:31-3:5', verses)).toEqual(['創1:31', '創2:1', '創2:2', '創3:1', '創3:2', '創3:3', '創3:4', '創3:5']);
    expect(expandVerseRefs('創2:1, 創3:5', verses)).toEqual(['創2:1', '創3:5']);
    expect(expandVerseRefs('創2:1、2', verses)).toEqual(['創2:1', '創2:2']);
  });

  it('主線與預設收合旁支的節點框不重疊', () => {
    const graph = buildGraph(DATA);
    const layout = computeLayout(DATA, new Set());
    expect(findOverlaps(layout.nodes)).toEqual([]);
    expect(layout.nodes.length).toBeGreaterThanOrEqual(graph.spineIds.size);
  });

});

describe('讀經資料閘門（代上 1–9 章）', () => {
  const verses = READING.chapters.flatMap((chapter) => chapter.verses.map((verse) => ({ chapter: chapter.n, verse })));
  const personIds = new Set(DATA.persons.map((person) => person.id));

  it('407 節全收，經文和正式經文逐字相同', () => {
    expect(READING.chapters.map((chapter) => chapter.n)).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9]);
    expect(verses.length).toBe(407);
    for (const { chapter, verse } of verses) expect(verse.text, `代上${chapter}:${verse.v}`).toBe(VERSES[`代上${chapter}:${verse.v}`]);
  });

  it('每個標記的位置都在經文裡，前後不重疊', () => {
    const errors: string[] = [];
    for (const { chapter, verse } of verses) {
      let end = 0;
      for (const token of verse.t) {
        if (token.s < end || token.e <= token.s || token.e > verse.text.length) errors.push(`代上${chapter}:${verse.v} ${token.s}-${token.e}`);
        end = token.e;
      }
    }
    expect(errors).toEqual([]);
  });

  it('人名對到的人物都存在，而且在大圖上有節點', () => {
    const layoutIds = new Set(computeLayout(DATA, everythingOpen(DATA)).nodes.map((node) => node.id));
    const missing: string[] = [];
    for (const { chapter, verse } of verses) {
      for (const token of verse.t) {
        for (const id of [token.id, token.of, ...(token.from ?? []), ...(token.to ?? [])].filter((value): value is string => Boolean(value))) {
          if (!personIds.has(id) || !layoutIds.has(id)) missing.push(`代上${chapter}:${verse.v} ${id}`);
        }
      }
    }
    expect(missing).toEqual([]);
    expect(verses.reduce((sum, { verse }) => sum + verse.t.filter((token) => token.k === 'p' && token.id).length, 0)).toBeGreaterThan(1500);
  });

  it('名單牌子與讀經提醒都對得上', () => {
    const plaques = new Set((DATA.placements?.nodes ?? []).map((node) => node.id));
    for (const { chapter, verse } of verses) {
      if (verse.hold) expect(plaques.has(verse.hold), `代上${chapter}:${verse.v} ${verse.hold}`).toBe(true);
      if (verse.note !== undefined) expect(READING.notes[verse.note], `代上${chapter}:${verse.v}`).toBeTruthy();
    }
    for (const note of READING.notes) {
      expect(note.text).toBeTruthy();
      for (const key of note.verses) expect(VERSES[key], key).toBeTruthy();
    }
  });
});

describe('三千人物版面壓力測試', () => {
  const synthetic = makeSyntheticData(3000);
  const expanded = new Set(branchRoots(synthetic, buildGraph(synthetic)).map((item) => item.rootId));

  it('合成資料有兩條 76 代主線、旁支與多種關係', () => {
    const routes = Object.values(synthetic.spine.lines);
    expect(routes.every((route) => route.length === 76)).toBe(true);
    expect(routes.every((route) => synthetic.persons.find((person) => person.id === route[0])?.name === '亞當')).toBe(true);
    expect(routes.every((route) => synthetic.persons.find((person) => person.id === route.at(-1))?.name === '耶穌')).toBe(true);
    expect(synthetic.persons.length).toBeGreaterThanOrEqual(2900);
    expect(synthetic.persons.length).toBeLessThanOrEqual(3100);
    expect(synthetic.persons.some((person) => (person.parents?.length ?? 0) > 1)).toBe(true);
    expect(synthetic.persons.some((person) => (person.descends?.length ?? 0) > 0)).toBe(true);
    expect(synthetic.persons.some((person) => (person.kin?.length ?? 0) > 0)).toBe(true);
    for (const route of routes) {
      for (let index = 1; index < route.length; index += 1) {
        const prior = route[index - 1]!;
        const child = synthetic.persons.find((person) => person.id === route[index]);
        expect(child?.parents?.some((relation) => relation.id === prior), `${prior} → ${route[index]}`).toBe(true);
      }
    }
  });

  it('全部旁支收合時，節點框也不重疊', () => {
    const layout = computeLayout(synthetic);
    expect(findOverlaps(layout.nodes).slice(0, 1)).toEqual([]);
  });

  it('全部展開時節點不重疊，版面計算低於 500 毫秒', () => {
    const start = performance.now();
    const layout = computeLayout(synthetic, expanded);
    const elapsed = performance.now() - start;
    expect(layout.nodes.length).toBe(synthetic.persons.length);
    const collisions = findOverlaps(layout.nodes);
    const collisionNodes = layout.nodes.filter((node) => collisions[0]?.split(' × ').includes(node.id));
    const details = collisionNodes.map((node) => ({
      node,
      root: layout.nodes.find((candidate) => candidate.id === node.sideRoot),
      parent: synthetic.persons.find((person) => person.id === node.id)?.parents,
    }));
    expect(collisions.slice(0, 1), JSON.stringify(details)).toEqual([]);
    expect(elapsed).toBeLessThan(500);
  });
});
