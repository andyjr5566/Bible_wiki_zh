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


class SourceError(RuntimeError):
    """source_manifest 宣告了 OK 來源、但實際讀不到任何 raw_data 檔時拋出。

    最典型成因：manifest 第4欄漏寫 `raw_data/` 前綴（裸檔名），舊版 parse_manifest
    會靜默丟棄整列 → M3/M6 拿到空來源、模型只能憑訓練知識杜撰註釋。此例外讓這種
    「閘門全過但內容其實沒讀到來源」的靜默失效當場爆出來。
    """


def parse_manifest(manifest_path, root):
    """讀 source_manifest.md，回傳 [(label, Path)]（僅狀態含 OK 的來源）。

    第4欄可寫 `raw_data/xxx.txt` 或裸檔名 `xxx.txt`（裸檔名一律歸到 raw_data/ 下）。
    非 raw_data 的 .txt（如 raw_scripture/… 的經文本文列）不算註釋來源，略過。
    """
    root = Path(root)
    sources = []
    for label, _kind, _url, rel_path in _manifest_rows(manifest_path):
        if not rel_path.endswith(".txt"):
            continue
        parts = Path(rel_path).parts
        if parts and parts[0] == "raw_data":
            resolved = root / Path(rel_path)
        elif len(parts) == 1:  # 裸檔名 → 補 raw_data/ 前綴
            resolved = root / "raw_data" / parts[0]
        else:  # 其它相對路徑（raw_scripture/… 經文本文等）不是註釋來源
            continue
        sources.append((label, resolved))
    return sources


def require_sources(manifest_path, root):
    """M3/M6 生成前的護欄：回傳可用來源；宣告了 OK 來源卻一個都讀不到就報錯。

    回傳存在於磁碟的 [(label, Path)]。若 manifest 宣告了 OK 來源、但解析後沒有
    任何檔案存在，拋 SourceError 並指明最可能的成因與修法——避免模型在空來源下
    生成、卻一路通過結構閘門（申命記 1-6 的杜撰註釋即此因）。
    """
    declared = parse_manifest(manifest_path, root)
    present = [(label, path) for label, path in declared if Path(path).exists()]
    if declared and not present:
        sample = declared[0][1]
        raise SourceError(
            f"source_manifest.md 宣告了 {len(declared)} 個 OK 來源，但解析後沒有任何"
            f"檔案存在（例：{sample}）。最可能成因：manifest 第4欄漏寫 raw_data/ "
            f"前綴或檔名有誤，raw_data 尚未爬取。M3/M6 需要來源全文，已中止以免"
            f"用空來源杜撰內容。請用 util/build_source_manifest.py 重新產生 manifest，"
            f"或確認 raw_data/ 下有對應 .txt 後重跑。\n  manifest：{manifest_path}"
        )
    missing = [path for label, path in declared if not Path(path).exists()]
    if missing:
        joined = "、".join(str(p.name) for p in missing)
        raise SourceError(
            f"source_manifest.md 有 {len(missing)} 個 OK 來源檔讀不到：{joined}。"
            f"部分來源缺檔會讓該來源的觀點在 M3/M6 靜默消失。請補齊 raw_data 或把"
            f"該列狀態改為非 OK 後重跑。\n  manifest：{manifest_path}"
        )
    return present


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
