// build-data.mjs 的測試：輸出決定性；在 vault 裡再跑一次完整建置，確認沒有錯誤、兩次結果一致；
// 另外把 data/*.yaml 複製一份故意弄壞，確認每一種錯誤都會指出是哪一筆、哪個欄位。
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import YAML from 'yaml';
import { afterAll, describe, expect, it } from 'vitest';
import { buildAll, renderOutput, stableStringify } from './build-data.mjs';
import { IN_VAULT, SITE_DIR } from './lib.mjs';

describe('stableStringify', () => {
  it('key 排序固定，和輸入順序無關', () => {
    expect(stableStringify({ b: 1, a: { d: [{ z: 1, y: 2 }], c: 3 } })).toBe(stableStringify({ a: { c: 3, d: [{ y: 2, z: 1 }] }, b: 1 }));
  });
  it('陣列順序保留、結尾有換行、undefined 不輸出', () => {
    const s = stableStringify({ a: [3, 1, 2], u: undefined });
    expect(JSON.parse(s)).toEqual({ a: [3, 1, 2] });
    expect(s.endsWith('\n')).toBe(true);
    expect(s).not.toContain('"u"');
  });
});

describe.skipIf(!IN_VAULT)('完整建置（需要 vault）', () => {
  it('沒有錯誤，兩次結果完全一致（不含時間戳）', () => {
    const a = buildAll();
    expect(a.errors).toEqual([]);
    const b = buildAll();
    expect(renderOutput(a.data)).toBe(renderOutput(b.data));
  });
});

describe.skipIf(!IN_VAULT)('故意弄壞資料：錯誤要指出哪一筆、哪個欄位', () => {
  const tmp = mkdtempSync(join(tmpdir(), 'jf-data-'));
  afterAll(() => rmSync(tmp, { recursive: true, force: true }));

  /** 複製 data/ 到暫存資料夾，讓 mutate 改 yaml 物件，再建置 */
  function broken(mutate, { audio } = {}) {
    const dir = mkdtempSync(join(tmp, 'case-'));
    const dataDir = join(dir, 'data');
    mkdirSync(dataDir);
    const docs = {};
    for (const name of ['feasts', 'story', 'commentary', 'step', 'audio-sources']) {
      docs[name] = YAML.parse(readFileSync(resolve(SITE_DIR, 'data', `${name}.yaml`), 'utf8'));
    }
    mutate(docs);
    for (const [name, doc] of Object.entries(docs)) writeFileSync(join(dataDir, `${name}.yaml`), YAML.stringify(doc), 'utf8');
    const audioDir = join(dir, 'audio');
    mkdirSync(audioDir);
    for (const f of audio ?? []) writeFileSync(join(audioDir, f), 'x');
    return buildAll({ dataDir, audioDir }).errors;
  }
  const note = (docs, id) => docs.commentary.passover.find((n) => n.id === id);
  const hit = (errors, ...parts) => errors.some((e) => parts.every((p) => e.includes(p)));
  const allAudio = () => YAML.parse(readFileSync(resolve(SITE_DIR, 'data/audio-sources.yaml'), 'utf8')).map((a) => a.file);

  it('引文對不上 raw', () => {
    const errors = broken((d) => { note(d, 'ct-abib').quote += '（多出來的字）'; }, { audio: allAudio() });
    expect(hit(errors, 'commentary.yaml passover[ct-abib].quote', '找不到逐字原文')).toBe(true);
  });
  it('GT 歸屬寫錯', () => {
    const errors = broken((d) => { note(d, 'gt-bg-abib').work = '《丁道爾聖經註釋》'; }, { audio: allAudio() });
    expect(hit(errors, 'passover[gt-bg-abib].quote', '歸屬不符')).toBe(true);
  });
  it('KC 有 quote 沒有 quoteZh', () => {
    const errors = broken((d) => { delete note(d, 'kc-abib').quoteZh; }, { audio: allAudio() });
    expect(hit(errors, 'passover[kc-abib].quoteZh')).toBe(true);
  });
  it('quote 與 paraphrase 都沒有', () => {
    const errors = broken((d) => { delete note(d, 'ct-abib').quote; delete note(d, 'ct-abib').paraphrase; }, { audio: allAudio() });
    expect(hit(errors, 'passover[ct-abib]', '至少要有 quote 或 paraphrase')).toBe(true);
  });
  it('STEP 的 Strong 不一致', () => {
    const errors = broken((d) => { d.step.find((s) => s.id === 'abib').expect_strong = 'H25'; }, { audio: allAudio() });
    expect(hit(errors, 'step.yaml [abib]', 'H24', 'expect_strong')).toBe(true);
  });
  it('經文參照對不到 raw_scripture', () => {
    const errors = broken((d) => { d.feasts.chapters[1].passages.push('出12:99'); d.story.passover[0].verse = '出99:1'; }, { audio: allAudio() });
    expect(hit(errors, 'passages[', '出12:99', '超出')).toBe(true);
    expect(hit(errors, 'story.yaml passover[blood].verse', '出99')).toBe(true);
  });
  it('條目不存在', () => {
    const errors = broken((d) => { d.feasts.chapters[1].entries.push('不存在的條目'); }, { audio: allAudio() });
    expect(hit(errors, 'feasts.yaml chapters[passover].entries[', '不存在的條目')).toBe(true);
  });
  it('story 引用不存在的註釋與原文字、==高亮== 兩處', () => {
    const errors = broken((d) => {
      d.story.passover[0].notes = ['no-such-note'];
      d.story.passover[0].words = ['no-such-word'];
      d.story.passover[0].text = '==甲==和==乙==';
    }, { audio: allAudio() });
    expect(hit(errors, 'story.yaml passover[blood].notes', 'no-such-note')).toBe(true);
    expect(hit(errors, 'story.yaml passover[blood].words', 'no-such-word')).toBe(true);
    expect(hit(errors, 'story.yaml passover[blood].text', '最多一處')).toBe(true);
  });
  it('音檔：沒有授權紀錄、檔案不存在、授權不是 CC0、pages 不含 page', () => {
    const errors = broken((d) => {
      d['audio-sources'][0].license = 'CC-BY';
      d['audio-sources'][1].pages = ['https://example.org/x'];
    }, { audio: ['night-wind.mp3', 'lamb.mp3', 'stray.mp3'] });
    expect(hit(errors, 'public/audio/stray.mp3', '沒有授權紀錄')).toBe(true);
    expect(hit(errors, 'audio-sources.yaml [dip].file', 'dip.mp3')).toBe(true);
    expect(hit(errors, 'audio-sources.yaml [night-wind]', 'CC0')).toBe(true);
    expect(hit(errors, 'audio-sources.yaml [lamb]', '包含 page')).toBe(true);
  });
});
