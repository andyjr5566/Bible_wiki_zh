// 夜間世界與隔日世界：所有場景物件與它們隨 s（cue＋進度）的狀態。
import {
  BoxGeometry,
  BufferGeometry,
  Color,
  CylinderGeometry,
  DoubleSide,
  Group,
  InstancedMesh,
  Matrix4,
  Mesh,
  Object3D,
  PerspectiveCamera,
  PlaneGeometry,
  Scene,
  ShaderMaterial,
  SphereGeometry,
  Vector3,
} from 'three';
import { story } from '../story/state';
import {
  barleyGeo,
  basinGeo,
  bedGeo,
  cattleGeo,
  doorFrameGeo,
  doorLeafGeo,
  flameGeo,
  houseBodyGeo,
  lambGeo,
  mergeParts,
  palmFrondsGeo,
  palmTrunkGeo,
  personGeo,
  T,
  torchGeo,
  type Part,
  type PersonOpts,
} from './geo';
import { decalMat, FIXED, glowMat, hullMat, litMat, moonMat, skyMat, solid, solidInstanced, U } from './materials';
import { CUE_IDX, DAY_S, HYSSOP_IDX, OX, departDist, torchOn, upShiftAt, windowOff, type TrackOut } from './tracks';
import { clamp, lerp, mulberry32, smooth } from './util';

const RAD = Math.PI / 180;
const DESK_HYSSOP = [0, 0, 0, 0, 0, 0, 0, 0];
const DESK_MEAL = [0, 0, 0, 0, 0, 0, 0, 0];
const PARTS = ['lintel', 'left', 'right'] as const;
const MOON_R = 900;

export interface Frame {
  s: number;
  idx: number;
  dt: number;
  time: number;
  dark: number;
  motionOff: boolean;
}

export interface DecalRig {
  mesh: Mesh;
  mat: ShaderMaterial;
  grow: number;
}

export interface HouseRig {
  group: Group;
  x: number;
  leafPivot: Group;
  decals: DecalRig[];
  door: Vector3;
  delay: number;
  markT: number;
  d: number;
}

const _v = new Vector3();
const _dummy = new Object3D();
const _col = new Color();
const _m = new Vector3();

export class World {
  scene = new Scene();
  camera = new PerspectiveCamera(50, 1, 0.1, 8000);
  skyM: ShaderMaterial;
  moon: Mesh;
  moonHull: Mesh;
  moonM: ShaderMaterial;
  night = new Group();
  day = new Group();
  houses: HouseRig[] = [];
  hero!: HouseRig;
  basinPos = new Vector3(-1.35, 0, 0.95);
  doorD = 0;
  /** 有讀者觸發的動畫正在播放（減少動態時用來判斷要不要繼續畫） */
  busy = false;
  private doneTimer = 0;
  private onShut: () => void;
  private shutFired = false;

  // 動態物件
  private lamb = new Group();
  private lambProps = new Group();
  private doorwayPerson = new Group();
  private winMat: ShaderMaterial;
  private torchMat: ShaderMaterial;
  private barleyGroups: InstancedMesh[] = [];
  private procG = new Group();
  private procPeople: { mesh: InstancedMesh; items: { x0: number; z: number; ph: number; sc: number }[] }[] = [];
  private procAnimals: { mesh: InstancedMesh; items: { x0: number; z: number; ph: number; sc: number }[] }[] = [];
  private farLine: Group;
  private farLineMesh: InstancedMesh;
  private doorGlowMat: ShaderMaterial;
  private spillMat: ShaderMaterial;

  constructor(onShut: () => void) {
    this.onShut = onShut;
    const sc = this.scene;
    sc.add(this.night, this.day);

    // ---- 天空與月亮
    this.skyM = skyMat();
    const sky = new Mesh(new PlaneGeometry(2, 2), this.skyM);
    sky.frustumCulled = false;
    sky.renderOrder = -100;
    sc.add(sky);

    this.moonM = moonMat();
    this.moon = new Mesh(new SphereGeometry(1, 36, 24), this.moonM);
    this.moon.renderOrder = -90;
    this.moon.frustumCulled = false;
    this.moonHull = new Mesh(new SphereGeometry(1, 36, 24), hullMat(2.2));
    this.moonHull.renderOrder = -91;
    this.moonHull.frustumCulled = false;
    sc.add(this.moonHull, this.moon);

    // ---- 材質
    const mGround = litMat({ base: 'paper', angle: 0, angle2: 0, space: 5.4, seed: 2, bias: -0.26 });
    const mHill = litMat({ base: 'paper', angle: 4, angle2: 0, space: 5.0, seed: 6, bias: -0.3 });
    const mMud = litMat({ base: FIXED.ochre, angle: 86, angle2: 8, space: 4.8, seed: 3, cross: true });
    const mMudPaper = litMat({ base: 'paper', angle: 84, angle2: 6, space: 5, seed: 4 });
    const mWood = litMat({ base: '#6e5433', angle: 74, angle2: 10, space: 4.4, seed: 5 });
    const mTrunk = litMat({ base: '#8f7145', angle: 82, angle2: 10, space: 4.6, seed: 7, cross: true });
    const mFrond = litMat({ base: '#5c5836', angle: 28, angle2: 28, space: 4.6, seed: 8, side: DoubleSide });
    const mSilh = litMat({ base: 'silh' });
    const mBlood = litMat({ base: FIXED.blood, line: '#3a0c09', angle: 20, space: 4.6, bias: 0.25 });
    this.doorGlowMat = glowMat({ hatch: 0.75, edge: '#2a1c0a' });
    this.spillMat = glowMat({ spill: true });

    // ---- 地面與遠山
    const ground = new Mesh(new PlaneGeometry(9000, 9000), mGround);
    ground.rotation.x = -Math.PI / 2;
    sc.add(ground);
    const hill = (x: number, z: number, sx: number, sy: number, sz: number) => {
      const m = new Mesh(new SphereGeometry(1, 20, 10, 0, Math.PI * 2, 0, Math.PI / 2), mHill);
      m.position.set(x, 0, z);
      m.scale.set(sx, sy, sz);
      this.night.add(m);
    };
    hill(-120, -170, 100, 15, 55);
    hill(150, -200, 120, 20, 60);
    hill(0, -260, 170, 12, 50);
    hill(-260, -60, 90, 13, 80);
    hill(60, -78, 58, 15.5, 42); // 埃及城所在的山丘
    hill(OX + 70, -150, 110, 16, 55);
    hill(OX - 90, -170, 100, 12, 50);

    // ---- 以色列人的村子：主角的家在 x=0，鄰舍分列兩側
    this.buildVillage(mMud, mMudPaper, mWood, mSilh, mBlood);

    // ---- 椰棗樹
    const palmSets = [
      { t: palmTrunkGeo(7.5, 0.9), f: palmFrondsGeo(7.5, 0.9, 3) },
      { t: palmTrunkGeo(6.2, -0.7), f: palmFrondsGeo(6.2, -0.7, 9) },
      { t: palmTrunkGeo(8.6, 1.1), f: palmFrondsGeo(8.6, 1.1, 14) },
    ];
    const palmAt = (parent: Group, x: number, z: number, kind: number, yaw: number, scale = 1) => {
      const g = new Group();
      const ps = palmSets[kind];
      g.add(solid(ps.t, mTrunk, 2.4));
      g.add(new Mesh(ps.f, mFrond));
      g.position.set(x, 0, z);
      g.rotation.y = yaw;
      g.scale.setScalar(scale);
      parent.add(g);
    };
    palmAt(this.night, -6.2, -7.5, 0, 0.4, 1.1);
    palmAt(this.night, 11.5, -9, 2, 2.2);
    palmAt(this.night, -17.5, 3.2, 1, 1.3);
    palmAt(this.night, 20.5, 5.5, 0, 3.6, 0.95);
    palmAt(this.night, -28, -4, 2, 0.8);
    palmAt(this.night, 31, -6, 1, 2.9);
    palmAt(this.night, -13, 8.5, 1, 1.6, 0.9);
    palmAt(this.day, OX + 7.5, -2, 0, 2.0, 1.1);
    palmAt(this.day, OX - 9, -6, 2, 0.5);

    // ---- 大麥田
    const bg = barleyGeo();
    const bm = litMat({ base: FIXED.ochre, parts: ['#a07f4f', '#c6a96c'], partAlt: '#7e6b3d', angle: 80, space: 5, wind: true, seed: 9 });
    // 三群麥株：A 在鏡頭下降的路徑兩側（只在開場畫面用），B／C 是遠處與兩側（半夜到出發的前景也會用）
    const groups = [2000, 900, 500];
    const rnd = mulberry32(21);
    // 鏡頭走過麥田的路徑（xz），讓葉片不要貼在鏡頭上
    const path: number[][] = [[0.4, 38], [0.4, 30], [0.2, 21], [-0.4, 17], [-1.9, 8.2]];
    const nearPath = (x: number, z: number): boolean => {
      for (let k = 0; k < path.length - 1; k++) {
        const [ax, az] = path[k];
        const [bx, bz] = path[k + 1];
        const dx = bx - ax;
        const dz = bz - az;
        const t = clamp(((x - ax) * dx + (z - az) * dz) / (dx * dx + dz * dz));
        if (Math.hypot(x - (ax + dx * t), z - (az + dz * t)) < 1.5) return true;
      }
      return false;
    };
    groups.forEach((total, gi) => {
      const barley = new InstancedMesh(bg, bm, total);
      barley.frustumCulled = false;
      for (let i = 0; i < total; i++) {
        let x = 0;
        let z = 0;
        for (let tries = 0; tries < 8; tries++) {
          if (gi === 0) {
            x = (rnd() - 0.5) * 11 * (0.4 + rnd() * 0.6);
            z = 14 + rnd() * 18;
          } else if (gi === 1) {
            x = (rnd() - 0.5) * 40;
            z = 11.5 + rnd() * 28;
          } else {
            x = (rnd() - 0.5) * 90;
            z = 11.5 + rnd() * 44;
          }
          if (!nearPath(x, z)) break;
        }
        _dummy.position.set(x, 0, z);
        _dummy.rotation.set((rnd() - 0.5) * 0.12, rnd() * Math.PI * 2, (rnd() - 0.5) * 0.12);
        const h = 0.62 + rnd() * 0.34;
        _dummy.scale.set(0.9 + rnd() * 0.7, h, 1);
        _dummy.updateMatrix();
        barley.setMatrixAt(i, _dummy.matrix);
        _col.setRGB(rnd(), 0, 0);
        barley.setColorAt(i, _col);
      }
      this.barleyGroups.push(barley);
      this.night.add(barley);
    });
    // ---- 羊羔（拴在主角家門口）
    const lmat = litMat({ base: 'paper', parts: ['#e9e1cc', '#14110e'], angle: 52, space: 4.4, seed: 12 });
    this.lamb.add(solid(lambGeo(), lmat, 2.2));
    this.lamb.position.set(1.95, 0, 1.55);
    this.lamb.rotation.y = 0.9;
    this.night.add(this.lamb);
    const stake = new Mesh(new CylinderGeometry(0.04, 0.05, 0.6, 5), mWood);
    stake.position.set(1.45, 0.3, 0.95);
    this.lambProps.add(stake);
    const rope = new Mesh(new CylinderGeometry(0.012, 0.012, 1, 4), mSilh);
    {
      const a = new Vector3(1.45, 0.5, 0.95);
      const b = new Vector3(1.75, 0.62, 1.4);
      const dir = _v.copy(b).sub(a);
      rope.scale.y = dir.length();
      rope.position.copy(a).addScaledVector(dir, 0.5);
      rope.quaternion.setFromUnitVectors(new Vector3(0, 1, 0), dir.normalize());
    }
    this.lambProps.add(rope);
    this.night.add(this.lambProps);

    // ---- 埃及的城、宮殿與火炬
    const city = this.buildCity(mSilh);
    this.winMat = city.winMat;
    this.torchMat = city.torchMat;

    // ---- 埃及人的近屋（哀號那一幕的近景）
    this.buildNearEgypt(mMud, mSilh);

    // ---- 隊伍
    this.procG.visible = false;
    this.night.add(this.procG);
    this.buildProcession();
    const far = this.buildFarLine();
    this.farLine = far.group;
    this.farLineMesh = far.mesh;
    this.night.add(this.farLine);

    // ---- 隔日（應許之地）
    this.buildDay(mMud, mWood, mSilh);

  }

  // ------------------------------------------------------------- 村子
  private buildVillage(mMud: ShaderMaterial, mMudPaper: ShaderMaterial, mWood: ShaderMaterial, _mSilh: ShaderMaterial, mBlood: ShaderMaterial): void {
    const rnd = mulberry32(5);
    const frameG = doorFrameGeo();
    const leafG = doorLeafGeo();
    const glowG = new PlaneGeometry(1.5, 2.3);
    const winG = new PlaneGeometry(0.62, 0.52);
    const spillG = new PlaneGeometry(2.4, 2.3);
    const specs: { x: number; w: number; h: number; d: number; z: number; paper: boolean }[] = [{ x: 0, w: 7, h: 3.3, d: 5.2, z: 0, paper: false }];
    let cur = 3.5;
    for (let i = 0; i < 4; i++) {
      const w = 5.4 + rnd() * 2;
      specs.push({ x: cur + 0.9 + w / 2, w, h: 2.8 + rnd() * 0.9, d: 4.4 + rnd(), z: (rnd() - 0.5) * 1.1, paper: rnd() > 0.6 });
      cur += 0.9 + w;
    }
    cur = -3.5;
    for (let i = 0; i < 4; i++) {
      const w = 5.4 + rnd() * 2;
      specs.push({ x: cur - 0.9 - w / 2, w, h: 2.8 + rnd() * 0.9, d: 4.4 + rnd(), z: (rnd() - 0.5) * 1.1, paper: rnd() > 0.6 });
      cur -= 0.9 + w;
    }
    specs.forEach((sp, i) => {
      const g = new Group();
      g.position.set(sp.x, 0, sp.z);
      const body = houseBodyGeo({ w: sp.w, h: sp.h, d: sp.d, doorX: 0, tunnel: 1.6, roofHut: i % 3 === 1 });
      g.add(solid(body, sp.paper ? mMudPaper : mMud, 2.6));
      g.add(solid(frameG, mWood, 2.0));
      const pivot = new Group();
      pivot.position.set(-0.7, 0, -0.02);
      pivot.add(solid(leafG, mWood, 1.8));
      g.add(pivot);
      const glow = new Mesh(glowG, this.doorGlowMat);
      glow.position.set(0, 1.15, -1.58);
      g.add(glow);
      const spill = new Mesh(spillG, this.spillMat);
      spill.rotation.x = -Math.PI / 2;
      spill.position.set(0, 0.03, 1.15);
      spill.renderOrder = 4;
      g.add(spill);
      // 窗（只有部分人家）
      if (i === 0 || i % 2 === 1) {
        const wx = i === 0 ? 2.5 : sp.w * 0.28;
        const win = new Mesh(winG, this.doorGlowMat);
        win.position.set(wx, 1.9, 0.012);
        g.add(win);
        const wf = solid(new BoxGeometry(0.78, 0.68, 0.1), mWood, 1.6);
        wf.position.set(wx, 1.9, -0.05);
        g.add(wf);
      }
      // 血跡貼花：門楣、左門柱、右門柱
      const decals: DecalRig[] = [];
      const defs = [
        { x: 0, y: 2.46, size: [2.1, 0.7], rad: [0.66, 0.13] },
        { x: -0.9, y: 1.3, size: [0.62, 1.7], rad: [0.12, 0.6] },
        { x: 0.9, y: 1.3, size: [0.62, 1.7], rad: [0.12, 0.6] },
      ];
      defs.forEach((df, k) => {
        const mat = decalMat();
        (mat.uniforms.uSize.value as { set: (a: number, b: number) => void }).set(df.size[0], df.size[1]);
        (mat.uniforms.uRad.value as { set: (a: number, b: number) => void }).set(df.rad[0], df.rad[1]);
        mat.uniforms.uSeed.value = 1.7 + i * 3.1 + k * 7.3;
        const mesh = new Mesh(new PlaneGeometry(df.size[0], df.size[1]), mat);
        mesh.position.set(df.x, df.y, 0.236);
        mesh.renderOrder = 5;
        mesh.visible = false;
        g.add(mesh);
        decals.push({ mesh, mat, grow: 0 });
      });
      this.night.add(g);
      const rig: HouseRig = {
        group: g,
        x: sp.x,
        leafPivot: pivot,
        decals,
        door: new Vector3(sp.x, 1.25, sp.z + 0.25),
        delay: i === 0 ? 0 : 0.25 + rnd() * 0.9,
        markT: 0,
        d: rnd(),
      };
      this.houses.push(rig);
    });
    this.hero = this.houses[0];

    // 主角家的門內人影、門口的盆與羊羔的血盆
    const personG = personGeo({ armL: [0.06, 0.12], armR: [0.06, 0.12], belt: true });
    const mDoorMan = litMat({ base: '#10132a', line: '#6b5a3a', angle: 62, angle2: 20, space: 4.6, bias: -0.1, seed: 41, parts: ['#10132a', '#0d0f1f', '#0d0f1f', '#10132a', '#10132a', '#10132a'] });
    this.doorwayPerson.add(solid(personG, mDoorMan, 2.2));
    this.doorwayPerson.position.set(0, 0, -0.35);
    this.hero.group.add(this.doorwayPerson);

    const bs = basinGeo();
    const mBowl = litMat({ base: '#7b5a39', angle: 20, space: 4.4, seed: 13 });
    const basin = new Group();
    basin.add(solid(bs.bowl, mBowl, 2.2));
    basin.add(new Mesh(bs.blood, mBlood));
    basin.position.copy(this.basinPos);
    this.night.add(basin);
  }

  // ------------------------------------------------------------- 埃及的城
  private buildCity(mSilh: ShaderMaterial): { winMat: ShaderMaterial; torchMat: ShaderMaterial } {
    const rnd = mulberry32(31);
    const hillH = (x: number, z: number) => {
      const dx = (x - 60) / 58;
      const dz = (z + 78) / 42;
      const v = 1 - dx * dx - dz * dz;
      return v > 0 ? 15.5 * Math.sqrt(v) : 0;
    };
    const boxes: Part[] = [];
    const wins: { x: number; y: number; z: number; th: number }[] = [];
    for (let i = 0; i < 60; i++) {
      const x = 18 + rnd() * 84;
      const z = -118 + rnd() * 78;
      const y0 = hillH(x, z);
      if (y0 < 0.6) continue;
      if (x > 44 && x < 76 && z > -90 && z < -66) continue;
      const w = 4 + rnd() * 5;
      const h = 3.5 + rnd() * 6;
      const d = 4 + rnd() * 4;
      boxes.push({ g: new BoxGeometry(w, h, d), m: T(x, y0 - 0.8 + h / 2, z) });
      const nw = 1 + Math.floor(rnd() * 3);
      for (let k = 0; k < nw; k++) {
        wins.push({ x: x + (rnd() - 0.5) * (w - 1.6), y: y0 - 0.8 + h * (0.4 + rnd() * 0.4), z: z + d / 2 + 0.04, th: 0.05 + rnd() * 0.95 });
      }
    }
    // 宮殿
    const py = 15.2;
    const pal: Part[] = [
      { g: new BoxGeometry(26, 9, 10), m: T(60, py + 4.5, -78) },
      { g: new BoxGeometry(14, 4, 8), m: T(60, py + 11, -78) },
      { g: new BoxGeometry(5, 15, 5), m: T(46.5, py + 7.5, -75) },
      { g: new BoxGeometry(5, 15, 5), m: T(73.5, py + 7.5, -75) },
      { g: new BoxGeometry(10, 6, 8), m: T(41, py + 3, -81) },
      { g: new BoxGeometry(10, 6, 8), m: T(79, py + 3, -81) },
    ];
    for (let i = 0; i < 6; i++) pal.push({ g: new CylinderGeometry(0.7, 0.8, 8.4, 7), m: T(51 + i * 3.6, py + 4.2, -72.6) });
    const cityGeo = mergeParts([...boxes, ...pal]);
    const cityM = solid(cityGeo, mSilh, 1.3);
    this.night.add(cityM);
    // 宮殿正面的窗
    for (let k = 0; k < 5; k++) wins.push({ x: 53 + k * 3.5, y: py + 5.2, z: -72.9, th: 0.02 + rnd() * 0.98 });
    wins.push({ x: 46.5, y: py + 12, z: -72.4, th: 0.4 }, { x: 73.5, y: py + 12, z: -72.4, th: 0.7 });

    const winMat = glowMat({ hatch: 0.25 });
    const winMesh = new InstancedMesh(new PlaneGeometry(1, 1.3), winMat, wins.length);
    winMesh.frustumCulled = false;
    wins.forEach((w, i) => {
      _dummy.position.set(w.x, w.y, w.z);
      _dummy.rotation.set(0, 0, 0);
      _dummy.scale.set(1, 1, 1);
      _dummy.updateMatrix();
      winMesh.setMatrixAt(i, _dummy.matrix);
      _col.setRGB(w.th, 0, 0);
      winMesh.setColorAt(i, _col);
    });
    this.night.add(winMesh);

    // 火炬
    const torchM = glowMat({ on: '#f0c46a', edge: '#b24a14', hatch: 0.9, flick: 0.35 });
    const tg = solid(torchGeo(), mSilh, 1.5);
    for (const x of [51.5, 68.5]) {
      const t = tg.clone();
      t.position.set(x, py, -69.5);
      this.night.add(t);
      const fl = new Mesh(flameGeo(), torchM);
      fl.position.set(x, py + 1.8, -69.5);
      fl.scale.setScalar(6);
      this.night.add(fl);
    }
    return { winMat, torchMat: torchM };
  }

  // ------------------------------------------------------------- 近景的埃及人家
  private buildNearEgypt(mMud: ShaderMaterial, mSilh: ShaderMaterial): void {
    const g = new Group();
    g.position.set(47.5, 0, -22);
    g.rotation.y = 0.38;
    g.scale.setScalar(1.5);
    const w = 7;
    const h = 3.5;
    const d = 5.2;
    const td = 1.5;
    const wx0 = -2.2;
    const wx1 = -0.55;
    const sill = 0.7;
    const top = 2.45;
    const parts: Part[] = [
      { g: new BoxGeometry(wx0 + w / 2, h, td), m: T((wx0 - w / 2) / 2, h / 2, -td / 2) },
      { g: new BoxGeometry(w / 2 - wx1, h, td), m: T((wx1 + w / 2) / 2, h / 2, -td / 2) },
      { g: new BoxGeometry(wx1 - wx0, sill, td), m: T((wx0 + wx1) / 2, sill / 2, -td / 2) },
      { g: new BoxGeometry(wx1 - wx0, h - top, td), m: T((wx0 + wx1) / 2, top + (h - top) / 2, -td / 2) },
      { g: new BoxGeometry(w, h, d - td), m: T(0, h / 2, -td - (d - td) / 2) },
      { g: new BoxGeometry(w + 0.3, 0.22, d + 0.3), m: T(0, h + 0.1, -d / 2) },
    ];
    g.add(solid(mergeParts(parts), mMud, 2.6));
    const wcx = (wx0 + wx1) / 2;
    const room = new Mesh(new PlaneGeometry(wx1 - wx0 + 0.2, top - sill + 0.2), glowMat({ hatch: 0.7, edge: '#2a1c0a' }));
    room.position.set(wcx, (sill + top) / 2, -td + 0.02);
    g.add(room);
    // 床與俯身的人影
    const mBed = litMat({ base: '#6e5433', angle: 70, space: 4.4 });
    const bed = solid(bedGeo(), mBed, 1.6);
    bed.position.set(wcx + 0.05, 0.2, -0.95);
    g.add(bed);
    const bender = solid(personGeo({ bow: 0.95, armL: [0.9, 0.15], armR: [0.9, 0.15], wrap: true }), mSilh, 2.0);
    bender.position.set(wcx - 0.12, 0, -0.45);
    bender.rotation.y = Math.PI;
    g.add(bender);
    this.night.add(g);
  }

  // ------------------------------------------------------------- 出埃及的隊伍
  private buildProcession(): void {
    const rnd = mulberry32(77);
    const mP = litMat({ base: FIXED.ochre, parts: ['#a88758', '#14110e', '#2b2218', '#4e3a22', '#14110e', '#d8cdb4'], partAlt: '#cdbf9e', angle: 40, space: 4.4, seed: 14 });
    const mSheep = litMat({ base: 'paper', parts: ['#e9e1cc', '#14110e'], angle: 50, space: 4.4, seed: 15 });
    const mCow = litMat({ base: '#6b5030', parts: ['#6b5030', '#14110e'], angle: 50, space: 4.4, seed: 16 });
    const mk = (geo: BufferGeometry, mat: ShaderMaterial, n: number, outline: number) => {
      const r = solidInstanced(geo, mat, n, outline);
      this.procG.add(r.group);
      return r.main;
    };
    const A: PersonOpts = { bundle: true, staff: false, belt: true, armL: [0.1, 0.15], armR: [0.55, 0.1], low: true };
    const B: PersonOpts = { staff: true, staffSide: 'R', belt: true, armL: [0.2, 0.15], armR: [0.35, 0.15], low: true };
    const peopleA = mk(personGeo(A), mP, 22, 1.8);
    const peopleB = mk(personGeo(B), mP, 18, 1.8);
    const sheep = mk(lambGeo(true), mSheep, 22, 1.5);
    const cattle = mk(cattleGeo(true), mCow, 8, 1.5);
    const mkItems = (n: number, startX: number, gap: number, zLo: number, zHi: number, scLo: number, scHi: number) => {
      const out: { x0: number; z: number; ph: number; sc: number }[] = [];
      for (let i = 0; i < n; i++) out.push({ x0: startX + i * gap + rnd() * gap * 0.8, z: zLo + rnd() * (zHi - zLo), ph: rnd() * 6.28, sc: scLo + rnd() * (scHi - scLo) });
      return out;
    };
    this.procPeople.push({ mesh: peopleA, items: mkItems(22, 3, 4.4, 6.8, 9.4, 0.95, 1.06) });
    this.procPeople.push({ mesh: peopleB, items: mkItems(18, 4.2, 5.2, 4.8, 7.2, 0.95, 1.08) });
    this.procAnimals.push({ mesh: sheep, items: mkItems(22, 2, 4.4, 8.2, 10.6, 0.85, 1.15) });
    this.procAnimals.push({ mesh: cattle, items: mkItems(8, 6, 12, 4.4, 6.2, 0.95, 1.1) });
  }

  private buildFarLine(): { group: Group; mesh: InstancedMesh } {
    const mSil = litMat({ base: 'silh' });
    const g = new Group();
    const r = solidInstanced(personGeo({ bundle: true, belt: false, low: true, tiny: true }), mSil, 70, 0);
    g.add(r.group);
    const rnd = mulberry32(5);
    for (let i = 0; i < 70; i++) {
      _dummy.position.set(-150 + i * 1.5 + rnd() * 0.5, 0, -150 - rnd() * 4);
      _dummy.rotation.set(0, -Math.PI / 2, 0);
      _dummy.scale.setScalar(2.4);
      _dummy.updateMatrix();
      r.main.setMatrixAt(i, _dummy.matrix);
    }
    r.main.instanceMatrix.needsUpdate = true;
    g.visible = false;
    return { group: g, mesh: r.main };
  }

  // ------------------------------------------------------------- 日後
  private buildDay(mMud: ShaderMaterial, mWood: ShaderMaterial, mSilh: ShaderMaterial): void {
    void mSilh;
    const g = this.day;
    g.position.set(OX, 0, 0);
    // 主屋與兩側鄰居
    const frameG = doorFrameGeo();
    const body = houseBodyGeo({ w: 6.6, h: 3.2, d: 5, doorX: 0, tunnel: 1.6 });
    g.add(solid(body, mMud, 2.6));
    g.add(solid(frameG, mWood, 2.0));
    const glow = new Mesh(new PlaneGeometry(1.5, 2.3), this.doorGlowMat);
    glow.position.set(0, 1.15, -1.58);
    g.add(glow);
    const l = houseBodyGeo({ w: 6, h: 2.9, d: 4.6, doorX: 1.4, tunnel: 1.6 });
    const left = solid(l, mMud, 2.6);
    left.position.set(-7.4, 0, -0.4);
    g.add(left);
    const r = houseBodyGeo({ w: 5.6, h: 3.4, d: 4.6 });
    const right = solid(r, mMud, 2.6);
    right.position.set(7.2, 0, -0.8);
    g.add(right);
    // 父親與孩子：背對鏡頭看著門框
    const mFather = litMat({ base: FIXED.ochre, parts: ['#a88758', '#14110e', '#2b2218', '#4e3a22', '#14110e', '#d8cdb4'], angle: 40, space: 4.4, seed: 17 });
    const mChild = litMat({ base: FIXED.ochre, parts: ['#cdbf9e', '#14110e', '#3a2e22', '#4e3a22', '#14110e', '#d8cdb4'], angle: 40, space: 4.4, seed: 18 });
    const father = solid(personGeo({ staff: true, staffSide: 'R', belt: true, slim: true, armL: [0.25, 0.14], armR: [0.5, 0.12] }), mFather, 2.4);
    father.position.set(0.95, 0, 2.3);
    father.rotation.y = Math.PI - 0.35;
    g.add(father);
    const child = solid(personGeo({ scale: 0.56, armL: [0.35, 0.95], armR: [1.45, 0.45], wrap: true }), mChild, 2.2);
    child.position.set(0.25, 0, 2.4);
    child.rotation.y = Math.PI + 0.1;
    g.add(child);
    g.visible = false;
  }

  // ------------------------------------------------------------- 每幀
  /**
   * 設定鏡頭（含 fitW 的寬度保證與微漂移）、月亮、光線、天空。
   * panel：meal 分格在畫面上的位置（CSS px）；沒有分格時傳 null。
   */
  updateScene(fr: Frame, tr: TrackOut, W: number, H: number, panel: { x: number; y: number; w: number; h: number } | null): void {
    const s = fr.s;
    const aspect = W / Math.max(H, 1);
    const cam = this.camera;
    const c = tr.cam;
    const mobileUI = W <= 720;
    // 以 view offset 平移整個畫面（不動鏡頭本身）：shiftPx > 0 把畫面推向右，shiftY > 0 把畫面推向上
    let shiftPx = 0;
    let shiftY = 0;
    if (mobileUI) shiftY = upShiftAt(s) * H;
    const aw = mobileUI ? 0 : smooth(1.05, 1.3, aspect);
    if (aw > 0) {
      // 塗血那一拍：說明框固定在左邊，門＋盆＋把手整組擺在右側
      const wH = aw * smooth(4.6, 5.15, s) * (1 - smooth(6.0, 6.3, s));
      if (wH > 0) {
        const left = W * 0.47;
        const right = W - Math.max(140, W * 0.1);
        const span = 3.9;
        const pxm = Math.max(120, right - left) / span;
        const fv = 40;
        const dist = W / pxm / (2 * Math.tan(fv * 0.5 * RAD) * aspect);
        const P = DESK_HYSSOP;
        P[0] = 0.22;
        P[1] = 1.5;
        P[2] = dist;
        P[3] = 0.05;
        P[4] = 1.22;
        P[5] = 0;
        P[6] = fv;
        P[7] = 0;
        for (let i = 0; i < 8; i++) c[i] = lerp(c[i], P[i], wH);
        shiftPx += wH * ((left + right) * 0.5 - W * 0.5);
      }
      // 日後：說明框改放左邊，父子與門框往右偏
      const wC = aw * smooth(11.7, 11.97, s);
      shiftPx += wC * W * 0.1;
    }
    // 吃羊羔：DOM 分格是「屋內」，有血的那扇門整個擺在分格正下方（桌機）／分格與說明框之間（手機）
    const wM = smooth(6.75, 7.25, s) * (1 - smooth(7.85, 8.3, s));
    if (wM > 0) {
      const panelBottom = panel ? panel.y + panel.h : H * 0.5;
      const panelCx = panel ? panel.x + panel.w * 0.5 : W * 0.5;
      const floorY = mobileUI ? H * 0.615 : H - 22;
      const pxm = clamp((floorY - panelBottom) / 2.95, 26, 90);
      const fv = 40;
      const dist = H / (2 * pxm * Math.tan(fv * 0.5 * RAD));
      const P = DESK_MEAL;
      P[0] = 0;
      P[1] = 1.6;
      P[2] = dist;
      P[3] = 0;
      P[4] = 1.6;
      P[5] = 0;
      P[6] = fv;
      P[7] = 0;
      for (let i = 0; i < 8; i++) c[i] = lerp(c[i], P[i], wM);
      // 地面線要落在 floorY：沒位移時地面在 H/2 + 1.6·pxm
      const needDown = floorY - (H * 0.5 + 1.6 * pxm);
      shiftY = lerp(shiftY, -needDown, wM);
      shiftPx += wM * (panelCx - W * 0.5);
    }
    const drift = fr.motionOff ? 0 : 1;
    const dx = Math.sin(fr.time * 0.31) * 0.05 * drift;
    const dy = Math.sin(fr.time * 0.23 + 1.3) * 0.035 * drift;
    let px = c[0] + dx;
    let py = c[1] + dy;
    let pz = c[2];
    const tx = c[3];
    const ty = c[4] + dy * 0.5;
    const tz = c[5];
    const fov = c[6];
    const fitW = c[7];
    if (fitW > 0) {
      const dX = px - tx;
      const dY = py - ty;
      const dZ = pz - tz;
      const dist = Math.hypot(dX, dY, dZ);
      const need = fitW * 0.5 / (Math.tan(fov * 0.5 * RAD) * aspect);
      if (dist < need) {
        const k = need / dist;
        px = tx + dX * k;
        py = ty + dY * k;
        pz = tz + dZ * k;
      }
    }
    cam.fov = fov;
    cam.aspect = aspect;
    cam.position.set(px, py, pz);
    cam.lookAt(tx, ty, tz);
    if (Math.abs(shiftPx) > 0.5 || Math.abs(shiftY) > 0.5) cam.setViewOffset(W, H, -shiftPx, shiftY, W, H);
    else if (cam.view !== null) cam.clearViewOffset();
    cam.updateProjectionMatrix();
    cam.updateMatrixWorld();

    // 光線
    const L = tr.light;
    U.uLightDir.value.set(L[0], L[1], L[2]).normalize();
    U.uAmb.value = L[3];
    U.uGain.value = L[4];
    U.uWind.value = fr.motionOff ? 0 : 0.34;

    // 天空
    const sk = this.skyM.uniforms;
    (sk.uInvProj.value as Matrix4).copy(cam.projectionMatrixInverse);
    (sk.uCamWorld.value as Matrix4).copy(cam.matrixWorld);
    sk.uHorizon.value = tr.sky[0];
    sk.uStars.value = tr.sky[1];
    sk.uSkyDay.value = tr.sky[2];
    sk.uTwinkle.value = fr.motionOff ? 0 : 1;

    // 月亮：方位角／仰角是世界固定的方向；相位由 day 決定，光源方向在視圖空間
    const az = tr.moon[0];
    const el = tr.moon[1] * RAD;
    const ang = tr.moon[2] * RAD;
    _v.set(Math.sin(az) * Math.cos(el), Math.sin(el), -Math.cos(az) * Math.cos(el));
    let angUse = ang;
    const wMoon = mobileUI ? tr.moonS[0] : 0;
    if (wMoon > 0.001) {
      // 手機：依指定的畫面位置反推方向（要扣掉 view offset 的位移）
      const e = cam.matrixWorld.elements;
      const tanV = Math.tan(cam.fov * 0.5 * RAD);
      const xN = tr.moonS[1] * 2 - 1;
      const yN = 1 - 2 * (tr.moonS[2] + shiftY / H);
      _m.set(
        -e[8] + e[0] * xN * tanV * aspect + e[4] * yN * tanV,
        -e[9] + e[1] * xN * tanV * aspect + e[5] * yN * tanV,
        -e[10] + e[2] * xN * tanV * aspect + e[6] * yN * tanV,
      ).normalize();
      _v.lerp(_m, wMoon).normalize();
      angUse = lerp(ang, ang * 0.8, wMoon);
    }
    this.moon.position.copy(cam.position).addScaledVector(_v, MOON_R);
    const r = MOON_R * Math.tan(angUse / 2);
    this.moon.scale.setScalar(r);
    this.moonHull.position.copy(this.moon.position);
    this.moonHull.scale.setScalar(r);
    const showMoon = tr.sky[2] < 0.5;
    this.moon.visible = showMoon;
    this.moonHull.visible = showMoon;
    const dayN = clamp((story.day - 1) / 13);
    const th = lerp(0.3 * Math.PI, Math.PI, dayN);
    (this.moonM.uniforms.uLightV.value as Vector3).set(Math.sin(th), 0.28 * (1 - dayN), -Math.cos(th));

    // 夜與日兩個世界的可見性
    const dayView = s >= DAY_S;
    this.night.visible = !dayView;
    this.day.visible = dayView;
  }

  updateObjects(fr: Frame): void {
    const s = fr.s;
    const dt = fr.dt;
    const idx = fr.idx;

    // ---- 門：時間追蹤，播放不受 motionOff 影響
    const target = idx >= CUE_IDX['door-shut'] && s < DAY_S ? 1 : 0;
    const prevD = this.doorD;
    this.doorD = clamp(this.doorD + Math.sign(target - this.doorD) * (dt / 0.95), 0, 1);
    if (Math.abs(this.doorD - target) < 1e-4) this.doorD = target;
    let busy = this.doorD !== target;
    if (this.doorD >= 1 && prevD < 1 && !this.shutFired) {
      this.shutFired = true;
      this.onShut();
    }
    if (this.doorD < 0.5) this.shutFired = false;

    // ---- 血跡
    const marksOn = idx >= HYSSOP_IDX && s < DAY_S;
    const hy = story.hyssop;
    this.doneTimer = marksOn && hy.done ? this.doneTimer + dt : 0;
    for (let i = 0; i < this.houses.length; i++) {
      const hh = this.houses[i];
      // 門板與人影
      const Di = i === 0 ? this.doorD : clamp(this.doorD * 1.5 - 0.5 * hh.d, 0, 1);
      const ang = 1.65 * (1 - smooth(0.2, 1, Di));
      hh.leafPivot.rotation.y = ang;
      // 血跡
      if (i === 0) {
        for (let k = 0; k < 3; k++) {
          const dr = hh.decals[k];
          const want = marksOn && hy.marks[PARTS[k]] ? 1 : 0;
          dr.grow = clamp(dr.grow + (want ? dt / 0.3 : -dt / 0.12) * (want || dr.grow > 0 ? 1 : 0), 0, 1);
          dr.mesh.visible = dr.grow > 0.001;
          dr.mat.uniforms.uGrow.value = dr.grow;
          if (dr.grow !== want) busy = true;
        }
      } else {
        hh.markT = marksOn && hy.done ? clamp((this.doneTimer - hh.delay) / 0.5, 0, 1) : 0;
        if (marksOn && hy.done && hh.markT < 1) busy = true;
        for (let k = 0; k < 3; k++) {
          const dr = hh.decals[k];
          dr.grow = clamp(hh.markT * 1.7 - k * 0.3, 0, 1);
          dr.mesh.visible = dr.grow > 0.001;
          dr.mat.uniforms.uGrow.value = dr.grow;
        }
      }
    }
    this.busy = busy;
    this.spillMat.uniforms.uOn.value = 1 - 0.55 * smooth(0.3, 1, this.doorD);
    // 主角家門內的人影：關門前先退進屋裡
    this.doorwayPerson.position.z = -0.35 - 1.05 * smooth(0, 0.45, this.doorD);
    this.doorwayPerson.visible = this.doorD < 0.999 && s < DAY_S;

    // ---- 麥田分群（控制三角形數）
    const field = s < DAY_S;
    this.barleyGroups[0].visible = s < 3.3;
    this.barleyGroups[1].visible = field && (s < 4.3 || s >= 7.6);
    this.barleyGroups[2].visible = field && (s < 4.3 || s >= 7.6);

    // ---- 羊羔：十四日黃昏被牽走
    const lg = smooth(3.8, 4.05, s);
    this.lamb.visible = lg < 0.999;
    this.lambProps.visible = lg < 0.999;
    this.lamb.position.x = 1.95 + 7 * lg;
    this.lamb.scale.setScalar(1 - lg);

    // ---- 埃及城：窗一扇一扇熄燈、火炬熄滅
    this.winMat.uniforms.uOff.value = windowOff(s);
    this.torchMat.uniforms.uOn.value = torchOn(s);
    this.torchMat.uniforms.uFlick.value = fr.motionOff ? 0 : 0.35;

    // ---- 隊伍
    const procOn = s >= 9.85 && s < DAY_S;
    this.procG.visible = procOn;
    if (procOn) this.updateProcession(s);
    this.farLine.visible = s >= 10.55 && s < DAY_S;
    if (this.farLine.visible) {
      const k = smooth(10.55, 11.0, s);
      this.farLine.scale.set(1, k, 1);
      this.farLine.position.x = -1.5 * (s - 10.55);
    }
  }

  private updateProcession(s: number): void {
    const dist = departDist(s);
    for (let k = 0; k < this.procPeople.length; k++) this.moveGroup(this.procPeople[k].mesh, this.procPeople[k].items, 0.07, false, dist);
    for (let k = 0; k < this.procAnimals.length; k++) this.moveGroup(this.procAnimals[k].mesh, this.procAnimals[k].items, 0.04, true, dist);
  }

  private moveGroup(mesh: InstancedMesh, items: { x0: number; z: number; ph: number; sc: number }[], bob: number, animal: boolean, dist: number): void {
    const stride = 0.78;
    for (let i = 0; i < items.length; i++) {
      const it = items[i];
      const phase = dist / stride + it.ph;
      _dummy.position.set(it.x0 - dist, Math.abs(Math.sin(phase)) * bob, it.z);
      _dummy.rotation.set(0, -Math.PI / 2 + (animal ? 0 : 0.05), Math.sin(phase) * (animal ? 0.03 : 0.045));
      _dummy.scale.setScalar(it.sc);
      _dummy.updateMatrix();
      mesh.setMatrixAt(i, _dummy.matrix);
    }
    mesh.instanceMatrix.needsUpdate = true;
  }
  get farLineRef(): InstancedMesh {
    return this.farLineMesh;
  }

  dispose(): void {
    this.scene.traverse((o) => {
      const m = o as Mesh;
      if (m.geometry) m.geometry.dispose();
      const mat = m.material as ShaderMaterial | ShaderMaterial[] | undefined;
      if (Array.isArray(mat)) mat.forEach((x) => x.dispose());
      else if (mat) mat.dispose();
    });
  }
}



















