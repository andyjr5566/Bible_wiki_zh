from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image


root = Path(sys.argv[1])
report = {}
failed = []
dialogue_path = root / 'dialogues.json'
dialogues = json.loads(dialogue_path.read_text(encoding='utf-8-sig')) if dialogue_path.exists() else []
for device in ("desktop", "mobile-landscape"):
    directory = root / device
    pairs = sorted(directory.glob("*-a.png"))
    values = []
    for first in pairs:
        second = first.with_name(first.name[:-6] + "-b.png")
        if not second.exists():
            failed.append(f"{device}/{first.stem}: missing paired screenshot")
            continue
        with Image.open(first) as a_img, Image.open(second) as b_img:
            a = np.asarray(a_img.convert("RGB"), dtype=np.int16)
            b = np.asarray(b_img.convert("RGB"), dtype=np.int16)
        if a.shape != b.shape:
            failed.append(f"{device}/{first.stem}: image sizes differ")
            continue
        ratio = float((np.max(np.abs(a - b), axis=2) > 0).mean())
        dialogue = '-family-' in first.stem
        beat = first.stem[:-2]
        values.append({"beat": beat, "changedPixels": ratio, "mode": 'dialogue-stability' if dialogue else 'idle-motion'})
        if dialogue:
            # 家人對話的鏡頭原本就停穩；檢查泡泡可見、文字與位置穩定。
            sample = next((s for s in dialogues if s['device'] == device and s['beat'] == beat), None)
            if not sample or not sample['visible'] or not sample['sameText'] or sample['dx'] > 1 or sample['dy'] > 1:
                failed.append(f'{device}/{beat}: speech bubble missing or unstable')
        elif ratio <= 0.005:
            failed.append(f"{device}/{first.stem}: only {ratio:.4%} changed pixels")
    report[device] = {"pairs": len(values), "motionPairs": sum(x['mode'] == 'idle-motion' for x in values), "dialoguePairs": sum(x['mode'] == 'dialogue-stability' for x in values), "pass": len(values) == 36 and not any(x.startswith(device + "/") for x in failed), "minChangedPixels": min((x["changedPixels"] for x in values if x['mode'] == 'idle-motion'), default=0), "beats": values}

report["errors"] = failed
report["status"] = "PASS" if not failed and all(report[d]["pairs"] == 36 for d in ("desktop", "mobile-landscape")) else "FAIL"
(root / "pixel-diff.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "beats"} if isinstance(v, dict) and "beats" in v else v for k, v in report.items()}, ensure_ascii=False, indent=2))
sys.exit(0 if report["status"] == "PASS" else 1)
