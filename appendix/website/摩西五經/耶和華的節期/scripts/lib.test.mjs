// lib.mjs 的純函式測試（不碰 vault）：經文參照、manifest 表格、STEP 表格、第一句。
import { describe, expect, it } from 'vitest';
import { firstSentence, parseChapterRef, parseManifest, parseRef, parseStepFile } from './lib.mjs';

describe('經文參照解析', () => {
  it('單節與節範圍', () => {
    expect(parseRef('出12:22')).toEqual({ abbr: '出', book: '出埃及記', chapter: 12, from: 22, to: 22 });
    expect(parseRef('出12:21-28')).toEqual({ abbr: '出', book: '出埃及記', chapter: 12, from: 21, to: 28 });
    expect(parseRef('利23:5')?.book).toBe('利未記');
    expect(parseRef('申16:1-7')?.book).toBe('申命記');
    expect(parseRef('民28:16')?.book).toBe('民數記');
    expect(parseRef('創1:1')?.book).toBe('創世記');
  });
  it('格式不對、倒過來的範圍、不是五經都回 null', () => {
    for (const bad of ['', '出12', '出12:', '出12:28-21', '出12:0', '詩1:2', '出十二22', '出12：22', '出12:1–5', undefined, null]) {
      expect(parseRef(bad), String(bad)).toBeNull();
    }
  });
  it('章參照', () => {
    expect(parseChapterRef('出12')).toEqual({ abbr: '出', book: '出埃及記', chapter: 12 });
    expect(parseChapterRef('出12:1')).toBeNull();
    expect(parseChapterRef('詩1')).toBeNull();
  });
});

describe('source_manifest 解析', () => {
  const md = [
    '| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |',
    '|------|------|-----|---------------|------|',
    '| ccbiblestudy CT | 逐節註解 | https://www.ccbiblestudy.org/Old%20Testament/02Exo/02CT12.htm | raw_data/ccbiblestudy_CT_exodus_12.txt | OK |',
    '| KingComments | 研經註解 | https://www.kingcomments.com/en/bible-studies/Exo/12 | raw_data/kingcomments_exodus_12.txt | OK |',
  ].join('\n');
  it('依表頭取欄位，略過分隔列', () => {
    const rows = parseManifest(md);
    expect(rows).toHaveLength(2);
    expect(rows[0]).toEqual({
      source: 'ccbiblestudy CT',
      type: '逐節註解',
      url: 'https://www.ccbiblestudy.org/Old%20Testament/02Exo/02CT12.htm',
      raw: 'raw_data/ccbiblestudy_CT_exodus_12.txt',
      status: 'OK',
    });
    expect(rows[1].source).toBe('KingComments');
  });
});

describe('STEP 表格解析', () => {
  // 取自 stepbible_exodus_13.txt 的 13:4（原文欄有 / 詞素分隔與 \ 跳脫）
  const text = [
    '# STEP Bible — Exodus 13',
    '',
    '## Exodus 13:4',
    '',
    '**Original:** הַיּ֖וֹם אַתֶּ֣ם יֹצְאִ֑ים בְּחֹ֖דֶשׁ הָאָבִֽיב׃',
    '',
    '| # | 原文 | Transliteration | Context gloss | Strong | Morphology | Brief lexicon |',
    '|---:|---|---|---|---|---|---|',
    '| 4 | בְּ/חֹ֖דֶשׁ | be./Cho.desh | in/ [the] month of | H2320G | HR/Ncmsc — Preposition + Noun (Singular Masculine, Construct) | חֹ֫דֶשׁ (cho.desh): month |',
    '| 5 | הָ/אָבִֽיב\\׃ | ha./\'a.Viv | <the>/ Abib | H24 | HTd/Ntbsa — Definite article (Hebrew) + Noun (Title, Singular Either gender, Absolute) | אָבִיב (a.viv): Abib |',
    '',
    '## Exodus 13:5',
    '',
    '**Original:** וְהָיָ֣ה',
    '',
    '| # | 原文 | Transliteration | Context gloss | Strong | Morphology | Brief lexicon |',
    '|---:|---|---|---|---|---|---|',
    '| 1 | וְ/הָיָ֣ה | ve./ha.Yah | and/ it will be | H1961 | Hc/Vqq3ms — Consecutive Conjunction + Verb | הָיָה (ha.yah): to be |',
  ].join('\n');

  it('每節一個區塊，抓出 Original 行與表格列', () => {
    const map = parseStepFile(text);
    expect([...map.keys()]).toEqual(['13:4', '13:5']);
    const sec = map.get('13:4');
    expect(sec.en).toBe('Exodus');
    expect(sec.original).toBe('הַיּ֖וֹם אַתֶּ֣ם יֹצְאִ֑ים בְּחֹ֖דֶשׁ הָאָבִֽיב׃');
    expect(sec.rows.map((r) => r.n)).toEqual([4, 5]);
    expect(sec.rows[1]).toMatchObject({ strong: 'H24', glossRaw: '<the>/ Abib', hebrewRaw: 'הָ/אָבִֽיב\\׃' });
  });
  it('欄數不對的列不收', () => {
    const map = parseStepFile('## Exodus 1:1\n\n| 1 | a | b | c |\n');
    expect(map.get('1:1').rows).toHaveLength(0);
  });
});

describe('條目簡介的第一句', () => {
  it('引號與括號裡的句號不算句尾', () => {
    expect(firstSentence('出12:2「你們要以本月為正月，為一年之首。」CT 說明位置。後面不要。')).toBe('出12:2「你們要以本月為正月，為一年之首。」CT 說明位置。');
    expect(firstSentence('這是第一句。這是第二句。')).toBe('這是第一句。');
    expect(firstSentence('沒有句號的一段')).toBe('沒有句號的一段');
  });
});
