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
import hashlib
import json
import re
import sys
import urllib.error
from pathlib import Path

import numpy as np
import yaml

try:
    from .model_client import ModelError, embed_texts, rerank_documents, select_endpoint
    from .build_embedding_index import (
        META_FILE, VECTORS_FILE, compute_index_fingerprint, entry_embed_text,
    )
    from .book_paths import book_directory, canonical_book_name
    from . import resolve_link_candidates as resolver
except ImportError:
    from model_client import ModelError, embed_texts, rerank_documents, select_endpoint
    import book_paths
    from book_paths import book_directory, canonical_book_name
    from build_embedding_index import (
        META_FILE, VECTORS_FILE, compute_index_fingerprint, entry_embed_text,
    )
    import resolve_link_candidates as resolver

QUERY_INPUT_TYPE = "query"
DEFAULT_TOP = 5
ROOT = Path(__file__).resolve().parent.parent
REPORT_FILENAME = "candidate_similarity.md"
RERANK_POLICY_VERSION = "2026.08.1"
CALIBRATION_FILE_REL = Path("_config") / "reranker_calibration.yaml"


def _file_sha256(path):
    """計算檔案的 SHA256；若檔案不存在回傳 'missing'。"""
    p = Path(path)
    if not p.is_file():
        return "missing"
    h = hashlib.sha256()
    try:
        # 正規化換行後計算 hash，避免 CRLF/LF 差異導致誤判
        data = p.read_bytes().replace(b"\r\n", b"\n")
        h.update(data)
        return h.hexdigest()
    except OSError:
        return "error"


def _load_calibration(root=ROOT):
    """載入 _config/reranker_calibration.yaml。"""
    calib_path = Path(root) / CALIBRATION_FILE_REL
    if not calib_path.is_file():
        return {"models": {}}
    try:
        data = yaml.safe_load(calib_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {"models": {}}
    except Exception:
        return {"models": {}}


def _is_circuit_breaker_exception(exc):
    """判斷是否為端點／系統級錯誤（連線拒絕、逾時、429、5xx），需觸發斷路器。"""
    if isinstance(exc, (TimeoutError, ConnectionRefusedError)):
        return True
    if isinstance(exc, urllib.error.URLError):
        return True
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code == 429 or exc.code >= 500
    msg = str(exc).lower()
    if any(k in msg for k in ["connection refused", "timed out", "timeout", "502", "503", "504", "429"]):
        return True
    return False


def extract_report_metadata(path_or_text):
    """解析 candidate_similarity.md 開頭的 candidate_similarity_meta 註解。"""
    if isinstance(path_or_text, (str, Path)) and Path(path_or_text).is_file():
        text = Path(path_or_text).read_text(encoding="utf-8")
    else:
        text = str(path_or_text)
    match = re.search(r"<!--\s*candidate_similarity_meta\s*\n([\s\S]*?)\n\s*-->", text)
    if not match:
        return None
    meta = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta

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
    stype = candidate.get("suggested_type") or candidate.get("type")
    if stype:
        parts.append(f"分類：{stype}")
    if candidate.get("evidence"):
        parts.append(str(candidate["evidence"]))
    phrases = [
        surface["phrase"] for surface in candidate.get("surfaces") or []
        if isinstance(surface, dict) and surface.get("phrase")
    ]
    if phrases:
        parts.append("經文用詞：" + "、".join(phrases))
    return "\n".join(parts)


def candidate_rerank_query(candidate, book=None, chapter=None):
    """候選的 Reranker 查詢文本：待建立詞＋出現位置＋候選類型＋本章上下文＋經文用詞。"""
    parts = [f"待建立詞：{candidate['name']}"]
    if book and chapter:
        parts.append(f"出現位置：{book} 第{chapter}章")
    stype = candidate.get("suggested_type") or candidate.get("type")
    if stype:
        parts.append(f"候選類型：{stype}")
    if candidate.get("evidence"):
        parts.append(f"本章上下文：{candidate['evidence']}")
    phrases = [
        surface["phrase"] for surface in candidate.get("surfaces") or []
        if isinstance(surface, dict) and surface.get("phrase")
    ]
    if phrases:
        parts.append("經文用詞：" + "、".join(phrases))
    return "\n".join(parts)


def entry_rerank_document(title, entry, root=ROOT):
    """條目的 Reranker 文件文本：標題＋分類＋別名＋定義／主題發展／累積摘要。"""
    return entry_embed_text(title, entry, root=root)


def _lexical_preview(name, link_index, homonyms):
    """預覽 resolver 對候選名的字面解析結果。

    回傳 (說明文字, 是否值得注意)。語義報告只看得到「像不像」，看不到
    resolver 實際會把候選連到哪——alias 錯登（安密巴 aliases 誤含以實各谷）
    會靜默把候選導向錯誤條目，兩個閘門都不會叫。在報告裡預覽字面解析，
    讓這種意外在跑 orchestrator 之前就穿幫。
    """
    _, options = resolver.homonym_options(name, homonyms)
    if options:
        targets = "、".join(option["target"] for option in options)
        return f"同名詞需人工選擇（將歸 D）：{targets}", True
    match_type, entry, title = resolver.find_in_index(name, link_index)
    if match_type == "conflict":
        return "名稱或 alias 多重指向（將歸 D）", True
    if entry:
        if match_type == "alias" and resolver.base_name(title) != resolver.base_name(name):
            return (f"經 alias 導向「{title}」——名稱不同，請確認確為同一實體", True)
        return f"對上既有「{title}」（{match_type}，將歸 A/B 累積）", False
    return "無字面對應 → 新建（C）", False


def candidate_report(book, chapter, top=5, root=ROOT, index=None,
                     threshold=None, link_index=None, homonyms=None,
                     reranker=None, use_rerank=True, require_rerank=False):
    """對整章 link_candidates 產生二階段語義近鄰與重排報告，寫入 .tmp/第x章/。

    架構：
    1. 字面規則篩選：確切同名／正規化同名無歧義條目標為確切命中，跳過 Reranker API。
    2. 第一階段檢索：模糊／衝突／新建候選透過 SemanticIndex 檢索 Top K（預設 5~8 名）。
    3. 第二階段裁判：使用 Cross-Encoder Reranker（如 nvidia/llama-nemotron-rerank-vl-1b-v2:free）
       對候選富查詢與既有條目摘要進行語意重排與重新打分。
    4. Deterministic Governance 優先判定：
       - homonym / conflict / alias warning → 永遠 ⚠，絕不給 ✅
       - 分類不相容 → 永遠 ⚠ 分類不相容，絕不給 ✅
       - 確切同名無歧義 → ✅ 建議使用既有條目
       - 未校準模型 → ⚠ 未校準模型僅供排序參考，需人工確認
       - 校準模型 → 依校準門檻與 Margin 判定 ✅ / ⚠ / 🆕
    5. 候選互查：比對本章內部各候選之間的語義重複。
    6. 寫入包含完整 Multi-factor 指紋的結構化元資料標頭（供 Freshness Gate 檢驗）。

    回傳 (report_path, 候選數, 有 ⚠／ⓘ 的候選數＋互查配對數)。
    """
    if threshold is None:
        threshold = REPORT_FLAG_FLOOR
    root = Path(root)
    canonical = canonical_book_name(book)
    candidates = resolver.load_candidates(canonical, chapter, root=root)
    book_dir = book_directory(root, canonical)
    tmp_dir = book_dir / ".tmp" / f"第{chapter}章"
    candidates_path = tmp_dir / "link_candidates.yaml"
    report_path = tmp_dir / REPORT_FILENAME

    index = index or SemanticIndex.load()
    if link_index is None:
        link_index = resolver.load_index()
    if homonyms is None:
        homonyms = resolver.load_homonyms()

    for c in candidates:
        stype = c.get("suggested_type") or c.get("type")
        if stype and stype not in resolver.VALID_TYPES:
            raise ValueError(
                f"candidates 條目「{c.get('name')}」的 type「{stype}」不是合法分類！"
                f"必須是 link_folder/ 下的合法資料夾之一：{resolver.VALID_TYPES}"
            )

    raw_path = root / "raw_scripture" / canonical / f"第{chapter}章.txt"
    scripture_text = raw_path.read_text(encoding="utf-8") if raw_path.exists() else ""
    surface_warnings = []
    if scripture_text:
        for c in candidates:
            for s in c.get("surfaces") or []:
                if isinstance(s, dict) and s.get("phrase"):
                    phrase = s["phrase"]
                    if phrase not in scripture_text:
                        surface_warnings.append(f"  - 條目「{c['name']}」的 surface「{phrase}」未出現在本章經文中")

    # 偵測 reranker 可用性與校準狀態
    rerank_model = None
    if use_rerank:
        if reranker is not None:
            rerank_model = getattr(reranker, "model_name", "custom-reranker")
        else:
            try:
                ep = select_endpoint(task="rerank")
                rerank_model = ep.get("model")
            except Exception:
                rerank_model = None

    calib_data = _load_calibration(root=root)
    models_calib = calib_data.get("models") or {}
    calib_entry = models_calib.get(rerank_model, {}) if rerank_model else {}
    is_calibrated = bool(calib_entry.get("calibrated") is True)
    calib_thresholds = calib_entry.get("thresholds") or calib_entry.get("provisional_thresholds") or {}

    lines = [
        f"# 候選語義近鄰報告：{canonical} 第{chapter}章",
        "",
        f"- 檢索模型：{index.meta.get('model')}｜重排模型：{rerank_model or '未啟用 (僅檢索)'}（{'已校準' if is_calibrated else '未校準/保守模式'}）｜全庫 {len(index.entries)} 條",
        "- 規則說明：字面確切匹配直接通過；模糊／衝突候選經檢索 Top K 後由 Reranker 裁判。",
        "  治理優先：同名歧義（D類）與分類不相容永遠標 ⚠；未校準模型僅供排序參考。",
        "  字面解析：列 resolver 實際比對結果——標「請確認」者務必人工核實。",
        "",
    ]
    if surface_warnings:
        lines.append("⚠️ 【經文匹配警示】下列 surfaces 未在本章經文中找到逐字匹配（若非經文詞請自 link_candidates.yaml 刪除）：")
        lines.extend(surface_warnings)
        lines.append("")
        for w in surface_warnings:
            print(f"⚠️ {w.strip()}")

    flagged = 0
    rerankable_candidates = 0
    rerank_attempted = 0
    rerank_succeeded = 0
    rerank_failed = 0
    circuit_open = False

    if not candidates:
        lines.append("（本章 link_candidates 為空）")
    else:
        queries = [candidate_query_text(candidate) for candidate in candidates]
        results, matrix = index.query_vectors(queries, top=top, return_matrix=True)

        for candidate, hits in zip(candidates, results):
            name = candidate["name"]
            base = resolver.base_name(name)
            suggested = candidate.get("suggested_type") or candidate.get("type")
            preview, attention = _lexical_preview(name, link_index, homonyms)

            match_type, matched, title = resolver.find_in_index(name, link_index)
            is_exact_match = bool(
                matched and not attention and
                resolver.base_name(title) == base and
                (not suggested or resolver.type_compatible(suggested, matched))
            )

            lines.append(f"## {name}（{suggested or '?'}）")
            
            # Query block
            lines.append("query:")
            lines.append(f"- 待建立詞：{name}")
            lines.append(f"- 出現位置：{canonical} 第{chapter}章")
            lines.append(f"- 候選類型：{suggested or '未指定'}")
            if candidate.get("evidence"):
                lines.append(f"- 本章上下文：{candidate['evidence']}")
            phrases = [
                s["phrase"] for s in candidate.get("surfaces") or []
                if isinstance(s, dict) and s.get("phrase")
            ]
            if phrases:
                lines.append(f"- 經文用詞：{'、'.join(phrases)}")
            lines.append("")

            lines.append(f"字面解析：{'⚠ ' if attention else ''}{preview}")
            lines.append("")

            # 執行 Rerank（若啟用且非確切命中）
            ranked_items = []
            has_rerank = False

            if not is_exact_match and hits:
                rerankable_candidates += 1
                if use_rerank and not circuit_open:
                    rerank_attempted += 1
                    q_text = candidate_rerank_query(candidate, book=canonical, chapter=chapter)
                    doc_texts = [entry_rerank_document(t, e, root=root) for t, s, e in hits]
                    try:
                        if reranker is not None:
                            rerank_res = reranker(q_text, doc_texts)
                        else:
                            rerank_res = rerank_documents(q_text, doc_texts, task="rerank")
                        
                        if rerank_res:
                            rerank_succeeded += 1
                            has_rerank = True
                            for r_item in rerank_res:
                                idx = r_item["index"]
                                if 0 <= idx < len(hits):
                                    t, s, e = hits[idx]
                                    ranked_items.append({
                                        "title": t,
                                        "sim_score": s,
                                        "rerank_score": r_item["relevance_score"],
                                        "entry": e,
                                    })
                    except Exception as exc:
                        rerank_failed += 1
                        if _is_circuit_breaker_exception(exc):
                            circuit_open = True
                            try:
                                print(f"⚠️ Reranker 端點系統性失敗，觸發斷路器熔斷：{exc}")
                            except Exception:
                                pass
                        else:
                            try:
                                print(f"⚠️ 候選「{name}」Rerank 失敗（降級單筆）：{exc}")
                            except Exception:
                                pass

            if not ranked_items:
                ranked_items = [
                    {"title": t, "sim_score": s, "rerank_score": None, "entry": e}
                    for t, s, e in hits
                ]

            # 產生表格與判定（嚴格遵循治理優先序）
            if ranked_items:
                top1 = ranked_items[0]
                top2 = ranked_items[1] if len(ranked_items) > 1 else None
                is_same_entity = resolver.base_name(top1["title"]) == base
                is_type_compat = not suggested or resolver.type_compatible(suggested, top1["entry"])

                if has_rerank:
                    lines.append("| Rank | Candidate | Similarity | Rerank | Path |")
                    lines.append("|---|---|---:|---:|---|")
                    for r_rank, item in enumerate(ranked_items, 1):
                        r_score_str = f"{item['rerank_score']:.3f}" if item["rerank_score"] is not None else "-"
                        path_str = item["entry"].get("path", "")
                        lines.append(f"| {r_rank} | {item['title']} | {item['sim_score']:.3f} | {r_score_str} | {path_str} |")
                    lines.append("")

                    top1_r = top1["rerank_score"] if top1["rerank_score"] is not None else 0.0
                    top2_r = top2["rerank_score"] if top2 and top2["rerank_score"] is not None else 0.0
                    margin = top1_r - top2_r if top2 and top2["rerank_score"] is not None else top1_r
                    lines.append(f"rerank_margin: {margin:.3f} (Top1 - Top2)")

                    # 治理優先序判定
                    score_low = calib_thresholds.get("score_low", 0.40) if is_calibrated else 0.40
                    if attention:
                        verdict = f"⚠ 字面解析有歧義／需人工確認（{preview}）"
                        flagged += 1
                    elif is_exact_match or (is_same_entity and is_type_compat and not attention):
                        verdict = f"✅ 建議使用既有條目 [[{top1['title']}]]（同名／字面對應）"
                    elif top1_r < score_low:
                        verdict = "🆕 建議建立新條目（既有條目相關度低）"
                    elif not is_type_compat:
                        verdict = (
                            f"⚠ 分類不相容（候選={suggested} vs 條目={top1['entry'].get('type')}），"
                            f"若確為同實體請確認是否改用 [[{top1['title']}]]"
                        )
                        flagged += 1
                    elif not is_calibrated:
                        verdict = f"⚠ 未校準模型（{rerank_model}），評分僅供排序參考，需人工確認"
                        flagged += 1
                    else:
                        score_high = calib_thresholds.get("score_high", 0.70)
                        margin_high = calib_thresholds.get("margin_high", 0.20)
                        margin_ambiguous = calib_thresholds.get("margin_ambiguous", 0.15)
                        if top1_r >= score_high and margin >= margin_high:
                            verdict = f"✅ 建議使用既有條目 [[{top1['title']}]]"
                        elif margin < margin_ambiguous:
                            verdict = f"⚠ 候選相近（Top1 與 Top2 分數差距 {margin:.3f} < {margin_ambiguous:.2f}），需 Agent / 人工判斷"
                            flagged += 1
                        elif top1_r >= score_low:
                            verdict = f"⚠ 相關度中等（{top1_r:.3f}），請確認是否使用既有條目 [[{top1['title']}]]"
                            flagged += 1
                        else:
                            verdict = "🆕 建議建立新條目（既有條目相關度低）"
                    lines.append(f"判定：{verdict}")
                else:
                    lines.append("| Rank | Candidate | Similarity | Path |")
                    lines.append("|---|---|---:|---|")
                    for r_rank, item in enumerate(ranked_items, 1):
                        path_str = item["entry"].get("path", "")
                        lines.append(f"| {r_rank} | {item['title']} | {item['sim_score']:.3f} | {path_str} |")
                    lines.append("")

                    # 治理優先序判定 (純 embedding 降級路徑)
                    if attention:
                        verdict = f"⚠ 字面解析有歧義／需人工確認（{preview}）"
                        flagged += 1
                    elif is_exact_match or (is_same_entity and is_type_compat and not attention):
                        verdict = f"✅ 建議使用既有條目 [[{top1['title']}]]（同名／字面對應）"
                    elif top1["sim_score"] >= threshold:
                        if not is_type_compat:
                            verdict = (
                                f"ⓘ 分類不相容（候選={suggested} vs 條目={top1['entry'].get('type')}），"
                                "若確為同實體請人工確認"
                            )
                            flagged += 1
                        else:
                            verdict = f"⚠ 語義相似度高（≥{threshold:.2f}），請確認是否同概念改用 [[{top1['title']}]]"
                            flagged += 1
                    else:
                        verdict = "🆕 建議建立新條目（無高相似既有條目）"
                    lines.append(f"判定：{verdict}")
            else:
                lines.append("（無相似條目）")
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

    # 計算狀態
    if not use_rerank or rerank_model is None:
        rerank_status = "disabled"
    elif rerankable_candidates == 0:
        rerank_status = "not_needed"
    elif rerank_failed == 0 and rerank_succeeded == rerankable_candidates:
        rerank_status = "success"
    elif rerank_succeeded > 0:
        rerank_status = "partial"
    else:
        rerank_status = "degraded"

    if require_rerank and rerank_status in ("partial", "degraded", "disabled"):
        raise ModelError(f"--require-rerank 要求 Reranker 正常運作，但目前狀態為 {rerank_status}")

    # 計算所有指紋與雜湊
    candidate_sha256 = _file_sha256(candidates_path)
    link_index_sha256 = _file_sha256(root / "util" / "output" / "link_index.json")
    homonyms_sha256 = _file_sha256(root / "_config" / "link_homonyms.yaml")
    calibration_sha256 = _file_sha256(root / CALIBRATION_FILE_REL)
    embedding_model = index.meta.get("model", "")
    embedding_index_fingerprint = compute_index_fingerprint(index.meta)

    meta_header = (
        "<!-- candidate_similarity_meta\n"
        "schema_version: 1\n"
        f"book: {canonical}\n"
        f"chapter: {chapter}\n"
        f"candidate_sha256: {candidate_sha256}\n"
        f"embedding_model: {embedding_model}\n"
        f"embedding_index_fingerprint: {embedding_index_fingerprint}\n"
        f"link_index_sha256: {link_index_sha256}\n"
        f"homonyms_sha256: {homonyms_sha256}\n"
        f"rerank_model: {rerank_model or 'none'}\n"
        f"rerank_policy_version: {RERANK_POLICY_VERSION}\n"
        f"calibration_sha256: {calibration_sha256}\n"
        f"rerank_status: {rerank_status}\n"
        f"rerankable_candidates: {rerankable_candidates}\n"
        f"rerank_attempted: {rerank_attempted}\n"
        f"rerank_succeeded: {rerank_succeeded}\n"
        "-->\n\n"
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(meta_header + "\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return report_path, len(candidates), flagged


def main():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="embedding 語義近似查詢與 rerank 重排裁判")
    parser.add_argument("term", nargs="?", help="要查詢的詞")
    parser.add_argument("--file", help="一行一詞的檔案，批次查詢")
    parser.add_argument(
        "--candidates", nargs=2, metavar=("書名", "章"),
        help="讀該章 link_candidates.yaml 產生候選近鄰報告（candidate_similarity.md）",
    )
    parser.add_argument("--top", type=int, default=DEFAULT_TOP, help="每詞取前幾名")
    parser.add_argument("--threshold", type=float, default=None, help="相似度門檻")
    parser.add_argument("--no-rerank", action="store_true", help="停用 Reranker 語意裁判")
    parser.add_argument("--require-rerank", action="store_true", help="強制要求 Reranker 成功（降級/失敗則 exit 1）")
    parser.add_argument("--json", action="store_true", help="輸出 JSON")
    args = parser.parse_args()

    if args.candidates:
        book, chapter = args.candidates[0], int(args.candidates[1])
        try:
            path, total, flagged = candidate_report(
                book, chapter, top=max(3, min(args.top, 10)),
                threshold=args.threshold,
                use_rerank=not args.no_rerank,
                require_rerank=args.require_rerank,
            )
        except (ModelError, FileNotFoundError, ValueError) as exc:
            print(f"❌ {exc}")
            return 1
        print(f"✅ 報告已寫入：{path}")
        print(f"   候選 {total} 個，其中 {flagged} 項需人工審核（⚠／ⓘ）——"
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
