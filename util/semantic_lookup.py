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
  python util/semantic_lookup.py --candidates 利未記 19   # 對整份 link_candidates.yaml
                                                         # 產生候選近鄰報告（步驟2後半）

--candidates 模式：讀取該章 link_candidates.yaml，把每個候選的「名稱＋分類＋
evidence＋surfaces」合成富查詢（比裸名多很多訊號），一次批量向量化後對全庫
索引找近鄰，寫報告到 .tmp/第x章/candidate_similarity.md。用途：候選定稿前
發現「措辭不同、意思相同」的既有條目，改宣告該條目名走 B 類累積，避免建出
近似重複。報告僅輔助人工分類，不改動任何檔案內容。

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
    from .book_paths import book_directory, canonical_book_name
    from . import resolve_link_candidates as resolver
except ImportError:
    from model_client import ModelError, embed_texts, select_endpoint
    from build_embedding_index import META_FILE, VECTORS_FILE
    from book_paths import book_directory, canonical_book_name
    import resolve_link_candidates as resolver

QUERY_INPUT_TYPE = "query"
DEFAULT_TOP = 5
ROOT = Path(__file__).resolve().parent.parent
REPORT_FILENAME = "candidate_similarity.md"

# 候選報告的 ⚠ 規則：只標「top-1、非同實體、分類相容、≥ 此下限」的近鄰。
# 跨 5 卷 151 候選實測（創40／出26／利19／民21／申13，富查詢）：
# - 絕對門檻不可行：條例密集章的兄弟條目彼此 0.6–0.75，0.55 會標 93%。
# - 真改名／重複對（酒政_酒政長→酒政、剪除（kareth）→從民中剪除（karet）、
#   孝敬父母→當孝敬父母）全以 top-1 之姿出現且 ≥0.68——「top-1 是不是自己」
#   比絕對分數更能分辨；同實體判定用 resolver.base_name（字面比對就會自動對上）。
# - 全新章節（用遮罩模擬「本章條目尚不存在」）top-1 必為別的條目，僅 top-1
#   規則標 42%；主要 FP 是「事件候選→其主角人物／地點」這種跨分類鄰居，而
#   真改名對幾乎都分類相容（原文→原文、神學→神學）——加 type_compatible
#   條件後降到 17%，且不損失任何已確認真對。
# 下限 0.60 偏向查全（申24 的真重複對 0.62–0.64 也要抓到）。
# 換 embedding 模型後需重新校準。
REPORT_FLAG_FLOOR = 0.60

# 候選互查（本章候選彼此比對，query-query 空間）的 ⚠ 門檻。全新章節裡
# 「兩個候選其實同概念」在索引裡查不到（兩者都還不存在），只有互查能抓——
# 申13 的「惡人勸誘全城（叛教之城）↔叛教之城必被毀滅（叛教之城）」（0.901）
# 就這樣變成現存的章內重複。實測分佈：真重複 ≥0.84，相關但不同概念
# （聖所↔至聖所 0.767、五十個金鉤↔五十個銅鉤 0.758）≤0.78，取 0.80。
INTRA_FLAG_FLOOR = 0.80


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

    def query_vectors(self, texts, top=DEFAULT_TOP, return_matrix=False):
        """批次查詢多個詞，回傳 list[list[(title, score, meta)]]（省重複載入）。

        return_matrix=True 時回傳 (results, 正規化查詢矩陣)，供呼叫端
        免額外請求做候選互查等向量運算。
        """
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
        if return_matrix:
            return out, matrix
        return out


def _format_hits(term, hits):
    lines = [f"「{term}」的語義近鄰："]
    for title, score, entry in hits:
        lines.append(f"  {score:.3f}  {title}（{entry.get('type', '?')}）")
    return "\n".join(lines)


def candidate_query_text(candidate):
    """候選的富查詢文本：名稱＋分類＋evidence＋surfaces 經文用詞。

    evidence 常含經文引句，訊號遠比裸名多——檢索模型是「短查詢對長段落」
    的非對稱設計，查詢側多給上下文能明顯改善近鄰品質。
    """
    parts = [candidate["name"]]
    if candidate.get("suggested_type"):
        parts.append(f"分類：{candidate['suggested_type']}")
    if candidate.get("evidence"):
        parts.append(str(candidate["evidence"]))
    phrases = [
        surface["phrase"] for surface in candidate.get("surfaces") or []
        if isinstance(surface, dict) and surface.get("phrase")
    ]
    if phrases:
        parts.append("經文用詞：" + "、".join(phrases))
    return "\n".join(parts)


def candidate_report(book, chapter, top=3, root=ROOT, index=None,
                     threshold=None):
    """對整章 link_candidates 產生語義近鄰報告，寫入 .tmp/第x章/。

    兩節：（1）對全庫索引查近鄰——⚠ 只標「top-1、非同實體、分類相容、
    ≥ threshold（預設 REPORT_FLAG_FLOOR）」；（2）候選互查——全新章節裡
    兩個同概念候選在索引查不到（都還不存在），只有彼此比對能抓，
    ⚠ 標 ≥ INTRA_FLAG_FLOOR 的配對。校準依據見兩常數註解。
    回傳 (report_path, 候選數, 有 ⚠ 的候選數＋互查配對數)。只寫報告檔，
    不改動 candidates 或任何條目——判斷與改名永遠是人工的事。
    """
    if threshold is None:
        threshold = REPORT_FLAG_FLOOR
    canonical = canonical_book_name(book)
    candidates = resolver.load_candidates(canonical, chapter, root=root)
    report_path = (
        book_directory(root, canonical) / ".tmp" / f"第{chapter}章" / REPORT_FILENAME
    )
    index = index or SemanticIndex.load()
    lines = [
        f"# 候選語義近鄰報告：{canonical} 第{chapter}章",
        "",
        f"- 索引模型：{index.meta.get('model')}｜{len(index.entries)} 條｜"
        f"⚠＝top-1 非同實體、分類相容、≥ {threshold}",
        "- 查詢文本＝候選名＋分類＋evidence＋surfaces。本報告僅輔助分類判斷：",
        "  ⚠ 近鄰若與候選**同概念** → 把候選名改成該既有條目名（resolver 會歸 A/B 累積）；",
        "  名稱雖近但**確為不同概念** → 照建，不受此報告限制。其餘近鄰只是脈絡。",
        "",
    ]
    flagged = 0
    if not candidates:
        lines.append("（本章 link_candidates 為空）")
    else:
        queries = [candidate_query_text(candidate) for candidate in candidates]
        results, matrix = index.query_vectors(queries, top=top, return_matrix=True)
        for candidate, hits in zip(candidates, results):
            name = candidate["name"]
            base = resolver.base_name(name)
            suggested = candidate.get("suggested_type")
            lines.append(f"## {name}（{suggested or '?'}）")
            for rank, (title, score, entry) in enumerate(hits):
                mark = ""
                note_extra = ""
                if resolver.base_name(title) == base:
                    note_extra = "；resolver 可自動對上（同名／裸名）"
                elif (rank == 0 and score >= threshold
                      and (not suggested or resolver.type_compatible(suggested, entry))):
                    mark = " ⚠"
                    flagged += 1
                lines.append(
                    f"- {score:.3f}{mark} {title}（{entry.get('type', '?')}{note_extra}）"
                )
            lines.append("")
        # 候選互查：本章候選彼此比對（query-query 空間）
        pair_scores = matrix @ matrix.T
        pairs = []
        for a in range(len(candidates)):
            for b in range(a + 1, len(candidates)):
                if pair_scores[a, b] >= INTRA_FLAG_FLOOR:
                    pairs.append((
                        float(pair_scores[a, b]),
                        candidates[a]["name"], candidates[b]["name"],
                    ))
        pairs.sort(reverse=True)
        lines.append(f"## 候選互查（本章內部，⚠＝彼此相似 ≥ {INTRA_FLAG_FLOOR}）")
        if pairs:
            lines.append("兩個候選可能是同一概念——考慮合併成一個候選（另一個用 surfaces 涵蓋），")
            lines.append("或確認確為兩個條目再照建：")
            for score, name_a, name_b in pairs:
                dup = "；同名重複候選，請刪一筆" if name_a == name_b else ""
                lines.append(f"- {score:.3f} ⚠ {name_a} ↔ {name_b}{dup}")
                flagged += 1
        else:
            lines.append("（無 ≥ 門檻的配對）")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return report_path, len(candidates), flagged


def main():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="embedding 語義近似查詢")
    parser.add_argument("term", nargs="?", help="要查詢的詞")
    parser.add_argument("--file", help="一行一詞的檔案，批次查詢")
    parser.add_argument(
        "--candidates", nargs=2, metavar=("書名", "章"),
        help="讀該章 link_candidates.yaml 產生候選近鄰報告（candidate_similarity.md）",
    )
    parser.add_argument("--top", type=int, default=DEFAULT_TOP, help="每詞取前幾名")
    parser.add_argument("--json", action="store_true", help="輸出 JSON")
    args = parser.parse_args()

    if args.candidates:
        book, chapter = args.candidates[0], int(args.candidates[1])
        try:
            path, total, flagged = candidate_report(
                book, chapter, top=max(3, min(args.top, 10))
            )
        except (ModelError, FileNotFoundError, ValueError) as exc:
            print(f"❌ {exc}")
            return 1
        print(f"✅ 報告已寫入：{path}")
        print(f"   候選 {total} 個，其中 {flagged} 個的 top-1 是高分非同實體近鄰（⚠）——"
              "逐一檢視是否改用既有條目名（走 B 類累積）。")
        return 0

    terms = []
    if args.term:
        terms.append(args.term)
    if args.file:
        terms.extend(
            line.strip() for line in Path(args.file).read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    if not terms:
        parser.error("請提供要查詢的詞、--file 詞表，或 --candidates 書名 章")

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
