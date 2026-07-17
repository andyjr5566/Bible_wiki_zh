#!/usr/bin/env python3
"""全庫重複條目報告：對現有 embedding 索引兩兩比對，找出已存在的近似重複。

與 semantic_lookup 互補——semantic_lookup 防「新增」近似重複（查新候選），
本報告清「已存在」的近似重複（現有條目彼此比對）。純用既有索引做一次矩陣
運算，不呼叫 embedding 端點。

只出報告供人工判斷，絕不自動合併：近似 ≠ 重複。「示巴（地點）」與
「示巴（起誓、豐盛）（原文）」是蓄意的地名＋字義雙條目，不是重複；本報告
把這類「裸名相同但分類不同」標記成 intentional，與真重複分流，避免洗版。

門檻是 passage↔passage 空間（與 semantic_lookup 的 query→passage 不同）：
全庫實測完全同義的命名變體落在 0.93+，0.90 以上是高密度真問題區；再低會
混入大量「相關但不同」。預設 0.90。

  python util/embedding_dup_report.py                 # 門檻 0.90，人類可讀
  python util/embedding_dup_report.py --threshold 0.93
  python util/embedding_dup_report.py --json          # 給後續合併工具吃
  python util/embedding_dup_report.py --include-intentional  # 連蓄意雙條目一起列
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

try:
    from .semantic_lookup import SemanticIndex
except ImportError:
    from semantic_lookup import SemanticIndex

DEFAULT_THRESHOLD = 0.90
# 括號（含全形）內的限定詞：地點「示巴」vs 原文「示巴（起誓、豐盛）」的裸名相同。
PAREN_RE = re.compile(r"[（(].*?[）)]")
OLD_SUFFIX_RE = re.compile(r"_old$|_old（|_old\(")


def base_name(title):
    """去掉括號限定詞、_old 尾巴、空白，取「裸名」用於判斷是否同概念。"""
    stripped = OLD_SUFFIX_RE.sub("", title)
    stripped = PAREN_RE.sub("", stripped)
    return stripped.replace("_old", "").strip()


def pair_flags(a, b):
    """給一對條目貼啟發式標籤，供分流；不做自動判定。"""
    flags = []
    ta, tb = a["title"], b["title"]
    if "_old" in ta or "_old" in tb:
        flags.append("OLD")            # 遷移殘渣，通常刪舊留新
    same_type = a["type"] == b["type"]
    same_base = base_name(ta) == base_name(tb)
    if same_type and same_base:
        flags.append("SAME")           # 同分類同裸名 → 高度可能真重複
    if (not same_type) and same_base:
        flags.append("INTENTIONAL")    # 不同分類同裸名 → 多為蓄意雙條目（地點＋原文）
    if same_base and (ta in tb or tb in ta):
        flags.append("SUBSTRING")      # 一名是另一名的子串（多為變體）
    return flags


def find_pairs(index, threshold):
    matrix = index.vectors
    scores = matrix @ matrix.T
    n = scores.shape[0]
    iu = np.triu_indices(n, k=1)
    sims = scores[iu]
    mask = sims >= threshold
    rows, cols, vals = iu[0][mask], iu[1][mask], sims[mask]
    order = np.argsort(-vals)
    pairs = []
    for k in order:
        a = index.entries[rows[k]]
        b = index.entries[cols[k]]
        pairs.append({
            "score": round(float(vals[k]), 4),
            "a": {"title": a["title"], "type": a["type"], "path": a["path"]},
            "b": {"title": b["title"], "type": b["type"], "path": b["path"]},
            "flags": pair_flags(a, b),
        })
    return pairs


def main():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="全庫重複條目報告")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--json", action="store_true", help="輸出 JSON")
    parser.add_argument(
        "--include-intentional", action="store_true",
        help="連 INTENTIONAL（不同分類同裸名，多為蓄意雙條目）也列出",
    )
    parser.add_argument("--out", type=Path, help="JSON 寫入檔案（配合合併工具）")
    args = parser.parse_args()

    try:
        index = SemanticIndex.load()
    except Exception as exc:
        print(f"❌ 無法載入索引：{exc}")
        return 1

    pairs = find_pairs(index, args.threshold)
    kept = [
        p for p in pairs
        if args.include_intentional or "INTENTIONAL" not in p["flags"]
    ]
    intentional = len(pairs) - len(kept)

    if args.json or args.out:
        payload = {"threshold": args.threshold, "pairs": kept}
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        if args.out:
            args.out.write_text(text, encoding="utf-8")
            print(f"✅ 已寫入 {args.out}（{len(kept)} 對）")
        else:
            print(text)
        return 0

    print(f"門檻 {args.threshold}：{len(kept)} 對待複查"
          + (f"（另隱藏 {intentional} 對 INTENTIONAL 蓄意雙條目）" if intentional else ""))
    print("旗標：OLD=遷移殘渣  SAME=同類同裸名  SUBSTRING=子串  INTENTIONAL=不同類同裸名\n")
    for p in kept:
        tag = " ".join(p["flags"]) or "-"
        print(f"  {p['score']:.3f}  [{tag}]")
        print(f"         {p['a']['title']}（{p['a']['type']}）")
        print(f"         {p['b']['title']}（{p['b']['type']}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
