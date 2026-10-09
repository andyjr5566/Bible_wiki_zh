// 日後的屋子（OX）：no-leaven 的室內（剖開的鄰屋，擦乾淨倒扣的摶麵盆）與 remember 的桌邊（父親坐著、孩子在旁、桌上薄餅）。
// 加進 world.day 這個 Group（原點在 OX）。
import { BoxGeometry, CylinderGeometry, DoubleSide, Group, Mesh, PlaneGeometry } from 'three';
import { basinGeo, mergeParts, personGeo, tableGeo, T, type Part } from './geo';
import { flatBreadGeo, shelfGeo } from './geo2';
import { FIXED, glowMat, litMat, solid } from './materials';
import { CUT } from './tracks';
import { robeMat } from './props';

const box = (w: number, h: number, d: number, x = 0, y = 0, z = 0): Part => ({ g: new BoxGeometry(w, h, d), m: T(x, y, z) });

export class Home {
  group = new Group();
  /** 剖開的鄰屋（前牆拿掉，看得到裡面） */
  kitchen = new Group();
  /** remember 的桌邊 */
  table = new Group();

  constructor() {
    this.buildKitchen();
    this.buildTable();
    this.group.add(this.kitchen, this.table);
    this.kitchen.visible = false;
    this.table.visible = false;
  }

  private buildKitchen(): void {
    const k = this.kitchen;
    k.position.set(-7.4, 0, -0.4);
    const mWall = litMat({ base: FIXED.ochre, angle: 88, angle2: 10, space: 4.8, seed: 31, cross: true });
    const mFloor = litMat({ base: '#8a6a45', angle: 4, angle2: 4, space: 5, seed: 32 });
    const mWood = litMat({ base: '#6e5433', angle: 74, angle2: 10, space: 4.4, seed: 33 });
    const W = 6;
    const D = 4.6;
    const H = 2.9;
    // 牆、地、頂
    k.add(solid(mergeParts([box(W + 0.6, H, 0.3, 0, H / 2, -D - 0.15), box(0.3, H, D, -W / 2 - 0.15, H / 2, -D / 2), box(0.3, H, D, W / 2 + 0.15, H / 2, -D / 2), box(W + 0.9, 0.24, D + 0.3, 0, H + 0.12, -D / 2)]), mWall, 2.6));
    const floor = new Mesh(new BoxGeometry(W, 0.1, D), mFloor);
    floor.position.set(0, -0.045, -D / 2);
    k.add(floor);
    // 屋樑
    const beams: Part[] = [];
    for (let i = 0; i < 4; i++) beams.push({ g: new CylinderGeometry(0.075, 0.075, W, 6), m: T(0, H - 0.08, -0.6 - i * 1.15, 0, 0, Math.PI / 2) });
    k.add(solid(mergeParts(beams), mWood, 1.8));

    // 後牆的窗：白天的光
    const winMat = glowMat({ hatch: 0.55, edge: '#a07a30' });
    const win = new Mesh(new PlaneGeometry(0.95, 1.05), winMat);
    win.position.set(1.65, 1.75, -D + 0.012);
    k.add(win);
    const wf = solid(mergeParts([box(1.15, 0.1, 0.12, 0, 0.58, 0), box(1.15, 0.1, 0.12, 0, -0.58, 0), box(0.1, 1.25, 0.12, -0.52, 0, 0), box(0.1, 1.25, 0.12, 0.52, 0, 0)]), mWood, 1.6);
    wf.position.set(1.65, 1.75, -D + 0.05);
    k.add(wf);
    // 窗光落在地上
    const pool = new Mesh(new PlaneGeometry(3.2, 3.2), glowMat({ pool: true }));
    pool.rotation.x = -Math.PI / 2;
    pool.position.set(1.0, 0.03, -D + 1.7);
    pool.renderOrder = 4;
    k.add(pool);

    // 架板與倒扣的摶麵盆（擦乾淨了）
    const shelf = solid(shelfGeo(2.1), mWood, 2.0);
    shelf.position.set(-0.7, 1.3, -D + 0.22);
    k.add(shelf);
    const bs = basinGeo();
    const mBowl = litMat({ base: '#7b5a39', angle: 20, space: 4.4, seed: 13 });
    const bowl = solid(bs.bowl, mBowl, 2.2);
    bowl.scale.setScalar(1.5);
    bowl.rotation.x = Math.PI;
    bowl.position.set(-0.7, 1.335 + 0.3 * 1.5, -D + 0.22);
    k.add(bowl);
    // 釘子上掛著擦盆的布
    const peg = new Mesh(new CylinderGeometry(0.03, 0.03, 0.2, 5), mWood);
    peg.rotation.x = Math.PI / 2;
    peg.position.set(0.7, 1.6, -D + 0.12);
    k.add(peg);
    const mCloth = litMat({ base: '#dcd2bb', angle: 10, space: 4.4, seed: 54, side: DoubleSide });
    const cloth = solid(new BoxGeometry(0.3, 0.55, 0.025), mCloth, 1.5);
    cloth.position.set(0.7, 1.3, -D + 0.17);
    cloth.rotation.z = 0.04;
    k.add(cloth);
  }

  private buildTable(): void {
    const t = this.table;
    const mWood = litMat({ base: '#6e5433', angle: 74, angle2: 10, space: 4.4, seed: 5 });
    const tbl = solid(tableGeo(), mWood, 2.0);
    tbl.scale.setScalar(0.85);
    tbl.position.set(1.7, 0, 2.6);
    t.add(tbl);
    const mBread = litMat({ base: '#d9c690', angle: 20, space: 3.8, seed: 34, bias: 0.12 });
    const b1 = solid(flatBreadGeo(3, 0.19), mBread, 1.3);
    b1.position.set(1.35, 0.54, 2.55);
    const b2 = solid(flatBreadGeo(2, 0.18), mBread, 1.3);
    b2.position.set(1.95, 0.54, 2.7);
    b2.rotation.y = 0.7;
    t.add(b1, b2);
    // 坐墊
    const mCush = litMat({ base: '#a85b3a', angle: 40, space: 4.4, seed: 90 });
    const cush = new Mesh(new CylinderGeometry(0.4, 0.42, 0.07, 10), mCush);
    cush.position.set(0.55, 0.035, 2.65);
    t.add(cush);
    // 父親坐著，孩子站在桌的另一邊
    const father = solid(personGeo({ sit: true, slim: true, belt: true, armL: [0.9, 0.14], armR: [0.7, 0.14] }), robeMat('#a88758', 17), 2.4);
    father.position.set(0.55, 0.07, 2.65);
    father.rotation.y = Math.PI / 2 - 0.1;
    const child = solid(personGeo({ scale: 0.58, wrap: true, armL: [0.2, 0.2], armR: [0.95, 0.3] }), robeMat('#cdbf9e', 18, '#14110e', '#3a2e22'), 2.2);
    child.position.set(2.85, 0, 2.75);
    child.rotation.y = -Math.PI / 2 + 0.15;
    t.add(father, child);
  }

  update(s: number): void {
    const inside = s >= CUT['no-leaven'];
    this.kitchen.visible = inside;
    this.table.visible = inside;
  }
}
