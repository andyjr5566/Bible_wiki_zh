// 兩片田：初熟的大麥田（BX）與七七節的小麥田（WX）。
import { type BufferGeometry, Color, DoubleSide, Group, InstancedMesh, Mesh, ShaderMaterial, Vector3 } from 'three';
import { SITE } from '../data/site';
import { story } from '../story/state';
import { barleyGeo, cattleGeo, lambGeo, personGeo, personHand } from './geo';
import { clothGeo, fieldGeo, griddleGeo, loafGeo, rockGeo, sheafGeo, sickleGeo, flatBreadGeo } from './geo2';
import { litMat, solid, solidInstanced } from './materials';
import { BX, WX, c } from './tracks';
import { type FrameLite, hillMesh, robeMat, setInst } from './props';
import { clamp, hexTo, lerp, mulberry32, smooth } from './util';

/** 田地起伏：靠近鏡頭（z≥-2）平坦，越遠越有起伏 */
export function hf(x: number, z: number): number {
  const amp = smooth(-2, -30, z);
  const far = smooth(-45, -160, z) * 9;
  return amp * (1.5 * Math.sin(x * 0.045 + 1.3) * Math.cos(z * 0.06) + 0.95 * Math.sin(z * 0.1 - x * 0.03 + 2) + 0.5 * Math.sin(x * 0.13 + z * 0.09)) + far;
}

const _c1 = new Vector3();
const _c2 = new Vector3();
function mix3(out: Vector3, a: string, b: string, t: number): Vector3 {
  hexTo(a, _c1);
  hexTo(b, _c2);
  return out.lerpVectors(_c1, _c2, clamp(t));
}

/** 供應量的名稱 → 剪影種類 */
function animalKind(name: string): { kind: 'bull' | 'ram' | 'goat' | 'lamb'; sc: number } {
  if (name.includes('牛')) return { kind: 'bull', sc: 0.78 };
  if (name.includes('山羊')) return { kind: 'goat', sc: 1.05 };
  if (name.includes('綿羊羔')) return { kind: 'lamb', sc: 1.12 };
  if (name.includes('羔')) return { kind: 'lamb', sc: 1.0 };
  return { kind: 'ram', sc: 1.2 };
}

export class Fields {
  barley = new Group();
  wheat = new Group();
  private wheatMat!: ShaderMaterial;
  private wheatGround!: ShaderMaterial;
  private cutSheaves = new Group();
  private reaper!: Group;
  private gleaner!: Group;

  constructor() {
    this.buildBarley();
    this.buildWheat();
    this.barley.visible = false;
    this.wheat.visible = false;
  }

  // ---------------------------------------------------------------- 大麥田
  private buildBarley(): void {
    const g = this.barley;
    g.position.set(BX, 0, 0);
    const rnd = mulberry32(91);
    // 地面
    const mGround = litMat({ base: '#c7a65e', line: '#6a4f22', angle: 84, angle2: 80, space: 5, seed: 81, cross: true });
    const ground = new Mesh(fieldGeo(600, 560, 72, hf, 50, -250), mGround);
    ground.position.y = 0.03;
    g.add(ground);
    const mHill = litMat({ base: '#b9985a', line: '#5d4623', angle: 4, space: 5, seed: 6, bias: -0.2 });
    g.add(hillMesh(mHill, -70, -190, 110, 12, 50), hillMesh(mHill, 90, -210, 140, 16, 60), hillMesh(mHill, 10, -280, 190, 11, 50));

    // 大麥：成熟（土黃），風浪由禾捆搖動帶起
    const bg = barleyGeo({ stem: 1.8, earW: 0.034 });
    const bm = litMat({ base: '#c6a96c', parts: ['#b99d5a', '#dab95f'], partAlt: '#8e7640', angle: 80, space: 5, wind: true, gust: true, seed: 9, bias: 0.22 });
    const total = 7000;
    const barley = new InstancedMesh(bg, bm, total);
    barley.frustumCulled = false;
    const col = new Color();
    let n = 0;
    while (n < total) {
      const x = -16 + rnd() * 56;
      const z = 3.5 - Math.pow(rnd(), 1.7) * 47;
      if (z > -0.9 && x > 1.5) continue; // 田邊的小路：祭司、羊羔、禾捆堆都站在這裡
      const inCut = x > -0.5 && x < 3.8 && z > -3.6 && z < 2;
      if (z > 3.2) continue;
      const h = inCut ? 0.12 : 0.78 + rnd() * 0.26;
      setInst(barley, n, x, hf(x, z), z, rnd() * Math.PI * 2, 1.1 + rnd() * 0.6, h, (rnd() - 0.5) * 0.12, (rnd() - 0.5) * 0.12);
      col.setRGB(rnd(), 0, 0);
      barley.setColorAt(n, col);
      n++;
    }
    g.add(barley);

    // 禾捆與割麥的人
    const mSheaf = litMat({ base: '#c6a35a', parts: ['#b79a55', '#d9b861', '#6a4a26'], angle: 70, space: 4, seed: 71 });
    const sg = sheafGeo(3);
    const sheaf1 = solid(sg, mSheaf, 1.6);
    sheaf1.position.set(1.7, 0, 0.9);
    sheaf1.rotation.set(0.04, 0.5, -0.05);
    g.add(sheaf1);
    this.sheafLying(g, mSheaf, sg, 2.7, 0.14, 1.6, 0.3, 1.3);
    this.sheafLying(g, mSheaf, sg, 3.1, 0.14, 0.2, 0.5, -0.4);

    const ro = { bow: 0.85, belt: true, armL: [1.05, 0.08], armR: [1.0, 0.16] } as const;
    const reaper = new Group();
    reaper.add(solid(personGeo({ ...ro, armL: [...ro.armL], armR: [...ro.armR] }), robeMat('#a88758', 17), 2.4));
    const mSick = litMat({ base: '#9a9890', parts: ['#a8a8a0', '#6e5433'], angle: 30, space: 3.6, seed: 72 });
    const sick = solid(sickleGeo(), mSick, 1.4);
    const hand = personHand({ ...ro, armL: [...ro.armL], armR: [...ro.armR] }, 'R');
    sick.position.copy(hand).add(new Vector3(0, -0.02, 0.02));
    sick.rotation.set(Math.PI / 2 + 0.2, 0.2, 0.0);
    reaper.add(sick);
    reaper.position.set(0.2, 0, -0.3);
    reaper.rotation.y = -Math.PI / 2;
    this.reaper = reaper;
    g.add(reaper);

    // 遠一些的割麥人（彎腰的剪影）與散放的禾捆
    const bent = solidInstanced(personGeo({ bow: 0.9, belt: true, low: true, armL: [1.0, 0.1], armR: [1.0, 0.1] }), robeMat('#b59a68', 19), 6, 1.6);
    g.add(bent.group);
    const spots: [number, number][] = [[-5, -5], [-8.5, -9], [-3.5, -13], [-11, -15], [-6.5, -19], [-2, -22]];
    spots.forEach(([x, z], i) => setInst(bent.main, i, x, hf(x, z), z, -Math.PI / 2 + (rnd() - 0.5) * 0.4, 1 + rnd() * 0.06));
    bent.main.instanceMatrix.needsUpdate = true;
    for (const [x, z] of [[-3, -6], [-6, -10.5], [-1.5, -14], [-8, -16.5]]) {
      const s = solid(sg, mSheaf, 1.2);
      s.position.set(x, hf(x, z), z);
      s.rotation.set(0.05, rnd() * 6, 0);
      g.add(s);
    }

    // 羊羔（lamb-offering）：一歲的公綿羊羔，側身站著
    const lmat = litMat({ base: 'paper', parts: ['#e9e1cc', '#14110e'], angle: 52, space: 4.4, seed: 12 });
    const lamb = solid(lambGeo(), lmat, 2.2);
    lamb.position.set(17, 0, 0.6);
    lamb.rotation.y = Math.PI / 2 - 0.35;
    lamb.scale.setScalar(1.25);
    g.add(lamb);

    // not-yet：收好的禾捆整齊堆在田邊，旁邊一個空的烘烤盤
    const layers: [number, number[]][] = [[0.15, [-0.66, 0, 0.66]], [0.44, [-0.33, 0.33]], [0.73, [0]]];
    const stack = solidInstanced(sheafGeo(9, 18, 1.7), mSheaf, 12, 1.3);
    let si = 0;
    layers.forEach(([y, zs], li) => {
      for (const z of zs) {
        for (const xo of [-0.5, 0.5]) {
          // 躺著的禾捆：沿 x 軸放，底（切口）在 +x 端
          setInst(stack.main, si++, 25 + xo + (li % 2 ? 0.2 : 0) + 0.48 + (rnd() - 0.5) * 0.06, y, 0.3 + z, (rnd() - 0.5) * 0.1, 1, 1, 0, Math.PI / 2);
        }
      }
    });
    stack.main.instanceMatrix.needsUpdate = true;
    g.add(stack.group);
    const mClay = litMat({ base: '#5b4630', angle: 25, space: 4, seed: 73 });
    const gr = solid(griddleGeo(), mClay, 1.8);
    gr.position.set(27.6, 0.18, 1.1);
    gr.scale.setScalar(1.1);
    g.add(gr);
    const mRock = litMat({ base: '#a69a82', angle: 50, space: 4.4, seed: 51, cross: true });
    for (const [x, z] of [[-0.22, 0.15], [0.2, 0.2], [0, -0.22]]) {
      const r = solid(rockGeo(5), mRock, 1.4);
      r.scale.set(0.12, 0.1, 0.12);
      r.position.set(27.6 + x * 1.1, 0.07, 1.1 + z * 1.1);
      g.add(r);
    }
  }

  private sheafLying(g: Group, mat: ShaderMaterial, geo: BufferGeometry, x: number, y: number, z: number, ry: number, rz: number): void {
    const s = solid(geo, mat, 1.4);
    s.position.set(x, y, z);
    s.rotation.set(0, ry, Math.PI / 2 + rz * 0.05);
    g.add(s);
  }

  // ---------------------------------------------------------------- 小麥田
  private buildWheat(): void {
    const g = this.wheat;
    g.position.set(WX, 0, 0);
    const rnd = mulberry32(131);
    this.wheatGround = litMat({ base: '#c2a763', line: '#5a4420', angle: 84, angle2: 80, space: 5, seed: 82, cross: true });
    const ground = new Mesh(fieldGeo(600, 560, 72, hf, 50, -250), this.wheatGround);
    ground.position.y = 0.03;
    g.add(ground);
    const mHill = litMat({ base: '#b9985a', line: '#5d4623', angle: 4, space: 5, seed: 6, bias: -0.2 });
    g.add(hillMesh(mHill, -70, -190, 110, 12, 50), hillMesh(mHill, 90, -210, 140, 16, 60), hillMesh(mHill, 10, -280, 190, 11, 50));

    this.wheatMat = litMat({ base: '#c6a96c', parts: ['#7d9244', '#97a94f'], partAlt: '#6a7c38', angle: 80, space: 5, wind: true, crop: true, seed: 10, bias: 0.22 });
    const wg = barleyGeo({ earW: 0.03, earTop: 1.12, leafLen: 1.15, stem: 1.6 });
    const total = 6600;
    const wheat = new InstancedMesh(wg, this.wheatMat, total);
    wheat.frustumCulled = false;
    const col = new Color();
    const RX0 = -16;
    const RX1 = 64;
    const RZ1 = -0.7;
    const RZ0 = -40;
    const CORNER = 8;
    let n = 0;
    while (n < total) {
      let x = RX0 + rnd() * (RX1 - RX0);
      let z = RZ1 - Math.pow(rnd(), 1.6) * (RZ1 - RZ0);
      if (rnd() < 0.12) {
        // 鏡頭前（count 那一拍）田往前多伸一塊
        x = RX0 + rnd() * 19;
        z = RZ1 + rnd() * 5.2;
      }
      const cx = x < RX0 + CORNER || x > RX1 - CORNER;
      const cz = z > RZ1 - CORNER || z < RZ0 + CORNER;
      const zone = cx && cz ? 1 : 0;
      setInst(wheat, n, x, hf(x, z), z, rnd() * Math.PI * 2, 1.1 + rnd() * 0.6, 0.8 + rnd() * 0.25, (rnd() - 0.5) * 0.12, (rnd() - 0.5) * 0.12);
      col.setRGB(rnd(), zone, 0);
      wheat.setColorAt(n, col);
      n++;
    }
    g.add(wheat);

    // 收完的田：散放的禾捆
    const mSheaf = litMat({ base: '#d2b05a', parts: ['#cdac55', '#e6c25f', '#6a4a26'], angle: 70, space: 4, seed: 74 });
    const sg = sheafGeo(5);
    for (let i = 0; i < 9; i++) {
      const x = 4 + rnd() * 30;
      const z = -3 - rnd() * 14;
      const s = solid(sg, mSheaf, 1.2);
      s.position.set(x, hf(x, z), z);
      s.rotation.set(0.05, rnd() * 6, 0);
      this.cutSheaves.add(s);
    }
    this.cutSheaves.visible = false;
    g.add(this.cutSheaves);

    // two-loaves：布上兩個發起來的餅，旁邊一束小麥
    const mCloth = litMat({ base: '#e0d6bf', angle: 10, space: 4.4, seed: 54, side: DoubleSide });
    const cloth = solid(clothGeo(1.6, 1.1), mCloth, 1.6);
    cloth.position.set(6.3, 0.04, 0.95);
    cloth.rotation.y = -0.1;
    g.add(cloth);
    const mLoaf = litMat({ base: '#c58a45', parts: ['#c9904a', '#6b3f1a'], angle: 28, space: 3.8, seed: 75 });
    const lg = loafGeo();
    const l1 = solid(lg, mLoaf, 1.8);
    l1.position.set(5.65, 0.14, 0.82);
    l1.rotation.y = 0.18;
    l1.scale.setScalar(1.1);
    const l2 = solid(lg, mLoaf, 1.8);
    l2.position.set(6.4, 0.14, 1.0);
    l2.rotation.y = -0.22;
    l2.scale.setScalar(1.1);
    g.add(l1, l2);
    const sw = solid(sg, mSheaf, 1.4);
    sw.position.set(7.35, 0.11, 0.7);
    sw.rotation.set(0, 0.5, Math.PI / 2 - 0.1);
    sw.scale.setScalar(0.85);
    g.add(sw);
    // 對照用的薄餅不放在這裡（無酵餅在 remember 的桌上）
    void flatBreadGeo;

    // weeks-offerings：祭牲的剪影排成一列，數量讀 SITE.offerings['利23:18-19']
    const group = SITE.offerings?.['利23:18-19'];
    const items: { kind: 'bull' | 'ram' | 'goat' | 'lamb'; sc: number }[] = [];
    if (group) for (const it of group.items) for (let k = 0; k < it.count; k++) items.push(animalKind(it.animal));
    const mSil = litMat({ base: 'silh' });
    const geos = { bull: cattleGeo(), ram: lambGeo(false, 'ram'), goat: lambGeo(false, 'goat'), lamb: lambGeo() };
    let ax = 12.5;
    items.forEach((it, i) => {
      const a = solid(geos[it.kind], mSil, 1.8);
      a.position.set(ax, 0, 1.6 + (i % 2) * 0.15);
      a.rotation.y = Math.PI / 2 - 0.08;
      a.scale.setScalar(it.sc);
      g.add(a);
      const next = items[i + 1];
      ax += next && next.kind !== it.kind ? 1.55 : 1.1;
    });

    // rejoice：申16:11 列出的人，用不同高矮的剪影表現
    const folks: { x: number; z: number; sc: number; robe: string; wrap: string; o: Parameters<typeof personGeo>[0] }[] = [
      { x: 42.40, z: 2.50, sc: 1.02, robe: '#a88758', wrap: '#2b2218', o: { belt: true, staff: true, staffSide: 'R', armL: [0.4, 0.2], armR: [0.3, 0.15] } },
      { x: 43.05, z: 1.25, sc: 0.93, robe: '#cdbf9e', wrap: '#6b5a3a', o: { slim: true, veil: true, belt: true, armL: [0.5, 0.15], armR: [0.5, 0.15] } },
      { x: 43.70, z: 2.50, sc: 0.74, robe: '#b79a68', wrap: '#2b2218', o: { belt: true, armL: [0.6, 0.2], armR: [0.2, 0.15] } },
      { x: 44.35, z: 1.25, sc: 0.64, robe: '#d8cdb4', wrap: '#7a5a3a', o: { veil: true, armL: [0.2, 0.15], armR: [0.7, 0.2] } },
      { x: 45.00, z: 2.50, sc: 0.99, robe: '#8f7550', wrap: '#2b2218', o: { slim: true, belt: true, armL: [0.8, 0.2], armR: [0.3, 0.15] } },
      { x: 45.65, z: 1.25, sc: 0.92, robe: '#c9b27a', wrap: '#8a5a3a', o: { slim: true, veil: true, belt: true, armL: [0.3, 0.15], armR: [0.6, 0.2] } },
      { x: 46.30, z: 2.50, sc: 1.04, robe: '#e9e1cc', wrap: '#2b2218', o: { belt: false, armL: [0.2, 0.15], armR: [0.5, 0.2] } },
      { x: 46.95, z: 1.25, sc: 1.0, robe: '#6c5a3d', wrap: '#b79a68', o: { slim: true, belt: true, staff: true, staffSide: 'L', armL: [0.3, 0.2], armR: [0.4, 0.15] } },
      { x: 47.60, z: 2.50, sc: 0.56, robe: '#b79a68', wrap: '#2b2218', o: { armL: [0.5, 0.2], armR: [0.4, 0.2] } },
      { x: 48.25, z: 1.25, sc: 0.62, robe: '#cdbf9e', wrap: '#6b5a3a', o: { veil: true, armL: [0.3, 0.2], armR: [0.6, 0.2] } },
      { x: 48.90, z: 2.50, sc: 0.9, robe: '#8a7a5c', wrap: '#4a3a2a', o: { slim: true, veil: true, belt: true, staff: true, staffSide: 'R', armL: [0.3, 0.15], armR: [0.4, 0.2] } },
      { x: 49.55, z: 1.25, sc: 0.97, robe: '#a88758', wrap: '#2b2218', o: { belt: true, bow: 0.1, staff: true, staffSide: 'L', armL: [0.35, 0.2], armR: [0.3, 0.15] } },
    ];
    folks.forEach((f, i) => {
      const p = solid(personGeo(f.o), robeMat(f.robe, 40 + i, '#14110e', f.wrap), 2.2);
      p.position.set(f.x, 0, f.z);
      p.rotation.y = (46 - f.x) * 0.05 + (i % 2 ? 0.08 : -0.08);
      p.scale.setScalar(f.sc);
      g.add(p);
    });

    // corners：彎腰拾取遺落穗子的人
    const gl = new Group();
    gl.add(solid(personGeo({ bow: 1.05, belt: true, armL: [1.35, 0.1], armR: [0.7, 0.12] }), robeMat('#9a8058', 50), 2.4));
    gl.position.set(54.8, 0, -2.4);
    this.gleaner = gl;
    gl.rotation.y = Math.PI / 2 + 0.3;
    g.add(gl);
  }

  // ---------------------------------------------------------------- 每幀
  update(fr: FrameLite, s: number): void {
    void fr;
    void this.reaper;
    // 小麥：依 story.count 由殘茬長成、轉金；corners 時割掉田心
    const count = clamp(story.count, 0, 50);
    const m = this.wheatMat;
    m.uniforms.uGrow.value = lerp(0.2, 1, smooth(2, 26, count));
    m.uniforms.uCut.value = smooth(c('corners', 0.0), c('corners', 0.4), s);
    this.cutSheaves.visible = m.uniforms.uCut.value > 0.6;
    this.gleaner.visible = s >= c('corners', -0.15);
    const cols = m.uniforms.uPartCol.value as Vector3[];
    const green = smooth(2, 18, count);
    const gold = smooth(28, 50, count);
    const stem = mix3(cols[0], '#b8a266', '#7d9244', green);
    stem.lerp(hexTo('#cfae56', _c2), gold);
    const ear = mix3(cols[1], '#c2ac6c', '#97a94f', green);
    ear.lerp(hexTo('#e6c25f', _c2), gold);
    (m.uniforms.uPartAlt.value as Vector3).copy(stem).multiplyScalar(0.82);
    const gb = mix3(this.wheatGround.uniforms.uBase.value as Vector3, '#c2a763', '#97a458', green);
    gb.lerp(hexTo('#cdae66', _c2), gold);
  }
}
