import { describe, expect, it } from 'vitest';
import { existsSync, statSync } from 'node:fs';
import { resolve } from 'node:path';
import site from '../data/site.json';
import { musicFor } from './audio';

const beats = site.segments.flatMap(segment => segment.beats.map(beat => ({ segment: segment.id, cue: beat.cue, id: beat.id })));

describe('配樂安排', () => {
  it('每一拍都有曲子，只有第19節整個安靜', () => {
    for (const beat of beats) {
      const music = musicFor(beat.cue, beat.segment);
      expect(music === null, beat.id).toBe(beat.cue === 'cannot');
    }
  });
  it('平靜處用平靜的曲子，史詩處用高亢的，第四幕用合唱', () => {
    const pick = (id: string) => { const b = beats.find(x => x.id === id)!; return musicFor(b.cue, b.segment); };
    expect(pick('beat-02-gather')).toBe('ruins');
    expect(pick('beat-06-beyond-river')).toBe('plains');
    expect(pick('beat-08-egypt')).toBe('laments');
    expect(pick('beat-09-east')).toBe('laments');
    expect(pick('beat-10-jericho')).toBe('laments');
    expect(pick('beat-12-family-2')).toBe('plains');
    expect(pick('beat-13-now')).toBe('plains');
    expect(pick('beat-17-answer-1')).toBe('choir');
    expect(pick('beat-23-family-4')).toBe('ruins');
    expect(pick('beat-26-raise')).toBe('ruins');
    expect(pick('beat-30-joshua-dies')).toBe('hope');
    expect(pick('beat-36-epilogue-stone')).toBe('hope');
  });
  it('五首成品都在，每首不超過 1.5 MB', () => {
    for (const name of ['ruins', 'plains', 'laments', 'hope', 'choir']) {
      const file = resolve('src/assets/music', `${name}.mp3`);
      expect(existsSync(file), name).toBe(true);
      expect(statSync(file).size, name).toBeLessThan(1_500_000);
    }
  });
});
