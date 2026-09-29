import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';

import type { View } from '../data/stops';

/**
 * 會幕主場景。模型 tabernacle-main.glb（thedeserttabernacle，CC BY-NC）沿用舊版的擺放：
 * 縮放 0.3、繞 Y 軸轉 -90°，使 +Z 為東、+X 為北。
 */

/** 四層頂蓋，由內而外（材質名來自模型本身） */
// 實測對照（截圖逐一上色確認）：First_Curtain_Mat＝繡基路伯的細麻幔子、ThirdCovering＝染紅的公羊皮、
// FourthCovering＝海狗皮頂蓋。這個模型沒有做山羊毛罩棚那一層；Inner/Outer_Curtain 是內幔與門簾，不屬頂蓋。
export const LAYER_MATERIALS: Record<'linen' | 'goathair' | 'ramskin' | 'seacow', readonly string[]> = {
  linen: ['First_Curtain_Mat'],
  goathair: [],
  ramskin: ['ThirdCovering'],
  seacow: ['FourthCovering'],
};
export type LayerId = keyof typeof LAYER_MATERIALS;
export const MODEL_HAS_LAYER = (id: LayerId) => LAYER_MATERIALS[id].length > 0;

export interface Stage {
  go(view: View, peel: boolean): void;
  setLayer(id: LayerId, visible: boolean): void;
  resetLayers(): void;
  setAutoRotate(on: boolean): void;
  interact(fn: () => void): void;
  debug: { materials(): string[]; scene: THREE.Scene };
}

const OVERVIEW: View = { pos: [34, 22, 40], target: [0, 0, 2], fov: 42 };

function weaveTexture(cherubim: boolean): THREE.CanvasTexture {
  const c = document.createElement('canvas');
  c.width = 512;
  c.height = 256;
  const g = c.getContext('2d')!;
  const bands = ['#2f4f9a', '#6a3b8c', '#b3263a', '#efe6d2'];
  const bw = c.width / 16;
  for (let i = 0; i < 16; i++) {
    g.fillStyle = bands[i % 4];
    g.fillRect(i * bw, 0, bw + 1, c.height);
  }
  g.globalAlpha = 0.16;
  for (let y = 0; y < c.height; y += 4) {
    g.fillStyle = y % 8 ? '#000' : '#fff';
    g.fillRect(0, y, c.width, 1);
  }
  if (cherubim) {
    // 基路伯的繡紋：只畫成抽象的金色翅膀，經文沒有描述它的樣子
    g.globalAlpha = 0.75;
    g.strokeStyle = '#e0b44a';
    g.lineWidth = 5;
    for (let i = 0; i < 4; i++) {
      const cx = 64 + i * 128;
      g.beginPath();
      g.moveTo(cx, 158);
      g.quadraticCurveTo(cx - 50, 118, cx - 44, 68);
      g.moveTo(cx, 158);
      g.quadraticCurveTo(cx + 50, 118, cx + 44, 68);
      g.stroke();
    }
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  return t;
}

export async function createStage(host: HTMLElement, opts: { reducedMotion: boolean; lowPower: boolean; onProgress?: (p: number) => void }): Promise<Stage> {
  const renderer = new THREE.WebGLRenderer({ antialias: !opts.lowPower, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(devicePixelRatio, opts.lowPower ? 1 : 1.75));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.shadowMap.enabled = !opts.lowPower;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.domElement.setAttribute('role', 'img');
  renderer.domElement.setAttribute('aria-label', '可以拖曳轉動的 3D 會幕（示意重建）');
  host.append(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#e8d6b4');
  scene.fog = new THREE.Fog('#e8d6b4', 60, 160);
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

  const camera = new THREE.PerspectiveCamera(OVERVIEW.fov, 1, 0.05, 400);
  camera.position.set(...OVERVIEW.pos);

  scene.add(new THREE.HemisphereLight(0xfff3dc, 0x8a6b44, 0.8));
  const sun = new THREE.DirectionalLight(0xfff0d0, 2.2);
  sun.position.set(20, 30, 14);
  sun.castShadow = !opts.lowPower;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -26, right: 26, top: 26, bottom: -26, near: 1, far: 90 });
  sun.shadow.bias = -0.0004;
  scene.add(sun);
  // 聖所裡面暗，掀開頂之後補一點暖光，才看得見器具
  const inner = new THREE.PointLight(0xffd9a0, 0, 12, 1.5);
  inner.position.set(0, 2.6, -5);
  scene.add(inner);

  const sand = (() => {
    const c = document.createElement('canvas');
    c.width = c.height = 256;
    const g = c.getContext('2d')!;
    g.fillStyle = '#d8c29a';
    g.fillRect(0, 0, 256, 256);
    for (let i = 0; i < 2600; i++) {
      const v = 180 + Math.random() * 50;
      g.fillStyle = `rgba(${v},${v * 0.86},${v * 0.66},${0.25 + Math.random() * 0.3})`;
      g.fillRect(Math.random() * 256, Math.random() * 256, 1.5, 1.5);
    }
    const t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.repeat.set(40, 40);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  })();
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshStandardMaterial({ map: sand, roughness: 1 }));
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.02;
  ground.receiveShadow = true;
  scene.add(ground);

  const loader = new GLTFLoader();
  const gltf = await loader.loadAsync(new URL('models/tabernacle-main.glb', document.baseURI).href, (e) => {
    if (e.total) opts.onProgress?.(e.loaded / e.total);
  });
  const model = gltf.scene;
  model.scale.setScalar(0.3);
  model.rotation.y = -Math.PI / 2;
  const layerMeshes: Record<LayerId, THREE.Mesh[]> = { linen: [], goathair: [], ramskin: [], seacow: [] };
  const matNames = new Set<string>();
  model.traverse((o) => {
    const m = o as THREE.Mesh;
    if (!m.isMesh) return;
    m.castShadow = !opts.lowPower;
    m.receiveShadow = !opts.lowPower;
    const mats = Array.isArray(m.material) ? m.material : [m.material];
    for (const mat of mats) {
      matNames.add(mat.name);
      for (const [id, names] of Object.entries(LAYER_MATERIALS) as [LayerId, readonly string[]][]) {
        if (names.includes(mat.name)) layerMeshes[id].push(m);
      }
    }
  });
  // 院門與帳幕門簾（Outer_Curtain）、內幔（Inner_Curtain）原本是漩渦貼圖；換成三色線加細麻的織紋（出26:31、36；27:16）
  const gateTex = weaveTexture(false);
  const veilTex = weaveTexture(true);
  model.traverse((o) => {
    const m = o as THREE.Mesh;
    if (!m.isMesh) return;
    const mat = m.material as THREE.MeshStandardMaterial;
    if (mat.name === 'Outer_Curtain' || mat.name === 'Inner_Curtain') {
      m.material = new THREE.MeshStandardMaterial({ name: mat.name, map: mat.name === 'Inner_Curtain' ? veilTex : gateTex, roughness: 0.85, side: THREE.DoubleSide });
    }
  });
  // 約櫃、桌子、燈臺在模型裡是半透明或米白色；經文說「包上精金」「用精金做」（出25:11、24、31），統一成金色
  const gold = new THREE.MeshStandardMaterial({ name: 'scripture_gold', color: '#d9ab3f', metalness: 1, roughness: 0.3 });
  for (const name of ['Ark001', 'Border002', 'LampStand001']) {
    model.getObjectByName(name)?.traverse((o) => {
      const m = o as THREE.Mesh;
      if (m.isMesh) m.material = gold;
    });
  }
  scene.add(model);

  const layerState: Record<LayerId, boolean> = { linen: true, goathair: true, ramskin: true, seacow: true };
  let peeled = false;
  const applyLayers = () => {
    for (const id of Object.keys(layerMeshes) as LayerId[]) {
      for (const m of layerMeshes[id]) m.visible = !peeled && layerState[id];
    }
    const open = peeled || !layerState.linen;
    inner.intensity = open ? 6 : 0;
  };

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(...OVERVIEW.target);
  controls.enableDamping = true;
  controls.maxPolarAngle = Math.PI * 0.49;
  controls.minDistance = 0.8;
  controls.maxDistance = 90;
  controls.autoRotate = !opts.reducedMotion;
  controls.autoRotateSpeed = 0.3;

  // 以時間計算，而不是以幀數：模型大、機器慢的時候，鏡頭也在固定時間內到位
  let tween: { from: View; to: View; start: number; dur: number } | null = null;
  const current = (): View => ({ pos: camera.position.toArray() as View['pos'], target: controls.target.toArray() as View['target'], fov: camera.fov });
  const listeners: (() => void)[] = [];
  controls.addEventListener('start', () => {
    tween = null;
    listeners.forEach((f) => f());
  });

  let visible = true;
  const io = new IntersectionObserver(([e]) => (visible = e.isIntersecting));
  io.observe(host);
  const resize = () => {
    const w = host.clientWidth;
    const h = host.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / Math.max(1, h);
    camera.updateProjectionMatrix();
  };
  new ResizeObserver(resize).observe(host);
  resize();

  const a = new THREE.Vector3();
  const b = new THREE.Vector3();
  function frame() {
    requestAnimationFrame(frame);
    if (!visible || document.hidden) return;
    if (tween) {
      const t = tween.dur ? Math.min(1, (performance.now() - tween.start) / tween.dur) : 1;
      const e = t < 0.5 ? 4 * t ** 3 : 1 - (-2 * t + 2) ** 3 / 2;
      camera.position.lerpVectors(a.set(...tween.from.pos), b.set(...tween.to.pos), e);
      controls.target.lerpVectors(a.set(...tween.from.target), b.set(...tween.to.target), e);
      camera.fov = tween.from.fov + (tween.to.fov - tween.from.fov) * e;
      camera.updateProjectionMatrix();
      if (t >= 1) tween = null;
    }
    controls.update();
    renderer.render(scene, camera);
  }
  frame();

  return {
    go(view, peel) {
      controls.autoRotate = false;
      peeled = peel;
      applyLayers();
      tween = { from: current(), to: view, start: performance.now(), dur: opts.reducedMotion ? 0 : 1600 };
    },
    setLayer(id, v) {
      layerState[id] = v;
      applyLayers();
    },
    resetLayers() {
      (Object.keys(layerState) as LayerId[]).forEach((k) => (layerState[k] = true));
      applyLayers();
    },
    setAutoRotate(on) {
      controls.autoRotate = on && !opts.reducedMotion;
    },
    interact(fn) {
      listeners.push(fn);
    },
    debug: { materials: () => [...matNames], scene },
  };
}

export { OVERVIEW };
