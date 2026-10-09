/**
 * 章末與頁尾：
 * - 章末（每個節期章的最後一拍之後）：經文全文、延伸閱讀、新約、下一個節期。
 *   開場章（opening）沒有自己的章末，它的經文與條目併進接下來第一個節期章的章末。
 * - 頁尾「資料來源與授權」。
 */
import type { AudioSource, StoryChapter } from '../data/types';
import { SITE } from '../data/site';
import { entryUrl } from '../data/links';
import { ext, h } from './dom';
import { STEP_REPO } from './panels';

const uniq = <T>(xs: T[]): T[] => [...new Set(xs)];

function entryItem(title: string): HTMLElement | null {
  const e = SITE.entries[title];
  if (!e) return null;
  return h('li', { class: 'jf-entry' },
    h('p', { class: 'jf-entry-name' }, e.title),
    h('p', { class: 'jf-entry-gist' }, e.gist),
    h('p', { class: 'jf-entry-go' }, ext(entryUrl(e.type, e.title), '查看完整條目（另開網頁）')));
}

function passageItem(ref: string): HTMLElement | null {
  const block = SITE.verses[ref];
  if (!block) return null;
  return h('details', { class: 'jf-pass' },
    h('summary', { class: 'jf-pass-sum' }, h('span', { class: 'jf-pass-ref' }, block.ref)),
    h('div', { class: 'jf-pass-body' },
      block.lines.map((ln) => h('p', { class: 'jf-pass-line' }, h('span', { class: 'jf-vn jf-vn-inline', 'aria-label': `第${ln.v}節` }, String(ln.v)), ln.text))));
}

export function buildEndings(): HTMLElement[] {
  const out: HTMLElement[] = [];
  let carry: StoryChapter[] = [];
  for (const chapter of SITE.chapters) {
    if (chapter.kind === 'opening') {
      carry.push(chapter);
      continue;
    }
    const group = [...carry, chapter];
    carry = [];
    out.push(buildEnding(chapter, group));
  }
  return out;
}

function buildEnding(chapter: StoryChapter, group: StoryChapter[]): HTMLElement {
  // 開場章併進來的經文，若已被這章較大的一段完整包含（例如出12:1-6 之於出12:1-14），就不重複列
  const all = uniq(group.flatMap((c) => c.passages));
  const contained = (a: string, b: string) => {
    const x = SITE.verses[a];
    const y = SITE.verses[b];
    return !!x && !!y && a !== b && x.book === y.book && x.chapter === y.chapter && x.from <= y.from && x.to >= y.to && (x.from < y.from || x.to > y.to);
  };
  const kept = all.filter((p) => !all.some((q) => contained(q, p)));
  // 書卷照第一次出現的順序，同一卷內照章節順序排
  const bookOrder = [...new Set(kept.map((p) => SITE.verses[p]?.book))];
  const passages = [...kept].sort((a, b) => {
    const x = SITE.verses[a];
    const y = SITE.verses[b];
    if (!x || !y) return 0;
    return bookOrder.indexOf(x.book) - bookOrder.indexOf(y.book) || x.chapter - y.chapter || x.from - y.from;
  });
  const entries = uniq(group.flatMap((c) => c.entries));
  const nt = uniq(group.flatMap((c) => c.nt));
  const passageEls = passages.map(passageItem).filter(Boolean);
  const entryEls = entries.map(entryItem).filter(Boolean);
  const ntEls = nt.map(entryItem).filter(Boolean);
  const n = chapter.next;

  return h('section', { class: 'jf-end', id: `jf-end-${chapter.id}`, 'data-chapter': chapter.id, 'aria-label': `${chapter.title}章末` },
    h('div', { class: 'jf-end-inner' },
      h('header', { class: 'jf-end-head' },
        h('h2', { class: 'jf-end-title' }, chapter.title),
        chapter.date ? h('p', { class: 'jf-end-date' }, chapter.date) : null),
      passageEls.length
        ? h('div', { class: 'jf-end-block' },
          h('h3', { class: 'jf-end-h' }, '經文全文'),
          h('div', { class: 'jf-pass-list' }, passageEls))
        : null,
      entryEls.length
        ? h('div', { class: 'jf-end-block' },
          h('h3', { class: 'jf-end-h' }, '延伸閱讀'),
          h('ul', { class: 'jf-entries' }, entryEls))
        : null,
      ntEls.length
        ? h('div', { class: 'jf-end-block' },
          h('h3', { class: 'jf-end-h' }, '新約'),
          h('ul', { class: 'jf-entries jf-entries-one' }, ntEls))
        : null,
      n
        ? h('div', { class: 'jf-end-block jf-next' },
          h('h3', { class: 'jf-end-h' }, '下一個節期'),
          h('p', { class: 'jf-next-line' }, h('span', { class: 'jf-next-title' }, n.title), h('span', { class: 'jf-next-date' }, n.date)))
        : null));
}

// ---------------------------------------------------------------------------

const CC0 = 'https://creativecommons.org/publicdomain/zero/1.0/';
const CC_BY = 'https://creativecommons.org/licenses/by/4.0/';

function audioItem(a: AudioSource): HTMLElement {
  const pages = a.pages && a.pages.length ? a.pages : [a.page];
  return h('li', { class: 'jf-audio' },
    h('p', { class: 'jf-audio-main' },
      h('span', { class: 'jf-audio-title', lang: 'en' }, a.title),
      '　',
      h('span', { class: 'jf-audio-author' }, a.author),
      '　',
      ext(CC0, 'CC0'),
      '　',
      pages.map((p, i) => [i > 0 ? '、' : '', ext(p, pages.length > 1 ? `來源頁 ${i + 1}` : '來源頁')])),
    a.edit ? h('p', { class: 'jf-audio-edit' }, `剪輯：${a.edit}`) : null);
}

export function buildCredits(): HTMLElement {
  // 每章的來源連結：同一章的幾個來源放在同一列
  const rows = new Map<string, { label: string; items: { site: string; url: string }[] }>();
  for (const s of SITE.sources) {
    const key = `${s.book}${s.chapter}`;
    if (!rows.has(key)) rows.set(key, { label: `${s.book} ${s.chapter} 章`, items: [] });
    rows.get(key)!.items.push({ site: s.site, url: s.url });
  }
  return h('footer', { class: 'jf-credits', id: 'jf-credits', 'aria-labelledby': 'jf-credits-h' },
    h('div', { class: 'jf-credits-inner' },
      h('h2', { class: 'jf-credits-h', id: 'jf-credits-h' }, '資料來源與授權'),
      h('div', { class: 'jf-credit-block' },
        h('h3', null, '經文'),
        h('p', null, '和合本。')),
      h('div', { class: 'jf-credit-block' },
        h('h3', null, '原文'),
        h('p', null, ext(STEP_REPO, 'STEP Bible（STEPBible-Data）'), '，依 ', ext(CC_BY, 'CC BY 4.0'), ' 授權使用。')),
      h('div', { class: 'jf-credit-block' },
        h('h3', null, '註釋與原文資料的原站'),
        h('ul', { class: 'jf-src-list' },
          [...rows.values()].map((r) =>
            h('li', null,
              h('span', { class: 'jf-src-label' }, r.label),
              r.items.map((it, i) => [i > 0 ? '　' : '', ext(it.url, it.site)]))))),
      h('div', { class: 'jf-credit-block' },
        h('h3', null, '音檔'),
        h('ul', { class: 'jf-audio-list' }, SITE.audio.map(audioItem))),
      h('p', { class: 'jf-credits-note' }, '本網站僅供非商業教育與聖經研讀使用。')));
}
