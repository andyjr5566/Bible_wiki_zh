// build-data.mjs 的測試：輸出決定性；在 vault 裡再跑一次完整建置，確認沒有錯誤、兩次結果一致；
// 另外把 data/*.yaml 複製一份故意弄壞，確認每一種錯誤都會指出是哪一筆、哪個欄位。
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import YAML from 'yaml';
import { afterAll, describe, expect, it } from 'vitest';
import { buildAll, renderOutput, stableStringify } from './build-data.mjs';
import { parseOfferings } from './checks.mjs';
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

const flat = (g) => g.items.map((i) => `${i.animal}${i.count}${i.role}`);

describe.skipIf(!IN_VAULT)('獻祭數字（檢查 #5）：parser 算出的結果要等於主筆讀經文得出的期望值', () => {
  const { data } = buildAll();
  const expected = {
    '民28:11-15': ['公牛犢2燔祭', '公綿羊1燔祭', '公羊羔7燔祭', '公山羊1贖罪祭'],
    '民28:19-22': ['公牛犢2燔祭', '公綿羊1燔祭', '公羊羔7燔祭', '公山羊1贖罪祭'],
    '民28:27-30': ['公牛犢2燔祭', '公綿羊1燔祭', '公羊羔7燔祭', '公山羊1贖罪'],
    '利23:18-19': ['羊羔7燔祭', '公牛犢1燔祭', '公綿羊2燔祭', '公山羊1贖罪祭', '公綿羊羔2平安祭'],
  };
  for (const [ref, want] of Object.entries(expected)) {
    it(ref, () => {
      expect(data.offerings[ref]?.ref).toBe(ref);
      expect(flat(data.offerings[ref])).toEqual(want);
    });
  }
  it('story.yaml 用到的獻祭出處都有解析結果，沒有多餘的', () => {
    const used = new Set(data.chapters.flatMap((c) => c.beats.flatMap((b) => b.offerings ?? [])));
    expect([...used].sort()).toEqual(Object.keys(data.offerings).sort());
  });
});

describe('獻祭 parser 反例：有一個「隻」沒被解析就要失敗', () => {
  it('多一隻鴿子（不在動物詞表）', () => {
    const r = parseOfferings(['又要將一隻公山羊為贖罪祭，三隻斑鳩為燔祭。']);
    expect(r.errors.length).toBe(1);
    expect(r.errors[0]).toContain('三隻斑鳩為燔祭');
  });
  it('數字不是一到十（十二隻）', () => {
    expect(parseOfferings(['要獻十二隻公牛犢為燔祭。']).errors.length).toBe(1);
  });
  it('份量句裡的「隻」不算祭牲，也不報錯', () => {
    const r = parseOfferings(['要獻兩隻公牛犢為燔祭。', '為那七隻羊羔，每隻要獻伊法十分之一。']);
    expect(r.errors).toEqual([]);
    expect(flat(r)).toEqual(['公牛犢2燔祭']);
  });
  it('沒有任何祭牲也算失敗', () => {
    expect(parseOfferings(['要獻調油的細麵。']).errors.length).toBe(1);
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
  it('beat 欄位：interaction、day、dayTo、badge、offerings', () => {
    const errors = broken((d) => {
      const [a, b, c, e] = d.story.unleavened;
      a.interaction = 'jump';
      b.day = 31;
      c.day = 15; c.dayTo = 15;
      e.badge = '';
      d.story.passover[0].dayTo = 20;
      d.story.passover[1].offerings = ['出12:99'];
      d.story.passover[2].offerings = ['出12:21-28'];
    }, { audio: allAudio() });
    expect(hit(errors, 'unleavened[bake].interaction', 'hyssop/bake/wave/count')).toBe(true);
    expect(hit(errors, 'unleavened[seven-days].day', '1–30')).toBe(true);
    expect(hit(errors, 'unleavened[no-leaven].dayTo', '大於 day')).toBe(true);
    expect(hit(errors, 'unleavened[remember].badge')).toBe(true);
    expect(hit(errors, 'passover[blood].dayTo', '一定要有 day')).toBe(true);
    expect(hit(errors, 'passover[hyssop].offerings[0]', '超出')).toBe(true);
    expect(hit(errors, 'passover[door].offerings[0]', '沒有解析出任何祭牲')).toBe(true);
  });
  it('offeringsLabel：沒有 offerings、太長、空字串', () => {
    const errors = broken((d) => {
      d.story.passover[0].offeringsLabel = '每日';
      d.story.passover[1].offerings = ['民28:19-22'];
      d.story.passover[1].offeringsLabel = '這個標籤實在是太長太長太長了';
      d.story.passover[2].offerings = ['民28:19-22'];
      d.story.passover[2].offeringsLabel = '';
    }, { audio: allAudio() });
    expect(hit(errors, 'passover[blood].offeringsLabel', '一定要有 offerings')).toBe(true);
    expect(hit(errors, 'passover[hyssop].offeringsLabel', '超過 12 字')).toBe(true);
    expect(hit(errors, 'passover[door].offeringsLabel', '非空字串')).toBe(true);
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
