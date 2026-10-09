// 兩處營地：疏割的野地（無酵節 bake、seven-days）與西乃的帳棚營地（二月逾越節）。
import { Color, ConeGeometry, DoubleSide, Group, InstancedMesh, Mesh, ShaderMaterial, SphereGeometry } from 'three';
import { basinGeo, breadGeo, dishGeo, lambGeo, personGeo, cattleGeo } from './geo';
import { clothGeo, fireBaseGeo, flamePlanesGeo, rockGeo, tentGeo } from './geo2';
import { flameMat, litMat, solid, solidInstanced } from './materials';
import { c, NX, SX } from './tracks';
import { type FrameLite, hillMesh, poolGlow, poolMesh, robeMat, setInst } from './props';
import { clamp, lerp, mulberry32, smooth } from './util';
import { story } from '../story/state';

export class Camp {
  succoth = new Group();
  sinai = new Group();
  private dough: Group;
  private doughMat: ShaderMaterial;
  private flameMats: ShaderMaterial[] = [];
  private flames: { m: Mesh; base: number; ph: number }[] = [];
  private near = new Group();
  private flameGeo = flamePlanesGeo();

  constructor() {
    this.doughMat = litMat({ base: '#dccb9c', angle: 25, space: 4, seed: 52, bake: true });
    this.dough = new Group();
    this.buildSuccoth();
    this.buildSinai();
    this.succoth.visible = false;
    this.sinai.visible = false;
  }

  // ---------------------------------------------------------------- 火
  private addFlames(parent: Group, x: number, z: number, heights: number[], size: number): void {
    const fm = flameMat();
    this.flameMats.push(fm);
    const fg = this.flameGeo;
    heights.forEach((h, i) => {
      const m = new Mesh(fg, fm);
      m.position.set(x + (i - (heights.length - 1) / 2) * 0.12 * size, 0.06, z + (i % 2 ? 0.05 : -0.05) * size);
      m.scale.set(size * (1.1 - i * 0.12), size * h, size * (1.1 - i * 0.12));
      parent.add(m);
      this.flames.push({ m, base: size * h, ph: i * 1.7 + x });
    });
  }

  // ---------------------------------------------------------------- 疏割
  private buildSuccoth(): void {
    const g = this.succoth;
    g.position.set(SX, 0, 0);
    const rnd = mulberry32(61);
    const mHill = litMat({ base: 'paper', angle: 4, angle2: 0, space: 5.0, seed: 6, bias: -0.3 });
    g.add(hillMesh(mHill, -110, -160, 100, 14, 55), hillMesh(mHill, 130, -190, 120, 18, 60), hillMesh(mHill, 10, -250, 180, 11, 50), hillMesh(mHill, -240, -80, 90, 12, 70));

    // 近景：石頭、生麵團、火、麵盆、布
    const mRock = litMat({ base: '#a69a82', angle: 50, space: 4.4, seed: 51, cross: true });
    const rock = solid(rockGeo(2), mRock, 2.2);
    rock.scale.set(0.56, 0.22, 0.46);
    rock.position.set(0, 0.17, 0);
    g.add(rock);
    const dg = new SphereGeometry(1, 20, 12);
    this.dough = solid(dg, this.doughMat, 2.0);
    g.add(this.dough);

    const mFire = litMat({ base: '#6f6a5e', parts: ['#7d7667', '#2a1d12'], angle: 30, space: 4, seed: 53 });
    const fire = solid(fireBaseGeo(), mFire, 1.6);
    fire.position.set(1.1, 0, -0.55);
    g.add(fire);
    this.addFlames(g, 1.1, -0.55, [1.0, 0.78, 0.6], 0.85);
    g.add(poolMesh(poolGlow(), 4.4, 1.1, -0.55));

    const bs = basinGeo();
    const mBowl = litMat({ base: '#7b5a39', angle: 20, space: 4.4, seed: 13 });
    const bowl = solid(bs.bowl, mBowl, 2.2);
    bowl.scale.setScalar(1.35);
    bowl.position.set(-1.0, 0, -0.1);
    g.add(bowl);
    const mCloth = litMat({ base: '#e6dec9', angle: 10, space: 4.4, seed: 54, side: DoubleSide, bias: 0.18 });
    const cloth = solid(clothGeo(0.8, 0.6), mCloth, 1.6);
    cloth.position.set(-1.35, 0, 0.75);
    cloth.rotation.y = 0.5;
    g.add(cloth);

    // 遠處：各家散開，各有一處小火、坐著的人與牲畜
    const clusters: [number, number][] = [[-9, -8], [6.5, -12], [-17, -17], [14, -22], [-4, -30], [23, -9], [-26, -27], [-33, -9], [32, -30]];
    const sit = solidInstanced(personGeo({ sit: true, low: true, belt: true }), robeMat('#a88758', 14), clusters.length * 4, 1.6);
    const stand = solidInstanced(personGeo({ low: true, belt: true, staff: true, staffSide: 'R' }), robeMat('#b59a68', 15), 14, 1.6);
    const sheep = solidInstanced(lambGeo(true), litMat({ base: 'paper', parts: ['#e9e1cc', '#14110e'], angle: 50, space: 4.4, seed: 15 }), 22, 1.4);
    const cattle = solidInstanced(cattleGeo(true), litMat({ base: '#6b5030', parts: ['#6b5030', '#14110e'], angle: 50, space: 4.4, seed: 16 }), 5, 1.4);
    g.add(sit.group, stand.group, sheep.group, cattle.group);
    let si = 0;
    let sti = 0;
    let shi = 0;
    clusters.forEach(([cx, cz]) => {
      this.addFlames(g, cx, cz, [1.0], 1.9);
      g.add(poolMesh(poolGlow(), 8, cx, cz));
      for (let k = 0; k < 4; k++) {
        const a = (k / 4) * Math.PI * 2 + rnd();
        const r = 1.8 + rnd() * 0.6;
        setInst(sit.main, si++, cx + Math.cos(a) * r, 0, cz + Math.sin(a) * r, Math.atan2(-Math.cos(a), -Math.sin(a)), 1.0 + rnd() * 0.1);
      }
      if (sti < 14) {
        setInst(stand.main, sti++, cx + 3 + rnd() * 2, 0, cz + 1 + rnd() * 2, rnd() * 6.28, 0.96 + rnd() * 0.1);
      }
      for (let k = 0; k < 2 && shi < 22; k++) setInst(sheep.main, shi++, cx - 3.5 + rnd() * 2, 0, cz + rnd() * 3, rnd() * 6.28, 0.9 + rnd() * 0.2);
    });
    for (let k = 0; k < 5; k++) setInst(cattle.main, k, -22 + rnd() * 52, 0, -14 - rnd() * 18, rnd() * 6.28, 1);
    while (shi < 22) setInst(sheep.main, shi++, -30 + rnd() * 60, 0, -6 - rnd() * 24, rnd() * 6.28, 1);
    while (sti < 14) setInst(stand.main, sti++, -30 + rnd() * 60, 0, -14 - rnd() * 18, rnd() * 6.28, 1);
    for (const r of [sit, stand, sheep, cattle]) {
      r.main.instanceMatrix.needsUpdate = true;
    }
    // 沒用到的實例收到遠處
    for (let i = si; i < sit.main.count; i++) setInst(sit.main, i, 0, -50, 0, 0, 0.001);

    // 草叢：幾簇小草增加地面層次
    const tuft = new InstancedMesh(new ConeGeometry(0.05, 0.4, 3), litMat({ base: '#8a8a52', angle: 80, space: 4, seed: 55 }), 140);
    tuft.frustumCulled = false;
    for (let i = 0; i < 140; i++) setInst(tuft, i, (rnd() - 0.5) * 70, 0.18, 2 - rnd() * 40, rnd() * 6, 0.7 + rnd() * 0.8, 0.7 + rnd());
    g.add(tuft);
  }

  // ---------------------------------------------------------------- 西乃
  private buildSinai(): void {
    const g = this.sinai;
    g.position.set(NX, 0, 0);
    const rnd = mulberry32(71);
    // 遠方低矮的山影（兩層）
    const mHill = litMat({ base: 'paper', angle: 4, angle2: 0, space: 5.0, seed: 6, bias: -0.3 });
    const mRidge = litMat({ base: 'paper', angle: 8, angle2: 10, space: 4.6, seed: 19, bias: -0.18, cross: true });
    const ridgeGeo = new ConeGeometry(1, 1, 7, 1);
    const ridges: [number, number, number, number][] = [
      [-260, -330, 140, 30], [-130, -310, 120, 22], [20, -340, 170, 34], [170, -320, 130, 24], [300, -340, 150, 30], [-380, -300, 110, 20],
      [-60, -420, 220, 46], [220, -430, 200, 40],
    ];
    for (const [x, z, w, h] of ridges) {
      const m = new Mesh(ridgeGeo, mRidge);
      m.position.set(x, h / 2 - 1, z);
      m.scale.set(w, h, w * 0.55);
      m.rotation.y = rnd() * 3;
      g.add(m);
    }
    g.add(hillMesh(mHill, -80, -150, 110, 8, 40), hillMesh(mHill, 110, -170, 120, 9, 40));

    // 帳棚：人字形低面數帳棚，門朝向中央
    const tg = tentGeo();
    const mTent = litMat({ base: '#3b2e22', parts: ['#403328', '#e7b55a'], partAlt: '#56422e', angle: 70, space: 4.4, seed: 61, cross: true });
    const CX = -6;
    const CZ = -36;
    const spots: { x: number; z: number; yaw: number; sc: number; a: number }[] = [];
    for (let x = -62; x <= 46; x += 6.8) {
      for (let z = -78; z <= -3; z += 6.4) {
        const px = x + (rnd() - 0.5) * 2.4;
        const pz = z + (rnd() - 0.5) * 2.4;
        if (Math.abs(px - CX) < 13 && Math.abs(pz - CZ) < 12) continue;
        if (Math.abs(px + 5) < 9 && pz > -26) continue; // 通往中央帳棚的空地：近景留空，讓人與營地隔著一點距離
        if (pz > -12 && px > -1 && px < 32) continue;
        spots.push({ x: px, z: pz, yaw: Math.atan2(CX - px, CZ - pz) + (rnd() - 0.5) * 0.5 + (rnd() < 0.45 ? Math.PI / 2 : 0), sc: 1.0 + rnd() * 0.45, a: rnd() });
      }
    }
    const tents = solidInstanced(tg, mTent, spots.length, 1.5);
    g.add(tents.group);
    spots.forEach((p, i) => {
      setInst(tents.main, i, p.x, 0, p.z, p.yaw, p.sc);
      tents.main.setColorAt(i, new Color(p.a, 0, 0));
    });
    tents.main.instanceMatrix.needsUpdate = true;
    if (tents.main.instanceColor) tents.main.instanceColor.needsUpdate = true;

    // 中央較大的帳棚
    const bigMat = litMat({ base: '#4d3d2c', parts: ['#5a4934', '#f0c46a'], angle: 70, space: 4.4, seed: 62, cross: true });
    const big = solid(tg, bigMat, 2.0);
    big.position.set(CX, 0, CZ);
    big.scale.set(2.5, 2.3, 2.5);
    g.add(big);
    // 營火的光點：帳棚之間幾處小火
    const fires: [number, number][] = [[-30, -30], [14, -26], [-20, -58], [24, -52], [-4, -62], [30, -68], [-40, -18], [8, -14]];
    for (const [fx, fz] of fires) {
      this.addFlames(g, fx, fz, [1.0], 1.4);
      g.add(poolMesh(poolGlow(), 6, fx, fz));
    }

    // 近景：帳棚前站著的人、摩西與亞倫（剪影，不畫五官、不加光環）
    g.add(this.near);
    const t1 = solid(tg, mTent, 1.8);
    t1.position.set(4.6, 0, 0.2);
    t1.scale.setScalar(1.25);
    this.near.add(t1);
    const men: { x: number; z: number; sc: number; robe: string; o: Parameters<typeof personGeo>[0] }[] = [
      { x: 2.6, z: 5.6, sc: 1.0, robe: '#a88758', o: { slim: true, belt: true, armL: [1.25, 0.35], armR: [0.1, 0.12] } },
      { x: 3.5, z: 6.2, sc: 0.95, robe: '#cdbf9e', o: { slim: true, belt: true, armL: [0.1, 0.12], armR: [0.7, 0.2] } },
      { x: 4.4, z: 5.5, sc: 1.03, robe: '#8f7550', o: { slim: true, belt: true, staff: true, staffSide: 'R', armL: [0.6, 0.2], armR: [0.3, 0.15] } },
      { x: 5.3, z: 6.2, sc: 0.92, robe: '#b79a68', o: { slim: true, belt: true, armL: [0.9, 0.25], armR: [0.1, 0.12] } },
    ];
    men.forEach((m, i) => {
      const p = solid(personGeo(m.o), robeMat(m.robe, 20 + i), 2.2);
      p.position.set(m.x, 0, m.z);
      p.rotation.y = Math.PI / 2 - 0.1 + i * 0.05;
      p.scale.setScalar(m.sc);
      this.near.add(p);
    });
    const mSil = litMat({ base: 'silh' });
    const moses = solid(personGeo({ slim: true, belt: false, armL: [0.15, 0.14], armR: [0.35, 0.18] }), mSil, 2.2);
    moses.position.set(7.2, 0, 5.7);
    moses.rotation.y = -Math.PI / 2 + 0.15;
    moses.scale.setScalar(1.06);
    this.near.add(moses);
    const aaron = solid(personGeo({ slim: true, belt: false, armL: [0.4, 0.16], armR: [0.12, 0.14] }), mSil, 2.2);
    aaron.position.set(8.0, 0, 6.6);
    aaron.rotation.y = -Math.PI / 2 - 0.1;
    aaron.scale.setScalar(0.98);
    this.near.add(aaron);

    // second-month：一個營帳前，幾個人圍著站著吃（戶外）
    const t2 = solid(tg, mTent, 1.8);
    t2.position.set(22, 0, -2.6);
    t2.scale.setScalar(1.3);
    g.add(t2);
    const mCl = litMat({ base: '#d8cdb4', angle: 8, space: 4.4, seed: 63, side: DoubleSide });
    const mat = solid(clothGeo(1.5, 1.0), mCl, 1.4);
    mat.position.set(22, 0, 3.6);
    g.add(mat);
    const mBread = litMat({ base: '#c9b27a', angle: 20, space: 4, seed: 34, bias: 0.1 });
    for (const [bx, bz] of [[-0.35, 2.55], [-0.15, 2.8]]) {
      const b = new Mesh(breadGeo(), mBread);
      b.position.set(22 + bx, 0.03, bz + 0.9);
      g.add(b);
    }
    const dish = solid(dishGeo(), litMat({ base: '#8a6a45', angle: 30, space: 4, seed: 35 }), 1.4);
    dish.position.set(22.35, 0.02, 3.55);
    g.add(dish);
    const eaters: { a: number; r: number; robe: string; o: Parameters<typeof personGeo>[0]; sc: number }[] = [
      { a: -2.6, r: 1.5, robe: '#a88758', o: { staff: true, staffSide: 'R', belt: true, armL: [0.8, 0.1], armR: [0.4, 0.2] }, sc: 1 },
      { a: -1.95, r: 1.45, robe: '#cdbf9e', o: { belt: true, armL: [0.9, 0.1], armR: [0.5, 0.12] }, sc: 0.94 },
      { a: -1.2, r: 1.45, robe: '#8f7550', o: { staff: true, staffSide: 'L', belt: true, armL: [0.4, 0.2], armR: [0.85, 0.1] }, sc: 0.98 },
      { a: -0.55, r: 1.5, robe: '#b79a68', o: { belt: true, armL: [0.85, 0.12], armR: [0.4, 0.2] }, sc: 0.62 },
    ];
    eaters.forEach((e, i) => {
      const px = 22 + Math.cos(e.a) * e.r;
      const pz = 3.6 + Math.sin(e.a) * e.r * 0.8;
      const p = solid(personGeo(e.o), robeMat(e.robe, 30 + i), 2.2);
      p.position.set(px, 0, pz);
      p.rotation.y = Math.atan2(22.1 - px, 3.6 - pz) + (i % 2 ? 0.15 : -0.12);
      p.scale.setScalar(e.sc);
      g.add(p);
    });
  }

  // ---------------------------------------------------------------- 每幀
  update(fr: FrameLite, s: number): void {
    this.near.visible = s >= c('unclean');
    const p = clamp(story.bake.progress);
    const k = smooth(0, 1, p);
    const sx = lerp(0.36, 0.52, k);
    const sy = lerp(0.2, 0.05, k);
    this.dough.scale.set(sx, sy, sx * 0.92);
    this.dough.position.set(0, 0.38 + sy * 0.82, 0);
    this.doughMat.uniforms.uBake.value = k;
    const fl = fr.motionOff ? 0 : 1;
    for (const m of this.flameMats) m.uniforms.uFlick.value = fl;
    for (const f of this.flames) {
      const w = fr.motionOff ? 1 : 1 + 0.12 * Math.sin(fr.time * 9 + f.ph) + 0.07 * Math.sin(fr.time * 14.3 + f.ph * 2);
      f.m.scale.y = f.base * w;
    }
  }
}
