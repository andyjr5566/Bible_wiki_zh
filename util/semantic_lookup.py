#!/usr/bin/env python3
"""對 embedding 索引做語義近似查詢，找出與詞義最像的既有條目。

用途：建 link_candidates 前，先查打算新建的候選名是否已有措辭不同、
意思相同的既有條目——字面比對（resolve_link_candidates）看不出來，
只有語義相似度能揪出，避免建出近似重複條目。

一切結果只供人工判斷：本模組不建立、不改動任何連結。相似度不是機械
可證的判準，門檻只用來排序與提示，永遠不當作自動決策的依據。

  python util/semantic_lookup.py "不可搶奪鄰舍"          # 查單一詞
  python util/semantic_lookup.py "不可搶奪鄰舍" --top 8   # 取前 8 名
  python util/semantic_lookup.py --file candidates.txt   # 一行一詞批查

程式化使用：
  from semantic_lookup import SemanticIndex
  index = SemanticIndex.load()
  hits = index.query("不可搶奪鄰舍", top=5)   # [(title, score, meta), ...]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

try:
    from .model_client import ModelError, embed_texts, select_endpoint
    from .build_embedding_index import META_FILE, VECTORS_FILE
except ImportError:
    from model_client import ModelError, embed_texts, select_endpoint
    from build_embedding_index import META_FILE, VECTORS_FILE

QUERY_INPUT_TYPE = "query"
DEFAULT_TOP = 5


class SemanticIndex:
    """載入 embedding 索引並提供近似查詢。"""

    def __init__(self, meta, vectors):
        self.meta = meta
        self.vectors = vectors  # 已正規化 (N, dim) float32
        self.entries = meta["entries"]

    @classmethod
    def load(cls, meta_file=META_FILE, vectors_file=VECTORS_FILE, check_model=True):
        if not (meta_file.exists() and vectors_file.exists()):
            raise ModelError(
                "embedding 索引不存在；請先跑 python util/build_embedding_index.py"
            )
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        vectors = np.load(vectors_file)["vectors"]
        if len(meta.get("entries", [])) != vectors.shape[0]:
            raise ModelError("embedding 索引損壞：meta 與向量列數不符，請 --rebuild")
        if check_model:
            current = select_endpoint(task="embedding").get("model")
            if current and current != meta.get("model"):
                raise ModelError(
                    f"索引是「{meta.get('model')}」建的，目前設定是「{current}」；"
                    "向量跨模型不可比，請跑 build_embedding_index.py --rebuild"
                )
        return cls(meta, vectors)

    def _embed_query(self, text):
        vector = np.asarray(
            embed_texts([text], input_type=QUERY_INPUT_TYPE)[0], dtype=np.float32
        )
        norm = np.linalg.norm(vector)
        return vector / norm if norm else vector

    def query(self, text, top=DEFAULT_TOP, exclude_title=None):
        """回傳 [(title, score, meta_entry), ...]，score 為餘弦相似度、由高到低。"""
        query_vector = self._embed_query(text)
        scores = self.vectors @ query_vector
        order = np.argsort(-scores)
        results = []
        for i in order:
            entry = self.entries[i]
            if exclude_title is not None and entry["title"] == exclude_title:
                continue
            results.append((entry["title"], float(scores[i]), entry))
            if len(results) >= top:
                break
        return results

    def query_vectors(self, texts, top=DEFAULT_TOP):
        """批次查詢多個詞，回傳 list[list[(title, score, meta)]]（省重複載入）。"""
        vectors = embed_texts(list(texts), input_type=QUERY_INPUT_TYPE)
        matrix = np.asarray(vectors, dtype=np.float32)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        matrix = matrix / norms
        all_scores = self.vectors @ matrix.T  # (N, len(texts))
        out = []
        for col in range(all_scores.shape[1]):
            scores = all_scores[:, col]
            order = np.argsort(-scores)[:top]
            out.append([
                (self.entries[i]["title"], float(scores[i]), self.entries[i])
                for i in order
            ])
        return out


def _format_hits(term, hits):
    lines = [f"「{term}」的語義近鄰："]
    for title, score, entry in hits:
        lines.append(f"  {score:.3f}  {title}（{entry.get('type', '?')}）")
    return "\n".join(lines)


def main():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="embedding 語義近似查詢")
    parser.add_argument("term", nargs="?", help="要查詢的詞")
    parser.add_argument("--file", help="一行一詞的檔案，批次查詢")
    parser.add_argument("--top", type=int, default=DEFAULT_TOP, help="每詞取前幾名")
    parser.add_argument("--json", action="store_true", help="輸出 JSON")
    args = parser.parse_args()

    terms = []
    if args.term:
        terms.append(args.term)
    if args.file:
        terms.extend(
            line.strip() for line in Path(args.file).read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    if not terms:
        parser.error("請提供要查詢的詞，或用 --file 指定詞表")

    try:
        index = SemanticIndex.load()
        results = index.query_vectors(terms, top=args.top)
    except ModelError as exc:
        print(f"❌ {exc}")
        return 1

    if args.json:
        payload = [
            {"term": term, "hits": [
                {"title": t, "score": s, "type": e.get("type"), "path": e.get("path")}
                for t, s, e in hits
            ]}
            for term, hits in zip(terms, results)
        ]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for term, hits in zip(terms, results):
            print(_format_hits(term, hits))
    return 0


if __name__ == "__main__":
    sys.exit(main())
