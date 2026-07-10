#!/usr/bin/env python3
"""從 raw_data 依關鍵詞切出來源摘錄，供 orchestrator 注入模型提示。

最小 context 原則：內容任務只餵該任務需要的段落，而不是整份 raw text。
來源清單以章節的 source_manifest.md 為準（只用狀態 OK 的檔案），避免猜檔名。
"""
import re
from pathlib import Path

MANIFEST_ROW_RE = re.compile(r"^\|(.+)\|\s*$")


def parse_manifest(manifest_path, root):
    """讀 source_manifest.md，回傳 [(label, Path)]（僅狀態含 OK 的來源）。"""
    manifest_path = Path(manifest_path)
    sources = []
    if not manifest_path.exists():
        return sources
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        match = MANIFEST_ROW_RE.match(line.strip())
        if not match:
            continue
        cells = [cell.strip() for cell in match.group(1).split("|")]
        if len(cells) < 5:
            continue
        label, kind, _url, rel_path, status = cells[:5]
        if "OK" not in status:
            continue
        if not (rel_path.startswith("raw_data") and rel_path.endswith(".txt")):
            continue
        sources.append((kind or label, Path(root) / rel_path))
    return sources


def _paragraphs(text):
    return [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]


def keyword_variants(name):
    """條目名的比對變體：完整名 + 去掉括號註解的核心詞。"""
    variants = {name.strip()}
    core = re.sub(r"（[^）]*）|\([^)]*\)", "", name).strip()
    if core:
        variants.add(core)
    return [v for v in variants if v]


def slice_for_keywords(sources, keywords, *, max_paras_per_source=4, max_chars=2500):
    """回傳含任一關鍵詞的段落摘錄（依來源分組、標籤標示、總長度上限）。"""
    keywords = [k for k in keywords if k]
    if not keywords:
        return ""
    chunks = []
    for label, path in sources:
        if not path.exists():
            continue
        matched = []
        for paragraph in _paragraphs(path.read_text(encoding="utf-8")):
            if any(keyword in paragraph for keyword in keywords):
                matched.append(paragraph)
            if len(matched) >= max_paras_per_source:
                break
        if matched:
            chunks.append(f"【{label}】\n" + "\n".join(matched))
    return "\n\n".join(chunks)[:max_chars]


def chapter_digest(sources, *, per_source_chars=900, max_chars=3200):
    """章節層級摘要：每個來源取開頭一段（含綱要），供整章型任務參考。"""
    chunks = []
    for label, path in sources:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").strip()
        if text:
            chunks.append(f"【{label}】\n{text[:per_source_chars]}")
    return "\n\n".join(chunks)[:max_chars]
