import { svgEl } from './dom';

/**
 * 讀經模式的水墨效果：墨線（筆刷邊緣、由父畫到子）、朱印（職稱）、墨暈（正在讀的名字）。
 * 這裡只做圖形；位置由畫布算好傳進來。
 */

const SVG_NS = 'http://www.w3.org/2000/svg';
let defsReady = false;

/** 筆刷邊緣與印泥質感的濾鏡，整張畫布只建一次。 */
export function ensureInkDefs(svg: SVGSVGElement): void {
  if (defsReady && svg.querySelector('#ag-rd-brush')) return;
  defsReady = true;
  const defs = svgEl('defs', {});
  // 墨線：細小的亂紋讓邊緣不規則，像毛筆在紙上拖過
  const brush = svgEl('filter', { id: 'ag-rd-brush', x: '-20%', y: '-20%', width: '140%', height: '140%' });
  brush.append(
    svgEl('feTurbulence', { type: 'fractalNoise', baseFrequency: '0.9', numOctaves: '2', seed: '7', result: 'grain' }),
    svgEl('feDisplacementMap', { in: 'SourceGraphic', in2: 'grain', scale: '2.6', xChannelSelector: 'R', yChannelSelector: 'G', result: 'rough' }),
    svgEl('feGaussianBlur', { in: 'rough', stdDeviation: '0.25' }),
  );
  // 墨暈：往外化開的淡墨
  const bleed = svgEl('filter', { id: 'ag-rd-bleed', x: '-60%', y: '-60%', width: '220%', height: '220%' });
  bleed.append(
    svgEl('feTurbulence', { type: 'fractalNoise', baseFrequency: '0.035', numOctaves: '3', seed: '3', result: 'cloud' }),
    svgEl('feDisplacementMap', { in: 'SourceGraphic', in2: 'cloud', scale: '14', xChannelSelector: 'R', yChannelSelector: 'G', result: 'spread' }),
    svgEl('feGaussianBlur', { in: 'spread', stdDeviation: '5' }),
  );
  // 朱印：印泥不均勻，邊角有缺
  const seal = svgEl('filter', { id: 'ag-rd-seal', x: '-10%', y: '-10%', width: '120%', height: '120%' });
  seal.append(
    svgEl('feTurbulence', { type: 'fractalNoise', baseFrequency: '1.4', numOctaves: '1', seed: '11', result: 'speck' }),
    svgEl('feColorMatrix', { in: 'speck', type: 'matrix', values: '0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.4 1.5', result: 'holes' }),
    svgEl('feComposite', { in: 'SourceGraphic', in2: 'holes', operator: 'in', result: 'inked' }),
    svgEl('feDisplacementMap', { in: 'inked', in2: 'speck', scale: '0.7', xChannelSelector: 'R', yChannelSelector: 'G' }),
  );
  defs.append(brush, bleed, seal);
  svg.prepend(defs);
}

/** 一條墨線：底下一道淡墨暈，上面一道主筆；animate 時由起點畫到終點。 */
export function inkStroke(d: string, animate: boolean, delay = 0): SVGGElement {
  const group = svgEl('g', { class: 'ag-rd-ink' });
  const wash = svgEl('path', { d, class: 'ag-rd-ink-wash' });
  const line = svgEl('path', { d, class: 'ag-rd-ink-line', filter: 'url(#ag-rd-brush)' });
  group.append(wash, line);
  if (animate) {
    requestAnimationFrame(() => {
      for (const path of [wash, line]) {
        const length = Math.max(1, path.getTotalLength());
        path.style.strokeDasharray = `${length}`;
        path.style.strokeDashoffset = `${length}`;
        path.getBoundingClientRect();
        path.style.transition = `stroke-dashoffset 760ms cubic-bezier(.45,.05,.25,1) ${delay}ms`;
        path.style.strokeDashoffset = '0';
      }
    });
  }
  return group;
}

/** 朱印：兩個字以內一行直寫，三、四個字兩行直寫，更長就橫寫。印放在 (x, y) 的左上角。 */
export function sealMark(label: string, x: number, y: number, animate: boolean): SVGGElement {
  const chars = Array.from(label);
  const size = 19;
  let columns: string[][];
  if (chars.length <= 2) columns = [chars];
  else if (chars.length <= 4) columns = [chars.slice(0, Math.ceil(chars.length / 2)), chars.slice(Math.ceil(chars.length / 2))];
  else columns = [];
  const group = svgEl('g', { class: 'ag-rd-seal', transform: `translate(${x} ${y}) rotate(-4)` });
  // 蓋印的動畫放在內層：外層的 transform 管位置，CSS 動畫的 transform 會蓋掉它
  const body = svgEl('g', { filter: 'url(#ag-rd-seal)', class: animate ? 'ag-rd-seal-stamp' : '' });
  if (columns.length) {
    const rows = Math.max(...columns.map((column) => column.length));
    const width = columns.length * size + 8;
    const height = rows * size + 8;
    body.append(svgEl('rect', { x: 0, y: 0, width, height, rx: 2.5, class: 'ag-rd-seal-ink' }));
    // 直寫由右往左排
    columns.forEach((column, index) => {
      column.forEach((char, row) => {
        const text = svgEl('text', {
          class: 'ag-rd-seal-text', x: width - 4 - size / 2 - index * size, y: 4 + size / 2 + row * size + (rows - column.length) * size / 2,
          'text-anchor': 'middle', 'dominant-baseline': 'central',
        });
        text.textContent = char;
        body.append(text);
      });
    });
  } else {
    const width = chars.length * 15 + 12;
    body.append(svgEl('rect', { x: 0, y: 0, width, height: 25, rx: 2.5, class: 'ag-rd-seal-ink' }));
    const text = svgEl('text', { class: 'ag-rd-seal-text ag-rd-seal-text-wide', x: width / 2, y: 12.5, 'text-anchor': 'middle', 'dominant-baseline': 'central' });
    text.textContent = label;
    body.append(text);
  }
  group.append(body);
  return group;
}

/** 正在讀的名字後面化開的一團墨暈。 */
export function inkHalo(x: number, y: number, rx: number, ry: number): SVGEllipseElement {
  const halo = document.createElementNS(SVG_NS, 'ellipse') as SVGEllipseElement;
  halo.setAttribute('class', 'ag-rd-halo');
  halo.setAttribute('cx', String(x));
  halo.setAttribute('cy', String(y));
  halo.setAttribute('rx', String(rx));
  halo.setAttribute('ry', String(ry));
  halo.setAttribute('filter', 'url(#ag-rd-bleed)');
  return halo;
}
