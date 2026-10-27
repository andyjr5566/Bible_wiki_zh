// 每一組（最多 3 句）最後一句完整浮現後，到被換掉或開始淡出之前，還能停多久（標準 1×，自動播放的秒數）。
import { readFileSync } from 'node:fs';
import { sentencePlan, verseWeight, GROUP_SIZE, storyLines, stationRhythm, beatRhythm } from '../src/data/story-content.mjs';
const data = JSON.parse(readFileSync(new URL('../src/data/site.json', import.meta.url), 'utf8'));
const st = JSON.parse(readFileSync(new URL('../src/data/stations.json', import.meta.url), 'utf8'));
const stationList = Array.isArray(st) ? st : st.stations;
const PACE = 1.5, REVEAL = 0.8, SPREAD = 0.835, FADE_AT = .86;
const cc = t => [...t.replace(/[，。；：、「」！？\s]/gu, '')].length;
const rows = [];
function unit(label, beat, station) {
  const lines = storyLines(beat, data, station);
  if (!lines.length) return;
  const r = station ? stationRhythm(station, data) : beatRhythm(beat, data);
  const hasNote = Boolean(beat.note);
  const win = station ? (hasNote ? .70 : 1) : ((hasNote ? .70 : .86) - (beat.headline ? .3 : 0));
  const readBase = r.seconds * win;
  const total = lines.reduce((n, l) => n + verseWeight(l.text), 0);
  for (const line of lines) {
    const { parts: sent, weights: w } = sentencePlan(line.text);
    const isEnd = i => i % GROUP_SIZE === GROUP_SIZE - 1 || i === sent.length - 1;
    const C = w.reduce((a, b) => a + b, 0);
    const perVerse = readBase * verseWeight(line.text) / total;
    const starts = []; let cum = 0;
    for (const x of w) { starts.push(.025 + cum / C * SPREAD); cum += x; }
    sent.forEach((t, i) => {
      if (!isEnd(i)) return;
      const end = i === sent.length - 1 ? FADE_AT : starts[i + 1];
      const hold = ((end - starts[i]) * perVerse - REVEAL) / PACE;
      rows.push({ label, v: line.v, i, last: i === sent.length - 1, chars: cc(t), hold, text: t });
    });
  }
}
for (const beat of data.segments.flatMap(s => s.beats)) {
  const list = stationList.filter(s => s.beat === beat.id);
  if (list.length) for (const s of list) unit(`${beat.cue}/${s.id}`, beat, s); else unit(beat.cue, beat, null);
}
rows.sort((a, b) => a.hold - b.hold);
const n = x => rows.filter(r => r.hold < x).length;
console.log(`組尾句 ${rows.length} 句｜完整顯示後停留 <1秒 ${n(1)}、<1.5秒 ${n(1.5)}、<2秒 ${n(2)}｜中位 ${rows[rows.length >> 1].hold.toFixed(1)} 秒`);
for (const r of rows.slice(0, Number(process.argv[2] ?? 8))) console.log(`${r.label.padEnd(26)} v${r.v} 第${r.i + 1}句${r.last ? '(節末)' : '(組末)'} ${String(r.chars).padStart(2)}字 停 ${r.hold.toFixed(2)}s「${r.text}」`);
