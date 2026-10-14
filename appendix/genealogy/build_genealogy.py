#!/usr/bin/env python3
"""族譜附錄：從 YAML 資料驗證並產生 Obsidian 頁面。

資料是唯一來源（`<卷>/genealogy.yaml` 人物關係、`<卷>/extras.yaml` 對照表與人物卡），
頁面由本程式產生，不手改。驗證全部以 `raw_scripture/` 和合本為準：

- 每個人名（或 `as` 標的經文寫法）、`of`（某地之祖）、`mother` 都必須逐字出現在所引經節。
- 所有「」引句必須逐字出現在同一條目所引的經節。
- 平行經文對照兩邊的字串、人數表的數字字串、城邑名都要逐字出現在各自經節。
- 範圍內每一節都要被資料涵蓋，或在 `uncovered` 註明理由。
- 產出頁面的跨檔 [[ 連結目標必須列在 series.yaml 的 ready 頁面中。

用法：
    python appendix/genealogy/build_genealogy.py 歷代志上            # 驗證＋產生頁面
    python appendix/genealogy/build_genealogy.py 歷代志上 --check    # 只驗證
    python appendix/genealogy/build_genealogy.py 歷代志上 --review out.md  # 另輸出逐節對照表供人工複核
    python appendix/genealogy/build_genealogy.py 歷代志上/大衛王朝   # 指定系列頁面
    python appendix/genealogy/build_genealogy.py --all                # 驗證並產生所有 ready 頁面
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPTURE = ROOT / "raw_scripture"
HERE = Path(__file__).resolve().parent

ABBR = {
    "創": "創世記", "出": "出埃及記", "利": "利未記", "民": "民數記", "申": "申命記",
    "書": "約書亞記", "士": "士師記", "得": "路得記", "撒上": "撒母耳記上", "撒下": "撒母耳記下",
    "王上": "列王紀上", "王下": "列王紀下", "代上": "歷代志上", "代下": "歷代志下",
    "拉": "以斯拉記", "尼": "尼希米記", "斯": "以斯帖記", "伯": "約伯記", "詩": "詩篇",
    "箴": "箴言", "傳": "傳道書", "歌": "雅歌", "賽": "以賽亞書", "耶": "耶利米書",
    "哀": "耶利米哀歌", "結": "以西結書", "但": "但以理書", "何": "何西阿書", "珥": "約珥書",
    "摩": "阿摩司書", "俄": "俄巴底亞書", "拿": "約拿書", "彌": "彌迦書", "鴻": "那鴻書",
    "哈": "哈巴谷書", "番": "西番雅書", "該": "哈該書", "亞": "撒迦利亞書", "瑪": "瑪拉基書",
    "太": "馬太福音", "可": "馬可福音", "路": "路加福音", "約": "約翰福音", "徒": "使徒行傳",
    "羅": "羅馬書", "林前": "哥林多前書", "林後": "哥林多後書", "加": "加拉太書",
    "弗": "以弗所書", "腓": "腓立比書", "西": "歌羅西書",
    "帖前": "帖撒羅尼迦前書", "帖後": "帖撒羅尼迦後書",
    "提前": "提摩太前書", "提後": "提摩太後書", "多": "提多書", "門": "腓利門書",
    "來": "希伯來書", "雅": "雅各書", "彼前": "彼得前書", "彼後": "彼得後書",
    "約一": "約翰一書", "約二": "約翰二書", "約三": "約翰三書", "猶": "猶大書", "啟": "啟示錄",
}
FULL_TO_ABBR = {v: k for k, v in ABBR.items()}
QUOTE_RE = re.compile(r"「([^「」]+)」")
PUNCT_RE = re.compile(r"[，。、；：！？「」『』（）()\s─—…‧·]")


class Scripture:
    def __init__(self) -> None:
        self.cache: dict[tuple[str, int], list[str]] = {}

    def chapter(self, book: str, ch: int) -> list[str]:
        key = (book, ch)
        if key not in self.cache:
            path = SCRIPTURE / book / f"第{ch}章.txt"
            self.cache[key] = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
        return self.cache[key]

    def verse(self, book: str, ch: int, v: int) -> str | None:
        lines = self.chapter(book, ch)
        return lines[v - 1] if 1 <= v <= len(lines) else None


def parse_refs(refs: str, default_book: str, scripture: Scripture | None = None) -> list[tuple[str, int, int]]:
    """「2:10-15, 撒下 13:20, 3:1-4:2」→ [(書, 章, 節), ...]；格式錯拋 ValueError。"""
    out: list[tuple[str, int, int]] = []
    for part in re.split(r"[,，;；]\s*", str(refs).strip()):
        if not part:
            continue
        book = default_book
        m = re.match(r"^([^\d\s]+)\s*(.*)$", part)
        if m:
            abbr, part = m.group(1), m.group(2)
            if abbr not in ABBR:
                raise ValueError(f"未知書卷簡稱：{abbr}")
            book = ABBR[abbr]
        m = re.fullmatch(r"(\d+):(\d+)(?:[-–](?:(\d+):)?(\d+))?", part)
        if not m:
            raise ValueError(f"經節格式錯誤：{part}")
        c1, v1 = int(m.group(1)), int(m.group(2))
        c2 = int(m.group(3)) if m.group(3) else c1
        v2 = int(m.group(4)) if m.group(4) else v1
        if c2 == c1:
            out += [(book, c1, v) for v in range(v1, v2 + 1)]
        elif c2 > c1 and scripture is not None:
            if min(c1, c2, v1, v2) < 1:
                raise ValueError(f"跨章範圍端點必須是正整數：{part}")
            first_count = len(scripture.chapter(book, c1))
            last_count = len(scripture.chapter(book, c2))
            if not first_count or not last_count:
                raise ValueError(f"經節章數不存在：{part}")
            if v1 > first_count or v2 > last_count:
                raise ValueError(f"跨章範圍端點不存在：{part}")
            out += [(book, c1, v) for v in range(v1, first_count + 1)]
            for chapter in range(c1 + 1, c2):
                count = len(scripture.chapter(book, chapter))
                if not count:
                    raise ValueError(f"跨章範圍中間章數不存在：{part}")
                out += [(book, chapter, v) for v in range(1, count + 1)]
            out += [(book, c2, v) for v in range(1, v2 + 1)]
        else:
            raise ValueError(f"跨章範圍請拆開寫：{part}")
    return out



def prefix_book(refs: str, abbr: str) -> str:
    """「4:5, 4:7」→「代上4:5, 代上4:7」：每一段沒有書卷簡稱的都補上。"""
    parts = re.split(r"([,，;；]\s*)", str(refs).strip())
    return "".join(p if (i % 2 or not p or re.match(r"^[^\d\s]", p)) else abbr + p for i, p in enumerate(parts))

def norm(s: str) -> str:
    return PUNCT_RE.sub("", s)


def display(node_id: str) -> str:
    return node_id.split("#", 1)[0]


def fmt_ref(refs: str, default_book: str) -> str:
    """顯示用：預設卷書省略書名，其他卷書用簡稱。"""
    return str(refs).replace("-", "–")


KING_GREEN = "#2e9d6a"
KING_RED = "#d0453b"
KING_GOLD = "#d4a82e"
KING_COLORS = {
    "good": KING_GREEN, "good_caveat": KING_GREEN,
    "good_to_bad": KING_GREEN, "bad_to_good": KING_RED,
    "bad": KING_RED, "none": "#8a8f98",
}
KING_MARKS = {
    "good": "●", "good_caveat": "●但", "good_to_bad": "◐",
    "bad_to_good": "◑", "bad": "○", "none": "—",
}
KING_LABELS = {
    "good": "行正", "good_caveat": "行正，另有但書",
    "good_to_bad": "好轉壞", "bad_to_good": "壞轉好",
    "bad": "行惡", "none": "沒有評語",
}
KING_CATEGORIES = tuple(KING_MARKS)
KING_GRADIENTS = {"good_to_bad": "gb", "bad_to_good": "bg"}


def _king_interval(king: dict) -> tuple[int, int]:
    years = king["years"]
    return int(years.get("co_start", years["start"])), int(years["end"])


def _overlaps(first: tuple[int, int], second: tuple[int, int]) -> bool:
    # 主前年數字大＝早；只在前後交接的那一年相接不算重疊
    return max(first[1], second[1]) < min(first[0], second[0])


def _king_columns(kings: list[dict]) -> dict[int, tuple[float, float]]:
    """分配南北國王的年代子欄；沒有重疊的王保留原欄寬。"""
    result: dict[int, tuple[float, float]] = {}
    for kingdom, base_x in (("猶大", 178), ("以色列", 274)):
        rows = [king for king in kings if king.get("kingdom") == kingdom]
        rows.sort(key=lambda king: (-_king_interval(king)[0], -int(king["years"]["start"]), str(king.get("name", ""))))
        groups: list[list[dict]] = []
        group: list[dict] = []
        group_end = None
        for king in rows:
            interval = _king_interval(king)
            if group and interval[0] <= group_end:
                groups.append(group)
                group = []
                group_end = None
            group.append(king)
            group_end = interval[1] if group_end is None else min(group_end, interval[1])
        if group:
            groups.append(group)

        for group in groups:
            if len(group) == 1:
                result[id(group[0])] = (float(base_x), 28.0)
                continue
            lanes: list[list[dict]] = []
            lane_for: dict[int, int] = {}
            for king in group:
                interval = _king_interval(king)
                lane_index = next((index for index, lane in enumerate(lanes)
                                   if all(not _overlaps(interval, _king_interval(other)) for other in lane)), None)
                if lane_index is None:
                    lane_index = len(lanes)
                    lanes.append([])
                lanes[lane_index].append(king)
                lane_for[id(king)] = lane_index
            lane_count = len(lanes)
            width = (28 - 2 * (lane_count - 1)) / lane_count
            for king in group:
                lane_index = lane_for[id(king)]
                result[id(king)] = (base_x + lane_index * (width + 2), width)
    return result


def _svg_defs(prefix: str) -> list[str]:
    return [
        "<defs>",
        f'<linearGradient id="kgrad-{prefix}-gb" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{KING_GREEN}"/><stop offset="100%" stop-color="{KING_RED}"/></linearGradient>',
        f'<linearGradient id="kgrad-{prefix}-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{KING_RED}"/><stop offset="100%" stop-color="{KING_GREEN}"/></linearGradient>',
        "</defs>",
    ]




TABLE_ROW_RE = re.compile(r"^(> )*\|")
TABLE_LINK_RE = re.compile(r"\[\[([^\]|]*?[^\]|\\])\|([^\]]*)\]\]")


def escape_table_links(page: str) -> str:
    """Obsidian 表格裡的 [[目標|文字]] 要寫成 [[目標\\|文字]]，否則 | 會被當成欄位分隔。"""
    lines = page.split("\n")
    for i, line in enumerate(lines):
        if TABLE_ROW_RE.match(line):
            lines[i] = TABLE_LINK_RE.sub(lambda m: "[[" + m.group(1) + "\\|" + m.group(2) + "]]", line)
    return "\n".join(lines)

def bar_pads(names: list[str]) -> dict[str, str]:
    """長條圖名稱補齊。名稱全是全形字時沿用全形空白；混有半形字時依顯示寬度補半形空白。"""
    import unicodedata
    if all(unicodedata.east_asian_width(ch) in "WF" for name in names for ch in name):
        width = max(len(name) for name in names)
        return {name: "　" * (width - len(name)) for name in names}
    def cells(text: str) -> int:
        return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)
    width = max(cells(name) for name in names)
    return {name: " " * (width - cells(name)) for name in names}

def timeline_svg(kings: list[dict], mini: bool = False) -> str:
    """產生不含空白段落的直式南北國年代 SVG。"""
    prefix = "mini" if mini else "full"
    if not kings:
        return "\n".join([
            '<svg viewBox="0 0 480 92" role="img" aria-label="南北國列王年代圖" style="width:100%;max-width:560px;height:auto;display:block;margin:0 auto" font-family="inherit">',
            *_svg_defs(prefix),
            '<text x="0" y="70" fill="currentColor">沒有君王年代資料</text>',
            "</svg>",
        ])
    starts = [int(king["years"].get("co_start", king["years"]["start"])) for king in kings]
    ends = [int(king["years"]["end"]) for king in kings]
    top_year = ((max(starts) + 9) // 10) * 10
    bottom_year = (min(ends) // 10) * 10
    if top_year == bottom_year:
        top_year += 10
        bottom_year -= 10
    scale = 1 if mini else 3
    plot_top = 98
    summary_space = 44 if mini else 40
    height = plot_top + (top_year - bottom_year) * scale + summary_space
    esc = lambda value: html.escape(str(value), quote=True)
    lines = [f'<svg viewBox="0 0 480 {height}" role="img" aria-label="南北國列王年代圖" style="width:100%;max-width:560px;height:auto;display:block;margin:0 auto" font-family="inherit">']
    lines.extend(_svg_defs(prefix))

    legend = [
        ("good", 0, 14), ("good_caveat", 160, 14), ("good_to_bad", 320, 14),
        ("bad_to_good", 0, 32), ("bad", 160, 32), ("none", 320, 32),
    ]
    for category, x, y in legend:
        fill = f"url(#kgrad-{prefix}-{KING_GRADIENTS[category]})" if category in KING_GRADIENTS else KING_COLORS[category]
        stroke = f' stroke="{KING_GOLD}" stroke-width="2.5"' if category == "good_caveat" else ""
        lines.append(f'<rect x="{x + 1}" y="{y - 10}" width="11" height="11" fill="{fill}"{stroke}/>')
        lines.append(f'<text x="{x + 17}" y="{y}" font-size="11" fill="currentColor">{KING_MARKS[category]} {KING_LABELS[category]}</text>')
    lines.append('<text x="0" y="50" font-size="11" fill="currentColor">※ 兩卷寫法不同</text>')
    lines.append('<rect x="111" y="40" width="11" height="11" fill="#8a8f98" fill-opacity="0.3" stroke="#8a8f98" stroke-dasharray="3 2"/><text x="127" y="50" font-size="11" fill="currentColor">淡色虛線：共治</text>')
    lines.append('<rect x="241" y="40" width="11" height="11" fill="#8a8f98" fill-opacity="0.4" stroke="currentColor" stroke-dasharray="3 2"/><text x="257" y="50" font-size="11" fill="currentColor">半透明虛線：推估</text>')
    lines.append('<text x="0" y="66" font-size="11" fill="currentColor">同一國同時有兩位王（共治或並立）時，色條並排成窄欄。</text>')
    lines.append('<text x="192" y="88" text-anchor="middle" font-size="12" fill="currentColor">猶大</text>')
    lines.append('<text x="288" y="88" text-anchor="middle" font-size="12" fill="currentColor">以色列</text>')

    def y_of(year: int) -> float:
        return plot_top + (top_year - year) * scale

    interval = 100 if mini else 50
    first_tick = ((bottom_year + interval - 1) // interval) * interval
    for year in range(first_tick, top_year + 1, interval):
        y = y_of(year)
        lines.append(f'<line x1="44" y1="{y:.1f}" x2="480" y2="{y:.1f}" stroke="#9aa0a6" stroke-opacity="0.15"/>')
        lines.append(f'<text x="0" y="{y + 4:.1f}" font-size="11" fill="currentColor">主前 {year}</text>')

    columns = _king_columns(kings)
    label_rows: dict[str, list[tuple[dict, float, float, float, str, str]]] = {"left": [], "right": [], "unified": []}
    for king in kings:
        years = king["years"]
        start, end = int(years["start"]), int(years["end"])
        category = (king.get("verdict") or {}).get("class", "none")
        color = KING_COLORS.get(category, KING_COLORS["none"])
        kingdom = king.get("kingdom")
        if kingdom == "統一":
            x, width = 178.0, 124.0
        else:
            x, width = columns[id(king)]
        gradient = f"url(#kgrad-{prefix}-{KING_GRADIENTS[category]})" if category in KING_GRADIENTS else color
        y_start, y_end = y_of(start), y_of(end)
        bar_top, bar_bottom = min(y_start, y_end), max(y_start, y_end)
        bar_height = max(2, bar_bottom - bar_top)
        opacity = "0.4" if years.get("estimate") else "0.8"
        dash = ' stroke-dasharray="4 3"' if years.get("estimate") else ""
        if years.get("co_start") is not None:
            co_top, co_bottom = sorted((y_of(int(years["co_start"])), y_of(start)))
            co_color = KING_GREEN if category == "good_to_bad" else KING_RED if category == "bad_to_good" else color
            lines.append(f'<rect x="{x:.2f}" y="{co_top:.1f}" width="{width:.2f}" height="{max(2, co_bottom - co_top):.1f}" fill="{co_color}" fill-opacity="0.3" stroke="{co_color}" stroke-dasharray="4 3"/>')
        stroke = f' stroke="{KING_GOLD}" stroke-width="2.5"' if category == "good_caveat" else (' stroke="currentColor"' if years.get("estimate") else "")
        lines.append(f'<rect x="{x:.2f}" y="{bar_top:.1f}" width="{width:.2f}" height="{bar_height:.1f}" fill="{gradient}" fill-opacity="{opacity}"{stroke}{dash}/>')
        if mini:
            continue
        mark = KING_MARKS.get(category, "—") + ("※" if (king.get("verdict") or {}).get("differs") else "")
        label = f"{king.get('name', king.get('id', ''))} {mark}"
        middle = (bar_top + bar_bottom) / 2
        if kingdom == "統一" and bar_height >= 14:
            label_rows["unified"].append((king, middle, middle, bar_top, label, "center"))
        elif kingdom == "統一":
            label_rows["left"].append((king, middle, middle, bar_top, label, "unified"))
        elif kingdom == "猶大":
            label_rows["left"].append((king, middle, middle, bar_top, label, "left"))
        else:
            label_rows["right"].append((king, middle, middle, bar_top, label, "right"))

    if not mini:
        max_label_y = height - summary_space + 2
        for lane, rows in label_rows.items():
            rows.sort(key=lambda row: row[1])
            placed = []
            for row in rows:
                y = row[1]
                if placed and y - placed[-1][1] < 14:
                    y = placed[-1][1] + 14
                placed.append((row, y))
            overflow = max(0, placed[-1][1] - max_label_y) if placed else 0
            for row, y in placed:
                king, ideal, _, bar_top, label, align = row
                label_y = y - overflow
                start, end = int(king["years"]["start"]), int(king["years"]["end"])
                bar_mid = (y_of(start) + y_of(end)) / 2
                bar_x, bar_width = (240.0, 124.0) if king.get("kingdom") == "統一" else columns[id(king)]
                bar_center = bar_x + bar_width / 2
                if align == "right":
                    text_x, anchor = 308, "start"
                elif align == "center":
                    text_x, anchor = 240, "middle"
                else:
                    text_x, anchor = 172, "end"
                bar_min = min(y_of(start), y_of(end))
                bar_max = max(y_of(start), y_of(end))
                if label_y < bar_min or label_y > bar_max:
                    lines.append(f'<line x1="{text_x}" y1="{label_y:.1f}" x2="{bar_center:.2f}" y2="{bar_mid:.1f}" stroke="currentColor" stroke-opacity="0.4" stroke-width="0.7"/>')
                lines.append(f'<text x="{text_x}" y="{label_y + 4:.1f}" text-anchor="{anchor}" font-size="12" fill="currentColor">{esc(label)}</text>')
    else:
        def count_for(kingdom: str, category: str) -> int:
            return sum(1 for king in kings if king.get("kingdom") == kingdom and (king.get("verdict") or {}).get("class", "none") == category)
        judah = "　".join(f"{KING_MARKS[c]} {count_for('猶大', c)}" for c in KING_CATEGORIES)
        israel = "　".join(f"{KING_MARKS[c]} {count_for('以色列', c)}" for c in KING_CATEGORIES)
        lines.append(f'<text x="0" y="{height - 24}" font-size="11" fill="currentColor">猶大　{judah}</text>')
        lines.append(f'<text x="0" y="{height - 8}" font-size="11" fill="currentColor">以色列　{israel}</text>')
    lines.append("</svg>")
    return "\n".join(lines)


class Builder:
    def __init__(self, book_dir: Path, data_name: str = "genealogy", data_spec: str = "歷代志上") -> None:
        self.dir = book_dir
        self.data_name = data_name
        self.data_spec = data_spec.replace(chr(92), "/")
        self.data_path = book_dir / f"{data_name}.yaml"
        self.data = yaml.safe_load(self.data_path.read_text(encoding="utf-8"))
        extras_path = book_dir / ("extras.yaml" if data_name == "genealogy" else f"{data_name}.extras.yaml")
        self.extras = yaml.safe_load(extras_path.read_text(encoding="utf-8")) if extras_path.is_file() else {}
        series_path = HERE / "series.yaml"
        self.series = yaml.safe_load(series_path.read_text(encoding="utf-8")) if series_path.is_file() else {"pages": []}
        self.page_type = self.data.get("type", "genealogy")
        self.book = self.data["book"]
        self.abbr = FULL_TO_ABBR[self.book]
        self.sc = Scripture()
        self.errors: list[str] = []
        self.kings_registry: dict = {}
        self.kings_by_id: dict[str, dict] = {}
        self.nodes: "OrderedDict[str, dict]" = OrderedDict()
        self.people: "OrderedDict[str, dict]" = OrderedDict()
        self.section_titles: dict[str, str] = {}
        self.section_order: dict[str, int] = {}
        self.group_headings: dict[str, str] = {}
        self.grouped_sections = False
        self.section_extra: dict[str, list[str]] = defaultdict(list)
        self.children: dict[str, list[str]] = defaultdict(list)
        self.covered: set[tuple[int, int]] = set()
        self.verse_names: dict[tuple[int, int], list[str]] = defaultdict(list)
        self._loading_import = False
        self._imported_page: str | None = None
        self._current_section_title = ""

    # ---------- 驗證工具 ----------
    def err(self, where: str, msg: str) -> None:
        self.errors.append(f"[{where}] {msg}")

    def refs(self, refs: str, where: str) -> list[tuple[str, int, int]]:
        try:
            parsed = parse_refs(refs, self.book, self.sc)
        except ValueError as exc:
            self.err(where, str(exc))
            return []
        for b, c, v in parsed:
            if self.sc.verse(b, c, v) is None:
                self.err(where, f"經節不存在：{b} {c}:{v}")
        return parsed

    def text_of(self, parsed) -> str:
        return "".join(self.sc.verse(b, c, v) or "" for b, c, v in parsed)

    def need_text(self, needle: str, parsed, where: str, what: str) -> None:
        if not parsed:
            return
        if norm(needle) not in norm(self.text_of(parsed)):
            span = ", ".join(f"{FULL_TO_ABBR.get(b, b)}{c}:{v}" for b, c, v in parsed[:3])
            self.err(where, f"{what}「{needle}」不在所引經文（{span}{'…' if len(parsed) > 3 else ''}）")

    def has_literal_text(self, needle: str, parsed) -> bool:
        return any(needle in (self.sc.verse(book, chapter, verse) or "") for book, chapter, verse in parsed)

    def need_literal_text(self, needle: str, parsed, where: str, what: str) -> None:
        if parsed and not self.has_literal_text(needle, parsed):
            span = ", ".join(f"{FULL_TO_ABBR.get(b, b)}{c}:{v}" for b, c, v in parsed[:3])
            self.err(where, f"{what}「{needle}」未逐字出現在所引經文（{span}{'…' if len(parsed) > 3 else ''}）")

    def need_exact_text(self, needle: str, parsed, where: str, what: str) -> None:
        if parsed and needle not in self.text_of(parsed):
            span = ", ".join(f"{FULL_TO_ABBR.get(b, b)}{c}:{v}" for b, c, v in parsed[:3])
            self.err(where, f"{what}「{needle}」未逐字出現在所引經文（{span}{'…' if len(parsed) > 3 else ''}）")

    def check_exact_quotes(self, text: str, parsed, where: str) -> None:
        for quote in QUOTE_RE.findall(text or ""):
            self.need_exact_text(quote, parsed, where, "引句")

    def registry_refs(self, refs: str, where: str) -> list[tuple[str, int, int]]:
        if not str(refs or "").strip():
            self.err(where, "經節不能空白")
            return []
        for part in re.split(r"[,，;；]\s*", str(refs or "").strip()):
            if not part:
                continue
            match = re.match(r"^([^\d\s]+)\s*\d+:\d+", part)
            if not match or match.group(1) not in ABBR:
                self.err(where, f"登錄檔經節必須以有效書卷簡稱開頭：{part}")
        return self.refs(refs, where)

    def check_quotes(self, text: str, parsed, where: str) -> None:
        for q in QUOTE_RE.findall(text or ""):
            self.need_text(q, parsed, where, "引句")

    def cover(self, parsed) -> None:
        for b, c, v in parsed:
            if b == self.book:
                self.covered.add((c, v))

    def validate_section_groups(self, data: dict) -> bool:
        groups = data.get("groups")
        if not groups:
            return False
        if not isinstance(groups, list):
            self.err("groups", "groups 必須是清單")
            return True

        group_ids: set[str] = set()
        for i, group in enumerate(groups):
            where = f"groups#{i + 1}"
            if not isinstance(group, dict):
                self.err(where, "group 必須是 mapping")
                continue
            group_id = str(group.get("id") or "").strip()
            heading = str(group.get("heading") or "").strip()
            if not group_id:
                self.err(where, "group 需要 id")
                continue
            if group_id in group_ids:
                self.err(where, f"group id 重複：{group_id}")
                continue
            group_ids.add(group_id)
            if not heading:
                self.err(where, f"group {group_id} 需要 heading")
                heading = group_id
            self.group_headings[group_id] = heading

        seen: set[str] = set()
        previous: str | None = None
        for i, section in enumerate(data.get("sections", []) or []):
            if not isinstance(section, dict):
                continue
            where = str(section.get("id") or f"sections#{i + 1}")
            group_id = section.get("group")
            if not isinstance(group_id, str) or group_id not in group_ids:
                self.err(where, f"group 不存在於 groups：{group_id}")
            elif group_id != previous and group_id in seen:
                self.err(where, f"group {group_id} 的段落必須連續")
            if group_id != previous:
                if isinstance(group_id, str) and group_id in group_ids:
                    seen.add(group_id)
                previous = group_id if isinstance(group_id, str) else None
        return True

    def load_registry(self, required: bool = False) -> None:
        spec = self.data.get("kings_registry")
        if not spec:
            if required:
                self.err("kings_registry", "此頁型需要 kings_registry")
            return
        path = (self.data_path.parent / str(spec)).resolve()
        try:
            registry = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError) as exc:
            self.err("kings_registry", f"無法載入君王登錄檔：{exc}")
            return
        self.kings_registry = registry
        chronology = registry.get("chronology") or {}
        for field in ("label", "source", "note"):
            if not chronology.get(field):
                self.err(f"chronology.{field}", "年代資料需要此欄位")
        ids: set[str] = set()
        titles: set[str] = set()
        has_estimate = False
        for i, king in enumerate(registry.get("kings", []) or []):
            where = f"kings#{i + 1}"
            if not isinstance(king, dict):
                self.err(where, "王項目必須是 mapping")
                continue
            kid = str(king.get("id") or "")
            name = str(king.get("name") or kid)
            title = str(king.get("title") or name)
            king["title"] = title
            if not kid:
                self.err(where, "王項目需要 id")
            elif kid in ids:
                self.err(where, f"id 重複：{kid}")
            else:
                ids.add(kid)
            if not king.get("name"):
                self.err(where, "王項目需要 name")
            if title in titles:
                self.err(where, f"title 重複：{title}")
            titles.add(title)
            if kid:
                self.kings_by_id[kid] = king
            if king.get("kingdom") not in {"統一", "猶大", "以色列"}:
                self.err(where, "kingdom 必須是統一、猶大或以色列")

            verdict = king.get("verdict") or {}
            category = verdict.get("class")
            if category not in KING_CATEGORIES:
                self.err(where, "verdict.class 必須是 good、good_caveat、good_to_bad、bad_to_good、bad 或 none；mixed 已移除")
            items = verdict.get("items", []) or []
            valid_items = [item for item in items if isinstance(item, dict)]
            roles: list[str] = []
            for j, item in enumerate(items):
                iwhere = f"{where}.verdict.items#{j + 1}"
                if not isinstance(item, dict):
                    self.err(iwhere, "item 必須是 mapping")
                    continue
                role = item.get("role")
                roles.append(role)
                if role not in {"評語", "但書", "轉變"}:
                    self.err(iwhere, "role 只能是評語、但書或轉變")
                ref = str(item.get("ref") or "")
                parsed = self.registry_refs(ref, iwhere)
                if not str(item.get("quote") or "").strip():
                    self.err(iwhere, "quote 不能空白")
                ref_abbr = re.match(r"^([^\d\s]+)", ref.strip())
                if item.get("book") not in ABBR or not ref_abbr or item.get("book") != ref_abbr.group(1):
                    self.err(iwhere, "book 必須等於 ref 開頭的書卷簡稱")
                self.need_exact_text(str(item.get("quote") or ""), parsed, iwhere, "quote")
            has_evaluation = "評語" in roles
            has_caveat = "但書" in roles
            has_change = "轉變" in roles
            if category == "good":
                if not has_evaluation:
                    self.err(where, "class=good 至少需要一個評語")
                if has_caveat or has_change:
                    self.err(where, "class=good 不可含但書或轉變")
            elif category == "good_caveat":
                if not has_evaluation or not has_caveat:
                    self.err(where, "class=good_caveat 至少需要一個評語與一個但書")
                if has_change:
                    self.err(where, "class=good_caveat 不可含轉變")
            elif category == "bad":
                if not has_evaluation:
                    self.err(where, "class=bad 至少需要一個評語")
                if has_change:
                    self.err(where, "class=bad 不可含轉變")
            elif category in {"good_to_bad", "bad_to_good"}:
                if not has_evaluation or not has_change:
                    self.err(where, f"class={category} 至少需要一個評語與一個轉變")
            elif category == "none" and has_evaluation:
                self.err(where, "class=none 不可有評語")
            basis = verdict.get("basis")
            if category != "none" and not basis:
                self.err(where, "class 不是 none 時必須提供 basis")
            if basis and basis not in ABBR:
                self.err(where, f"basis 不是有效書卷簡稱：{basis}")
            if basis and not any(item.get("book") == basis for item in valid_items):
                self.err(where, "basis 必須至少對應一個 item 的 book")

            for field in ("synchronism",):
                for j, entry in enumerate(king.get(field, []) or []):
                    ewhere = f"{where}.{field}#{j + 1}"
                    if not isinstance(entry, dict):
                        self.err(ewhere, "項目必須是 mapping")
                        continue
                    parsed = self.registry_refs(str(entry.get("ref") or ""), ewhere)
                    if not str(entry.get("quote") or "").strip():
                        self.err(ewhere, "quote 不能空白")
                    self.need_exact_text(str(entry.get("quote") or ""), parsed, ewhere, "quote")

            prose = king.get("prose") or {}
            if not str(prose.get("text") or "").strip():
                self.err(where, "prose.text 不能空白")
            if not str(prose.get("refs") or "").strip():
                self.err(where, "prose.refs 不能空白")
            prose_parsed = self.registry_refs(str(prose.get("refs") or ""), f"{where}.prose.refs")
            self.check_exact_quotes(str(prose.get("text") or ""), prose_parsed, f"{where}.prose.text")
            for field in ("kings_refs", "chronicles_refs"):
                if king.get(field):
                    self.registry_refs(str(king[field]), f"{where}.{field}")
            for j, note in enumerate(king.get("notes", []) or []):
                nwhere = f"{where}.notes#{j + 1}"
                if not isinstance(note, dict):
                    self.err(nwhere, "讀經提醒必須是 mapping")
                    continue
                if not str(note.get("text") or "").strip():
                    self.err(nwhere, "text 不能空白")
                parsed = self.registry_refs(str(note.get("refs") or ""), nwhere)
                self.check_exact_quotes(str(note.get("text") or ""), parsed, nwhere)

            years = king.get("years") or {}
            has_estimate = has_estimate or bool(years.get("estimate"))
            try:
                start, end = int(years["start"]), int(years["end"])
                if start < end:
                    self.err(where, "years.start 必須大於或等於 years.end")
                if years.get("co_start") is not None and int(years["co_start"]) < start:
                    self.err(where, "years.co_start 必須大於或等於 years.start")
            except (KeyError, TypeError, ValueError):
                self.err(where, "years 需要有效的 start 與 end")

        if has_estimate and not chronology.get("estimate_source"):
            self.err("chronology.estimate_source", "有推估年代時需要 estimate_source")
        if required and not registry.get("kings"):
            self.err("kings_registry", "登錄檔沒有 kings")

    @staticmethod
    def verdict_display(king: dict) -> tuple[str, str]:
        category = (king.get("verdict") or {}).get("class")
        mark = KING_MARKS.get(category, KING_MARKS["none"])
        label = KING_LABELS.get(category, KING_LABELS["none"])
        if (king.get("verdict") or {}).get("differs"):
            mark += "※"
        return mark, label

    def king_years(self, king: dict) -> str:
        years = king["years"]
        start, end = int(years["start"]), int(years["end"])
        text = f"約主前 {start}–{end}" if start != end else f"約主前 {start}"
        if years.get("co_start") is not None:
            text += f"（約主前 {int(years['co_start'])} 起共治）"
        if years.get("estimate"):
            text += "（推估）"
        return text

    def validate_card(self, card: dict, where: str) -> None:
        if not isinstance(card, dict):
            self.err(where, "card 必須是 mapping")
            return
        king_id = card.get("king")
        if king_id and king_id not in self.kings_by_id:
            self.err(where, f"card.king 不在君王登錄檔：{king_id}")
        fields = card.get("fields", [])
        if not isinstance(fields, list):
            self.err(where, "card.fields 必須是清單")
            return
        for i, field in enumerate(fields):
            fwhere = f"{where}.fields#{i + 1}"
            if not isinstance(field, dict):
                self.err(fwhere, "field 必須是 mapping")
                continue
            for key in ("label", "text", "ref"):
                if not str(field.get(key) or "").strip():
                    self.err(fwhere, f"{key} 不能空白")
            parsed = self.refs(str(field.get("ref") or ""), fwhere)
            self.check_exact_quotes(str(field.get("text") or ""), parsed, fwhere)
            checks = field.get("check", []) or []
            if not isinstance(checks, list):
                self.err(fwhere, "check 必須是清單")
            else:
                for check in checks:
                    self.need_exact_text(str(check), parsed, fwhere, "核對字串")
            self.cover(parsed)

    # ---------- 族譜資料 ----------
    def record_names(self, shown: str, parsed) -> None:
        for b, c, v in parsed:
            if b == self.book:
                self.verse_names[(c, v)].append(shown)

    def in_section(self, nid: str, sid: str) -> bool:
        return self.nodes[nid]["section"] == sid or nid in self.section_extra.get(sid, [])

    def mark_section_extra(self, nid: str, sid: str) -> None:
        if nid not in self.section_extra[sid]:
            self.section_extra[sid].append(nid)

    def add_node(self, item, parent: str | None, rel: str, st: dict, parsed, where: str, section: str) -> str | None:
        if isinstance(item, str):
            item = {"id": item}
        nid = item["id"]
        shown = item.get("as", display(nid))
        self.need_text(shown, parsed, where, "人名")
        if item.get("of"):
            self.need_text(item["of"], parsed, where, "地名")
        for s in item.get("check", []):
            self.need_text(s, parsed, where, "註記用字")
        self.check_quotes(item.get("note", ""), parsed, where)
        seen = st.setdefault("_seen", set())
        if nid in seen:
            self.err(where, f"同一句裡「{nid}」出現兩次；同名不同人請用「名#識別」")
        seen.add(nid)
        self.record_names(shown, parsed)
        if nid in self.nodes:
            # 已定義：同一父系視為重述（例如 6:50–53、9:35–44），父系不同就是衝突
            node = self.nodes[nid]
            if node["parent"] != parent:
                self.err(where, f"「{nid}」已在 {node['ref']} 定義為 {node['parent']} 的後代，此處卻接在 {parent}；"
                                "同名不同人請用「名#識別」")
            if item.get("as") and item["as"] != node["name"]:
                node["aliases"].append((st["ref"], item["as"]))
            node["restated"].append(st["ref"])
            if not self._loading_import and node.get("imported_page"):
                self.mark_section_extra(nid, section)
                node.setdefault("used_section", section)
            return nid
        node_section = f"@{self._imported_page}:{section}" if self._loading_import else section
        self.nodes[nid] = {
            "id": nid, "name": display(nid), "parent": parent, "rel": item.get("rel", rel),
            "ref": st["ref"], "of": item.get("of"), "of_word": item.get("of_word", "之祖"),
            "note": item.get("note"), "kind": item.get("kind"),
            "mark": item.get("mark"), "mother": item.get("mother", st.get("mother")),
            "aliases": [(st["ref"], item["as"])] if item.get("as") else [], "restated": [],
            "section": node_section, "section_title": self._current_section_title,
            "imported_page": self._imported_page if self._loading_import else None,
            "pnote": item.get("pnote", st.get("pnote")),
        }
        if parent:
            self.children[parent].append(nid)
        return nid

    def ensure_parent(self, pid: str, st: dict, parsed, where: str, section: str) -> bool:
        if pid in self.nodes:
            if not self._loading_import and self.nodes[pid].get("imported_page"):
                self.nodes[pid].setdefault("used_section", section)
            shown = st.get("parent_as", display(pid))
            if st.get("parent_in_text", True):
                self.need_text(shown, parsed, where, "父名")
            if shown != self.nodes[pid]["name"] and (st["ref"], shown) not in self.nodes[pid]["aliases"]:
                self.nodes[pid]["aliases"].append((st["ref"], shown))
            return True
        if st.get("new_parent"):
            self.add_node({"id": pid, "as": st.get("parent_as", display(pid))}, None, "子",
                          {**st, "restate": False}, parsed, where, section)
            return True
        self.err(where, f"父名「{pid}」尚未定義（新的源頭請標 new_parent: true）")
        return False

    def load_genealogy(self, data: dict | None = None, imported_page: str | None = None) -> None:
        data = data or self.data
        old_book, old_abbr = self.book, self.abbr
        if imported_page:
            self.book = data["book"]
            self.abbr = FULL_TO_ABBR[self.book]
        self._loading_import = imported_page is not None
        self._imported_page = imported_page
        if not imported_page:
            self.grouped_sections = self.validate_section_groups(data)
            self.section_order = {sec["id"]: i for i, sec in enumerate(data["sections"])}
            self.section_titles = {sec["id"]: sec["title"] for sec in data["sections"]}
            lo, hi = data["scope"]
            intro_refs = [(data["book"], chapter, verse)
                          for chapter in range(lo, hi + 1)
                          for verse in range(1, len(self.sc.chapter(data["book"], chapter)) + 1)]
            if data.get("check_intro_quotes"):
                self.check_quotes(data.get("intro", ""), intro_refs, "intro")
        for sec in data["sections"]:
            sid = sec["id"]
            label = f"import[{imported_page}]::{sid}" if imported_page else sid
            self._current_section_title = sec["title"]
            section_refs = self.refs(sec["range"], f"{label}.range")
            # 段落說明的引句檢查由頁面 check_intro_quotes 開啟（族譜頁的說明用「」標示用語，不檢查）
            if data.get("check_intro_quotes"):
                self.check_quotes(sec.get("intro", ""), section_refs, f"{label}.intro")
            if "card" in sec:
                self.validate_card(sec["card"], f"{label}.card")
            for i, st in enumerate(sec.get("statements", [])):
                where = f"{label}#{i + 1}({st.get('ref')})"
                parsed = self.refs(st["ref"], where)
                if not self._loading_import:
                    self.cover(parsed)
                if st.get("mother"):
                    self.need_text(st["mother"], parsed, where, "母名")
                for s in st.get("check", []):
                    self.need_text(s, parsed, where, "註記用字")
                self.check_quotes(st.get("note", ""), parsed, where)
                if "chain" in st:
                    chain = st["chain"]
                    first = chain[0] if isinstance(chain[0], str) else chain[0]["id"]
                    if first in self.nodes:
                        if not self._loading_import and self.nodes[first].get("imported_page"):
                            self.nodes[first].setdefault("used_section", sid)
                            self.mark_section_extra(first, sid)
                        shown = chain[0].get("as", display(first)) if isinstance(chain[0], dict) else display(first)
                        self.need_text(shown, parsed, where, "人名")
                        self.record_names(shown, parsed)
                        prev = first
                    elif st.get("new_parent") or st.get("new_root"):
                        prev = self.add_node(chain[0], None, "子", {**st, "restate": False}, parsed, where, sid)
                    else:
                        self.err(where, f"鏈首「{first}」尚未定義（新的源頭請標 new_root: true）")
                        continue
                    for item in chain[1:]:
                        prev = self.add_node(item, prev, "子", st, parsed, where, sid)
                elif "children" in st:
                    pid = st["parent"]
                    if not self.ensure_parent(pid, st, parsed, where, sid):
                        continue
                    for item in st["children"]:
                        self.add_node(item, pid, st.get("rel", "子"), st, parsed, where, sid)
                elif "roots" in st:
                    for item in st["roots"]:
                        self.add_node(item, None, "子", st, parsed, where, sid)
                elif "places" in st:
                    for p in st["places"]:
                        self.need_text(p, parsed, where, "地名")
                elif st.get("covers"):
                    pass  # 只宣告涵蓋（敘事節、總結句），內容在 note
                elif "roster" in st:
                    pass
                else:
                    self.err(where, "statement 需要 chain / children / roots / roster / covers 其一")
                if "roster" in st and not self._loading_import:
                    self.load_roster(st, parsed, where, sid, sec["title"])
            for note in sec.get("notes", []):
                where = f"{label}.notes"
                parsed = self.refs(note["refs"], where)
                self.check_quotes(note["text"], parsed, where)
            if sec.get("spine"):
                a, b = sec["spine"]
                if a not in self.nodes or b not in self.nodes:
                    self.err(f"{label}.spine", f"主線端點不存在：{a} / {b}")
                elif not self.path(a, b):
                    self.err(f"{label}.spine", f"{b} 不是 {a} 的後代")
            if sec.get("org"):
                self.validate_org(sec["org"], f"{label}.org")
        self._loading_import = False
        self._imported_page = None
        self._current_section_title = ""
        self.book, self.abbr = old_book, old_abbr

    def load_imports(self) -> None:
        for i, item in enumerate(self.data.get("imports", [])):
            where = f"imports#{i + 1}"
            try:
                path = (self.dir / item["file"]).resolve()
                imported = yaml.safe_load(path.read_text(encoding="utf-8"))
                page = item["page"]
            except (KeyError, OSError, yaml.YAMLError) as exc:
                self.err(where, f"無法載入匯入資料：{exc}")
                continue
            self.load_genealogy(imported, page)
        self.load_genealogy()
        overview = self.data.get("overview") or {}
        if overview.get("org"):
            self.validate_org(overview["org"], "overview.org")

    def validate_org(self, roots: list[dict], where: str) -> None:
        def visit(nodes: list[dict], path: str) -> None:
            for i, node in enumerate(nodes):
                here = f"{path}#{i + 1}"
                parsed = self.refs(node.get("ref", ""), here)
                checks = node.get("check")
                if not isinstance(checks, list) or not checks:
                    self.err(here, "org 節點的 check 必須是至少含一項的清單")
                else:
                    for check in checks:
                        if not self.has_literal_text(check, parsed):
                            self.err(here, f"核對字串「{check}」未逐字出現在所引經文")
                if not self._loading_import:
                    self.cover(parsed)
                if node.get("children"):
                    visit(node["children"], here + ".children")
        visit(roots or [], where)

    def load_roster(self, st: dict, statement_parsed, where: str, section: str, section_title: str) -> None:
        seen = st.setdefault("_seen", set())
        for i, member in enumerate(st.get("roster", [])):
            mwhere = f"{where}.roster#{i + 1}"
            if not isinstance(member, dict) or not member.get("id"):
                self.err(mwhere, "roster 成員需要 id")
                continue
            nid = member["id"]
            ref = str(member.get("ref", st["ref"]))
            parsed = self.refs(ref, mwhere)
            shown = member.get("as", display(nid))
            self.need_literal_text(shown, parsed, mwhere, "人名")
            for field, what in (("pos", "次序或職分"), ("desc", "經文介紹"), ("count", "人數")):
                if member.get(field):
                    self.need_literal_text(member[field], parsed, mwhere, what)
            self.check_quotes(member.get("note", ""), parsed, mwhere)
            if nid in seen:
                self.err(mwhere, f"同一句裡「{nid}」出現兩次；同名不同人請用「名#識別」")
            seen.add(nid)
            self.cover(parsed)
            self.record_names(shown, parsed)
            if nid not in self.people:
                self.people[nid] = {
                    "id": nid, "name": display(nid), "first_ref": ref,
                    "first_section": section, "first_section_title": section_title,
                    "first_desc": member.get("desc"), "first_pos": member.get("pos"),
                    "appearances": [],
                }
            member["_appearance_index"] = len(self.people[nid]["appearances"])
            self.people[nid]["appearances"].append((ref, section))

    def path(self, a: str, b: str) -> list[str]:
        seq = [b]
        while seq[-1] != a:
            p = self.nodes[seq[-1]]["parent"]
            if p is None:
                return []
            seq.append(p)
        return list(reversed(seq))

    # ---------- 附表 ----------
    def load_extras(self) -> None:
        ex = self.extras or {}
        for i, card in enumerate(ex.get("cards", [])):
            where = f"cards#{i + 1}({card.get('id')})"
            if card["id"] not in self.nodes and card["id"] not in self.people:
                self.err(where, "人物卡對應的人物不在族譜或職分名單中")
            parsed = self.refs(card["refs"], where)
            self.check_quotes(card["text"], parsed, where)
        for i, row in enumerate(ex.get("parallels", [])):
            where = f"parallels#{i + 1}"
            for side in ("a", "b"):
                parsed = self.refs(row[f"{side}_ref"], where)
                for s in row[f"{side}_text"].split("／"):
                    self.need_text(s, parsed, where, f"{side} 方字串")
        for i, row in enumerate(ex.get("troops", [])):
            where = f"troops#{i + 1}"
            parsed = self.refs(row["ref"], where)
            self.need_text(row["text"], parsed, where, "人數")
        for i, row in enumerate(ex.get("cities", [])):
            where = f"cities#{i + 1}({row['family']})"
            parsed = self.refs(row["ref"], where)
            for city in row["cities"]:
                self.need_text(city.rstrip("*"), parsed, where, "城名")
            if row.get("count_text"):
                self.need_text(row["count_text"], self.refs(row["count_ref"], where), where, "城數")
        for i, table in enumerate(ex.get("tables", [])):
            where = f"tables#{i + 1}"
            if not isinstance(table, dict):
                self.err(where, "table 必須是 mapping")
                continue
            if not table.get("heading"):
                self.err(where, "heading 不能空白")
            columns = table.get("columns", [])
            if not isinstance(columns, list) or not columns:
                self.err(where, "columns 必須是非空清單")
                continue
            data_columns = len(columns) - (1 if columns[-1] == "經節" else 0)
            for j, row in enumerate(table.get("rows", []) or []):
                rwhere = f"{where}.rows#{j + 1}"
                if not isinstance(row, dict):
                    self.err(rwhere, "row 必須是 mapping")
                    continue
                cells = row.get("cells", [])
                if not isinstance(cells, list) or len(cells) != data_columns:
                    self.err(rwhere, f"cells 數量應為 {data_columns}")
                    continue
                if not str(row.get("ref") or "").strip():
                    self.err(rwhere, "ref 不能空白")
                parsed = self.refs(str(row.get("ref") or ""), rwhere)
                for cell in cells:
                    self.check_exact_quotes(str(cell), parsed, rwhere)
                checks = row.get("check", []) or []
                if not isinstance(checks, list):
                    self.err(rwhere, "check 必須是清單")
                else:
                    for check in checks:
                        self.need_exact_text(str(check), parsed, rwhere, "核對字串")
                self.cover(parsed)
        for name in ex.get("homonyms", []):
            ids = [i for i, n in self.nodes.items() if not n.get("imported_page") and n["name"] == name]
            ids += [i for i, person in self.people.items() if person["name"] == name and i not in ids]
            if len(ids) < 2:
                self.err("homonyms", f"「{name}」在資料裡只有 {len(ids)} 人，不算同名不同人")
        for i, item in enumerate(ex.get("uncovered", [])):
            parsed = self.refs(item["refs"], f"uncovered#{i + 1}")
            self.cover(parsed)
        for key in ("cards", "parallels", "troops", "cities"):
            for row in ex.get(key, []):
                for field in ("refs", "ref", "a_ref"):
                    if row.get(field):
                        self.cover(self.refs(row[field], key))

    def check_coverage(self) -> None:
        lo, hi = self.data["scope"]
        for c in range(lo, hi + 1):
            for v in range(1, len(self.sc.chapter(self.book, c)) + 1):
                if (c, v) not in self.covered:
                    self.err("coverage", f"{self.abbr}{c}:{v} 沒有任何資料涵蓋")

    # ---------- 產生頁面 ----------
    def label(self, nid: str, with_rel: bool = True) -> str:
        n = self.nodes[nid]
        s = n["name"]
        extra = []
        if with_rel and n["rel"] != "子":
            s = f"〔{n['rel']}〕{s}"
        if n["of"]:
            extra.append(f"{n['of']}{n['of_word']}")
        if n["pnote"]:
            extra.append(n["pnote"])
        by_alias: "OrderedDict[str, list[str]]" = OrderedDict()
        for ref, alias in n["aliases"]:
            if alias != n["name"]:
                by_alias.setdefault(alias, []).append(fmt_ref(ref, self.book))
        for alias, refs in by_alias.items():
            extra.append(f"{refs[0]} {'起' if len(refs) > 1 else ''}作{alias}")
        if n["note"]:
            extra.append(n["note"])
        return s + (f"（{'；'.join(extra)}）" if extra else "")

    def chain_run(self, nid: str, section: str | None = None) -> list[str]:
        section = section or self.nodes[nid]["section"]
        run = [nid]
        if not self.in_section(nid, section):
            return run
        while True:
            kids = self.children.get(run[-1], [])
            if len(kids) != 1:
                return run
            k = kids[0]
            n = self.nodes[k]
            if n["rel"] != "子" or n["mother"] or not self.in_section(k, section) or n["section"] != self.nodes[nid]["section"]:
                return run
            run.append(k)

    def render_list(self, nid: str, depth: int, out: list[str], section: str, prefix: str) -> None:
        run = self.chain_run(nid, section)
        text = " → ".join(self.label(x, with_rel=(i == 0)) for i, x in enumerate(run))
        if any(self.nodes[x]["mark"] == "main" for x in run):
            text = f"★ {text}"
        if len(run) >= 4:
            text += f"　*（{len(run)} 代）*"
        if self.data.get("chain_ref_span"):
            refs: list[tuple[str, dict]] = []
            seen_refs: set[str] = set()
            for chain_id in run:
                node = self.nodes[chain_id]
                for ref in re.split(r"[,，;；、]\s*", str(node["ref"])):
                    formatted = fmt_ref(ref.strip(), self.book)
                    if formatted and formatted not in seen_refs:
                        seen_refs.add(formatted)
                        refs.append((formatted, node))
            rendered_refs = []
            linked_import = False
            for ref, node in refs:
                if node.get("imported_page") and not linked_import:
                    page = node["imported_page"]
                    page = page[:-3] if page.endswith(".md") else page
                    rendered_refs.append(f"[[{page}#{node['section_title']}|族譜 {ref}]]")
                    linked_import = True
                else:
                    rendered_refs.append(ref)
            if linked_import:
                ref_text = "、".join(
                    item if item.startswith("[[") else f"{chr(96)}{item}{chr(96)}"
                    for item in rendered_refs
                )
            else:
                ref_text = f"{chr(96)}{'、'.join(rendered_refs)}{chr(96)}"
        else:
            ref = self.nodes[run[0]]["ref"]
            node = self.nodes[run[0]]
            if node.get("imported_page"):
                page = node["imported_page"]
                page = page[:-3] if page.endswith(".md") else page
                ref_text = f"[[{page}#{node['section_title']}|族譜 {fmt_ref(ref, self.book)}]]"
            else:
                ref_text = f"{chr(96)}{fmt_ref(ref, self.book)}{chr(96)}"
        out.append(f"{prefix}{'  ' * depth}- {text}　{ref_text}")
        last = run[-1]
        kids = [k for k in self.children.get(last, []) if self.in_section(k, section)]
        groups: "OrderedDict[str | None, list[str]]" = OrderedDict()
        for k in kids:
            groups.setdefault(self.nodes[k]["mother"], []).append(k)
        multi = len(groups) > 1 or (None not in groups and groups)
        for mother, members in groups.items():
            d = depth + 1
            if multi and mother:
                out.append(f"{prefix}{'  ' * d}- *{mother}所生*")
                d += 1
            for k in members:
                self.render_list(k, d, out, section, prefix)

    def mermaid(self, roots: list[str], section: str, limit: int = 60) -> list[str]:
        lines = ["```mermaid", "flowchart LR"]
        counter = [0]
        styled_main, styled_anchor, styled_mom = [], [], []

        def nid_of() -> str:
            counter[0] += 1
            return f"n{counter[0]}"

        def esc(s: str) -> str:
            return s.replace('"', "#quot;")

        budget = [limit]

        def walk(node: str, parent_mid: str | None, edge: str) -> None:
            run = self.chain_run(node, section)
            names = [self.nodes[x]["name"] for x in run]
            alias = next((a for _, a in self.nodes[run[0]]["aliases"] if a != names[0]), None)
            if alias:
                names[0] = f"{names[0]}（{alias}）"
            if len(names) > 4:
                parts = [" → ".join(names[i:i + 4]) for i in range(0, len(names), 4)]
                text = " →<br/>".join(parts) + f"<br/>（{len(names)} 代）"
            else:
                text = " → ".join(names)
            mid = nid_of()
            lines.append(f'  {mid}["{esc(text)}"]')
            if parent_mid:
                lines.append(f"  {parent_mid} -->{'|' + esc(edge) + '|' if edge else ''} {mid}")
            if any(self.nodes[x]["mark"] == "main" for x in run):
                styled_main.append(mid)
            if any(self.nodes[x].get("imported_page") for x in run) or not self.in_section(run[0], section):
                styled_anchor.append(mid)
            budget[0] -= 1
            kids = [k for k in self.children.get(run[-1], []) if self.in_section(k, section)]
            if not kids:
                return
            if budget[0] <= 0:
                more = nid_of()
                lines.append(f'  {more}["…另 {self.count_desc(kids, section)} 人，見完整名單"]')
                lines.append(f"  {mid} --> {more}")
                return
            # 同一母親、或同一種非「子」關係（子孫、諸族…）的兒女，收到一個小圓角節點底下
            group_nodes: dict[str, str] = {}
            rel_count: dict[str, int] = defaultdict(int)
            for k in kids:
                rel_count[self.nodes[k]["rel"]] += 1
            for k in kids:
                n = self.nodes[k]
                lab = n["rel"] if n["rel"] != "子" else ""
                key = f"{n['mother']}所生" if n["mother"] else (lab if lab and rel_count[n["rel"]] > 1 else None)
                src = mid
                if key:
                    if key not in group_nodes:
                        group_nodes[key] = nid_of()
                        lines.append(f'  {group_nodes[key]}(["{esc(key)}"])')
                        lines.append(f"  {mid} --- {group_nodes[key]}")
                        styled_mom.append(group_nodes[key])
                    src = group_nodes[key]
                    if not n["mother"]:
                        lab = ""
                walk(k, src, lab)

        for r in roots:
            walk(r, None, "")
        lines.append("  classDef main fill:#d4a82e44,stroke:#c9971c,stroke-width:2px,font-weight:bold")
        lines.append("  classDef anchor fill:#7a8ca533,stroke:#7a8ca5")
        if styled_main:
            lines.append(f"  class {','.join(styled_main)} main")
        lines.append("  classDef mom fill:#8a7bb022,stroke:#9a8cc4,stroke-dasharray:3 3,font-size:12px")
        if styled_anchor:
            lines.append(f"  class {','.join(styled_anchor)} anchor")
        if styled_mom:
            lines.append(f"  class {','.join(styled_mom)} mom")
        lines.append("```")
        return lines

    def count_desc(self, kids: list[str], section: str) -> int:
        total = 0
        stack = list(kids)
        while stack:
            k = stack.pop()
            total += 1
            stack += [c for c in self.children.get(k, []) if self.in_section(c, section)]
        return total

    def section_roots(self, sec: dict) -> list[str]:
        sid = sec["id"]
        roots: list[str] = []
        for nid, n in self.nodes.items():
            if not self.in_section(nid, sid):
                continue
            p = n["parent"]
            if p is None or not self.in_section(p, sid):
                top = p if p is not None else nid
                if top not in roots:
                    roots.append(top)
        return roots

    def depth_of(self, nid: str, section: str) -> int:
        kids = [k for k in self.children.get(nid, []) if self.in_section(k, section)]
        return 1 + max((self.depth_of(k, section) for k in kids), default=0)

    def verse_count(self, ranges: list[str]) -> int:
        seen = set()
        for r in ranges:
            for b, c, v in parse_refs(r, self.book, self.sc):
                seen.add((b, c, v))
        return len(seen)

    def render(self) -> str:
        d, ex = self.data, self.extras or {}
        out: list[str] = [f"# {d['title']}", ""]
        navigation = self.series_navigation()
        if navigation:
            out += [navigation, ""]
        out += [d["intro"].strip(), ""]
        out += ["<!-- 本頁由 appendix/genealogy/build_genealogy.py 從 appendix/genealogy/" + self.book + "/ 的資料檔產生，請改資料檔，不要直接改本頁。 -->", ""]
        howto = d.get("howto", [
            "**金色框**（名單裡標 ★）：作者一路追下去的主線，例如大衛王室、大祭司、掃羅家。",
            "**藍灰色框**：從前一段接過來的人，方便看出這一段掛在誰底下。",
            f"{chr(96)}2:10{chr(96)} 這樣的灰字是經節；沒寫書名的都是歷代志上。",
            "一長串單傳的世代收成一行「甲 → 乙 → 丙」，括號裡標代數。",
            "人名一律照和合本；別處經文寫法不同的，見文末「平行經文對照」。",
        ])
        out.append("> [!info] 怎麼讀這份圖")
        out += [f"> - {item}" for item in howto]
        out.append("")

        # 總覽
        overview = d.get("overview")
        if overview:
            out += ["## 總覽", "", f"### {overview.get('heading', '從亞當到以色列十二個兒子')}", ""]
            if overview.get("spine") or overview.get("tribes"):
                out += self.overview_mermaid()
            elif overview.get("org"):
                out += self.org_mermaid(overview["org"])
            if overview.get("bars"):
                out += ["", f"### {overview.get('bars_heading', '篇幅分給了誰')}", "",
                        overview.get("bars_intro", "每個支派在歷代志上 1–9 章佔幾節："), ""]
                out += self.bars()
                out.append("")
            if d.get("overview_note"):
                out += [d["overview_note"].strip(), ""]
        # 目錄
        out += ["### 目錄" if overview else "## 目錄", ""]
        if self.grouped_sections:
            current_group = None
            for sec in d["sections"]:
                group_id = sec["group"]
                if group_id != current_group:
                    current_group = group_id
                    heading = self.group_headings[group_id]
                    out.append(f"- **[[#{heading}|{heading}]]**")
                out.append(f"  - [[#{sec['title']}|{sec['title']}]]　`{fmt_ref(sec['range'], self.book)}`")
        else:
            current = None
            for sec in d["sections"]:
                if sec["chapter"] != current:
                    current = sec["chapter"]
                    ch_title = f"第 {current} 章　{d['chapters'][current]}"
                    out.append(f"- **[[#{ch_title}|第 {current} 章]]**")
                out.append(f"  - [[#{sec['title']}|{sec['title']}]]　`{fmt_ref(sec['range'], self.book)}`")
        if ex.get("parallels") or ex.get("homonyms") or ex.get("troops") or ex.get("cities") or ex.get("tables"):
            out.append("- **[[#附表|附表]]**")
            if ex.get("parallels"):
                out.append("  - [[#平行經文對照|平行經文對照]]")
            if ex.get("homonyms"):
                out.append("  - [[#同名不同人|同名不同人]]")
            if ex.get("troops"):
                out.append("  - [[#經文記下的人數|經文記下的人數]]")
            if ex.get("cities"):
                out.append("  - [[#利未人的城邑（6:54–81）|利未人的城邑（6:54–81）]]")
            for table in ex.get("tables", []) or []:
                heading = table.get("heading", "附表")
                out.append(f"  - [[#{heading}|{heading}]]")
        out.append("")
        # 各段
        cards = defaultdict(list)
        for card in ex.get("cards", []):
            node = self.nodes.get(card["id"])
            person = self.people.get(card["id"])
            occurrences = []
            if node:
                node_section = node.get("used_section") if node.get("imported_page") else node["section"]
                if node_section and not node_section.startswith("@"):
                    occurrences.append(node_section)
            if person:
                occurrences.append(person["first_section"])
            section_id = min(occurrences, key=lambda sid: self.section_order.get(sid, 10**9)) if occurrences else None
            if section_id:
                cards[section_id].append(card)
        current = None
        for sec in d["sections"]:
            if self.grouped_sections:
                group_id = sec["group"]
                if group_id != current:
                    current = group_id
                    out += ["---", "", f"## {self.group_headings[group_id]}", ""]
            elif sec["chapter"] != current:
                current = sec["chapter"]
                out += ["---", "", f"## 第 {current} 章　{d['chapters'][current]}", ""]
            out += [f"### {sec['title']}", "", f"`{fmt_ref(sec['range'], self.book)}`　{sec['intro'].strip()}", ""]
            if sec.get("card"):
                out += self.render_card(sec["card"], sec["title"])
            if sec.get("org"):
                out += self.org_mermaid(sec["org"]) + [""]
            if sec.get("spine"):
                p = self.path(*sec["spine"])
                names = " → ".join(self.nodes[x]["name"] for x in p)
                out += [f"> [!tip] 主線（{len(p)} 代）", f"> {names}", ""]
            roots = self.section_roots(sec)
            # 只把三代以上的家族畫成圖；零散的小家族只列在名單裡，圖才不會被切碎
            deep = [r for r in roots if self.depth_of(r, sec["id"]) >= 3]
            if deep:
                out += self.mermaid(deep, sec["id"]) + [""]
            if roots:
                listing: list[str] = []
                for r in roots:
                    self.render_list(r, 0, listing, sec["id"], "> ")
                fold = "-" if len(listing) > 25 else "+"
                out += [f"> [!abstract]{fold} 完整名單（{self.count_section(sec['id'])} 人）"] + listing + [""]
            # 同一段裡連續、沒有小標題的名單合成一張表（表格本來就連續輸出，分開只會變成一列一張）
            tables: list[dict] = []
            for st in sec.get("statements", []):
                if "roster" not in st:
                    continue
                for member in st["roster"]:
                    member.setdefault("ref", st["ref"])
                if not st.get("label") and tables and not tables[-1].get("label"):
                    tables[-1]["roster"] = tables[-1]["roster"] + st["roster"]
                else:
                    tables.append({**st})
            for st in tables:
                out += self.render_roster(st, sec)
            facts = []
            for st in sec.get("statements", []):
                ref = f"`{fmt_ref(st['ref'], self.book)}`"
                if "places" in st:
                    tail = f"　{st['note'].strip()}" if st.get("note") else ""
                    facts.append(f"- **{st['label']}**：{'、'.join(st['places'])}{tail}　{ref}")
                elif st.get("note"):
                    facts.append(f"- {st['note'].strip()}　{ref}")
            if facts:
                out += facts + [""]
            if cards.get(sec["id"]):
                out += ["**人物**", ""]
                for card in cards[sec["id"]]:
                    out.append(f"- **{display(card['id'])}**　{card['text'].strip()}　`{card['refs']}`")
                out.append("")
            if sec.get("notes"):
                out.append("> [!note] 讀經提醒")
                for note in sec["notes"]:
                    out.append(f"> - {note['text'].strip()}　`{note['refs']}`")
                out.append("")
            out += [f"[[#目錄|↑ 回到目錄]] · [[#{d['title']}|回到頂部]]", ""]
        out += self.tables()
        if d.get("footer"):
            out += ["---", "", d["footer"].strip(), ""]
        page = "\n".join(out)
        allowed = {
            item["path"][:-3] if item["path"].endswith(".md") else item["path"]
            for item in self.series.get("pages", []) if item.get("ready")
        }
        cross_links = []
        for link in re.findall(r"\[\[([^\]]+)\]\]", page):
            target = link.split("|", 1)[0].split("#", 1)[0]
            if target and target not in allowed:
                cross_links.append(target)
        if cross_links:
            self.err("render", f"頁面含未列入 ready 系列的跨檔 [[ 連結：{cross_links[:5]}")
        return page

    def series_navigation(self) -> str:
        ready = [item for item in self.series.get("pages", []) if item.get("ready")]
        if len(ready) <= 1:
            return ""
        own = next((item for item in ready
                    if str(item.get("data", "")).replace(chr(92), "/") == self.data_spec), None)
        if own is None:
            return ""
        labels = []
        for item in ready:
            if item is own:
                labels.append(f"**{item['short']}**")
            else:
                path = item["path"][:-3] if item["path"].endswith(".md") else item["path"]
                labels.append(f"[[{path}|{item['short']}]]")
        return "> 歷代志人物系列：" + " · ".join(labels)

    def series_data_file(self, item: dict) -> Path:
        normalized = str(item.get("data", "")).replace(chr(92), "/")
        parts = normalized.split("/")
        if len(parts) == 1:
            return HERE / parts[0] / "genealogy.yaml"
        return HERE.joinpath(*parts[:-1]) / f"{parts[-1]}.yaml"

    @staticmethod
    def page_target(item: dict) -> str:
        path = str(item.get("path", ""))
        return path[:-3] if path.endswith(".md") else path

    def render_compare(self) -> str:
        data = self.data
        registry = self.kings_registry
        kings = registry.get("kings", []) or []
        groups = data.get("groups", []) or []
        out = [f"# {data['title']}", ""]
        navigation = self.series_navigation()
        if navigation:
            out += [navigation, ""]
        out += [str(data.get("intro", "")).strip(), "",
                "<!-- 本頁由 appendix/genealogy/build_genealogy.py 從 YAML 資料產生，請改資料檔，不要直接改本頁。 -->", "",
                "> [!info] 怎麼讀這份圖"]
        out += [f"> - {item}" for item in data.get("howto", []) or []]
        out += ["", "## 目錄", "", "- [[#年代圖|年代圖]]", "- [[#評語對照|評語對照]]",
                "- [[#列王紀和歷代志寫法不同|寫法不同]]"]
        for group in groups:
            heading = str(group.get("heading", group.get("kingdom", "")))
            out.append(f"- [[#{heading}|{heading}]]")
            for king in kings:
                if king.get("kingdom") == group.get("kingdom"):
                    out.append(f"  - [[#{king.get('title', king.get('name', king.get('id')))}|{king.get('name', king.get('id'))}]]")
        out += ["", "## 年代圖", "", f"色條的長短照 {registry['chronology']['label']}，經文本身沒有公元年份。", "",
                "> [!info] 年代出處", f"> - {registry['chronology']['source']}"]
        if registry["chronology"].get("estimate_source"):
            out.append(f"> - 推估年代：{registry['chronology']['estimate_source']}")
        out.append(f"> - {registry['chronology']['note']}")
        out += [""] + timeline_svg(kings).splitlines() + ["", "## 評語對照", ""]
        for group in groups:
            kingdom = group.get("kingdom")
            heading = str(group.get("heading", kingdom))
            out += [f"### {heading}的王", ""]
            out += ["| 王 | 分類 | 評語原句 | 但書或轉變 | 經節 |", "|---|---|---|---|---|"]
            for king in kings:
                if king.get("kingdom") != kingdom:
                    continue
                items = (king.get("verdict") or {}).get("items", []) or []
                basis = (king.get("verdict") or {}).get("basis")
                evaluations = [item for item in items if item.get("book") == basis and item.get("role") == "評語"]
                qualifications = [item for item in items if item.get("role") in {"但書", "轉變"}]
                if (king.get("verdict") or {}).get("class") == "none":
                    evaluation_text = "經文沒有評語"
                else:
                    evaluation_text = "<br/>".join(f"「{item['quote']}」" for item in evaluations)
                qualification_text = "<br/>".join(f"{item['role']}：「{item['quote']}」" for item in qualifications)
                refs = []
                for item in evaluations + qualifications:
                    if item["ref"] not in refs:
                        refs.append(item["ref"])
                mark, label = self.verdict_display(king)
                name = str(king.get("name", king.get("id", "")))
                title = str(king.get("title", name))
                out.append(f"| [[#{title}|{name}]] | {mark} {label} | {evaluation_text} | {qualification_text} | {'<br/>'.join(fmt_ref(ref, self.book) for ref in refs)} |")
            out.append("")

        out += ["## 列王紀和歷代志寫法不同", "", "| 王 | 列王紀 | 歷代志 |", "|---|---|---|"]
        for king in kings:
            if not (king.get("verdict") or {}).get("differs"):
                continue
            items = (king.get("verdict") or {}).get("items", []) or []
            cells = []
            for books in ({"王上", "王下"}, {"代上", "代下"}):
                selected = [item for item in items if item.get("book") in books]
                cells.append("<br/>".join(f"{item['role']}：「{item['quote']}」　`{fmt_ref(item['ref'], self.book)}`" for item in selected) or "沒有評語")
            title = str(king.get("title", king.get("name", "")))
            name = str(king.get("name", king.get("id", "")))
            out.append(f"| [[#{title}|{name}]] | {cells[0]} | {cells[1]} |")
        out.append("")

        for group in groups:
            kingdom = group.get("kingdom")
            heading = str(group.get("heading", kingdom))
            out += [f"## {heading}", ""]
            if group.get("intro"):
                out += [str(group["intro"]).strip(), ""]
            for king in kings:
                if king.get("kingdom") != kingdom:
                    continue
                mark, label = self.verdict_display(king)
                title = str(king.get("title", king.get("name", king.get("id"))))
                name = str(king.get("name", king.get("id", "")))
                out += [f"### {title}", "", f"**{mark} {label}**　{self.king_years(king)}", ""]
                synchronisms = king.get("synchronism", []) or []
                if synchronisms:
                    values = [f"「{entry['quote']}」　`{fmt_ref(entry['ref'], self.book)}`" for entry in synchronisms]
                    out += ["對照紀年：" + "；".join(values), ""]
                prose = king["prose"]
                out += [str(prose["text"]).strip(), "", f"`{fmt_ref(prose['refs'], self.book)}`", ""]
                if kingdom == "以色列" and king.get("chronicles_refs"):
                    out += [f"歷代志下提到他：`{fmt_ref(king['chronicles_refs'], self.book)}`", ""]
                if king.get("kings_refs"):
                    books = []
                    for part in re.split(r"[,，;；]\s*", str(king["kings_refs"])):
                        name = "撒母耳記" if part.startswith("撒") else "列王紀" if part.startswith("王") else ""
                        if name and name not in books:
                            books.append(name)
                    out += [f"{'、'.join(books) or '列王紀'}：`{fmt_ref(king['kings_refs'], self.book)}`", ""]
                if king.get("notes"):
                    out.append("> [!note] 讀經提醒")
                    for note in king["notes"]:
                        out.append(f"> - {str(note['text']).strip()}　`{fmt_ref(note['refs'], self.book)}`")
                    out.append("")
                out += [f"[[#目錄|↑ 回到目錄]] · [[#{data['title']}|回到頂部]]", ""]
        return "\n".join(out).rstrip() + "\n"

    def overview_spine(self, spine: list[dict]) -> list[str]:
        lines = ["```mermaid", "flowchart LR"]
        for i, step in enumerate(spine):
            label = str(step.get("label", "")).replace('"', "#quot;")
            ref = str(step.get("ref", "")).replace('"', "#quot;")
            lines.append(f'  s{i}["{label}<br/><small>{ref}</small>"]')
            if i:
                lines.append(f"  s{i - 1} --> s{i}")
        lines.append("```")
        return lines

    def ready_page_data(self) -> list[tuple[dict, dict]]:
        pages = []
        for item in self.series.get("pages", []) or []:
            if not item.get("ready"):
                continue
            try:
                page_data = yaml.safe_load(self.series_data_file(item).read_text(encoding="utf-8")) or {}
                pages.append((item, page_data))
            except (OSError, yaml.YAMLError) as exc:
                self.err("series", f"無法讀取 ready 頁面 {item.get('data')}: {exc}")
        return pages

    def render_overview(self) -> str:
        data = self.data
        kings = self.kings_registry.get("kings", []) or []
        pages = self.ready_page_data()
        out = [f"# {data['title']}", ""]
        navigation = self.series_navigation()
        if navigation:
            out += [navigation, ""]
        out += [str(data.get("intro", "")).strip(), ""]
        if data.get("see_also"):
            # 系列以外的相關頁（例如「從亞當到耶穌的家譜」），只在總覽頁列一行，不加進系列導覽
            out += [str(data["see_also"]).strip(), ""]
        out += ["<!-- 本頁由 appendix/genealogy/build_genealogy.py 從 YAML 資料產生，請改資料檔，不要直接改本頁。 -->", "",
                "## 主線", ""]
        mini_intro = str(data.get("mini_intro") or "依君王登錄檔的分類整理南北國君王在位年代。")
        out += self.overview_spine(data.get("spine", []) or []) + ["", "## 南北國評語分布", "",
                mini_intro.strip(), ""]
        out += timeline_svg(kings, mini=True).splitlines() + [""]
        if (compare := self.compare_ready()):
            out.append(f"南北國列王的評語與經節詳見 [[{self.page_target(compare)}|{compare.get('short', '南北國列王對照')}]]。")
            out.append("")
        out += ["## 篇幅", ""]
        if data.get("pages_note"):
            out += [str(data["pages_note"]).strip(), ""]
        scoped = []
        for item, page_data in pages:
            scope = page_data.get("scope")
            book = page_data.get("book")
            if not scope or not book:
                continue
            try:
                count = sum(len(self.sc.chapter(book, chapter)) for chapter in range(int(scope[0]), int(scope[1]) + 1))
            except (TypeError, ValueError):
                self.err("series", f"scope 格式錯誤：{item.get('data')}")
                continue
            scoped.append((str(item.get("short", item.get("data", ""))), count))
        if scoped:
            top = max(count for _, count in scoped)
            pads = bar_pads([label for label, _ in scoped])
            out.append("```text")
            for label, count in sorted(scoped, key=lambda row: -row[1]):
                pad = pads[label]
                bar = "█" * max(1, round(count / top * 14)) if count else "·"
                out.append(f"{label}{pad} {bar} {count} 節")
            out += ["```", ""]
        else:
            out += ["目前沒有已發布且有 scope 的系列頁面。", ""]
        out += ["## 全系列目錄", ""]
        for item, page_data in pages:
            target = self.page_target(item)
            short = str(item.get("short", item.get("data", "")))
            out += [f"### [[{target}|{short}]]", ""]
            if page_data.get("type") == "compare":
                registry_path = (self.series_data_file(item).parent / str(page_data.get("kings_registry", ""))).resolve()
                try:
                    page_kings = yaml.safe_load(registry_path.read_text(encoding="utf-8")).get("kings", []) or []
                except (OSError, yaml.YAMLError, AttributeError) as exc:
                    self.err("series", f"無法讀取對照頁君王登錄檔 {item.get('data')}: {exc}")
                    page_kings = []
                for group in page_data.get("groups", []) or []:
                    group_heading = str(group.get("heading", group.get("kingdom", "")))
                    out.append(f"- {group_heading}")
                    for king in page_kings:
                        if king.get("kingdom") == group.get("kingdom"):
                            title = king.get("title", king.get("name", king.get("id")))
                            out.append(f"  - [[{target}#{title}|{king.get('name', king.get('id'))}]]")
            elif page_data.get("groups"):
                groups = page_data.get("groups", []) or []
                for group in groups:
                    group_id = str(group.get("id", ""))
                    group_heading = str(group.get("heading", group_id))
                    out.append(f"- **[[{target}#{group_heading}|{group_heading}]]**")
                    for section in page_data.get("sections", []) or []:
                        if section.get("group") == group_id:
                            title = str(section.get("title", ""))
                            out.append(f"  - [[{target}#{title}|{title}]]")
            else:
                chapters = page_data.get("chapters", {}) or {}
                current = None
                for section in page_data.get("sections", []) or []:
                    chapter = section.get("chapter")
                    if chapter != current:
                        current = chapter
                        chapter_title = f"第 {chapter} 章　{chapters.get(chapter, '')}".rstrip()
                        out.append(f"- [[{target}#{chapter_title}|{chapter_title}]]")
                    title = str(section.get("title", ""))
                    out.append(f"  - [[{target}#{title}|{title}]]")
            out.append("")
        return "\n".join(out).rstrip() + "\n"

    def org_mermaid(self, roots: list[dict]) -> list[str]:
        fence = chr(96) * 3
        lines = [fence + "mermaid", "flowchart TB"]
        counter = [0]
        root_ids = []

        def esc(text: str) -> str:
            return str(text).replace('"', "#quot;")

        def walk(node: dict, parent: str | None = None, is_root: bool = False) -> None:
            counter[0] += 1
            mid = f"o{counter[0]}"
            if is_root:
                root_ids.append(mid)
            label = f"{node['label']}<br/><small>{fmt_ref(node['ref'], self.book)}</small>"
            lines.append(f'  {mid}["{esc(label)}"]')
            if parent:
                lines.append(f"  {parent} --> {mid}")
            for child in node.get("children", []):
                walk(child, mid)

        for root in roots:
            walk(root, is_root=True)
        lines.append("  classDef main fill:#d4a82e44,stroke:#c9971c,stroke-width:2px,font-weight:bold")
        if root_ids:
            lines.append(f"  class {','.join(root_ids)} main")
        lines.append(fence)
        return lines

    def render_roster(self, st: dict, sec: dict) -> list[str]:
        members = st.get("roster", [])
        has_pos = any(member.get("pos") for member in members)
        has_count = any(member.get("count") for member in members)
        headers = (["次序"] if has_pos else []) + ["人名", "經文的介紹"] + (["人數"] if has_count else []) + ["經節"]
        lines = []
        tick = chr(96)
        if st.get("label"):
            lines += [f"**{st['label']}**　{tick}{fmt_ref(st['ref'], self.book)}{tick}", ""]
        lines += ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
        for member in members:
            nid = member["id"]
            name = member.get("as") or display(nid)
            person = self.people.get(nid)
            other = []
            if person:
                skip_index = member.get("_appearance_index")
                for index, (ref, section_id) in enumerate(person["appearances"]):
                    if index == skip_index:
                        continue
                    title = self.section_titles.get(section_id, section_id)
                    link = f"[[#{title}|{fmt_ref(ref, self.book)}]]"
                    if link not in other:
                        other.append(link)
            node = self.nodes.get(nid)
            genealogy = ""
            if node:
                node_ref = fmt_ref(node["ref"], self.book)
                if node.get("imported_page"):
                    page = node["imported_page"]
                    page = page[:-3] if page.endswith(".md") else page
                    genealogy = f"族譜見 [[{page}#{node['section_title']}|{node_ref}]]"
                else:
                    genealogy = f"族譜見 [[#{node['section_title']}|{node_ref}]]"
            annotations = []
            if member.get("as") and member["as"] != display(nid):
                annotations.append(f"別處作{display(nid)}")
            if other:
                annotations.append("又見 " + "、".join(other[:3]) + ("等" if len(other) > 3 else ""))
            if genealogy:
                annotations.append(genealogy)
            if annotations:
                name += "<br/><small>" + "；".join(annotations) + "</small>"
            description = member.get("desc", "")
            if member.get("note"):
                description = (description + "；" if description else "") + member["note"]
            values = []
            if has_pos:
                values.append(member.get("pos", ""))
            values += [name, description]
            if has_count:
                values.append(member.get("count", ""))
            values.append(f"{tick}{fmt_ref(member.get('ref', st['ref']), self.book)}{tick}")
            lines.append("| " + " | ".join(values) + " |")
        lines.append("")
        return lines

    def compare_ready(self) -> dict | None:
        return next((item for item in self.series.get("pages", [])
                     if item.get("ready") and item.get("data") == "南北國列王/對照"), None)

    def render_card(self, card: dict, section_title: str) -> list[str]:
        king = self.kings_by_id.get(card.get("king")) if card.get("king") else None
        if king:
            mark, category = self.verdict_display(king)
            heading = f"{king.get('name', king['id'])}　{mark} {category}　{self.king_years(king)}"
        else:
            heading = section_title
        lines = [f"> [!example] {heading}", "> | 項目 | 內容 | 經節 |", "> |---|---|---|"]
        rows = []
        for field in card.get("fields", []):
            rows.append((str(field.get("label", "")), str(field.get("text", "")), str(field.get("ref", ""))))
        if king:
            for item in (king.get("verdict") or {}).get("items", []) or []:
                if item.get("book") == self.abbr:
                    rows.append((str(item["role"]), f"「{item['quote']}」", str(item["ref"])))
            estimate = (king.get("years") or {}).get("estimate")
            suffix = "" if estimate else "（Thiele）"
            rows.append(("年代", self.king_years(king) + suffix, ""))
        for label, content, ref in rows:
            escape = lambda value: value.replace("|", r"\|")
            reference = f"`{fmt_ref(ref, self.book)}`" if ref else ""
            lines.append(f"> | {escape(label)} | {escape(content)} | {reference} |")
        if king and (compare_page := self.compare_ready()):
            path = compare_page["path"][:-3] if compare_page["path"].endswith(".md") else compare_page["path"]
            lines += [">", f"> 南北國對照：[[{path}#{king['title']}|{king.get('name', king['id'])}]]"]
        lines.append("")
        return lines

    def count_section(self, sid: str) -> int:
        return sum(1 for nid in self.nodes if self.in_section(nid, sid))

    def overview_mermaid(self) -> list[str]:
        ov = self.data["overview"]
        lines = ["```mermaid", "flowchart LR"]
        for i, step in enumerate(ov["spine"]):
            lines.append(f'  s{i}["{step["label"]}<br/><small>{step["ref"]}</small>"]')
            if i:
                lines.append(f"  s{i - 1} --> s{i}")
        last = f"s{len(ov['spine']) - 1}"
        for j, t in enumerate(ov.get("tribes", []) or []):
            where = t.get("where") or "沒有獨立段落"
            lines.append(f'  t{j}["{t["name"]}<br/><small>{where}</small>"]')
            lines.append(f"  {last} --> t{j}")
            if t.get("style"):
                lines.append(f"  class t{j} {t['style']}")
        lines += ["  classDef main fill:#d4a82e44,stroke:#c9971c,stroke-width:2px,font-weight:bold",
                  "  classDef none fill:#80808018,stroke:#999,stroke-dasharray:4 3",
                  "  class " + ",".join(f"s{i}" for i in range(len(ov["spine"]))) + " main", "```"]
        return lines

    def bars(self) -> list[str]:
        rows = []
        for g in self.data["overview"]["bars"]:
            n = self.verse_count(g["ranges"]) if g["ranges"] else 0
            rows.append((g["name"], n, "、".join(r.replace("-", "–") for r in g["ranges"]) or "沒有獨立段落"))
        rows.sort(key=lambda r: -r[1])
        pads = bar_pads([r[0] for r in rows])
        top = max(r[1] for r in rows)
        lines = ["```text"]
        for name, n, where in rows:
            bar = "█" * max(1, round(n / top * 30)) if n else "·"
            pad = pads[name]
            lines.append(f"{name}{pad} {bar} {n} 節" if n else f"{name}{pad} {bar} 沒有獨立段落")
        lines.append("```")
        return lines

    def tables(self) -> list[str]:
        ex = self.extras or {}
        out = ["---", "", "## 附表", ""]
        if ex.get("parallels"):
            out += ["### 平行經文對照", "", "同一件事或同一個人，在別處經文的寫法不同：", "",
                    f"| 項目 | {self.data.get('parallels_label', '歷代志上')} | 對照經文 | 說明 |", "|---|---|---|---|"]
            for r in ex["parallels"]:
                out.append(f"| {r['topic']} | {r['a_text']}　`{r['a_ref']}` | {r['b_text']}　`{r['b_ref']}` | {r.get('note', '')} |")
            out.append("")
            out += [f"[[#目錄|↑ 回到目錄]] · [[#{self.data['title']}|回到頂部]]", ""]
        if ex.get("homonyms"):
            out += ["### 同名不同人", "", "名字相同的不同人，看他掛在誰底下來分辨：", "",
                    "| 名字 | 各是誰 |", "|---|---|"]
            for name in ex["homonyms"]:
                who = []
                seen_ids = set()
                tick = chr(96)
                for i, n in self.nodes.items():
                    if n.get("imported_page") or n["name"] != name:
                        continue
                    if n["parent"]:
                        rel = {"子": "的兒子", "女": "的女兒"}.get(n["rel"], f"的{n['rel']}")
                        desc = f"{display(n['parent'])}{rel}"
                    else:
                        desc = n["pnote"] or n["note"] or "經文沒有寫父親"
                    who.append(f"{desc}　{tick}{n['ref']}{tick}")
                    seen_ids.add(i)
                for i, person in self.people.items():
                    if person["name"] != name or i in seen_ids:
                        continue
                    desc = person.get("first_desc") or person.get("first_pos") or f"見 {person['first_ref']}"
                    who.append(f"{desc}　{tick}{person['first_ref']}{tick}")
                    seen_ids.add(i)
                out.append(f"| {name}（{len(who)} 人） | {'<br/>'.join(who)} |")
            out.append("")
            out += [f"[[#目錄|↑ 回到目錄]] · [[#{self.data['title']}|回到頂部]]", ""]
        if ex.get("troops"):
            out += ["### 經文記下的人數", "", "| 誰 | 數目 | 經文原句 | 經節 |", "|---|---:|---|---|"]
            for r in ex["troops"]:
                out.append(f"| {r['who']} | {r['number']:,} | {r['text']} | `{r['ref']}` |")
            out.append("")
            out += [f"[[#目錄|↑ 回到目錄]] · [[#{self.data['title']}|回到頂部]]", ""]
        if ex.get("cities"):
            out += ["### 利未人的城邑（6:54–81）", "", "標 \\* 的是經文在這裡明說的逃城。", "",
                    "| 宗族 | 在哪個支派的地 | 城邑 | 經節 |", "|---|---|---|---|"]
            for r in ex["cities"]:
                cities = "、".join(c.replace("*", "\\*") for c in r["cities"])
                out.append(f"| {r['family']} | {r['tribe']} | {cities} | `{r['ref']}` |")
            out.append("")
            if ex.get("cities_note"):
                out += [ex["cities_note"].strip(), ""]
            out += [f"[[#目錄|↑ 回到目錄]] · [[#{self.data['title']}|回到頂部]]", ""]
        for table in ex.get("tables", []) or []:
            columns = list(table.get("columns", []))
            if not columns or columns[-1] != "經節":
                columns.append("經節")
            out += [f"### {table.get('heading', '附表')}", ""]
            if table.get("intro"):
                out += [str(table["intro"]).strip(), ""]
            out += ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
            for row in table.get("rows", []) or []:
                values = [str(cell).replace("|", r"\|") for cell in row.get("cells", [])]
                values.append(f"`{fmt_ref(row.get('ref', ''), self.book)}`")
                out.append("| " + " | ".join(values) + " |")
            out += ["", f"[[#目錄|↑ 回到目錄]] · [[#{self.data['title']}|回到頂部]]", ""]
        return out

    def review(self) -> str:
        lo, hi = self.data["scope"]
        lines = [f"# {self.book} {lo}–{hi} 章 逐節對照（複核用）", ""]
        for c in range(lo, hi + 1):
            lines.append(f"## 第{c}章")
            for v, text in enumerate(self.sc.chapter(self.book, c), 1):
                names = self.verse_names.get((c, v), [])
                lines.append(f"- **{c}:{v}** {text}")
                lines.append(f"  - 收錄：{'、'.join(names) if names else '（無人名紀錄）'}")
        lines += ["", "## 關係清單（子 → 父）", ""]
        for nid, n in self.nodes.items():
            lines.append(f"- {nid} ← {n['parent'] or '（源頭）'}〔{n['rel']}〕{('母：' + n['mother']) if n['mother'] else ''} `{n['ref']}`")
        return "\n".join(lines) + "\n"


class LineageBuilder:
    RELATION_FIELDS = ("parents", "spouses", "siblings", "kin", "descends")
    MERGE_FIELDS = ("names", "parents", "spouses", "siblings", "kin", "descends", "maybe_same")
    DIGITS = {"零": 0, "〇": 0, "○": 0, "一": 1, "二": 2, "兩": 2, "两": 2,
              "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
    UNITS = {"十": 10, "百": 100, "千": 1000}
    BIG_UNITS = {"萬": 10000, "万": 10000, "億": 100000000}

    def __init__(self, data_dir: Path) -> None:
        self.dir = data_dir.resolve()
        self.errors: list[str] = []
        self.sc = Scripture()
        self.people: OrderedDict[str, dict] = OrderedDict()
        self.refs_used: OrderedDict[str, str] = OrderedDict()
        self.imported: dict[str, dict] = {}
        self.notes_by_person: dict[str, list[str]] = defaultdict(list)
        self.marks_by_person: dict[str, list[dict]] = defaultdict(list)
        self.lines: dict[str, list[str]] = {"馬太": [], "路加": []}
        self.generations: dict[str, dict[str, int]] = defaultdict(dict)
        self.witness_ranges: dict[str, tuple[int, int]] = {}
        self.ages_result: dict = {"people": [], "events": [], "notes": []}
        self.age_begat: dict[str, str] = {}
        try:
            self.data = yaml.safe_load((self.dir / "頁面.yaml").read_text(encoding="utf-8")) or {}
            if not isinstance(self.data, dict):
                raise ValueError("根節點必須是 mapping")
            if self.data.get("type") != "lineage":
                self.err("頁面.yaml", "type 必須是 lineage")
        except (OSError, yaml.YAMLError, ValueError) as exc:
            self.data = {}
            self.err("頁面.yaml", f"無法讀取設定：{exc}")
        if not self.data.get("output"):
            self.err("頁面.yaml.output", "output 不能空白")
        self.spine_data = self._yaml("spine.yaml", {}) or {}
        self.witnesses = self._yaml("witnesses.yaml", []) or []
        self.ages = self._yaml("ages.yaml", {}) or {}
        self.notes = self._yaml("notes.yaml", []) or []
        self.tour = self._yaml("tour.yaml", []) or []
        self.sources = self._yaml("sources.yaml", []) or []
        self.name_meanings = self._yaml("名字字義.yaml", {}) or {}
        self.name_scripture = self._yaml("名字經文說明.yaml", {}) or {}
        self.meaning_zh = self._read_tsv("字義中譯.tsv")
        if not isinstance(self.spine_data, dict):
            self.err("spine.yaml", "根節點必須是 mapping")
            self.spine_data = {}
        for attr in ("witnesses", "notes", "tour", "sources"):
            if not isinstance(getattr(self, attr), list):
                self.err(attr + ".yaml", "根節點必須是清單")
                setattr(self, attr, [])
        if not isinstance(self.ages, dict):
            self.err("ages.yaml", "根節點必須是 mapping")
            self.ages = {}
        self._load_imports()
        self._load_people()
        self._validate_people()
        self._build_spine()
        self._validate_witnesses()
        self._calculate_marks()
        self._validate_notes()
        self._validate_ages()
        self._validate_families()
        self._validate_tour()
        self._validate_name_meanings()

    def err(self, where: str, msg: str) -> None:
        self.errors.append(f"[{where}] {msg}")

    def _read_tsv(self, name: str) -> dict[str, str]:
        path = self.dir / name
        if not path.is_file():
            return {}
        rows: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if "	" in line:
                key, value = line.split("	", 1)
                rows[key.strip()] = value.strip()
        return rows

    def _yaml(self, name: str, default):
        key = Path(name).stem
        files = self.data.get("files", {}) or {}
        configured = self.data.get(key + "_file")
        if not configured and isinstance(files, dict):
            configured = files.get(key)
        if not configured and isinstance(self.data.get(key), str):
            configured = self.data[key]
        path = (self.dir / str(configured)) if configured else (self.dir / name)
        if not path.is_file():
            return default
        try:
            value = yaml.safe_load(path.read_text(encoding="utf-8"))
            return default if value is None else value
        except (OSError, yaml.YAMLError) as exc:
            self.err(name, f"無法讀取資料：{exc}")
            return default

    def refs(self, value: str, where: str) -> list[tuple[str, int, int]]:
        text = str(value or "").strip()
        if not text:
            self.err(where, "經節不能空白")
            return []
        for part in re.split(r"[,，;；]\s*", text):
            match = re.match(r"^([^\d\s]+)\s*\d+:\d+", part)
            if not match or match.group(1) not in ABBR:
                self.err(where, f"經節必須使用完整書卷簡稱：{part}")
        try:
            parsed = parse_refs(text, "", self.sc)
        except ValueError as exc:
            self.err(where, str(exc))
            return []
        if not parsed:
            self.err(where, f"經節範圍是空的（起訖寫反了？）：{text}")
            return []
        for book, chapter, verse in parsed:
            content = self.sc.verse(book, chapter, verse)
            if content is None:
                self.err(where, f"經節不存在：{FULL_TO_ABBR.get(book, book)}{chapter}:{verse}")
            else:
                self.refs_used[f"{FULL_TO_ABBR.get(book, book)}{chapter}:{verse}"] = content
        return parsed

    def text_of(self, parsed) -> str:
        return "".join(self.sc.verse(book, chapter, verse) or "" for book, chapter, verse in parsed)

    def need_exact(self, needle: str, parsed, where: str, label: str) -> None:
        if parsed and str(needle) not in self.text_of(parsed):
            self.err(where, f"{label}「{needle}」未逐字出現在所引經文")

    def check_quotes(self, value: str, parsed, where: str) -> None:
        for quote in QUOTE_RE.findall(value or ""):
            self.need_exact(quote, parsed, where, "引句")

    @staticmethod
    def _dedupe_add(target: list, value) -> None:
        if value not in target:
            target.append(value)

    def _maybe_same_rows(self, pid: str) -> list[dict]:
        """可能同一人：兩邊任一方寫了就雙向顯示。"""
        rows = [dict(m) for m in self.people[pid].get("maybe_same", [])]
        seen = {str(m.get("id")) for m in rows}
        for other, person in self.people.items():
            for m in person.get("maybe_same", []):
                if str(m.get("id")) == pid and other not in seen:
                    rows.append({**m, "id": other})
                    seen.add(other)
        return rows

    def _merge_person(self, item: dict, where: str, imported: dict | None = None) -> None:
        if not isinstance(item, dict) or not item.get("id"):
            self.err(where, "人物資料需要 id")
            return
        pid = str(item["id"])
        if pid not in self.people:
            self.people[pid] = {
                "id": pid, "sex": None, "kind": "person", "names": [], "parents": [],
                "spouses": [], "siblings": [], "kin": [], "descends": [], "maybe_same": [],
                "desc": None, "note": None, "entry": None, "same_person": None,
                "mother_name": None, "mother_ref": None, "imported": None, "anchor": None,
            }
        person = self.people[pid]
        for field in ("sex", "desc", "entry", "same_person"):
            if item.get(field) is not None:
                if person[field] is not None:
                    self.err(where, f"{pid} 的 {field} 只能在一處填寫")
                else:
                    person[field] = item[field]
        if item.get("kind"):
            person["kind"] = item["kind"]
        if item.get("note"):
            if person["note"] and person["note"] != item["note"]:
                person["note"] += "\n\n" + str(item["note"])
            else:
                person["note"] = item["note"]
        for field in self.MERGE_FIELDS:
            values = item.get(field, []) or []
            if not isinstance(values, list):
                self.err(where + "." + field, "必須是清單")
                continue
            for value in values:
                if not isinstance(value, dict):
                    self.err(where + "." + field, "每筆資料必須是 mapping")
                    continue
                value = dict(value)
                if not imported:
                    value.pop("imported", None)  # 只有匯入程式可以標 imported，手寫資料不能藉此跳過檢查
                self._dedupe_add(person[field], value)
        if item.get("mother_name"):
            person["mother_name"] = item["mother_name"]
        if imported:
            person["imported"] = imported.get("page")
            person["anchor"] = imported.get("anchor")

    def _load_imports(self) -> None:
        for index, item in enumerate(self.data.get("imports", []) or []):
            where = f"imports#{index + 1}"
            try:
                path = (self.dir / item["file"]).resolve()
                imported_data = yaml.safe_load(path.read_text(encoding="utf-8"))
                page = str(item["page"])
                temp = Builder(path.parent, path.stem, str(item["file"]))
                temp.load_genealogy(imported_data, page)
                for error in temp.errors:
                    self.err(where, error)
                nodes = list(temp.nodes.values())
            except (KeyError, OSError, yaml.YAMLError, ValueError, TypeError) as exc:
                self.err(where, f"無法載入匯入資料：{exc}")
                continue
            ids = {node["id"] for node in nodes}
            for node in nodes:
                node_ref = str(node.get("ref", ""))
                ref = prefix_book(node_ref, "代上")
                names = [{"as": node.get("name") or display(node["id"]), "ref": ref}]
                for alias_ref, alias in node.get("aliases", []):
                    alias_ref = str(alias_ref)
                    alias_ref = prefix_book(alias_ref, "代上")
                    names.append({"as": alias, "ref": alias_ref})
                # 代上族譜頁為了畫圖，把姊妹、宗族也掛在「parent」底下，用 rel 標明；匯入時依 rel 分開：
                # 子／女是父母子女，妹子／姊妹是兄弟姊妹，其餘（子孫、諸族…）是後裔（代數不詳）。
                rel = node.get("rel") or "子"
                link = {"id": node["parent"], "ref": ref, "rel": rel, "imported": True} if node.get("parent") else None
                record = {
                    "id": node["id"], "names": names,
                    "parents": [link] if link and rel in ("子", "女") else [],
                    "siblings": [link] if link and rel in ("妹子", "姊妹") else [],
                    "descends": [link] if link and rel not in ("子", "女", "妹子", "姊妹") else [],
                }
                self._merge_person(record, where + "." + node["id"],
                                   {"page": page, "anchor": node.get("section_title", "")})
            for node in nodes:
                mother = node.get("mother")
                if not mother:
                    continue
                person = self.people[node["id"]]
                ref = str(node.get("ref", ""))
                person["mother_ref"] = prefix_book(ref, "代上")
                person["mother_name"] = mother

    def _load_people(self) -> None:
        files = self.data.get("files", {}) or {}
        configured = self.data.get("people_dir")
        if not configured and isinstance(files, dict):
            configured = files.get("people")
        if not configured and isinstance(self.data.get("people"), str):
            configured = self.data["people"]
        folder = (self.dir / str(configured)) if configured else self.dir / "people"
        if not folder.is_dir():
            self.err("people", "找不到 people 資料夾")
            return
        paths = sorted((p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in (".yaml", ".yml")),
                       key=lambda p: p.name)
        for path in paths:
            try:
                values = yaml.safe_load(path.read_text(encoding="utf-8")) or []
            except (OSError, yaml.YAMLError) as exc:
                self.err(path.name, f"無法讀取人物資料：{exc}")
                continue
            if not isinstance(values, list):
                self.err(path.name, "人物檔根節點必須是清單")
                continue
            for index, item in enumerate(values):
                self._merge_person(item, f"{path.name}#{index + 1}")
        # 匯入資料的母親是字串，不自動對到同名的人（代上的「他瑪」字串是猶大的兒婦，id「他瑪」卻是大衛的女兒）；
        # 只照頁面設定 imports[].mothers 明列的對應接上。
        mother_map: dict[str, str] = {}
        for item in self.data.get("imports", []) or []:
            mother_map.update({str(k): str(v) for k, v in (item.get("mothers") or {}).items()})
        for person in self.people.values():
            mother = person.get("mother_name")
            target = mother_map.get(mother) if mother else None
            if target and target in self.people:
                self._dedupe_add(person["parents"], {
                    "id": target, "ref": person.get("mother_ref", ""), "role": "母", "imported": True})
                person["mother_name"] = None

    def names_for(self, pid: str) -> list[str]:
        person = self.people.get(pid, {})
        names = [str(item.get("as", "")) for item in person.get("names", []) if item.get("as")]
        if display(pid):
            names.append(display(pid))
        return list(dict.fromkeys(names))

    def _validate_people(self) -> None:
        for pid, person in self.people.items():
            where = "people." + pid
            if person["sex"] not in (None, "m", "f"):
                self.err(where, "sex 只能是 m 或 f")
            if person["kind"] not in ("person", "people"):
                self.err(where, "kind 只能是 person 或 people")
            if not person["names"]:
                self.err(where, "人物至少需要一筆 names")
            all_refs = []
            for i, name in enumerate(person["names"]):
                if not name.get("as"):
                    self.err(f"{where}.names#{i + 1}", "as 不能空白")
                parsed = self.refs(name.get("ref", ""), f"{where}.names#{i + 1}")
                self.need_exact(str(name.get("as", "")), parsed, f"{where}.names#{i + 1}", "經文寫法")
                all_refs.extend(parsed)
            if person.get("same_person"):
                for ref in person["same_person"].get("refs", []) or []:
                    all_refs.extend(self.refs(ref, where + ".same_person"))
            for i, maybe in enumerate(person.get("maybe_same", [])):
                mwhere = f"{where}.maybe_same#{i + 1}"
                if str(maybe.get("id", "")) not in self.people:
                    self.err(mwhere, f"引用的人物不存在：{maybe.get('id')}")
                if str(maybe.get("id", "")) == pid:
                    self.err(mwhere, "不能指向自己")
                for ref in maybe.get("refs", []) or []:
                    all_refs.extend(self.refs(str(ref), mwhere))
                for quote in QUOTE_RE.findall(str(maybe.get("note") or "")):
                    self.need_exact(quote, [r for x in maybe.get("refs", []) or [] for r in self.refs(str(x), mwhere)], mwhere, "說明引句")
            for field in self.RELATION_FIELDS:
                for i, relation in enumerate(person[field]):
                    rwhere = f"{where}.{field}#{i + 1}"
                    other = str(relation.get("id", ""))
                    if other not in self.people:
                        self.err(rwhere, f"引用的人物不存在：{other}")
                        continue
                    parsed = self.refs(relation.get("ref", ""), rwhere)
                    all_refs.extend(parsed)
                    if relation.get("imported"):
                        # 匯入自代上族譜頁：該頁的 Builder 已依它的規則（整段名單、鏈）驗證過，這裡不重驗
                        continue
                    owner_names = self.names_for(pid)
                    other_names = self.names_for(other)
                    # who_ref：書信裡「我」「你」指誰的經節（例如羅1:1 寫信的是保羅），只用來核對人名，不顯示為依據
                    name_parsed = parsed + (self.refs(str(relation["who_ref"]), rwhere + ".who_ref")
                                            if relation.get("who_ref") else [])
                    if owner_names and not any(value in self.text_of(name_parsed) for value in owner_names):
                        self.err(rwhere, f"本人物名「{display(pid)}」未逐字出現在所引經文")
                    if other_names and not any(value in self.text_of(name_parsed) for value in other_names):
                        self.err(rwhere, f"對方人名「{display(other)}」未逐字出現在所引經文")
                    if field == "kin":
                        self.need_exact(str(relation.get("rel", "")), parsed, rwhere, "親屬用字")
                    if field == "parents" and relation.get("role") not in (None, "父", "母"):
                        self.err(rwhere, "parent role 只能是父或母")
                    if field == "descends" and relation.get("generations") in (2, 3, 4):
                        term = {2: "孫", 3: "曾孫", 4: "玄孫"}[relation["generations"]]
                        self.need_exact(term, parsed, rwhere, "代數用字")
                    if field == "parents":
                        prior = person["parents"][:i]
                        role = relation.get("role") or "父"
                        if any(old.get("ref") == relation.get("ref") and (old.get("role") or "父") == role for old in prior):
                            self.err(rwhere, f"parents 同一經節重複：{relation.get('ref')}")
            for quote in QUOTE_RE.findall(str(person.get("desc") or "") + "\n" + str(person.get("note") or "")):
                self.need_exact(quote, all_refs, where, "人物說明引句")
            if person.get("entry"):
                path = ROOT / "link_folder" / (str(person["entry"]) + ".md")
                if not path.is_file():
                    self.err(where, f"知識庫條目不存在：{path.relative_to(ROOT).as_posix()}")
            for sibling in person["siblings"]:
                other = sibling.get("id")
                if other not in self.people:
                    continue
                shared = {p.get("id") for p in person["parents"]} & {
                    p.get("id") for p in self.people[other]["parents"]}
                if shared:
                    self.err(where, f"與 {other} 已有共同父母資料，不應再列 siblings")
        self._check_parent_cycles()
    def _check_parent_cycles(self) -> None:
        state: dict[str, int] = {}
        stack: list[str] = []
        def visit(pid: str) -> None:
            state[pid] = 1
            stack.append(pid)
            for relation in self.people.get(pid, {}).get("parents", []):
                parent = relation.get("id")
                if parent not in self.people:
                    continue
                if state.get(parent) == 1:
                    self.err("parents", "父母關係形成環：" + " → ".join(stack[stack.index(parent):] + [parent]))
                elif state.get(parent, 0) == 0:
                    visit(parent)
            stack.pop()
            state[pid] = 2
        for pid in self.people:
            if state.get(pid, 0) == 0:
                visit(pid)

    def _validate_links(self) -> None:
        for index, link in enumerate(self.spine_data.get("links", []) or []):
            where = f"spine.links#{index + 1}"
            source, target = str(link.get("from", "")), str(link.get("to", ""))
            if source not in self.people or target not in self.people:
                self.err(where, f"連結端點不存在：{source} → {target}")
                continue
            parsed = self.refs(link.get("ref", ""), where)
            for pid, label in ((source, "起點人名"), (target, "終點人名")):
                if not any(name in self.text_of(parsed) for name in self.names_for(pid)):
                    self.err(where, f"{label}未逐字出現在所引經文")

    def _check_segment_chain(self, chain: list[str], where: str) -> None:
        if not chain:
            self.err(where, "主線段落不能空白")
        for pid in chain:
            if pid not in self.people:
                self.err(where, f"主線人物不存在：{pid}")

    def _append_chain(self, target: list[str], chain: list[str], where: str, partial: bool) -> None:
        if not chain:
            return
        if target and chain[0] == target[-1]:
            target.extend(chain[1:])
        else:
            if target and not partial:
                self.err(where, f"段落沒有首尾相接：{target[-1]} → {chain[0]}")
            target.extend(chain)

    def _build_spine(self) -> None:
        segments = self.spine_data.get("segments", []) or []
        if not isinstance(segments, list) or not segments:
            self.err("spine.segments", "至少需要一個主線段落")
            return
        partial = bool(self.data.get("partial", False))
        common: list[str] = []
        for index, segment in enumerate(segments):
            where = f"spine.segments#{index + 1}"
            routes = segment.get("lines") or {}
            if not isinstance(routes, dict):
                self.err(where, "lines 必須是 mapping")
                continue
            if "common" in routes:
                chain = [str(pid) for pid in routes.get("common", []) or []]
                self._check_segment_chain(chain, where + ".common")
                common.extend(chain)  # 首尾相接改在下面逐條線檢查（共同段之間可能夾著兩線小段）
            for line in ("馬太", "路加"):
                if line in routes:
                    self._check_segment_chain([str(pid) for pid in routes.get(line, []) or []],
                                              where + "." + line)
        if not common:
            self.err("spine", "需要 common 主線")
        for line in ("馬太", "路加"):
            # 依段落順序組成這條線：該段有這條線就走它，否則走共同段
            full: list[str] = []
            for index, segment in enumerate(segments):
                routes = segment.get("lines") or {}
                key = line if line in routes else ("common" if "common" in routes else None)
                if key is None:
                    continue
                chain = [str(pid) for pid in routes.get(key, []) or []]
                self._append_chain(full, chain, f"spine.{line}#{index + 1}", partial)
            self.lines[line] = full
            if len(full) != len(set(full)):
                self.err("spine." + line, "同一條線不可重複出現人物")
            for generation, pid in enumerate(full, 1):
                self.generations[pid][line] = generation
            if full and not partial and display(full[0]) != "亞當":
                self.err("spine." + line, "主線必須從亞當開始")
            if full and not partial and display(full[-1]) != "耶穌":
                self.err("spine." + line, "主線必須到耶穌")
            for parent, child in zip(full, full[1:]):
                if parent not in self.people or child not in self.people:
                    continue
                has_parent = any(rel.get("id") == parent for rel in self.people[child]["parents"])
                has_link = any(item.get("from") == parent and item.get("to") == child
                               for item in self.spine_data.get("links", []) or [])
                if not has_parent and not has_link and not partial:
                    self.err("spine." + line, f"相鄰人物沒有父子關係或 links：{parent} → {child}")
        for segment in segments:
            for chain in (segment.get("lines") or {}).values():
                for pid in chain or []:
                    if pid not in self.people:
                        self.err("spine", f"主線人物不存在：{pid}")
        self._validate_links()

    def _validate_witnesses(self) -> None:
        for index, witness in enumerate(self.witnesses):
            where = f"witnesses#{index + 1}({witness.get('id', '')})"
            parsed = self.refs(witness.get("ref", ""), where)
            text = norm(self.text_of(parsed))
            cursor, ids = 0, []
            for entry_index, entry in enumerate(witness.get("entries", []) or []):
                ewhere = f"{where}.entries#{entry_index + 1}"
                pid = str(entry.get("id", ""))
                if pid not in self.people:
                    self.err(ewhere, f"人物不存在：{pid}")
                    continue
                if entry.get("as"):
                    shown = str(entry["as"])
                else:
                    candidates = [display(pid)] + [n for n in self.names_for(pid) if n != display(pid)]
                    shown = next((n for n in candidates if text.find(norm(n), cursor) >= 0), candidates[0])
                self.need_exact(shown, parsed, ewhere, "見證寫法")
                position = text.find(norm(shown), cursor)
                if position < 0:
                    self.err(ewhere, f"見證寫法「{shown}」沒有依序出現在 {witness.get('ref')}")
                else:
                    cursor = position + len(norm(shown))
                if not entry.get("side"):
                    ids.append(pid)
            if witness.get("line") not in ("common", "馬太", "路加"):
                self.err(where, "line 必須是 common、馬太或路加")
            direction = witness.get("direction", "down")
            if direction not in ("down", "up"):
                self.err(where, "direction 只能是 down 或 up")
            witness["_spine_ids"] = ids[::-1] if direction == "up" else ids
            marks = witness.get("marks")
            if marks is not None and (not isinstance(marks, dict) or not marks.get("missing") or not marks.get("extra")):
                self.err(where + ".marks", "marks 需要 missing 和 extra")
        for line in ("馬太", "路加"):
            positions = {pid: index for index, pid in enumerate(self.lines[line])}
            for witness in self.witnesses:
                if witness.get("line") not in (line, "common"):
                    continue
                indices = [positions[pid] for pid in witness.get("_spine_ids", []) if pid in positions]
                if indices:
                    self.witness_ranges[str(witness.get("id")) + ":" + line] = (min(indices), max(indices))

    def _add_mark(self, pid: str, witness: dict, label: str) -> None:
        self._dedupe_add(self.marks_by_person[pid],
                         {"witness": str(witness.get("id", "")), "label": str(label)})

    def _calculate_marks(self) -> None:
        """標記由程式算：
        - X未列：有 marks 的見證裡相鄰兩人，在它那條線上中間被跳過的人（例：太1:8 約蘭→烏西雅）。
        - 只見X：只有這份見證列出的人，而且另一份見證把他前後兩人直接相接（例：路3:36 的該南）。"""
        for line in ("馬太", "路加"):
            route = self.lines[line]
            pos = {pid: index for index, pid in enumerate(route)}
            for witness in self.witnesses:
                marks = witness.get("marks") or {}
                if not marks or witness.get("line") != line:
                    continue
                seq = [pid for pid in witness.get("_spine_ids", []) if pid in pos]
                for a, b in zip(seq, seq[1:]):
                    if pos[b] - pos[a] > 1 and marks.get("missing"):
                        for skipped in route[pos[a] + 1:pos[b]]:
                            self._add_mark(skipped, witness, marks["missing"])
                others = [w for w in self.witnesses if w is not witness]
                for pid in seq:
                    i = pos[pid]
                    if i == 0 or i == len(route) - 1 or not marks.get("extra"):
                        continue
                    if any(pid in w.get("_spine_ids", []) for w in others):
                        continue
                    before, after = route[i - 1], route[i + 1]
                    for w in others:
                        ids = w.get("_spine_ids", [])
                        if any(x == before and y == after for x, y in zip(ids, ids[1:])):
                            self._add_mark(pid, witness, marks["extra"])
                            break

    def _source_map(self) -> dict[str, dict]:
        return {str(source.get("id")): source for source in self.sources if source.get("id")}

    def _source_text(self, source: dict, where: str) -> str:
        raw = source.get("raw")
        if not raw:
            if not source.get("verified"):
                self.err(where, "沒有 raw 時必須提供 verified 日期")
            return ""
        candidates = [(self.dir / str(raw)).resolve(), (ROOT / str(raw)).resolve()]
        path = next((candidate for candidate in candidates if candidate.is_file()), None)
        if path is None:
            self.err(where, f"raw 檔不存在：{raw}")
            return ""
        try:
            return path.read_text(encoding="utf-8")
        except OSError as exc:
            self.err(where, f"無法讀取 raw：{exc}")
            return ""

    def _validate_notes(self) -> None:
        source_map = self._source_map()
        raw_texts = {sid: self._source_text(source, "sources." + sid) for sid, source in source_map.items()}
        for index, note in enumerate(self.notes):
            where = f"notes#{index + 1}({note.get('id', '')})"
            for pid in note.get("attach", []) or []:
                if pid not in self.people:
                    self.err(where, f"掛載人物不存在：{pid}")
                else:
                    self._dedupe_add(self.notes_by_person[pid], str(note.get("id", "")))
            all_parsed = []
            for j, scripture in enumerate(note.get("scripture", []) or []):
                parsed = self.refs(scripture.get("ref", ""), f"{where}.scripture#{j + 1}")
                all_parsed.extend(parsed)
                if scripture.get("quote"):
                    self.need_exact(str(scripture["quote"]), parsed, where, "引句")
            self.check_quotes(str(note.get("text", "")), all_parsed, where + ".text")
            for j, view in enumerate(note.get("views", []) or []):
                vwhere = f"{where}.views#{j + 1}"
                sid = str(view.get("source", ""))
                if sid not in source_map:
                    self.err(vwhere, f"來源不存在：{sid}")
                    continue
                raw = " ".join(raw_texts.get(sid, "").split())
                quote = " ".join(str(view.get("quote", "")).split())
                if quote and raw and quote not in raw:
                    self.err(vwhere, f"來源引句未逐字出現在 raw：{sid}")
                letters = [c for c in quote if c.isalpha()]
                if letters and sum(c.isascii() for c in letters) > len(letters) / 2 and not view.get("translation"):
                    self.err(vwhere, "英文原句後面要附中譯（translation）")
                scripture_text = norm(self.text_of(all_parsed))
                for q in QUOTE_RE.findall(str(view.get("text", ""))):
                    if q not in raw and norm(q) not in scripture_text:
                        self.err(vwhere, f"轉述裡的引句「{q}」不在來源原文或本則經文裡")
    def _chinese_number(self, text: str) -> int:
        value = str(text).strip()
        if not value:
            raise ValueError("空白數字")
        if value.isdigit():
            return int(value)
        total = section = digit = 0
        for char in value:
            if char in self.DIGITS:
                digit = self.DIGITS[char]
            elif char in self.UNITS:
                section += (digit or 1) * self.UNITS[char]
                digit = 0
            elif char in self.BIG_UNITS:
                section += digit
                total += section * self.BIG_UNITS[char]
                section = digit = 0
            else:
                raise ValueError(f"不是支援的中文數字：{char}")
        return total + section + digit

    def _check_number(self, value, parsed, where: str, label: str) -> int | None:
        if isinstance(value, int):
            if label != "AM":
                self.err(where, f"{label}必須使用經文中的中文數字寫法")
            return value
        text = str(value)
        try:
            number = self._chinese_number(text)
        except ValueError as exc:
            self.err(where, str(exc))
            return None
        self.need_exact(text, parsed, where, label)
        return number

    def _validate_ages(self) -> None:
        event_data, event_years = {}, {}
        for index, event in enumerate(self.ages.get("events", []) or []):
            where = f"ages.events#{index + 1}({event.get('id', '')})"
            if event.get("person") not in self.people:
                self.err(where, f"人物不存在：{event.get('person')}")
            parsed = self.refs(event.get("ref", ""), where)
            event_data[str(event.get("id", ""))] = {
                **event, "_age_num": self._check_number(event.get("age"), parsed, where, "年歲")}
        records: OrderedDict[str, dict] = OrderedDict()
        people_rows = self.ages.get("people", []) or []
        for index, item in enumerate(people_rows):
            pid = str(item.get("id", ""))
            where = f"ages.people#{index + 1}({pid})"
            if pid not in self.people:
                self.err(where, f"人物不存在：{pid}")
            if pid in records:
                self.err(where, f"年歲資料重複：{pid}")
            record = {**item, "_where": where, "_born_am": None, "_total_num": None,
                      "_rest_num": 0, "_refs": []}
            records[pid] = record
            if (item.get("begat_age") or {}).get("age"):
                self.age_begat[pid] = str(item["begat_age"]["age"])
            born = item.get("born") or {}
            selectors = [key for key in ("am", "father", "event", "derive") if born.get(key) is not None]
            if len(selectors) != 1:
                self.err(where + ".born", "born 必須且只能指定 am、father、event 或 derive 其中一種")
            if born.get("am") is not None:
                if display(pid) != "亞當":
                    self.err(where + ".born.am", "只有亞當可以直接指定創世後年份（AM）")
                record["_born_am"] = self._check_number(born["am"], [], where + ".born.am", "AM")
                if record["_born_am"] != 0:
                    self.err(where + ".born.am", "亞當的出生年份必須是創世後 0 年")
            if born.get("father") and born.get("father") not in records and born.get("father") not in {
                    str(row.get("id", "")) for row in people_rows}:
                self.err(where + ".born", f"父親不在 ages.people：{born.get('father')}")
            for j, rest in enumerate(item.get("rest", []) or []):
                parsed = self.refs(rest.get("ref", ""), f"{where}.rest#{j + 1}")
                record["_refs"].extend(parsed)
                record["_rest_num"] += self._check_number(rest.get("years"), parsed, where + ".rest", "餘年") or 0
            if item.get("total"):
                parsed = self.refs(item["total"].get("ref", ""), where + ".total")
                record["_refs"].extend(parsed)
                record["_total_num"] = self._check_number(item["total"].get("years"), parsed, where + ".total", "壽數")
            if item.get("begat_age"):
                data = item["begat_age"]
                parsed = self.refs(data.get("ref", ""), where + ".begat_age")
                record["_refs"].extend(parsed)
                record["_begat_num"] = self._check_number(data.get("age"), parsed, where + ".begat_age", "生子年歲")
                if data.get("child") not in self.people:
                    self.err(where + ".begat_age", f"子女不存在：{data.get('child')}")
            for j, event in enumerate(item.get("events", []) or []):
                parsed = self.refs(event.get("ref", ""), f"{where}.events#{j + 1}")
                record["_refs"].extend(parsed)
                self._check_number(event.get("age"), parsed, f"{where}.events#{j + 1}", "事件年歲")
        for record in records.values():
            if record["_total_num"] is None and record.get("_begat_num") is not None:
                record["_total_num"] = record["_begat_num"] + record["_rest_num"]
            if (record.get("_begat_num") is not None and record.get("_total_num") is not None
                    and record.get("rest")
                    and record["_begat_num"] + record["_rest_num"] != record["_total_num"]):
                self.err(record["_where"], "生子年歲＋餘年不等於壽數")
        unresolved = set(records)
        for _ in range(len(records) + len(event_data) + 2):
            changed = False
            for pid in list(unresolved):
                record, born = records[pid], records[pid].get("born") or {}
                if record["_born_am"] is not None:
                    unresolved.remove(pid)
                    changed = True
                elif born.get("father") in records and records[born["father"]].get("_born_am") is not None:
                    where = record["_where"] + ".born"
                    parsed = self.refs(born.get("ref", ""), where)
                    age = self._check_number(born.get("age"), parsed, where, "父親生子年歲")
                    if age is not None:
                        record["_born_am"] = records[born["father"]]["_born_am"] + age
                        record["_refs"].extend(parsed)
                        unresolved.remove(pid)
                        changed = True
                elif born.get("event") in event_data and born.get("event") in event_years:
                    where = record["_where"] + ".born"
                    parsed = self.refs(born.get("ref", ""), where)
                    after = self._check_number(born.get("after"), parsed, where, "事件後年數")
                    if after is not None:
                        record["_born_am"] = event_years[born["event"]] + after
                        record["_refs"].extend(parsed)
                        unresolved.remove(pid)
                        changed = True
                elif born.get("derive"):
                    derive = born["derive"]
                    base = str(derive.get("person", ""))
                    if base not in records:
                        self.err(record["_where"], f"derive 人物不存在：{base}")
                        unresolved.remove(pid)
                        changed = True
                    elif records[base].get("_born_am") is not None:
                        where = record["_where"] + ".born.derive"
                        parsed = self.refs(derive.get("ref", ""), where)
                        age = self._check_number(derive.get("person_age"), parsed, where, "參照人物年歲")
                        this_refs = []
                        for ref in derive.get("this_refs", []) or []:
                            this_refs.extend(self.refs(ref, where + ".this_refs"))
                        if isinstance(derive.get("this_age"), list):
                            # 本人年歲由幾段經文數字相加（例如 三十歲＋七個豐年＋饑荒二年），每段各自逐字核對
                            this_age = 0
                            for k, part in enumerate(derive["this_age"]):
                                part_refs = self.refs(str(part.get("ref", "")), f"{where}.this_age#{k + 1}")
                                this_refs.extend(part_refs)
                                value = self._check_number(part.get("n"), part_refs, f"{where}.this_age#{k + 1}", "本人年歲")
                                this_age = None if value is None or this_age is None else this_age + value
                        else:
                            this_age = self._check_number(derive.get("this_age"), this_refs, where, "本人年歲")
                        record["_refs"].extend(parsed + this_refs)
                        if age is not None and this_age is not None:
                            record["_born_am"] = records[base]["_born_am"] + age - this_age
                            unresolved.remove(pid)
                            changed = True
            for event_id, event in event_data.items():
                person_id = str(event.get("person", ""))
                if event_id not in event_years and person_id in records and records[person_id].get("_born_am") is not None:
                    if event.get("_age_num") is not None:
                        event_years[event_id] = records[person_id]["_born_am"] + event["_age_num"]
                        changed = True
            if not changed:
                break
        for pid in unresolved:
            self.err(records[pid]["_where"], "born 無法推算創世後年份（AM）")
        for event_id, event in event_data.items():
            if event.get("person") not in records:
                self.err(f"ages.events({event_id})", f"事件人物缺少 ages.people：{event.get('person')}")
        output = []
        for pid, record in records.items():
            born, total = record.get("_born_am"), record.get("_total_num")
            refs = list(dict.fromkeys(
                f"{FULL_TO_ABBR.get(book, book)}{chapter}:{verse}" for book, chapter, verse in record["_refs"]))
            output.append({"id": pid, "born": born, "died": born + total if born is not None and total is not None else None,
                           "total": total, "refs": refs})
        events = [{key: value for key, value in event.items() if not key.startswith("_")} | {"am": event_years.get(eid)}
                  for eid, event in event_data.items()]
        self.ages_result = {"people": output, "events": events, "notes": self.ages.get("notes", []) or []}
        for index, note in enumerate(self.ages_result["notes"]):
            if isinstance(note, dict):
                nwhere = f"ages.notes#{index + 1}({note.get('id', '')})"
                parsed = self.refs(str(note.get("refs", "")), nwhere) if note.get("refs") else []
                if QUOTE_RE.search(str(note.get("text", ""))) and not parsed:
                    self.err(nwhere, "說明有「」引句，需要 refs")
                self.check_quotes(str(note.get("text", "")), parsed, nwhere)

    def _validate_families(self) -> None:
        for field in ("families", "nt_families"):
            for index, family in enumerate(self.data.get(field, []) or []):
                ids = family.get("roots", []) if field == "families" else family.get("members", [])
                for pid in ids or []:
                    if pid not in self.people:
                        self.err(f"頁面.yaml.{field}#{index + 1}", f"人物不存在：{pid}")

    def _validate_tour(self) -> None:
        for index, stop in enumerate(self.tour):
            where = f"tour#{index + 1}({stop.get('id', '')})"
            for pid in stop.get("focus", []) or []:
                if pid not in self.people:
                    self.err(where, f"focus 人物不存在：{pid}")
            # sequence：導覽時依序高亮的人；網站要在畫布上找得到他們，所以限定主線上的人
            spine_ids = set(self.lines.get("馬太", [])) | set(self.lines.get("路加", []))
            for pid in stop.get("sequence", []) or []:
                if pid not in self.people:
                    self.err(where, f"sequence 人物不存在：{pid}")
                elif pid not in spine_ids:
                    self.err(where, f"sequence 只能放主線上的人：{pid}")
            parsed = self.refs(stop.get("refs", ""), where)
            self.check_quotes(str(stop.get("text", "")), parsed, where)

    def _validate_name_meanings(self) -> None:
        """名字的原文與字義：STEP Bible 機械對位的結果（名字字義.yaml）加上經文自己的說明（名字經文說明.yaml）。"""
        if not isinstance(self.name_meanings, dict) or not isinstance(self.name_scripture, dict):
            self.err("名字字義", "根節點必須是 mapping")
            self.name_meanings, self.name_scripture = {}, {}
            return
        for pid, record in self.name_meanings.items():
            where = f"名字字義.{pid}"
            if pid not in self.people:
                self.err(where, "人物不存在")
                continue
            if not isinstance(record, dict) or not record.get("orig") or not record.get("strong"):
                self.err(where, "需要 orig 與 strong")
                continue
            self.refs(str(record.get("ref", "")), where)
            english = str(record.get("meaning_en") or "")
            if english and english not in self.meaning_zh:
                self.err(where, f"字義「{english}」缺中譯（字義中譯.tsv）")
        for pid, items in self.name_scripture.items():
            where = f"名字經文說明.{pid}"
            if pid not in self.people:
                self.err(where, "人物不存在")
                continue
            if not isinstance(items, list) or not items:
                self.err(where, "必須是非空清單")
                continue
            for index, item in enumerate(items):
                here = f"{where}#{index + 1}"
                if not isinstance(item, dict) or not item.get("ref") or not item.get("quote"):
                    self.err(here, "需要 ref 與 quote")
                    continue
                parsed = self.refs(str(item["ref"]), here)
                self.need_exact(str(item["quote"]), parsed, here, "引句")

    def name_meaning_of(self, pid: str) -> dict | None:
        record = self.name_meanings.get(pid)
        scripture = self.name_scripture.get(pid) or []
        if not record and not scripture:
            return None
        english = str((record or {}).get("meaning_en") or "")
        return {
            "orig": (record or {}).get("orig", ""), "translit": (record or {}).get("translit", ""),
            "strong": (record or {}).get("strong", ""), "nameEn": (record or {}).get("name_en", ""),
            "meaningEn": english, "meaningZh": self.meaning_zh.get(english, ""),
            "ref": (record or {}).get("ref", ""),
            "scripture": [{"ref": item["ref"], "quote": item["quote"]} for item in scripture],
        }

    def _render_name_meanings(self) -> list[str]:
        out = ["## 名字的意思", "",
               "主線上每個名字的原文與字義，取自 STEP Bible 的詞典（STEPBible.org，CC BY 4.0；字義依 Abridged BDB 簡編，中文為本頁譯）。"
               "詞典只列這個名字常見的字面意思，不一定是經文當下的用意；經文自己交代名字來由的地方，另列在最後一欄。", "",
               "| 人名 | 原文 | 字義 | 經文自己的說明 |", "|---|---|---|---|"]
        seen: set[str] = set()
        for pid in [*self.lines["馬太"], *self.lines["路加"]]:
            if pid in seen:
                continue
            seen.add(pid)
            info = self.name_meaning_of(pid)
            if not info:
                continue
            original = f"{info['orig']}（{info['translit']}）" if info["orig"] else "—"
            meaning = f"{info['meaningZh']}（{info['meaningEn']}）" if info["meaningEn"] else "—"
            says = "<br>".join(f"{item['ref']}：「{item['quote']}」" for item in info["scripture"]) or "—"
            out.append(f"| {self._name_link(pid)} | {original} | {meaning} | {says} |")
        out.append("")
        return out

    def _name_link(self, pid: str) -> str:
        person = self.people[pid]
        name = display(pid)
        if person.get("entry"):
            return f"[[link_folder/{person['entry']}|{name}]]"
        if person.get("imported"):
            page = str(person["imported"])
            page = page[:-3] if page.endswith(".md") else page
            return f"[[{page}#{person['anchor']}|{name}]]" if person.get("anchor") else name
        return name

    def _site_person_link(self, pid: str, label: str | None = None) -> str:
        from urllib.parse import quote
        site = str(self.data.get("site", "")).strip()
        if not site:
            return label or display(pid)
        target = f"{site}#p={quote(str(pid), safe='')}"
        return f"[{label or display(pid)}](<{target}>)"

    def _ref_link(self, ref: str) -> str:
        match = re.match(r"^([^\d]+)(\d+):", str(ref))
        if not match or match.group(1) not in ABBR:
            return str(ref)
        book = ABBR[match.group(1)]
        if book in ("馬太福音", "馬可福音", "路加福音", "約翰福音", "使徒行傳", "羅馬書",
                    "哥林多前書", "哥林多後書", "加拉太書", "以弗所書", "腓立比書", "歌羅西書",
                    "帖撒羅尼迦前書", "帖撒羅尼迦後書", "提摩太前書", "提摩太後書", "提多書",
                    "腓利門書", "希伯來書", "雅各書", "彼得前書", "彼得後書", "約翰一書",
                    "約翰二書", "約翰三書", "猶大書", "啟示錄"):
            return str(ref)
        number = list(ABBR.values()).index(book) + 1
        target = ROOT / f"{number:02d} {book}" / f"第{match.group(2)}章.md"
        if target.is_file():
            return f"[[{target.parent.name}/{target.stem}|{ref}]]"
        return str(ref)

    def _render_refs(self, refs: list[str]) -> str:
        return "、".join(self._ref_link(ref) for ref in dict.fromkeys(refs) if ref)

    def _segment_routes(self, segment: dict) -> dict[str, list[str]]:
        return {str(key): [str(pid) for pid in value or []]
                for key, value in (segment.get("lines") or {}).items()}

    def _mark_labels(self, pid: str) -> list[str]:
        labels = list(dict.fromkeys(mark["label"] for mark in self.marks_by_person.get(pid, [])))
        if self.notes_by_person.get(pid):
            labels.append("※")
        return labels

    def _split_segment(self, routes: dict[str, list[str]]) -> list[dict[str, list[str]]]:
        if "common" in routes:
            chain = routes["common"]
            parts, start = [], 0
            while start < len(chain):
                end = min(start + 25, len(chain))
                parts.append({"common": chain[start:end]})
                if end == len(chain):
                    break
                start = end - 1
            return parts or [routes]
        keys = [key for key in ("馬太", "路加") if key in routes]
        if len(set(pid for key in keys for pid in routes[key])) <= 25:
            return [routes]
        parts_by_line = {}
        for key in keys:
            chain, parts, start = routes[key], [], 0
            chunk_size = 25 if len(keys) == 1 else 12
            while start < len(chain):
                end = min(start + chunk_size, len(chain))
                parts.append(chain[start:end])
                if end == len(chain):
                    break
                start = end - 1
            parts_by_line[key] = parts
        count = max((len(values) for values in parts_by_line.values()), default=1)
        return [{key: values[index] for key, values in parts_by_line.items() if index < len(values)}
                for index in range(count)] or [routes]

    def _mermaid(self, routes: dict[str, list[str]], prefix: str) -> list[str]:
        fence = chr(96) * 3
        out = [fence + "mermaid", "flowchart TD",
               "  classDef mt stroke:#c8892b,stroke-width:2px",
               "  classDef lk stroke:#2f8f9d,stroke-width:2px"]
        unique = list(dict.fromkeys(pid for chain in routes.values() for pid in chain))
        ids = {pid: f"{prefix}n{index}" for index, pid in enumerate(unique, 1)}
        def label(pid: str) -> str:
            text = html.escape(display(pid), quote=True)
            marks = self._mark_labels(pid)
            if marks:
                text += "<br/><small>" + html.escape("、".join(marks)) + "</small>"
            return text
        if "common" in routes:
            chain = routes["common"]
            for pid in chain:
                out.append(f'  {ids[pid]}["{label(pid)}"]')
            for parent, child in zip(chain, chain[1:]):
                out.append(f"  {ids[parent]} --> {ids[child]}")
        else:
            shared = set(routes.get("馬太", [])) & set(routes.get("路加", []))
            for pid in routes.get("馬太", []):
                if pid in shared:
                    out.append(f'  {ids[pid]}["{label(pid)}"]')
            for line in ("馬太", "路加"):
                if line not in routes:
                    continue
                line_title = "馬太福音" if line == "馬太" else "路加福音"
                out.append(f'  subgraph {prefix}_{line}["{line_title}"]')
                chain = routes[line]
                for pid in chain:
                    if pid not in shared:
                        out.append(f'    {ids[pid]}["{label(pid)}"]')
                out.append("  end")
            # 連線寫在 subgraph 外面：寫在裡面時 mermaid 會把共同的人（例如大衛）也收進那一框
            for line in ("馬太", "路加"):
                chain = routes.get(line, [])
                for parent, child in zip(chain, chain[1:]):
                    out.append(f"  {ids[parent]} --> {ids[child]}")
            for line, class_name in (("馬太", "mt"), ("路加", "lk")):
                exclusive = [ids[pid] for pid in routes.get(line, []) if pid not in shared]
                if exclusive:
                    out.append("  class " + ",".join(exclusive) + " " + class_name)
        out.append(fence)
        return out

    def _render_diagrams(self) -> list[str]:
        out = ["## 主線分段圖", ""]
        site = str(self.data.get("site", "")).strip()
        for index, segment in enumerate(self.spine_data.get("segments", []) or []):
            title = str(segment.get("title", segment.get("id", f"段落{index + 1}")))
            parts = self._split_segment(self._segment_routes(segment))
            for part_index, part in enumerate(parts, 1):
                suffix = f"之{self._number_text(part_index)}" if len(parts) > 1 else ""
                out += [f"### {title}{suffix}", ""]
                out += self._mermaid(part, f"s{index}_{part_index}")
                out.append("")
                first = next((pid for key in ("common", "馬太", "路加")
                              for pid in part.get(key, []) or []), None)
                if site and first:
                    out += [self._site_person_link(first, "在網站上看這一段"), ""]
        return out

    @staticmethod
    def _number_text(number: int) -> str:
        names = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
        if number < 10:
            return names[number]
        if number < 20:
            return "十" + (names[number % 10] if number % 10 else "")
        return str(number)

    def _witness_shown(self, witness: dict, pid: str) -> str:
        for entry in witness.get("entries", []) or []:
            if entry.get("id") == pid and not entry.get("side"):
                return str(entry.get("as") or self.names_for(pid)[0])
        return ""

    def _render_table(self, ids: list[str], lines: list[str]) -> list[str]:
        witnesses = [w for w in self.witnesses
                     if any(self._witness_shown(w, pid).strip() for pid in ids)]
        headers = ["代數", "人名"] + [str(w.get("ref") or w.get("title", w.get("id", ""))) for w in witnesses]
        out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
        for pid in ids:
            generations = [self.generations.get(pid, {}).get(line) for line in lines]
            generations = [number for number in generations if number is not None]
            if generations and len(set(generations)) == 1:
                generation = str(generations[0])
            else:
                generation = "／".join(f"{line}{self.generations.get(pid, {}).get(line, '')}" for line in lines)
            name = self._name_link(pid)
            marks = [label for label in self._mark_labels(pid) if label != "※"]
            if marks:
                name += "（" + "、".join(marks) + "）"
            note_titles = {str(note.get("id", "")): str(note.get("title", note.get("id", "")))
                           for note in self.notes}
            for note_id in self.notes_by_person.get(pid, []):
                title = note_titles.get(str(note_id), str(note_id))
                name += f" [[#{title}|※]]"
            row = [generation, name] + [self._witness_shown(w, pid) for w in witnesses]
            out.append("| " + " | ".join(row) + " |")
        out.append("")
        return out

    def _render_tables(self) -> list[str]:
        out = ["## 世代對照表", ""]
        for index, segment in enumerate(self.spine_data.get("segments", []) or []):
            routes = self._segment_routes(segment)
            title = str(segment.get("title", segment.get("id", f"段落{index + 1}")))
            if "common" in routes:
                out += [f"### {title}", ""]
                out += self._render_table(routes["common"], ["馬太", "路加"])
            else:
                for line in ("馬太", "路加"):
                    if line in routes:
                        out += [f"### {title}｜{line}線", ""]
                        out += self._render_table(routes[line], [line])
        return out

    def _render_notes(self) -> list[str]:
        out = ["## 經文記載不同的地方", ""]
        sources = self._source_map()
        for note in self.notes:
            note_id = str(note.get("id", ""))
            out += [f'<a id="{html.escape(note_id, quote=True)}"></a>',
                    f"### {note.get('title', note_id)}", ""]
            if note.get("scripture"):
                out.append("> [!quote] 經文")
            for scripture in note.get("scripture", []) or []:
                ref = self._ref_link(str(scripture.get("ref", "")))
                out.append(f"> - {ref}：「{scripture.get('quote', '')}」")
            if note.get("scripture"):
                out.append("")
            if note.get("text"):
                out += [str(note["text"]).strip(), ""]
            if note.get("views"):
                out += ["**各家說法**", ""]
                for view in note["views"]:
                    source = sources.get(str(view.get("source", "")), {})
                    title = str(source.get("title", view.get("source", "")))
                    by = f"（{view.get('by')}）" if view.get("by") else ""
                    out.append(f"- **{title}**{by}：{str(view.get('text', '')).strip()}")
                    translation = f"（{view.get('translation')}）" if view.get("translation") else ""
                    out.append(f"  > 「{view.get('quote', '')}」{translation}")
                out.append("")
            source_links = []
            for source_id in dict.fromkeys(str(v.get("source", "")) for v in note.get("views", []) or []):
                source = sources.get(source_id, {})
                if source.get("url"):
                    source_links.append(f"[{source.get('title', source_id)}]({source['url']})")
            if note.get("views"):
                out += ["來源：" + "、".join(source_links), ""]
        return out

    def _timeline_svg(self) -> str:
        people = self.ages_result["people"]
        if not people:
            return ""
        event_years = [item["am"] for item in self.ages_result["events"] if item.get("am") is not None]
        year_values = ([int(item["born"]) for item in people if item.get("born") is not None]
                       + [int(item["died"]) for item in people if item.get("died") is not None]
                       + [int(year) for year in event_years])
        max_year = max(200, ((max(year_values or [0]) + 199) // 200) * 200)
        width, left, right, top, row_height = 900, 92, 28, 54, 26
        height = top + len(people) * row_height + 46
        axis_y = height - 38
        x = lambda year: left + max(0, min(max_year, year)) / max_year * (width - left - right)
        main_line = set(self.lines["馬太"]) | set(self.lines["路加"])
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="創世後年份時間軸">',
               '<style>text{fill:currentColor;font:14px sans-serif}.caption{font-size:12px;opacity:.75}.tick-label{font-size:11px;opacity:.8}.grid{stroke:currentColor;stroke-width:1;opacity:.12}.axis{stroke:currentColor;stroke-width:1;opacity:.5}.life{stroke-width:9;stroke-linecap:round}.life-main{stroke:currentColor;opacity:.8}.life-other{stroke:#9aa0a8;opacity:.75}.dot-main,.dot-other{fill:#c8892b}.event{stroke:#2e9d6a;stroke-width:2;stroke-dasharray:4 3}</style>',
               f'<text class="caption" x="{left}" y="18">依和合本的年歲推算</text>']
        for index, year in enumerate(range(0, max_year + 1, 200)):
            tick_x = x(year)
            out.append(f'<line class="grid" x1="{tick_x:.1f}" y1="{top - 5}" x2="{tick_x:.1f}" y2="{axis_y}"/>')
            if year % 400 == 0:
                out.append(f'<text class="tick-label" x="{tick_x:.1f}" y="{axis_y + 18}" text-anchor="middle">創世後 {year} 年</text>')
        for index, item in enumerate(people):
            y = top + index * row_height
            out.append(f'<text fill="currentColor" x="{left - 10}" y="{y + 4}" text-anchor="end">'
                       f'{html.escape(display(item["id"]))}</text>')
            born = int(item.get("born") or 0)
            died = int(item["died"]) if item.get("died") is not None else born
            kind = "main" if item["id"] in main_line else "other"
            out.append(f'<line class="life life-{kind}" x1="{x(born):.1f}" y1="{y}" x2="{x(died):.1f}" y2="{y}"/>')
            begat = self.age_begat.get(item["id"])
            if begat:
                at = born + self._chinese_number(begat)
                out.append(f'<circle class="dot-{kind}" cx="{x(at):.1f}" cy="{y}" r="4"/>')
        for event in self.ages_result["events"]:
            if event.get("am") is not None:
                event_x = x(event["am"])
                out.append(f'<line class="event" x1="{event_x:.1f}" y1="{top - 5}" x2="{event_x:.1f}" y2="{axis_y}"/>')
                label = "洪水" if str(event.get("id", "")) == "洪水" else str(event.get("label") or event.get("id", ""))
                out.append(f'<text fill="currentColor" x="{event_x + 4:.1f}" y="{top - 9}">'
                           f'{html.escape(label)}</text>')
        out.append(f'<line class="axis" x1="{left}" y1="{axis_y}" x2="{width - right}" y2="{axis_y}"/>')
        out.append("</svg>")
        return "\n".join(out)

    def _age_ref_ranges(self, refs: list[str]) -> list[str]:
        book_order = {abbr: index for index, abbr in enumerate(ABBR)}
        groups: dict[tuple[str, int], set[int]] = defaultdict(set)
        extras = []
        for ref in dict.fromkeys(str(value) for value in refs if value):
            match = re.fullmatch(r"([^\d]+)(\d+):(\d+)", ref)
            if match and match.group(1) in book_order:
                groups[(match.group(1), int(match.group(2)))].add(int(match.group(3)))
            else:
                extras.append(ref)
        result = []
        for book, chapter in sorted(groups, key=lambda key: (book_order[key[0]], key[1])):
            verses = sorted(groups[(book, chapter)])
            if not verses:
                continue
            start = end = verses[0]
            for verse in verses[1:]:
                if verse == end + 1:
                    end = verse
                    continue
                suffix = f"{start}-{end}" if end > start else str(start)
                result.append(f"{book}{chapter}:{suffix}")
                start = end = verse
            suffix = f"{start}-{end}" if end > start else str(start)
            result.append(f"{book}{chapter}:{suffix}")
        result.extend(sorted(set(extras)))
        return result

    def _render_ages(self) -> list[str]:
        out = ["## 年歲時間軸", ""]
        svg = self._timeline_svg()
        if svg:
            out += [svg, ""]
        out += ["| 人名 | 生於 | 壽數 | 死於 | 經節 |", "|---|---:|---:|---:|---|"]
        for item in self.ages_result["people"]:
            refs = self._age_ref_ranges(item.get("refs", []))
            out.append(f"| {self._name_link(item['id'])} | {item.get('born', '')} | {item.get('total', '')} | "
                       f"{item.get('died', '')} | {self._render_refs(refs)} |")
        out.append("")
        for note in self.ages_result.get("notes", []):
            out.append(f"- {note.get('text', '')}" if isinstance(note, dict) else f"- {note}")
        out.append("")
        return out

    def _family_count(self, roots: list[str]) -> int:
        return len(self._father_descendants(roots))

    def _father_descendants(self, roots) -> set[str]:
        children: dict[str, set[str]] = defaultdict(set)
        for child, person in self.people.items():
            for relation in person["parents"]:
                parent = str(relation.get("id", ""))
                if parent in self.people and relation.get("role") != "母":
                    children[parent].add(child)
        seen, queue = {str(pid) for pid in roots}, [str(pid) for pid in roots]
        while queue:
            for child in children.get(queue.pop(0), set()):
                if child not in seen:
                    seen.add(child)
                    queue.append(child)
        return seen

    def _render_families(self) -> list[str]:
        out = ["## 旁支索引", "", "| 家族 | 人數 | 經文 | 連結 |", "|---|---:|---|---|"]
        site = str(self.data.get("site", "")).strip()
        for family in self.data.get("families", []) or []:
            roots = [str(pid) for pid in family.get("roots", []) or []]
            links = []
            if site:
                from urllib.parse import quote
                family_id = quote(str(family.get("id", "")), safe="")
                links.append(f"[網站](<{site}#family={family_id}>)")
            imported_root = next((pid for pid in roots
                                  if self.people.get(pid, {}).get("imported")
                                  and self.people.get(pid, {}).get("anchor")), None)
            if imported_root:
                person = self.people[imported_root]
                page = str(person["imported"])
                page = page[:-3] if page.endswith(".md") else page
                links.append(f"[[{page}#{person['anchor']}|族譜頁]]")
            out.append(f"| {family.get('title', family.get('id', ''))} | {self._family_count(roots)} | "
                       f"{family.get('intro', '')} | {'、'.join(links)} |")
        unattached = len(self.unattached_people())
        out += ["", f"另有 {unattached} 位經文沒有交代與主線關係的人（多半是歷代志上各支派名單的源頭），"
                "在網站的『接不上主線的家族』裡。", ""]
        return out

    def unattached_people(self) -> set[str]:
        """網站「接不上主線的家族」分頁收的人（網站用同一條規則）：
        - 每人只有一個「樹上的父母」：先父親，沒有父親才看母親，都沒有才看後裔（代數不詳）的對象。
        - 從亞當沿這條線往下的是主樹；新約家族另有分頁，不算。
        - 沒有樹上父母、也沒有樹上子女，但和別人有任何記載關係的人（例如路得、他瑪是主線人物的母親），
          在對方的資訊卡出現，不算接不上。
        - 其餘的人（自成一支的家族，以及沒有任何關係的單獨記載）就是接不上主線的人。"""
        tree_parent: dict[str, str] = {}
        tree_children: dict[str, set[str]] = defaultdict(set)
        for pid, person in self.people.items():
            parents = person.get("parents", []) or []
            father = next((r for r in parents if r.get("role") != "母" and r.get("id") in self.people), None)
            mother = next((r for r in parents if r.get("role") == "母" and r.get("id") in self.people), None)
            descend = next((r for r in person.get("descends", []) or [] if r.get("id") in self.people), None)
            chosen = father or mother or descend
            if chosen:
                tree_parent[pid] = str(chosen["id"])
                tree_children[str(chosen["id"])].add(pid)
        main, stack = set(), ["亞當"]
        while stack:
            current = stack.pop()
            if current in main:
                continue
            main.add(current)
            stack.extend(tree_children[current] - main)
        related: dict[str, set[str]] = defaultdict(set)
        for pid, person in self.people.items():
            for field in self.RELATION_FIELDS:
                for relation in person.get(field, []) or []:
                    other = str(relation.get("id", ""))
                    if other in self.people and other != pid:
                        related[pid].add(other)
                        related[other].add(pid)
        nt_people = {str(pid) for family in self.data.get("nt_families", []) or []
                     for pid in family.get("members", []) or []}
        result = set()
        for pid in self.people:
            if pid in main or pid in nt_people:
                continue
            lone = pid not in tree_parent and not tree_children[pid]
            if lone and related[pid]:
                continue
            result.add(pid)
        return result

    def _nt_relation(self, family: dict, pid: str) -> list[tuple[str, str]]:
        def shown(other: str, ref: str) -> str:
            """這一節經文實際用的寫法（例如太16:17 稱彼得的父親「約拿」，約1:42 稱「約翰」）。"""
            try:
                text = self.text_of(self.refs(ref, "nt_relation"))
            except Exception:  # noqa: BLE001
                return display(other)
            names = sorted(self.names_for(other), key=len, reverse=True)
            if display(other) in text:
                return display(other)
            return next((n for n in names if n in text), display(other))
        person = self.people[pid]
        rows = []
        for relation in person["parents"]:
            other = str(relation.get("id", ""))
            if other not in self.people or other == pid:
                continue
            role = {"f": "女兒", "m": "兒子"}.get(person.get("sex"), "孩子")
            prefix = str(relation.get("qualifier") or "")
            rows.append(((prefix + "，" if prefix else "") + shown(other, str(relation.get("ref", ""))) + "的" + role, str(relation.get("ref", ""))))
        for relation in person["spouses"]:
            other = str(relation.get("id", ""))
            if other not in self.people or other == pid:
                continue
            role = {"f": "妻子", "m": "丈夫"}.get(person.get("sex"), "配偶")
            rows.append((display(other) + "的" + role, str(relation.get("ref", ""))))
        for relation in person["siblings"]:
            other = str(relation.get("id", ""))
            if other in self.people and other != pid:
                rows.append((display(other) + "的兄弟姊妹", str(relation.get("ref", ""))))
        for relation in person["kin"]:
            other = str(relation.get("id", ""))
            if other in self.people and other != pid:
                rows.append((display(other) + "的" + str(relation.get("rel", "")),
                             str(relation.get("ref", ""))))
        for relation in person["descends"]:
            other = str(relation.get("id", ""))
            if other in self.people and other != pid:
                rows.append((display(other) + "的後人", str(relation.get("ref", ""))))
        # 反向關係：寫在家族其他成員身上的父母、配偶、兄弟姊妹（例如「底買的兒子巴底買」寫在巴底買那筆）
        members = list(dict.fromkeys(family.get("members", []) or []))  # 照清單順序，輸出才穩定
        for other in members:
            if other == pid or other not in self.people:
                continue
            for relation in self.people[other]["parents"]:
                if relation.get("id") == pid:
                    role = "母親" if relation.get("role") == "母" else "父親"
                    prefix = str(relation.get("qualifier") or "")
                    rows.append(((prefix + "，" if prefix else "") + shown(other, str(relation.get("ref", ""))) + "的" + role,
                                 str(relation.get("ref", ""))))
            for relation in self.people[other]["spouses"]:
                if relation.get("id") == pid and not any(r.get("id") == other for r in person["spouses"]):
                    role = {"f": "妻子", "m": "丈夫"}.get(person.get("sex"), "配偶")
                    rows.append((display(other) + "的" + role, str(relation.get("ref", ""))))
            for relation in self.people[other]["siblings"]:
                if relation.get("id") == pid and not any(r.get("id") == other for r in person["siblings"]):
                    rows.append((display(other) + "的兄弟姊妹", str(relation.get("ref", ""))))
            for relation in self.people[other]["kin"]:
                if relation.get("id") == pid:
                    rows.append((display(other) + "是他的" + str(relation.get("rel", "")), str(relation.get("ref", ""))))
        return rows

    def _render_nt_families(self) -> list[str]:
        out = ["## 新約家族", ""]
        for family in self.data.get("nt_families", []) or []:
            out += [f"### {family.get('title', family.get('id', ''))}", ""]
            if family.get("intro"):
                out += [str(family["intro"]).strip(), ""]
            out += ["| 人物 | 關係 | 經節 |", "|---|---|---|"]
            for pid in family.get("members", []) or []:
                if pid not in self.people:
                    continue
                grouped: dict[str, list[str]] = {}
                for relation, ref in self._nt_relation(family, pid):
                    grouped.setdefault(relation, [])
                    if ref and ref not in grouped[relation]:
                        grouped[relation].append(ref)
                if not grouped:
                    grouped["—"] = []
                for relation, refs in grouped.items():
                    out.append(f"| {self._site_person_link(str(pid))} | {relation} | "
                               f"{self._render_refs(refs)} |")
            out.append("")
        return out

    def render(self) -> str:
        title = str(self.data.get("title", self.dir.name))
        out = [f"# {title}", ""]
        for field in ("intro", "reading"):
            if self.data.get(field):
                out += [str(self.data[field]).strip(), ""]
        if self.data.get("site"):
            out += [f"[互動網站](<{self.data['site']}>)", ""]
        out += self._render_diagrams()
        out += self._render_tables()
        out += self._render_name_meanings()
        out += self._render_notes()
        out += self._render_ages()
        out += self._render_families()
        out += self._render_nt_families()
        out += ["## 資料來源", ""]
        for source in self.sources:
            date = source.get("accessed") or source.get("verified") or ""
            out.append(f"- {source.get('title', source.get('id', ''))}（{source.get('kind', '')}，{date}）："
                       f"{source.get('url', '')}".rstrip("："))
        page = escape_table_links("\n".join(out).rstrip() + "\n")
        lines = page.splitlines()
        for index, line in enumerate(lines):
            if line.lstrip().startswith(">"):
                lines[index] = TABLE_LINK_RE.sub(
                    lambda match: "[[" + match.group(1) + "\\|" + match.group(2) + "]]", line)
        return "\n".join(lines).rstrip() + "\n"

    def review(self) -> str:
        out = [f"# {self.data.get('title', self.dir.name)} 複核", "", "## 主線逐代", ""]
        for line in ("馬太", "路加"):
            out += [f"### {line}線", ""]
            for pid in self.lines[line]:
                witnesses = []
                for witness in self.witnesses:
                    if witness.get("line") in (line, "common") and pid in witness.get("_spine_ids", []):
                        witnesses.append(f"{witness.get('title', witness.get('id'))}："
                                         f"{self._witness_shown(witness, pid)}（{witness.get('ref')}）")
                suffix = "；" + "；".join(witnesses) if witnesses else "；目前見證未列"
                out.append(f"- 第{self.generations.get(pid, {}).get(line, '?')}代 **{display(pid)}**{suffix}")
        out += ["", "## 程式計算的標記", ""]
        marked = [(pid, marks) for pid, marks in self.marks_by_person.items() if marks]
        for pid, marks in marked or [(None, [])]:
            if pid is None:
                out.append("- （沒有計算出標記）")
            else:
                out.append(f"- {display(pid)}：" + "；".join(f"{m['label']}（{m['witness']}）" for m in marks))
        out += ["", "## 見證對照", ""]
        for witness in self.witnesses:
            sequence = " → ".join(display(pid) for pid in witness.get("_spine_ids", []))
            out.append(f"- **{witness.get('title', witness.get('id'))}**（{witness.get('ref')}；"
                       f"{witness.get('line')}；{witness.get('direction', 'down')}）：{sequence}")
        out += ["", "## 年歲推算", "", "| 人物 | 生於 AM | 壽數 | 死於 AM |", "|---|---:|---:|---:|"]
        for item in self.ages_result.get("people", []):
            out.append(f"| {display(item['id'])} | {item.get('born', '')} | {item.get('total', '')} | {item.get('died', '')} |")
        out += ["", "## 關係經文抽查", ""]
        for pid, person in self.people.items():
            for field in self.RELATION_FIELDS:
                for relation in person[field]:
                    try:
                        parsed = parse_refs(str(relation.get("ref", "")), "", self.sc)
                    except ValueError:
                        parsed = []
                    out.append(f"- {display(pid)} — {field} → {display(str(relation.get('id', '')))}；"
                               f"{relation.get('ref')}：{self.text_of(parsed)}")
        return "\n".join(out).rstrip() + "\n"

    def export(self, output_dir: Path) -> None:
        import json
        output_dir.mkdir(parents=True, exist_ok=True)
        persons = []
        for pid, person in self.people.items():
            def relation_rows(field: str) -> list[dict]:
                rows = []
                for relation in person[field]:
                    row = dict(relation)
                    # qualifier 是關係本身的修飾（例如路3:23「依人看來」）；對方 id 的識別字另放 idQualifier
                    row["qualifier"] = str(relation.get("qualifier") or "")
                    row["idQualifier"] = str(row.get("id", "")).split("#", 1)[1] if "#" in str(row.get("id", "")) else ""
                    row.pop("imported", None)
                    rows.append(row)
                return rows
            gloss = ""
            if person.get("entry"):
                entry_path = ROOT / "link_folder" / (str(person["entry"]) + ".md")
                if entry_path.is_file():
                    text = entry_path.read_text(encoding="utf-8")
                    match = re.search(r"(?ms)^## 定義\s*\n(.*?)(?=^## |\Z)", text)
                    if match:
                        first = match.group(1).strip().split("。", 1)[0]
                        gloss = first + "。" if first else ""
            persons.append({
                "id": pid, "name": display(pid),
                "qualifier": str(pid).split("#", 1)[1] if "#" in pid else "",
                "sex": person.get("sex"), "kind": person.get("kind", "person"),
                "names": person.get("names", []), "parents": relation_rows("parents"),
                "spouses": relation_rows("spouses"), "siblings": relation_rows("siblings"),
                "kin": relation_rows("kin"), "descends": relation_rows("descends"),
                "maybeSame": self._maybe_same_rows(pid),
                "desc": person.get("desc"), "note": person.get("note"), "entry": person.get("entry"),
                "entryGloss": gloss, "mother_name": person.get("mother_name"),
                "gen": self.generations.get(pid, {}),
                "lines": (["common"] if pid in set(self.lines["馬太"]) & set(self.lines["路加"])
                          else [line for line in ("馬太", "路加") if pid in self.lines[line]]),
                "marks": self.marks_by_person.get(pid, []), "notes": self.notes_by_person.get(pid, []),
                "imported": person.get("imported"), "anchor": person.get("anchor"),
                "nameMeaning": self.name_meaning_of(pid),
            })
        segments = [{"id": segment.get("id"), "title": segment.get("title"),
                     "lines": self._segment_routes(segment)}
                    for segment in self.spine_data.get("segments", []) or []]
        payload = {
            "persons": persons, "spine": {"segments": segments, "lines": self.lines},
            "witnesses": [{k: v for k, v in witness.items() if not k.startswith("_")} for witness in self.witnesses],
            "ages": self.ages_result, "notes": self.notes, "tour": self.tour,
            "unattached": sorted(self.unattached_people()),
            "families": [{"id": family.get("id"), "title": family.get("title"),
                          "roots": family.get("roots", []), "count": self._family_count(family.get("roots", [])),
                          "intro": family.get("intro", "")} for family in self.data.get("families", []) or []],
            "ntFamilies": self.data.get("nt_families", []), "sources": self.sources,
        }
        (output_dir / "genealogy.json").write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":"), default=str), encoding="utf-8")
        (output_dir / "verses.json").write_text(
            json.dumps(self.refs_used, ensure_ascii=False, separators=(",", ":"), sort_keys=True), encoding="utf-8")

def build_page(data_spec: str, check: bool = False, review: str | None = None,
               print_summary: bool = True, export_json: str | None = None) -> bool:
    normalized = data_spec.replace(chr(92), "/")
    candidate = Path(data_spec).expanduser()
    lineage_dir = None
    if candidate.is_absolute():
        if candidate.is_dir() and (candidate / "頁面.yaml").is_file():
            lineage_dir = candidate
    else:
        spec_dir = HERE / Path(*normalized.split("/"))
        if spec_dir.is_dir() and (spec_dir / "頁面.yaml").is_file():
            lineage_dir = spec_dir
    if lineage_dir is not None:
        b = LineageBuilder(lineage_dir)
        page = b.render() if not b.errors else ""
        if review:
            review_path = Path(review)
            review_path.parent.mkdir(parents=True, exist_ok=True)
            review_path.write_text(b.review(), encoding="utf-8")
        if b.errors:
            print(f"FAIL：{len(b.errors)} 項")
            for error in b.errors:
                print(" ", error)
            return False
        if print_summary:
            print(f"PASS：{len(b.people)} 人、馬太線 {len(b.lines['馬太'])} 代、路加線 {len(b.lines['路加'])} 代")
        if not check:
            output = Path(str(b.data.get("output", "")))
            output = output if output.is_absolute() else ROOT / output
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(page, encoding="utf-8")
            try:
                shown = output.relative_to(ROOT).as_posix()
            except ValueError:
                shown = str(output)
            print(f"已寫入 {shown}")
        if export_json:
            b.export(Path(export_json).expanduser())
            print(f"已匯出 JSON：{Path(export_json).expanduser()}")
        return True
    parts = normalized.split("/")
    if len(parts) == 1:
        book_dir, data_name = HERE / parts[0], "genealogy"
    else:
        book_dir, data_name = HERE.joinpath(*parts[:-1]), parts[-1]
    b = Builder(book_dir, data_name, normalized)
    if b.page_type == "genealogy":
        b.load_registry()
        b.load_imports()
        b.load_extras()
        b.check_coverage()
        page = b.render() if not b.errors else ""
    elif b.page_type == "compare":
        b.load_registry(required=True)
        if not b.data.get("groups"):
            b.err("groups", "compare 頁需要 groups")
        page = b.render_compare() if not b.errors else ""
    elif b.page_type == "overview":
        b.load_registry(required=True)
        if not b.data.get("spine"):
            b.err("spine", "overview 頁需要 spine")
        page = b.render_overview() if not b.errors else ""
    else:
        b.err("type", f"未知頁型：{b.page_type}")
        page = ""
    page = escape_table_links(page)
    if review:
        Path(review).write_text(b.review(), encoding="utf-8")
    if b.errors:
        print(f"FAIL：{len(b.errors)} 項")
        for error in b.errors:
            print(" ", error)
        return False
    if print_summary:
        if b.page_type == "genealogy":
            page_node_ids = {nid for nid, node in b.nodes.items() if not node.get("imported_page")}
            people_count = len(page_node_ids | set(b.people))
            print(f"PASS：{people_count} 人、涵蓋 {len(b.covered)} 節")
        elif b.page_type == "compare":
            print(f"PASS：{len(b.kings_registry.get('kings', []))} 位君王")
        else:
            print(f"PASS：{len(b.kings_registry.get('kings', []))} 位君王、{len(b.series.get('pages', []))} 個系列頁面")
    if not check:
        out = ROOT / b.data["output"]
        out.write_text(page, encoding="utf-8")
        print(f"已寫入 {out.relative_to(ROOT).as_posix()}")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("book", nargs="?")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review")
    ap.add_argument("--export-json")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if args.all:
        series_path = HERE / "series.yaml"
        series = yaml.safe_load(series_path.read_text(encoding="utf-8"))
        failed = False
        for item in series.get("pages", []):
            if not item.get("ready"):
                continue
            try:
                passed = build_page(item["data"], check=args.check, review=args.review if not args.check else None, print_summary=False)
            except Exception as exc:
                print(f"FAIL：{item.get('data', '(unknown)')}：{exc}")
                passed = False
            print(f"{'PASS' if passed else 'FAIL'}：{item['data']}")
            failed = failed or not passed
        return 1 if failed else 0
    if not args.book:
        ap.error("請指定資料頁，或使用 --all")
    return 0 if build_page(args.book, check=args.check, review=args.review,
                           export_json=args.export_json) else 1


if __name__ == "__main__":
    sys.exit(main())
