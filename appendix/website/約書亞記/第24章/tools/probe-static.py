"""讀 probe-static.mjs 的截圖，列出捲了很久畫面卻幾乎沒變的段落（停格）。"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

folder = Path(sys.argv[1])
step = int(sys.argv[2]) if len(sys.argv) > 2 else 200
threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0  # 相鄰兩張平均亮度差（0–255）低於此值視為沒動
rows = json.loads((folder / "index.json").read_text(encoding="utf-8"))
prev = None
diffs = []
for r in rows:
    img = np.asarray(Image.open(folder / r["file"]).convert("L"), dtype=np.float32)
    diffs.append(0.0 if prev is None else float(np.abs(img - prev).mean()))
    prev = img

runs, start = [], None
for k, d in enumerate(diffs):
    still = k > 0 and d < threshold
    if still and start is None:
        start = k - 1
    if (not still or k == len(diffs) - 1) and start is not None:
        last = k - 1 if not still else k
        if last - start >= 1:
            runs.append((start, last))
        start = None
runs.sort(key=lambda s: -(s[1] - s[0]))
print(f"取樣 {len(rows)} 張、每 {step}px；平均差 {np.mean(diffs[1:]):.2f}")
for a, b in runs[:25]:
    px = (b - a) * step
    beats = sorted({rows[k]["beat"] for k in range(a, b + 1)})
    print(f"{px:5d}px 沒動｜y {rows[a]['y']}–{rows[b]['y']}｜{beats}｜進度 {rows[a]['p']}→{rows[b]['p']}")
