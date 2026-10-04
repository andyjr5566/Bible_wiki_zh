import { DB, laws, refText, topicById } from '../data/db';
import { WIKI_BASE } from '../data/links';
import { download, lawsCsv } from '../lib/csv';
import { ext, h } from '../ui/dom';
import { more } from '../ui/more';

export function aboutView(): HTMLElement {
  return h('div', { class: 'lm-page lm-about' },
    h('h1', null, '關於律法地圖'),
    h('p', null, '這是一份導覽，不是註釋書。它把摩西五經的律法依主題排好、把在別卷又說了一次的律法連起來，再帶你回到知識庫讀完整的內容。'),
    h('h2', null, '畫面上的東西從哪裡來'),
    h('ul', null,
      h('li', null, '經文：和合本，原文照錄，不改寫。'),
      h('li', null, '每條律法的一句白話說明、主題分類、段落：本站整理。白話說明只重述經文說了什麼，不加解釋，並標出依據哪幾節。'),
      h('li', null, '律法之間的關聯（「在別卷又說了一次」等）：每一條都要有知識庫裡的出處，找不到出處的就不連。'),
      h('li', null, '經文裡劃線的人物、地方、觀念：連到知識庫的條目。本站只給名稱和一句簡介，完整內容請按「查看完整條目」到知識庫讀。')),
    h('p', null, '知識庫：', ext(WIKI_BASE, WIKI_BASE)),
    h('h2', null, '三種閱讀深度'),
    h('ul', null,
      h('li', null, '入門：先給一句話看懂，其他收起來。可以從首頁的導覽路線開始。'),
      h('li', null, '查經：展開經文、相關律法與五卷並排。'),
      h('li', null, '研究：再展開證據出處、分布數字、字面差異與資料下載。')),
    h('p', null, '不管選哪一種，收起來的區塊都按得開。'),
    more('research', '下載本站資料',
      h('p', null, `目前 ${laws.length} 條條文、${DB.relations.length} 條關聯。`),
      h('div', { class: 'lm-actions' },
        h('button', { type: 'button', class: 'lm-btn', onclick: () => download('律法地圖-條文.csv', lawsCsv(laws, refText, (id) => topicById.get(id)?.name ?? id), 'text/csv;charset=utf-8') }, '條文清單（CSV）'),
        h('button', { type: 'button', class: 'lm-btn', onclick: () => download('律法地圖.json', JSON.stringify(DB, null, 2), 'application/json') }, '完整資料（JSON）'))),
    h('p', { class: 'lm-note' }, '本站僅供非商業的教育與聖經研讀使用。'));
}
