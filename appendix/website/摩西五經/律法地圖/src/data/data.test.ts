import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import { buildAll, lintPlain, renderOutputs } from '../../scripts/build-data.mjs';
import { extractRefs, IN_VAULT, ROOT, GIST_MAX } from '../../scripts/lib.mjs';
import data from './explorer.json';
import type { Explorer } from './types';
import { chapterUrl, entryUrl, WIKI_BASE } from './links';

const DB = data as unknown as Explorer;

describe('資料閘門（要在 vault 裡跑）', () => {
  const result = IN_VAULT ? buildAll() : null;

  it.skipIf(!IN_VAULT)('手寫資料沒有錯誤：經文範圍、依據節、子題、白話說明 lint、條目、關聯證據', () => {
    expect(result!.errors).toEqual([]);
  });

  it.skipIf(!IN_VAULT)('explorer.json 是最新的（改了 data/*.yaml 或 vault 之後要跑 npm run data）', () => {
    for (const [p, s] of Object.entries(renderOutputs(result!) as Record<string, string>)) {
      expect(existsSync(p), p).toBe(true);
      expect(readFileSync(p, 'utf8'), p).toBe(s);
    }
  });

  it.skipIf(!IN_VAULT)('經文逐字取自 raw_scripture', () => {
    for (const [key, text] of Object.entries(DB.verses)) {
      const m = /^(.)(\d+):(\d+)$/.exec(key)!;
      const book = DB.books.find((b) => b.abbr === m[1])!.name;
      const lines = readFileSync(resolve(ROOT, 'raw_scripture', book, `第${m[2]}章.txt`), 'utf8').replace(/^﻿/, '').split(/\r?\n/).filter(Boolean);
      expect(lines[Number(m[3]) - 1], key).toBe(text);
    }
  });

  it.skipIf(!IN_VAULT)('每個條目連結都對應 link_folder 裡真的存在的檔案', () => {
    for (const [title, info] of Object.entries(DB.entries)) {
      expect(existsSync(resolve(ROOT, 'link_folder', info.type, `${title}.md`)), title).toBe(true);
    }
  });
});

describe('不重工：知識庫內容只留名稱＋一句話＋連結', () => {
  it('條目簡介不超過 40 字', () => {
    for (const [title, info] of Object.entries(DB.entries)) expect([...info.gist].length, title).toBeLessThanOrEqual(GIST_MAX);
  });
  it('條目簡介不含原文字母與 Strong 編號', () => {
    for (const [title, info] of Object.entries(DB.entries)) expect(info.gist, title).not.toMatch(/[֐-׿]|\bH\d{3,}/);
  });
  it('連結是公開的網頁網址，不是 obsidian://', () => {
    const u = entryUrl('互文', '申15：12-18');
    expect(u.startsWith(WIKI_BASE)).toBe(true);
    expect(u).not.toMatch(/obsidian/i);
    expect(decodeURIComponent(u).endsWith('/link_folder/互文/申15：12-18')).toBe(true);
    expect(decodeURIComponent(chapterUrl(5, '申命記', 15)).endsWith('/05-申命記/第15章')).toBe(true);
  });
});

describe('結構', () => {
  it('每條律法都有段落、子題與白話說明', () => {
    const sections = new Set(DB.sections.map((s) => s.id));
    const topics = new Set(DB.topics.map((t) => t.id));
    for (const l of DB.laws) {
      expect(sections.has(l.section), l.id).toBe(true);
      expect(l.topics.length, l.id).toBeGreaterThan(0);
      for (const t of l.topics) expect(topics.has(t), `${l.id} ${t}`).toBe(true);
      expect(lintPlain(l.summary), l.id).toEqual([]);
    }
  });
  it('關聯兩端都存在，且都有證據', () => {
    const ids = new Set(DB.laws.map((l) => l.id));
    for (const r of DB.relations) {
      expect(ids.has(r.from) && ids.has(r.to)).toBe(true);
      expect(r.evidence.quote.length).toBeGreaterThan(0);
    }
  });
  it('經文片語位置落在經文範圍內', () => {
    for (const [key, links] of Object.entries(DB.links)) {
      const text = DB.verses[key];
      for (const k of links) expect(k.e <= text.length && k.s >= 0 && k.s < k.e, key).toBe(true);
    }
  });
});

describe('經文參照解析（證據引句用）', () => {
  it('各種寫法', () => {
    expect(extractRefs('申命記15章補充了出21:2-6的希伯來奴僕')).toEqual([
      { book: '申命記', chapter: 15, from: 1, to: Infinity },
      { book: '出埃及記', chapter: 21, from: 2, to: 6 },
    ]);
    expect(extractRefs('出二十11以神的創造為基礎')).toEqual([{ book: '出埃及記', chapter: 20, from: 11, to: 11 }]);
    expect(extractRefs('《出埃及記》二十一2～6同一條例')).toEqual([{ book: '出埃及記', chapter: 21, from: 2, to: 6 }]);
    expect(extractRefs('利25：39-43')).toEqual([{ book: '利未記', chapter: 25, from: 39, to: 43 }]);
  });
  it('一般文字不會被當成參照', () => {
    expect(extractRefs('他們出去歸回本家，利益歸主人')).toEqual([]);
  });
});
