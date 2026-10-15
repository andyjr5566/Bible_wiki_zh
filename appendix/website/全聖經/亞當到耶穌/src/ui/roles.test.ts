import { describe, expect, it } from 'vitest';
import rolesJson from '../data/roles.json';
import type { RoleBox, RolesData } from '../data/types';
import { pathSegments, roleSealRows, roleSealWidth, sealRectsOverlap, segmentHitsRect } from './ink';
import {
  MINI_H, MINI_W, buildRolesIndex, cellKey, chineseNumber, groupLayout, miniLayout, monthLabel, parseRef, pidOf, polar,
  refInRange, refText, roleTarget, sectorPath,
} from './roles';

const roles = rolesJson as unknown as RolesData;

describe('出處', () => {
  it('讀出書卷、章、起訖節', () => {
    expect(parseRef('代上12:1-7')).toEqual({ book: '代上', ch: 12, v1: 1, v2: 7 });
    expect(parseRef('撒下8:16')).toEqual({ book: '撒下', ch: 8, v1: 16, v2: 16 });
    expect(parseRef('代上27:32–34')).toEqual({ book: '代上', ch: 27, v1: 32, v2: 34 });
    expect(parseRef('沒有章節')).toBeNull();
  });
  it('一節落在一段範圍裡才算', () => {
    expect(refInRange('代上12:24', '代上12:23-40')).toBe(true);
    expect(refInRange('代上12:22', '代上12:23-40')).toBe(false);
    expect(refInRange('代上12:24', '代上13:23-40')).toBe(false);
    expect(refInRange('代上12:24', '撒下12:23-40')).toBe(false);
  });
  it('出處在畫面上用頓號', () => {
    expect(refText('代上18:15, 撒下8:16, 撒下20:23')).toBe('代上18:15、撒下8:16、撒下20:23');
    expect(refText('代上11:10-19')).toBe('代上11:10-19');
  });
});

describe('數字與月份', () => {
  it('中文數字', () => {
    expect([1, 7, 10, 11, 12, 20, 24].map(chineseNumber)).toEqual(['一', '七', '十', '十一', '十二', '二十', '二十四']);
  });
  it('十二個月', () => {
    expect([1, 2, 3, 10, 11, 12].map(monthLabel)).toEqual(['正月', '二月', '三月', '十月', '十一月', '十二月']);
  });
});

describe('環與輪盤的幾何', () => {
  it('角度從正上方起算、順時針', () => {
    expect(polar(100, 100, 50, 0)).toEqual({ x: 100, y: 50 });
    expect(polar(100, 100, 50, 90)).toEqual({ x: 150, y: 100 });
    expect(polar(100, 100, 50, 180)).toEqual({ x: 100, y: 150 });
    expect(polar(100, 100, 50, 270)).toEqual({ x: 50, y: 100 });
  });
  it('一格是外弧、內弧夾起來的封閉形狀', () => {
    const d = sectorPath(100, 100, 40, 80, 0, 90);
    expect(d).toBe('M100 20A80 80 0 0 1 180 100L140 100A40 40 0 0 0 100 60Z');
  });
  it('超過半圈要用大弧', () => {
    expect(sectorPath(0, 0, 10, 20, 0, 200)).toContain('0 1 1');
  });
});

describe('歸回連結指到的格子', () => {
  it('切出方塊 id 和成員 key（key 裡的冒號保留）', () => {
    expect(roleTarget('role:priests:耶大雅#第二班')).toEqual({ box: 'priests', key: '耶大雅#第二班' });
    expect(roleTarget('role:a:b:c')).toEqual({ box: 'a', key: 'b:c' });
    expect(roleTarget('約押')).toBeNull();
    expect(roleTarget('role:only')).toBeNull();
  });
});

describe('職位資料', () => {
  const index = buildRolesIndex(roles);
  it('四類、方塊都在', () => {
    expect(roles.categories.map((category) => category.id)).toEqual(['court', 'army', 'temple', 'tribes']);
    expect(index.boxes.size).toBeGreaterThan(20);
  });
  it('二十四班的環有二十四格、十二月輪盤有十二個月', () => {
    for (const { box } of index.boxes.values()) {
      if (box.kind === 'ring24') expect(new Set(box.members.map((member) => member.order))).toEqual(new Set(Array.from({ length: 24 }, (_, i) => i + 1)));
      if (box.kind === 'wheel12') expect(new Set(box.members.map((member) => member.order))).toEqual(new Set(Array.from({ length: 12 }, (_, i) => i + 1)));
    }
  });
  it('一人多職：比拿雅（耶何耶大的兒子）在護衛長、勇士首領、三月班長', () => {
    const places = index.byPid.get('比拿雅#耶何耶大之子') ?? [];
    expect(places.map((place) => place.box.id)).toEqual(['guards', 'chiefs', 'monthly']);
  });
  it('每個成員的格子都找得到，key 在方塊內不重複', () => {
    for (const { box } of index.boxes.values()) {
      const keys = box.members.map((member) => member.key);
      expect(new Set(keys).size).toBe(keys.length);
      for (const member of box.members) expect(index.byCell.get(cellKey(box.id, member.key))?.member).toBe(member);
    }
  });
  it('樹上有的人用 id，只在職位圖上的人用 rid', () => {
    const joab = index.byPid.get('約押');
    expect(joab?.[0]?.member.id).toBe('約押');
    expect(pidOf({ key: 'k', rid: 'r', name: 'n', ref: '' })).toBe('r');
    expect(pidOf({ key: 'k', id: 'i', name: 'n', ref: '' })).toBe('i');
  });
  it('投奔大衛的人：人數落在各自那一組，沒有掉在外面的', () => {
    const ziklag = index.boxes.get('ziklag')!.box;
    const { groups, rest } = groupLayout(ziklag);
    expect(rest).toEqual([]);
    expect(groups.reduce((sum, group) => sum + group.figures.length, 0)).toBe(ziklag.figures!.length);
    // 每一組的成員都找得到
    expect(groups.reduce((sum, group) => sum + group.members.length, 0)).toBe(ziklag.groups!.reduce((sum, group) => sum + group.keys.length, 0));
    // 人數照字串原樣
    const last = groups.at(-1)!;
    expect(last.figures.find((figure) => figure.label === '猶大支派')?.count).toBe('六千八百人');
  });
  it('沒有對到任何一組的人數放在最後', () => {
    const box: RoleBox = {
      id: 'x', title: 'x', ref: '', kind: 'groups', seal: 'x', members: [],
      groups: [{ title: 'a', ref: '代上12:1-7', keys: [] }],
      figures: [{ label: '甲', count: '一人', ref: '代上12:3' }, { label: '乙', count: '二人', ref: '代上12:30' }],
    };
    const { groups, rest } = groupLayout(box);
    expect(groups[0]!.figures.map((figure) => figure.label)).toEqual(['甲']);
    expect(rest.map((figure) => figure.label)).toEqual(['乙']);
  });
});

describe('讀經的小縮影', () => {
  const layout = miniLayout(roles);
  it('每個方塊都有位置，且都在縮影範圍內', () => {
    const all = roles.categories.flatMap((category) => category.boxes);
    expect(layout.boxes.size).toBe(all.length);
    for (const rect of layout.boxes.values()) {
      expect(rect.x).toBeGreaterThanOrEqual(0);
      expect(rect.y).toBeGreaterThan(layout.plaque.y + layout.plaque.h);
      expect(rect.x + rect.w).toBeLessThanOrEqual(MINI_W);
      expect(rect.y + rect.h).toBeLessThanOrEqual(MINI_H);
    }
  });
  it('同一欄的方塊由上往下排，不重疊', () => {
    for (const category of roles.categories) {
      const rects = category.boxes.map((box) => layout.boxes.get(box.id)!);
      for (let i = 1; i < rects.length; i += 1) expect(rects[i]!.y).toBeGreaterThanOrEqual(rects[i - 1]!.y + rects[i - 1]!.h);
    }
  });
  it('四欄由左往右', () => {
    const firsts = roles.categories.map((category) => layout.boxes.get(category.boxes[0]!.id)!.x);
    expect([...firsts].sort((a, b) => a - b)).toEqual(firsts);
  });
});

describe('職位印的幾何（家譜樹）', () => {
  it('寬度隨字數', () => {
    expect(roleSealWidth('元帥')).toBe(34);
    expect(roleSealWidth('第三班')).toBe(46);
  });
  it('一行放不下就換行', () => {
    const one = roleSealRows(['元帥'], 120);
    expect(one.items).toEqual([{ label: '元帥', x: 0, y: 0, w: 34 }]);
    expect(one.height).toBe(17);
    const many = roleSealRows(['祭司長', '族長', '獻祭', '祭司'], 100);
    expect(many.items.some((item) => item.y > 0)).toBe(true);
    expect(many.width).toBeLessThanOrEqual(100);
    expect(roleSealRows([], 100)).toEqual({ items: [], width: 0, height: 0 });
  });
  it('把連線路徑拆成線段', () => {
    expect(pathSegments('M10 20 H30 V40 H50')).toEqual([[10, 20, 30, 20], [30, 20, 30, 40], [30, 40, 50, 40]]);
    expect(pathSegments('M0 0 L10 10')).toEqual([[0, 0, 10, 10]]);
    expect(pathSegments('M5 5 V25')).toEqual([[5, 5, 5, 25]]);
  });
  it('矩形重疊與線段穿過矩形', () => {
    const a = { l: 0, t: 0, r: 10, b: 10 };
    expect(sealRectsOverlap(a, { l: 5, t: 5, r: 15, b: 15 })).toBe(true);
    expect(sealRectsOverlap(a, { l: 11, t: 0, r: 20, b: 10 })).toBe(false);
    expect(sealRectsOverlap(a, { l: 11, t: 0, r: 20, b: 10 }, 2)).toBe(true);
    expect(segmentHitsRect([-5, 5, 15, 5], a)).toBe(true);
    expect(segmentHitsRect([5, 20, 5, 30], a)).toBe(false);
    expect(segmentHitsRect([5, 12, 5, 30], a, 3)).toBe(true);
    expect(segmentHitsRect([-5, -5, 15, 15], a)).toBe(true);
    expect(segmentHitsRect([20, 0, 30, 10], a)).toBe(false);
  });
});
