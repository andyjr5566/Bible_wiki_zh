#!/usr/bin/env python3
"""建立 link_folder 條目的 embedding 索引，供語義近似查詢。

4300+ 條目早已超出人腦記憶，字面比對（resolve_link_candidates）對
「措辭不同、意思相同」的候選完全無感，結果就是建出近似重複條目。
本索引讓 semantic_lookup.py 能以語義相似度找出最像的既有條目——
一切近似結果只做附註與報告供人工判斷，不自動建立或改動任何連結。

索引與 embedding 模型綁定：meta 記錄模型名與維度；tasks.embedding 換了
模型而索引未重建時，載入端一律拒用——向量跨模型不可比，混用後相似度
數字看起來仍「合理」，是靜默錯誤。此時請跑 --rebuild。

  python util/build_embedding_index.py            # 增量更新（新增／變更／刪除）
  python util/build_embedding_index.py --rebuild  # 全量重建
  python util/build_embedding_index.py --status   # 顯示索引狀態，不動任何檔
"""
import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

import numpy as np

try:
    from .model_client import ModelError, embed_texts, select_endpoint
except ImportError:
    from model_client import ModelError, embed_texts, select_endpoint

UTIL_DIR = Path(__file__).resolve().parent
ROOT = UTIL_DIR.parent
LINK_INDEX_FILE = UTIL_DIR / "output" / "link_index.json"
META_FILE = UTIL_DIR / "output" / "embedding_index.meta.json"
VECTORS_FILE = UTIL_DIR / "output" / "embedding_index.npz"

SECTION_RE = re.compile(r"^##\s+(.+?)\s*$([\s\S]*?)(?=^##\s|\Z)", re.M)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
URL_RE = re.compile(r"https?://\S+")
# 建 embedding 文本時取用的段落與優先序：越前面越有鑑別度，截斷時先保留。
# 「來源依據」幾乎全是 URL，語義雜訊高，不取。
SECTION_PRIORITY = ("定義", "主題發展", "相關條目", "按書卷累積")
MAX_EMBED_CHARS = 2000
BATCH_SIZE = 256
INDEX_INPUT_TYPE = "passage"


def load_link_index(path=LINK_INDEX_FILE):
    """讀 link_index.json，只留正式條目（去掉 alias_of 轉向鍵）。"""
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        title: entry for title, entry in data.items() if "alias_of" not in entry
    }


def _strip_frontmatter(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            newline = text.find("\n", end + 1)
            return text[newline + 1:] if newline != -1 else ""
    return text


def _clean_section(content):
    """段落內文清成一行：去標題／項目符號／wikilink 語法／URL／角括號。"""
    kept = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue  # 跳過子標題（如累積段的「#### 第8章」章節連結）
        kept.append(stripped.lstrip("-*• ").strip())
    text = " ".join(kept)
    text = WIKILINK_RE.sub(lambda m: m.group(1).split("/")[-1], text)
    text = URL_RE.sub("", text)
    text = text.replace("<", " ").replace(">", " ")
    return " ".join(text.split())


def entry_embed_text(title, entry, root=ROOT):
    """條目的 embedding 文本：標題＋分類＋別名，再依優先序併入多段內文。

    塞進定義、主題發展、相關條目、按書卷累積，讓模型能萃取更多特徵；
    段落依 SECTION_PRIORITY 排序後截斷，最有鑑別度的定義永遠保留。
    """
    parts = [title]
    if entry.get("type"):
        parts.append(f"分類：{entry['type']}")
    aliases = [a for a in entry.get("aliases") or [] if a and a != title]
    if aliases:
        parts.append("別名：" + "、".join(aliases))
    md_path = root / entry.get("path", "")
    if md_path.is_file():
        body = HTML_COMMENT_RE.sub(" ", _strip_frontmatter(
            md_path.read_text(encoding="utf-8")))
        sections = {
            head.strip(): _clean_section(content)
            for head, content in SECTION_RE.findall(body)
        }
        for head in SECTION_PRIORITY:
            cleaned = sections.get(head)
            if cleaned:
                parts.append(f"{head}：{cleaned}")
    return "\n".join(parts)[:MAX_EMBED_CHARS]


def _hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def embedding_model():
    endpoint = select_endpoint(task="embedding")
    model = endpoint.get("model")
    if not model:
        raise ModelError("tasks.embedding 未指定模型（見 _config/model_endpoints.yaml）")
    return model


def load_stored(meta_file=META_FILE, vectors_file=VECTORS_FILE):
    """讀既有索引；不存在回 (None, None)。"""
    if not (meta_file.exists() and vectors_file.exists()):
        return None, None
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    vectors = np.load(vectors_file)["vectors"]
    if len(meta.get("entries", [])) != vectors.shape[0]:
        raise ModelError(
            "embedding 索引損壞：meta 條目數與向量列數不符，請 --rebuild"
        )
    return meta, vectors


def _normalize(matrix):
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


def build(rebuild=False, batch_size=BATCH_SIZE, root=ROOT):
    model = embedding_model()
    link_index = load_link_index()
    texts = {
        title: entry_embed_text(title, entry, root=root)
        for title, entry in link_index.items()
    }
    hashes = {title: _hash(text) for title, text in texts.items()}

    old_rows = {}
    old_vectors = None
    if not rebuild:
        meta, old_vectors = load_stored()
        if meta is not None:
            if meta.get("model") != model:
                raise ModelError(
                    f"索引是「{meta.get('model')}」建的，目前設定是「{model}」；"
                    "向量跨模型不可比，請跑 --rebuild"
                )
            old_rows = {
                item["title"]: (i, item["hash"])
                for i, item in enumerate(meta["entries"])
            }

    todo = [
        title for title in texts
        if title not in old_rows or old_rows[title][1] != hashes[title]
    ]
    removed = [title for title in old_rows if title not in texts]
    reused = len(texts) - len(todo)
    print(
        f"條目 {len(texts)}：沿用 {reused}、需嵌入 {len(todo)}、移除 {len(removed)}"
        f"（模型 {model}）"
    )

    new_vectors = {}
    if todo:
        started = time.monotonic()
        for start in range(0, len(todo), batch_size):
            batch = todo[start:start + batch_size]
            vectors = embed_texts(
                [texts[title] for title in batch], batch_size=batch_size,
                input_type=INDEX_INPUT_TYPE,
            )
            for title, vector in zip(batch, vectors):
                new_vectors[title] = vector
            done = start + len(batch)
            elapsed = time.monotonic() - started
            print(f"  已嵌入 {done}/{len(todo)}（{elapsed:.0f}s）", flush=True)

    titles = sorted(texts)
    dim = None
    if new_vectors:
        dim = len(next(iter(new_vectors.values())))
    elif old_vectors is not None:
        dim = old_vectors.shape[1]
    if dim is None:
        raise ModelError("沒有任何向量可寫入")

    matrix = np.zeros((len(titles), dim), dtype=np.float32)
    for i, title in enumerate(titles):
        if title in new_vectors:
            matrix[i] = np.asarray(new_vectors[title], dtype=np.float32)
        else:
            matrix[i] = old_vectors[old_rows[title][0]]
    matrix = _normalize(matrix)

    meta = {
        "model": model,
        "dim": dim,
        "input_type": INDEX_INPUT_TYPE,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "entries": [
            {
                "title": title,
                "path": link_index[title].get("path", ""),
                "type": link_index[title].get("type", ""),
                "hash": hashes[title],
            }
            for title in titles
        ],
    }
    VECTORS_FILE.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(VECTORS_FILE, vectors=matrix)
    META_FILE.write_text(
        json.dumps(meta, ensure_ascii=False), encoding="utf-8"
    )
    print(f"✅ 索引已寫入：{VECTORS_FILE.name}（{len(titles)} 條、{dim} 維）")
    return 0


def status():
    try:
        meta, vectors = load_stored()
    except ModelError as exc:
        print(f"❌ {exc}")
        return 1
    if meta is None:
        print("索引不存在；請先跑 python util/build_embedding_index.py")
        return 1
    print(
        f"模型 {meta['model']}｜{vectors.shape[0]} 條｜{meta['dim']} 維｜"
        f"建於 {meta.get('generated_at', '?')}"
    )
    try:
        current = embedding_model()
    except ModelError as exc:
        print(f"⚠ 無法讀目前設定：{exc}")
        return 1
    if current != meta["model"]:
        print(f"❌ 目前設定的模型是「{current}」，與索引不符；請 --rebuild")
        return 1
    print("✅ 與目前設定一致")
    return 0


def main():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="建立／更新 embedding 索引")
    parser.add_argument("--rebuild", action="store_true", help="忽略既有索引全量重建")
    parser.add_argument("--status", action="store_true", help="只顯示索引狀態")
    args = parser.parse_args()
    try:
        if args.status:
            return status()
        return build(rebuild=args.rebuild)
    except ModelError as exc:
        print(f"❌ {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
