import * as THREE from 'three';
import type { SiteData } from '../data/types';
import { buildCoffinModel } from './props';
import { stations } from './stations';

const SHECHEM_LON = 35.288;
const SHECHEM_LAT = 32.214;
const DEG_LAT_M = 6.2;
const DEG_LON_M = DEG_LAT_M * Math.cos((SHECHEM_LAT * Math.PI) / 180);

/** 將經緯度投影至以示劍 (0, 0) 為原點的 3D 記憶地圖平面 (+X 東, -Z 北, +Z 南) */
export function lonLatToMapXZ(lon: number, lat: number): [number, number] {
  const x = (lon - SHECHEM_LON) * DEG_LON_M;
  const z = -(lat - SHECHEM_LAT) * DEG_LAT_M;
  return [x, z];
}

export interface MemoryMapHandle {
  group: THREE.Group;
  coffinMarker: THREE.Group;
  coffinWorldPos: THREE.Vector3;
  coffinVisible: boolean;
  setVisibility(alpha: number): void;
  update(
    cue: string,
    beatProgress: number,
    onlyI: boolean,
    sameGive: boolean,
    dark: boolean,
    time: number,
    motionOff: boolean,
  ): void;
  applyReliefImage(img: HTMLImageElement): void;
  stationFlight(index: number, progress: number, verse: number, onlyI: boolean): THREE.Vector3;
}

export function createMemoryMap(data: SiteData): MemoryMapHandle {
  const group = new THREE.Group();
  group.name = 'jos_memory_map';
  group.position.y = 0.28;
  group.visible = false;

  const bbox = data.geo.wide.bbox; // w:28.5, e:48.0, s:26.5, n:38.5
  const [xMin, zMax] = lonLatToMapXZ(bbox.w, bbox.s);
  const [xMax, zMin] = lonLatToMapXZ(bbox.e, bbox.n);
  const mapW = xMax - xMin;
  const mapD = zMax - zMin;
  const centerX = (xMin + xMax) / 2;
  const centerZ = (zMin + zMax) / 2;

  const texCanvas = document.createElement('canvas');
  texCanvas.width = 2048;
  texCanvas.height = 1536;
  const ctx = texCanvas.getContext('2d')!;
  let reliefImg: HTMLImageElement | null = null;
  let lastDarkState: boolean | null = null;

  const mapTexture = new THREE.CanvasTexture(texCanvas);
  mapTexture.colorSpace = THREE.SRGBColorSpace;
  mapTexture.anisotropy = 4;

  function toPx(lon: number, lat: number): [number, number] {
    const u = (lon - bbox.w) / (bbox.e - bbox.w);
    const v = (bbox.n - lat) / (bbox.n - bbox.s);
    return [u * texCanvas.width, v * texCanvas.height];
  }

  function redrawMapCanvas(dark: boolean): void {
    const W = texCanvas.width;
    const H = texCanvas.height;

    // 1. 海面底色
    ctx.fillStyle = dark ? '#14130f' : '#cfc2a6';
    ctx.fillRect(0, 0, W, H);

    // 海面細微橫向版畫水紋
    ctx.strokeStyle = dark ? 'rgba(235,227,210,0.04)' : 'rgba(30,27,22,0.05)';
    ctx.lineWidth = 1;
    for (let y = 8; y < H; y += 14) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(W, y);
      ctx.stroke();
    }

    // 2. 陸地多邊形裁切＋羊皮紙底色＋（若有）真實高程暈渲疊加
    ctx.save();
    ctx.beginPath();
    for (const poly of data.geo.wide.land) {
      for (const ring of poly) {
        ring.forEach(([lon, lat], idx) => {
          const [px, py] = toPx(lon, lat);
          if (idx === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        });
        ctx.closePath();
      }
    }
    ctx.fillStyle = dark ? '#242018' : '#e8dec9';
    ctx.fill();

    if (reliefImg) {
      ctx.clip();
      ctx.globalAlpha = dark ? 0.36 : 0.62;
      ctx.globalCompositeOperation = dark ? 'soft-light' : 'multiply';
      ctx.drawImage(reliefImg, 0, 0, W, H);
      ctx.globalAlpha = 1;
      ctx.globalCompositeOperation = 'source-over';
    }
    ctx.restore();

    // 3. 海岸墨線
    ctx.strokeStyle = dark ? 'rgba(235,227,210,0.52)' : 'rgba(30,27,22,0.62)';
    ctx.lineWidth = 2.2;
    for (const poly of data.geo.wide.land) {
      for (const ring of poly) {
        ctx.beginPath();
        ring.forEach(([lon, lat], idx) => {
          const [px, py] = toPx(lon, lat);
          if (idx === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        });
        ctx.closePath();
        ctx.stroke();
      }
    }

    // 4. 內陸湖泊（加利利海、死海等）
    ctx.fillStyle = dark ? '#182229' : '#b8c3be';
    ctx.strokeStyle = dark ? 'rgba(235,227,210,0.45)' : 'rgba(30,27,22,0.55)';
    ctx.lineWidth = 1.6;
    for (const lk of data.geo.wide.lakes) {
      ctx.beginPath();
      for (const ring of lk.rings) {
        ring.forEach(([lon, lat], idx) => {
          const [px, py] = toPx(lon, lat);
          if (idx === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        });
        ctx.closePath();
      }
      ctx.fill();
      ctx.stroke();
    }

    // 5. 河流（幼發拉底河、底格里斯河、尼羅河、約但河等）
    ctx.strokeStyle = dark ? 'rgba(138,168,184,0.68)' : 'rgba(62,86,98,0.72)';
    ctx.lineWidth = 2.4;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    for (const rv of data.geo.wide.rivers) {
      if (rv.pts.length < 2) continue;
      ctx.beginPath();
      rv.pts.forEach(([lon, lat], idx) => {
        const [px, py] = toPx(lon, lat);
        if (idx === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      });
      ctx.stroke();
    }

    // 6. 經緯度細格線
    ctx.strokeStyle = dark ? 'rgba(235,227,210,0.07)' : 'rgba(30,27,22,0.08)';
    ctx.lineWidth = 1;
    for (let lon = 30; lon <= 46; lon += 2) {
      const [px] = toPx(lon, 32);
      ctx.beginPath();
      ctx.moveTo(px, 0);
      ctx.lineTo(px, H);
      ctx.stroke();
    }
    for (let lat = 28; lat <= 38; lat += 2) {
      const [, py] = toPx(35, lat);
      ctx.beginPath();
      ctx.moveTo(0, py);
      ctx.lineTo(W, py);
      ctx.stroke();
    }

    // 7. 主要地名墨字標記（直接繪在羊皮紙底圖上，清晰雅致、不重疊）
    const labels: { text: string; lon: number; lat: number; big?: boolean; italic?: boolean }[] = [
      { text: '大河那邊（幼發拉底河）', lon: 41.2, lat: 35.4, big: true },
      { text: '吾珥', lon: 46.1, lat: 30.65 },
      { text: '哈蘭', lon: 39.03, lat: 37.25 },
      { text: '迦南地', lon: 34.85, lat: 32.55, big: true },
      { text: '示劍', lon: 34.5, lat: 32.0 }, // 只移底圖文字，讓出棺材模型與行軍路線；地點座標不變。
      { text: '耶利哥', lon: 36.15, lat: 32.12 }, // 標籤向東北避開金色小燈與說明框；地點與燈的座標不變。
      { text: '摩押', lon: 36.15, lat: 31.42 },
      { text: '西珥山', lon: 35.65, lat: 30.22 },
      { text: '埃及', lon: 31.1, lat: 30.35, big: true },
      { text: '紅海', lon: 32.85, lat: 29.35 },
      { text: '曠野（許多年日）', lon: 33.85, lat: 29.55 },
      { text: '地中海', lon: 32.2, lat: 33.6, italic: true },
    ];

    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    for (const lb of labels) {
      const [px, py] = toPx(lb.lon, lb.lat);
      ctx.font = `${lb.big ? '700 26px' : '600 20px'} "Noto Serif TC", serif`;
      ctx.fillStyle = dark ? 'rgba(235,227,210,0.86)' : 'rgba(30,27,22,0.84)';
      ctx.fillText(lb.text, px, py);
    }

    mapTexture.needsUpdate = true;
  }

  redrawMapCanvas(false);

  const boardMat = new THREE.MeshStandardMaterial({
    map: mapTexture,
    roughness: 0.95,
    metalness: 0.0,
    transparent: true,
    opacity: 1,
  });
  const boardMesh = new THREE.Mesh(new THREE.PlaneGeometry(mapW, mapD, 1, 1), boardMat);
  boardMesh.rotation.x = -Math.PI / 2;
  boardMesh.position.set(centerX, 0, centerZ);
  boardMesh.receiveShadow = true;
  group.add(boardMesh);

  // ---- 歷史路線折點（從吾珥→哈蘭→示劍→希伯崙→埃及→紅海→曠野→摩押→耶利哥→示劍） ----
  function pXZ(placeId: string): THREE.Vector3 {
    const pl = data.places[placeId];
    if (!pl) return new THREE.Vector3(0, 0.14, 0);
    const [x, z] = lonLatToMapXZ(pl.lon, pl.lat);
    return new THREE.Vector3(x, 0.14, z);
  }

  const flightStops = stations.map(s => pXZ(s.place));
  const flightPosition = new THREE.Vector3();
  const curvePts = flightStops;
  const routeCurve = new THREE.CatmullRomCurve3(curvePts, false, 'catmullrom', 0.35);
  const TOTAL_SAMPLES = 240;
  const sampledPts = routeCurve.getPoints(TOTAL_SAMPLES);
  const routeGeo = new THREE.BufferGeometry().setFromPoints(sampledPts);
  routeGeo.setDrawRange(0, 2);

  const routeMat = new THREE.LineBasicMaterial({
    color: '#d8a44f',
    transparent: true,
    opacity: 0.9,
  });
  const routeLine = new THREE.Line(routeGeo, routeMat);
  group.add(routeLine);

  // ---- 20 盞「神說『我』」的金色小燈 (--jos-lamp) ----
  const lampGroup = new THREE.Group();
  interface LampRecord {
    verse: number;
    root: THREE.Group;
    flame: THREE.Mesh;
    pillar: THREE.Mesh;
    halo: THREE.Mesh;
  }
  const lamps: LampRecord[] = [];
  const lampCountPerPlace = new Map<string, number>();

  for (const verb of data.step.oneCsVerbs) {
    const countHere = lampCountPerPlace.get(verb.placeId) ?? 0;
    lampCountPerPlace.set(verb.placeId, countHere + 1);

    const base = pXZ(verb.placeId);
    // 同一地點多個 1cs 動詞以黃金角微幅散開，20 盞燈顆顆可辨
    const goldenAngle = countHere * 2.39996;
    const spread = countHere === 0 ? 0 : 0.62 + countHere * 0.26;
    const lx = base.x + Math.cos(goldenAngle) * spread;
    const lz = base.z + Math.sin(goldenAngle) * spread;

    const lRoot = new THREE.Group();
    lRoot.position.set(lx, 0.16, lz);

    const flame = new THREE.Mesh(
      new THREE.SphereGeometry(0.26, 12, 10),
      new THREE.MeshBasicMaterial({ color: '#e0aa4c', transparent: true, opacity: 0 }),
    );
    flame.position.y = 0.25;
    lRoot.add(flame);

    const pillar = new THREE.Mesh(
      new THREE.CylinderGeometry(0.06, 0.18, 2.6, 10),
      new THREE.MeshBasicMaterial({
        color: '#e0aa4c',
        transparent: true,
        opacity: 0,
        depthWrite: false,
      }),
    );
    pillar.position.y = 1.3;
    lRoot.add(pillar);

    const halo = new THREE.Mesh(
      new THREE.RingGeometry(0.32, 0.56, 20),
      new THREE.MeshBasicMaterial({
        color: '#b5832a',
        transparent: true,
        opacity: 0,
        side: THREE.DoubleSide,
        depthWrite: false,
      }),
    );
    halo.rotation.x = -Math.PI / 2;
    halo.position.y = 0.03;
    lRoot.add(halo);

    lampGroup.add(lRoot);
    lamps.push({ verse: verb.verse, root: lRoot, flame, pillar, halo });
  }
  group.add(lampGroup);

  // ---- 7 處「同一個『給』」(H5414) 橄欖金圓環 ----
  const givePlaces = ['canaan-walk', 'seir', 'egypt', 'heshbon', 'jericho', 'shechem', 'ephraim-hill'];
  const giveRings: THREE.Mesh[] = givePlaces.map((pid, idx) => {
    const p = pXZ(pid);
    const ring = new THREE.Mesh(
      new THREE.RingGeometry(0.55 + (idx % 2) * 0.12, 0.78 + (idx % 2) * 0.12, 24),
      new THREE.MeshBasicMaterial({
        color: '#6e874c',
        transparent: true,
        opacity: 0,
        side: THREE.DoubleSide,
      }),
    );
    ring.rotation.x = -Math.PI / 2;
    ring.position.set(p.x, 0.2, p.z);
    group.add(ring);
    return ring;
  });

  // ---- 約瑟的棺材記號（規則 1 前因後果：第4節末在埃及出現，一路隨隊伍到示劍） ----
  const coffinMarker = buildCoffinModel(0.75);
  coffinMarker.visible = false;
  group.add(coffinMarker);
  const coffinWorldPos = new THREE.Vector3();
  let coffinVisible = false;

  // 棺材行進專線（埃及 → 蘭塞 → 紅海 → 西乃 → 加低斯 → 摩押 → 耶利哥 → 示劍）
  const coffinCurve = new THREE.CatmullRomCurve3(
    [
      pXZ('egypt'),
      pXZ('rameses'),
      pXZ('redsea'),
      pXZ('sinai'),
      pXZ('kadesh'),
      pXZ('moab'),
      pXZ('jericho'),
      pXZ('shechem'),
    ],
    false,
    'catmullrom',
    0.35,
  );

  const CUE_ROUTE_FRAC: Record<string, [number, number, number]> = {
    'beyond-river': [0.0, 0.08, 2],
    abraham: [0.08, 0.37, 4],
    egypt: [0.37, 0.63, 7],
    east: [0.63, 0.82, 10],
    jericho: [0.82, 0.95, 12],
    gifts: [0.95, 1.0, 13],
    'family-2': [1.0, 1.0, 13],
  };

  const COFFIN_FRAC: Record<string, [number, number]> = {
    abraham: [0, 0],
    egypt: [0.0, 0.52],
    east: [0.52, 0.78],
    jericho: [0.78, 0.96],
    gifts: [0.96, 1.0],
    'family-2': [1.0, 1.0],
  };

  return {
    group,
    coffinMarker,
    coffinWorldPos,
    get coffinVisible() {
      return coffinVisible;
    },
    setVisibility(alpha: number) {
      const a = Math.max(0, Math.min(1, alpha));
      group.visible = a > 0.01;
      boardMat.opacity = a;
      routeMat.opacity = a * 0.92;
    },
    update(cue, beatProgress, onlyI, sameGive, dark, time, motionOff) {
      if (lastDarkState !== dark) {
        lastDarkState = dark;
        redrawMapCanvas(dark);
      }
      if (!group.visible) {
        coffinVisible = false;
        return;
      }

      const [r0, r1, maxVerse] = CUE_ROUTE_FRAC[cue] ?? [1, 1, 13];
      const frac = r0 + (r1 - r0) * beatProgress;
      const drawCount = Math.max(2, Math.round(frac * TOTAL_SAMPLES));
      routeGeo.setDrawRange(0, drawCount);

      // 20 盞「神說『我』」的燈
      const pulse = motionOff ? 1 : 0.92 + Math.sin(time * 2.8) * 0.08;
      for (const lp of lamps) {
        const reached = lp.verse <= maxVerse;
        const fMat = lp.flame.material as THREE.MeshBasicMaterial;
        const pMat = lp.pillar.material as THREE.MeshBasicMaterial;
        const hMat = lp.halo.material as THREE.MeshBasicMaterial;

        if (onlyI) {
          fMat.opacity = 0.98;
          pMat.opacity = 0.52 * pulse;
          hMat.opacity = 0.78 * pulse;
          lp.flame.scale.setScalar(1.35 * pulse);
        } else if (reached) {
          fMat.opacity = 0.84;
          pMat.opacity = lp.verse === maxVerse ? 0.28 : 0.08;
          hMat.opacity = 0.45;
          lp.flame.scale.setScalar(1.0);
        } else {
          fMat.opacity = 0.12;
          pMat.opacity = 0;
          hMat.opacity = 0;
          lp.flame.scale.setScalar(0.75);
        }
      }

      // 7 處「同一個『給』」圓環
      for (const gr of giveRings) {
        const gMat = gr.material as THREE.MeshBasicMaterial;
        gMat.opacity = sameGive ? 0.85 * pulse : 0;
      }

      // 約瑟棺材記號：第4節後半出現於埃及，第5節起跟著隊伍走完曠野進入迦南
      if (cue in COFFIN_FRAC && (cue !== 'abraham' || beatProgress > 0.62)) {
        const [c0, c1] = COFFIN_FRAC[cue];
        const cf = c0 + (c1 - c0) * beatProgress;
        const pos = coffinCurve.getPointAt(Math.max(0, Math.min(1, cf)));
        const tangent = coffinCurve.getTangentAt(Math.max(0.001, Math.min(0.999, cf)));
        coffinMarker.visible = true;
        coffinMarker.position.set(pos.x, 0.22, pos.z);
        coffinMarker.rotation.y = Math.atan2(tangent.z, -tangent.x);
        coffinMarker.getWorldPosition(coffinWorldPos);
        coffinVisible = true;
      } else {
        coffinMarker.visible = false;
        coffinVisible = false;
      }
    },
    stationFlight(index, progress, verse, onlyI) {
      routeCurve.getPoint((Math.max(0, index - 1) + (index > 0 ? progress : 0)) / 10, flightPosition);
      routeGeo.setDrawRange(0, Math.max(2, Math.round(((Math.max(0, index - 1) + progress) / 10) * TOTAL_SAMPLES)));
      for (const lamp of lamps) {
        const reached = lamp.verse <= verse;
        (lamp.flame.material as THREE.MeshBasicMaterial).opacity = reached ? .98 : onlyI ? .12 : .04;
        (lamp.pillar.material as THREE.MeshBasicMaterial).opacity = reached ? .35 : 0;
        (lamp.halo.material as THREE.MeshBasicMaterial).opacity = reached ? .7 : 0;
      }
      return flightPosition;
    },
    applyReliefImage(img: HTMLImageElement) {
      reliefImg = img;
      redrawMapCanvas(lastDarkState ?? false);
    },
  };
}
