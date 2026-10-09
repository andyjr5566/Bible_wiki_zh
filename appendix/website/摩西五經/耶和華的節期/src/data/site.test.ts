// 產出的 site.json 一致性：每一拍引用的註釋與原文字都解析得到、每則註釋有原站網址、
// 每個原文字有希伯來文、經文與條目都收齊。內容本身的對 vault 檢查在 scripts/build-data.mjs。
import { describe, expect, it } from 'vitest';
import { SITE } from './site';
import { chapterUrl, entryUrl } from './links';

const beats = SITE.chapters.flatMap((c) => c.beats.map((b) => ({ chapter: c.id, ...b })));

describe('site.json 一致性', () => {
  it('標題與標語', () => {
    expect(SITE.title).toBe('耶和華的節期');
    expect(SITE.motto.ref).toBe('利23:2');
    expect(SITE.motto.book).toBe('利未記');
    expect(SITE.motto.lines.length).toBeGreaterThan(0);
  });

  it('章與拍：id 不重複、每章都有拍', () => {
    expect(new Set(SITE.chapters.map((c) => c.id)).size).toBe(SITE.chapters.length);
    for (const c of SITE.chapters) {
      expect(c.beats.length, c.id).toBeGreaterThan(0);
      expect(new Set(c.beats.map((b) => b.id)).size, c.id).toBe(c.beats.length);
      for (const k of ['paper', 'ink', 'accent', 'glow'] as const) expect(c.palette[k], `${c.id}.${k}`).toMatch(/^#[0-9a-fA-F]{6}$/);
    }
  });

  it('每一拍的 notes、words 都解析得到', () => {
    for (const b of beats) {
      for (const id of b.notes ?? []) expect(SITE.commentary[id], `${b.chapter}/${b.id} notes ${id}`).toBeDefined();
      for (const id of b.words ?? []) expect(SITE.step[id], `${b.chapter}/${b.id} words ${id}`).toBeDefined();
    }
  });

  it('每一拍的 verse 與每章的 passages 都有經文', () => {
    for (const b of beats) {
      if (b.verse) expect(SITE.verses[b.verse]?.lines.length, `${b.chapter}/${b.id} verse ${b.verse}`).toBeGreaterThan(0);
    }
    for (const c of SITE.chapters) for (const p of c.passages) expect(SITE.verses[p]?.lines.length, `${c.id} ${p}`).toBeGreaterThan(0);
  });

  it('經文每節有字、節號連續', () => {
    for (const [ref, v] of Object.entries(SITE.verses)) {
      expect(v.ref).toBe(ref);
      expect(v.lines.map((l) => l.v), ref).toEqual(Array.from({ length: v.to - v.from + 1 }, (_, i) => v.from + i));
      for (const l of v.lines) expect(l.text.trim().length, `${ref}:${l.v}`).toBeGreaterThan(0);
    }
  });

  it('每則註釋有原站網址，且有 quote 或 paraphrase；英文來源的引文附中譯', () => {
    for (const n of Object.values(SITE.commentary)) {
      expect(n.url, n.id).toMatch(/^https?:\/\//);
      expect(n.quote || n.paraphrase, n.id).toBeTruthy();
      expect(n.work.trim().length, n.id).toBeGreaterThan(0);
      if ((n.source === 'KC' || n.source === 'BH') && n.quote) expect(n.quoteZh, n.id).toBeTruthy();
      if (n.source === 'CT' || n.source === 'GT') expect(n.quoteZh, n.id).toBeUndefined();
    }
  });

  it('授權頁的來源涵蓋每則註釋與每個原文字用到的章', () => {
    const has = (book: string, chapter: number, source: string) => SITE.sources.some((s) => s.book === book && s.chapter === chapter && s.source === source && /^https?:\/\//.test(s.url));
    for (const n of Object.values(SITE.commentary)) expect(has(n.book, n.chapter, n.source), `${n.id} 的來源`).toBe(true);
    for (const w of Object.values(SITE.step)) {
      const m = /^(.)(\d+):/.exec(w.ref)!;
      const book = { 創: '創世記', 出: '出埃及記', 利: '利未記', 民: '民數記', 申: '申命記' }[m[1] as '出'];
      expect(has(book, Number(m[2]), 'STEP'), `${w.id} 的 STEP 來源`).toBe(true);
    }
  });

  it('每個原文字都有希伯來文、Strong、詞形與說明', () => {
    for (const w of Object.values(SITE.step)) {
      expect(w.hebrew, w.id).toMatch(/[֐-׿]/);
      expect(w.strong, w.id).toMatch(/^H\d+/);
      expect(w.translit.length, w.id).toBeGreaterThan(0);
      expect(w.gloss.length, w.id).toBeGreaterThan(0);
      expect(w.morph.length, w.id).toBeGreaterThan(0);
      expect(w.lexicon.length, w.id).toBeGreaterThan(0);
      expect(w.note.length, w.id).toBeGreaterThan(0);
      expect(w.hebrew, w.id).not.toMatch(/[/\\]/);
    }
  });

  it('條目：章裡列的 entries、nt 都在 entries 表裡，且有類型', () => {
    for (const c of SITE.chapters) {
      for (const t of [...c.entries, ...c.nt]) {
        expect(SITE.entries[t], `${c.id} ${t}`).toBeDefined();
        expect(SITE.entries[t].type.length, t).toBeGreaterThan(0);
        expect(SITE.entries[t].title).toBe(t);
      }
    }
  });

  it('每段文字的 ==…== 最多一處', () => {
    const count = (s: string | undefined) => (s?.match(/==[^=]+?==/g) ?? []).length;
    for (const b of beats) expect(count(b.text), `${b.chapter}/${b.id}`).toBeLessThanOrEqual(1);
    for (const n of Object.values(SITE.commentary)) expect(count(n.paraphrase), n.id).toBeLessThanOrEqual(1);
    for (const w of Object.values(SITE.step)) expect(count(w.note), w.id).toBeLessThanOrEqual(1);
  });

  it('音檔：license 是 CC0、有來源頁；pages（若有）包含 page', () => {
    expect(new Set(SITE.audio.map((a) => a.id)).size).toBe(SITE.audio.length);
    for (const a of SITE.audio) {
      expect(a.license, a.id).toBe('CC0');
      expect(a.page, a.id).toMatch(/^https?:\/\//);
      expect(a.downloaded, a.id).toMatch(/^\d{4}-\d{2}-\d{2}$/);
      if (a.pages) {
        expect(a.pages, a.id).toContain(a.page);
        for (const u of a.pages) expect(u, a.id).toMatch(/^https?:\/\//);
      }
    }
  });
});

describe('links.ts', () => {
  it('條目與章節網址有編碼', () => {
    expect(entryUrl('歷史', '逾越節')).toMatch(/\/link_folder\/%E6%AD%B7%E5%8F%B2\/%E9%80%BE%E8%B6%8A%E7%AF%80$/);
    expect(chapterUrl(2, '出埃及記', 12)).toMatch(/\/02-%E5%87%BA%E5%9F%83%E5%8F%8A%E8%A8%98\/%E7%AC%AC12%E7%AB%A0$/);
  });
});
