import { DEBATES } from '../data/debates';
import { GIVING, MATERIALS } from '../data/materials';
import { EPIGRAPH, ORDER_VOICES, REVEAL, STOPS, TITLE, WALK, type Stop } from '../data/stops';
import type { LayerId, Stage } from '../three/tabernacle';
import { fill, h, motionOff, svg } from './dom';
import { openDrawer } from './drawer';
import { factLine, interpHeading, refChip, refChips, voiceBlock } from './evidence';
import { ICONS } from './icons';
import { METAL } from './meta';

const LAYERS: { id: LayerId; name: string; swatch: string; ref: string }[] = [
  { id: 'seacow', name: '海狗皮（最外層）', swatch: '#3a3a3a', ref: '出26:14' },
  { id: 'ramskin', name: '染紅的公羊皮', swatch: '#c96a78', ref: '出26:14' },
  { id: 'goathair', name: '山羊毛罩棚', swatch: '#4a3a2e', ref: '出26:7' },
  { id: 'linen', name: '細麻幔子（最內層）', swatch: '#8a4fb0', ref: '出26:1' },
];

type Order = 'walk' | 'reveal';

export function mountTour(host: HTMLElement) {
  const stageHost = h('div', { class: 'stage-canvas' });
  const poster = h('div', { class: 'stage-poster' }, h('span', { class: 'loading' }, '載入會幕模型…'));
  const now = h('div', { class: 'stage-now', 'aria-live': 'polite' });
  const btnPeel = h('button', { class: 'chipbtn', type: 'button', 'aria-pressed': 'false', disabled: true }, '掀開頂');
  const btnAll = h('button', { class: 'chipbtn', type: 'button', disabled: true }, '看全景');
  const btnAuto = h('button', { class: 'chipbtn strong', type: 'button', disabled: true }, svg(ICONS.play), '自動導覽');
  const stage = h('div', { class: 'tour-stage' }, stageHost, poster, now, h('div', { class: 'stage-controls' }, btnAuto, btnPeel, btnAll));

  let world: Stage | null = null;
  let order: Order = 'walk';
  let active: Stop | null = null;
  let activeId = '';
  let peelOverride: boolean | null = null;

  /* ---------------------------------------------------------- 開場 */
  const result = h('div', { class: 'entry-result', 'aria-live': 'polite' });
  const sel = h('select', { class: 'slot', 'aria-label': '帶著什麼' },
    h('option', { value: '' }, '選一樣'), ...MATERIALS.map((m) => h('option', { value: m.id }, m.name)));
  const fit = () => {
    const probe = h('span', { class: 'slot-probe' }, sel.options[sel.selectedIndex].text);
    sel.after(probe);
    sel.style.width = `${probe.offsetWidth + 10}px`;
    probe.remove();
  };
  sel.addEventListener('change', () => {
    sel.classList.toggle('filled', !!sel.value);
    fit();
    const m = MATERIALS.find((x) => x.id === sel.value);
    if (!m) return fill(result, h('span', { class: 'entry-muted' }, '選一樣材料，看它最後用在哪裡。'));
    fill(result,
      h('div', { class: 'entry-muted' }, '它後來變成了：'),
      h('ul', { class: 'uses' }, ...m.uses.map((u) => h('li', null,
        h('span', { class: 'swatch', style: `background:${m.swatch}` }), u.text, ' ', refChip(u.ref, u.q),
        u.stop ? h('button', { class: 'go', type: 'button', onclick: () => goTo(u.stop!) }, '去看', svg(ICONS.next)) : null))));
  });
  requestAnimationFrame(fit);
  document.fonts?.ready.then(fit);
  fill(result, h('span', { class: 'entry-muted' }, '選一樣材料，看它最後用在哪裡。'));

  const intro = h('header', { class: 'tour-intro', 'data-stop': 'intro' },
    h('div', { class: 'title-block' },
      h('h1', null, TITLE.text),
      h('div', { class: 'epi' }, h('p', { class: 'epigraph' }, `「${EPIGRAPH.text}」`), refChip(EPIGRAPH.ref, EPIGRAPH.text))),
    h('p', { class: 'intro-lede' }, '出埃及記 25 到 27 章，神在山上把會幕的樣式告訴摩西：一座可以拆開、抬著走的帳幕，和圍著它的院子。這裡照經文的尺寸和材料，一站一站走進去。'),
    h('p', { class: 'entry-line' }, '我帶著', sel, '送到會幕去。'),
    result,
    h('p', { class: 'giving' }, factLine(GIVING)),
    h('p', { class: 'scroll-hint' }, '往下捲動，從東門走進去。'),
  );

  /* ---------------------------------------------------------- 次序切換 */
  const orderNote = h('div', { class: 'order-note' });
  const orderBtns = h('div', { class: 'order-btns', role: 'group', 'aria-label': '導覽次序' });
  const orderBox = h('div', { class: 'order card' }, h('b', null, '用哪個次序走？'), orderBtns, orderNote);

  /* ---------------------------------------------------------- 各站 */
  const cardsEl = h('div', { class: 'stops' });
  const cards = new Map<string, HTMLElement>();
  for (const s of STOPS) cards.set(s.id, stopCard(s));

  function stopCard(s: Stop): HTMLElement {
    const metal = METAL[s.metal];
    const related = DEBATES.filter((d) => d.stop === s.id);
    const body = h('div', { class: 'stop-body' },
      h('p', { class: 'lede' }, s.lede),
      h('ul', { class: 'facts' }, ...s.facts.map((f) => h('li', { class: f.status === 'not_stated' ? 'unsaid' : '' }, factLine(f)))),
    );
    if (s.id === 'layers') body.append(layerPanel());
    if (s.model) {
      body.append(h('button', { class: 'btn', type: 'button', onclick: () => openModel(s) }, svg(ICONS.cube), `轉一轉${s.model.name}的模型`));
    }
    if (s.voices.length) {
      body.append(h('details', { class: 'voices interp-layer' },
        h('summary', null, `註釋家怎麼讀（${s.voices.length}）`), interpHeading(), ...s.voices.map(voiceBlock)));
    }
    if (related.length) {
      body.append(h('div', { class: 'related' }, h('span', null, '經文沒說的：'),
        ...related.map((d) => h('a', { href: `#deb-${d.id}`, onclick: () => ((document.getElementById(`deb-${d.id}`) as HTMLDetailsElement | null)?.setAttribute('open', '')) }, d.question))));
    }
    return h('article', { class: 'stop card', 'data-stop': s.id, id: `stop-${s.id}`, style: `--m:${metal.color}` },
      h('div', { class: 'stop-head' },
        h('span', { class: 'stop-n' }),
        h('span', { class: 'metal', title: '這一站主要的材料' }, metal.label),
        h('h2', null, s.title),
        h('span', { class: 'stop-ref' }, refChip(s.refs))),
      body);
  }

  function layerPanel(): HTMLElement {
    const box = h('div', { class: 'layers' }, h('b', null, '一層一層掀開看'));
    const state: Record<LayerId, boolean> = { seacow: true, ramskin: true, goathair: true, linen: true };
    const note = h('p', { class: 'layer-note' });
    for (const l of LAYERS) {
      const missing = l.id === 'goathair';
      box.append(h('button', {
        class: 'layer', type: 'button', 'aria-pressed': 'true', disabled: missing,
        onclick: (e: Event) => {
          state[l.id] = !state[l.id];
          (e.currentTarget as HTMLElement).setAttribute('aria-pressed', String(state[l.id]));
          world?.setLayer(l.id, state[l.id]);
        },
      }, h('span', { class: 'swatch', style: `background:${l.swatch}` }), h('span', null, l.name), refChip(l.ref),
      missing ? h('small', null, '這個 3D 模型沒有做這一層') : null));
    }
    note.textContent = '按一下就把那一層收起來，再按一下蓋回去。模型沒有做山羊毛罩棚，所以那一層沒辦法掀。';
    box.append(note);
    return box;
  }

  function openModel(s: Stop) {
    const view = h('div', { class: 'detail-view' }, h('span', { class: 'loading' }, '載入模型…'));
    openDrawer(s.model!.name,
      view,
      h('p', { style: 'font-size:.85em;color:var(--ink-3)' }, '拖曳轉動，滾輪或兩指縮放。模型是示意重建，作者 thedeserttabernacle（CC BY-NC）。',
        s.model!.gold ? '約櫃的材質統一改成金色，照出25:11「裡外包上精金」。' : ''),
      h('ul', null, ...s.facts.map((f) => h('li', null, factLine(f)))));
    import('../three/detail').then(({ mountDetail }) => mountDetail(view, s.model!.file, { gold: s.model!.gold, reducedMotion: motionOff() }))
      .then(() => view.querySelector('.loading')?.remove())
      .catch(() => fill(view, h('span', { class: 'loading' }, '模型載入失敗。')));
  }

  function renderOrder() {
    const list = order === 'walk' ? WALK : REVEAL;
    fill(orderBtns,
      h('button', { class: 'opt', type: 'button', 'aria-pressed': String(order === 'walk'), onclick: () => setOrder('walk') }, '人走進去的次序'),
      h('button', { class: 'opt', type: 'button', 'aria-pressed': String(order === 'reveal'), onclick: () => setOrder('reveal') }, '神吩咐的次序'));
    fill(orderNote,
      h('p', null, order === 'walk'
        ? '從東門進院子，經過燔祭壇，進帳幕，最後到幔子後面的約櫃。'
        : '出25 章先講約櫃，再講桌子和燈臺；出26 章講帳幕；出27 章才講燔祭壇和院子。從最裡面講到最外面。'),
      interpHeading(), voiceBlock(ORDER_VOICES[0]));
    list.forEach((s, i) => {
      const c = cards.get(s.id)!;
      c.querySelector('.stop-n')!.textContent = String(i + 1);
      cardsEl.append(c);
    });
  }
  function setOrder(o: Order) {
    if (o === order) return;
    order = o;
    renderOrder();
    goTo((order === 'walk' ? WALK : REVEAL)[0].id);
  }

  host.append(stage, h('div', { class: 'tour-cards' }, intro, orderBox, cardsEl,
    h('div', { class: 'tour-end card' }, h('b', null, '走完了。'),
      h('p', null, '出27 章最後兩節講點燈的油，接下來出28 章講祭司的衣服。想看這座會幕後來怎麼用來獻祭，下一站是利未記。'),
      h('a', { class: 'btn', href: '../../../利未記/第1章/dist/index.html' }, '會幕前的一天：利未記 1–9 章', svg(ICONS.next)))));
  renderOrder();

  /* ---------------------------------------------------------- 捲動驅動鏡頭 */
  function show(id: string) {
    if (id === activeId) return;
    activeId = id;
    const s = STOPS.find((x) => x.id === id) ?? null;
    active = s;
    cards.forEach((c, k) => c.classList.toggle('on', k === id));
    peelOverride = null;
    btnPeel.setAttribute('aria-pressed', String(!!s?.peel));
    if (!s) {
      fill(now, h('b', null, '會幕全景'), h('span', null, '拖曳可以轉動'));
      world?.go({ pos: [34, 22, 40], target: [0, 0, 2], fov: 42 }, false);
      world?.setAutoRotate(true);
      return;
    }
    fill(now, h('span', { class: 'metal', style: `--m:${METAL[s.metal].color}` }, METAL[s.metal].label), h('b', null, s.title), h('span', null, s.refs));
    world?.go(s.view, s.peel ?? false);
  }
  function goTo(id: string) {
    const c = cards.get(id);
    if (!c) return;
    c.scrollIntoView({ behavior: motionOff() ? 'auto' : 'smooth', block: 'center' });
  }
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) if (e.isIntersecting) show((e.target as HTMLElement).dataset.stop!);
  }, { rootMargin: '-45% 0px -50% 0px' });
  io.observe(intro);
  cards.forEach((c) => io.observe(c));

  /* ---------------------------------------------------------- 控制 */
  let autoToken = 0;
  const stopAuto = () => {
    if (!autoToken) return;
    autoToken = 0;
    fill(btnAuto, svg(ICONS.play), '自動導覽');
  };
  btnAuto.addEventListener('click', async () => {
    if (autoToken) return stopAuto();
    const my = (autoToken = Date.now());
    fill(btnAuto, svg(ICONS.pause), '停下來');
    const list = order === 'walk' ? WALK : REVEAL;
    const start = active ? list.indexOf(active) + 1 : 0;
    for (let i = start >= list.length ? 0 : start; i < list.length; i++) {
      if (autoToken !== my) return;
      goTo(list[i].id);
      await new Promise((r) => setTimeout(r, motionOff() ? 5000 : 7000));
    }
    stopAuto();
  });
  for (const ev of ['wheel', 'touchstart', 'keydown']) addEventListener(ev, () => autoToken && stopAuto(), { passive: true });
  btnPeel.addEventListener('click', () => {
    const cur = peelOverride ?? !!active?.peel;
    peelOverride = !cur;
    btnPeel.setAttribute('aria-pressed', String(peelOverride));
    const v = active?.view ?? { pos: [16, 12, 10] as [number, number, number], target: [0, 1, -5] as [number, number, number], fov: 44 };
    world?.go(v, peelOverride);
  });
  btnAll.addEventListener('click', () => {
    activeId = '';
    show('intro');
  });

  /* ---------------------------------------------------------- 載入 3D */
  const lowPower = (navigator.hardwareConcurrency ?? 8) <= 4 || matchMedia('(max-width: 560px)').matches;
  const canWebGL = (() => {
    try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch { return false; }
  })();
  const loading = poster.querySelector('.loading')!;
  if (!canWebGL) loading.textContent = '這台裝置不支援 3D。文字導覽照樣可以讀。';
  else {
    import('../three/tabernacle').then(({ createStage }) => createStage(stageHost, {
      reducedMotion: motionOff(), lowPower, onProgress: (p) => (loading.textContent = `載入會幕模型… ${Math.round(p * 100)}%`),
    })).then((st) => {
      world = st;
      poster.remove();
      [btnPeel, btnAll, btnAuto].forEach((b) => b.removeAttribute('disabled'));
      const cur = activeId || 'intro';
      activeId = '';
      show(cur);
    }).catch((err) => {
      console.error(err);
      loading.textContent = '3D 模型載入失敗。文字導覽照樣可以讀。';
    });
  }
  void refChips;
}
