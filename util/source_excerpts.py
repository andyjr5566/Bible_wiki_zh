#!/usr/bin/env python3
"""把整章來源（raw_data 全文）餵給模型，維持原版 scheme「全部資料直接餵進去」。

不做關鍵詞切片；來源清單以章節的 source_manifest.md 為準（只用狀態 OK 的
檔案）。大章節（§9）以字數預算護欄粗略等比截斷，避免 context 爆掉。
"""
import re
from pathlib import Path

MANIFEST_ROW_RE = re.compile(r"^\|(.+)\|\s*$")

# §9 超長章節判準（任一成立即視為大章節）
LARGE_VERSES = 60
LARGE_TOTAL_CHARS = 250_000
LARGE_SINGLE_CHARS = 120_000


def _manifest_rows(manifest_path):
    """source_manifest.md 中狀態 OK 的資料列 → [(label, kind, url, rel_path)]。"""
    manifest_path = Path(manifest_path)
    rows = []
    if not manifest_path.exists():
        return rows
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        match = MANIFEST_ROW_RE.match(line.strip())
        if not match:
            continue
        cells = [cell.strip() for cell in match.group(1).split("|")]
        if len(cells) < 5:
            continue
        label, kind, url, rel_path, status = cells[:5]
        if "OK" not in status:
            continue
        rows.append((label, kind, url, rel_path))
    return rows


def parse_manifest(manifest_path, root):
    """讀 source_manifest.md，回傳 [(label, Path)]（僅狀態含 OK 的來源）。"""
    return [
        (label, Path(root) / rel_path)
        for label, _kind, _url, rel_path in _manifest_rows(manifest_path)
        if rel_path.startswith("raw_data") and rel_path.endswith(".txt")
    ]


def manifest_urls(manifest_path):
    """讀 source_manifest.md，回傳 [(label, url)]（僅狀態 OK 且 URL 為 http(s)）。

    章節「參考資料」與條目「來源依據」的 URL 以此為唯一事實來源，不由模型手寫。
    """
    return [
        (label, url)
        for label, _kind, url, _rel_path in _manifest_rows(manifest_path)
        if url.startswith("http")
    ]


def manifest_kind_urls(manifest_path):
    """讀 source_manifest.md，回傳 [(類型, url)]（僅狀態 OK 且 URL 為 http(s)）。

    類型欄是 BH/CT/GT/KC 簡稱；條目 sources 的「標籤: 位置說明（URL）」以此
    驗證標籤與 URL 成對（出25 實例：模型寫 KC 標籤卻附 CT 的 URL）。
    """
    return [
        (kind, url)
        for _label, kind, url, _rel_path in _manifest_rows(manifest_path)
        if url.startswith("http")
    ]


def _read_all(sources):
    texts = []
    for label, path in sources:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").strip()
        if text:
            texts.append((label, text))
    return texts


def full_source_text(sources, *, char_budget=LARGE_TOTAL_CHARS):
    """所有 OK 來源的全文（依來源標籤分組）。

    超過預算時各來源等比截斷（大章節護欄）；一般章節不截斷、全文餵入。
    """
    texts = _read_all(sources)
    total = sum(len(text) for _, text in texts)
    chunks = []
    for label, text in texts:
        if total > char_budget:
            keep = max(1000, int(len(text) * char_budget / total))
            text = text[:keep] + "\n…（大章節截斷，其餘見分段）"
        chunks.append(f"【{label}】\n{text}")
    return "\n\n".join(chunks)


def is_large_chapter(sources, raw_verses):
    """§9 判準：經文超過 60 節、單一來源過大、或來源合計過大。"""
    if len(raw_verses) > LARGE_VERSES:
        return True
    texts = _read_all(sources)
    if any(len(text) > LARGE_SINGLE_CHARS for _, text in texts):
        return True
    return sum(len(text) for _, text in texts) > LARGE_TOTAL_CHARS
