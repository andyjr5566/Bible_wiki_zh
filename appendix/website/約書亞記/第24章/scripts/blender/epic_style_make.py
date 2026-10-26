"""風格比較樣張產生器（系統 Python；呼叫 Blender 背景模式渲染，再用 epic_post.py 後製）。

用法（PowerShell，從本站根目錄）：
    python -I scripts\\blender\\epic_style_make.py cover A
    python -I scripts\\blender\\epic_style_make.py redsea B --force
    python -I scripts\\blender\\epic_style_make.py all            # 兩個鏡頭 x 三種風格 + 比較圖
    python -I scripts\\blender\\epic_style_make.py compare        # 只重拼比較圖

輸出：lab/renders/style/<cover|redsea>-<A|B|C>.png（1280x720）、<shot>-compare.png。
中間檔（.f32 原始線性資料）在 lab/renders/epic/_work/，風格 C 重用風格 A 的渲染。
"""
import json
import sys as _sys
try:
    _sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import os
import subprocess
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
WORK = os.path.join(ROOT, "lab", "renders", "epic", "_work")
OUT = os.path.join(ROOT, "lab", "renders", "style")

W, H = 1280, 720
SAMPLES = 32

DARK = {"xc": -95, "core": 12, "soft": 28, "k": 1.15, "behind": 0.55}

CONFIG = {
    "cover": {
        "script": "epic_cover.py",
        "A": {"blender": "A", "env": {}, "post_style": "A",
              "post": {"haze_gain": 0.9, "mist_z0": 790, "mist_rho": 0.009, "mist_H": 140, "ray_gain": 16.0, "ray_len": 0.9,
                       "exposure": 0.8, "sat": 0.85, "vig": 0.65, "bloom": 0.7}},
        "B": {"blender": "B", "env": {}, "post_style": "B",
              "post": {"focus_m": 12, "dof_k": 3.0, "haze_dist": 6000, "exposure": 1.4, "sat": 1.05}},
        "C": {"reuse": "A", "post_style": "C",
              "post": {"mist_rho": 0, "sat": 1.3, "exposure": 1.1, "levels": 10}},
    },
    "redsea": {
        "script": "epic_redsea.py",
        "A": {"blender": "A", "env": {}, "post_style": "A",
              "post": {"dark": DARK, "haze_dist": 9000, "haze_gain": 1.0, "haze_mix": 0.97, "mist_rho": 0, "exposure": 1.5}},
        "B": {"blender": "B", "env": {}, "post_style": "B",
              "post": {"dark": dict(DARK, behind=0.75), "focus_m": 14, "dof_k": 2.5, "exposure": 1.5, "haze_dist": 6000}},
        "C": {"reuse": "A", "post_style": "C",
              "post": {"dark": DARK, "mist_rho": 0, "sat": 1.3, "exposure": 1.3, "levels": 10}},
    },
}


def run_blender(shot, style_cfg, base, force):
    if os.path.exists(base + ".f32") and os.path.exists(base + "_depth.f32") and not force:
        print("  reuse render", os.path.basename(base))
        return None
    env = dict(os.environ)
    env.update({k: str(v) for k, v in style_cfg["env"].items()})
    script = os.path.join(HERE, CONFIG[shot]["script"])
    args = [BLENDER, "-b", "--factory-startup", "--python", script, "--", "--style", style_cfg["blender"],
            "--w", str(W), "--h", str(H), "--samples", str(SAMPLES), "--out", base]
    t = time.time()
    r = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    dt = time.time() - t
    tail = "\n".join(r.stdout.splitlines()[-6:])
    if r.returncode != 0 or not os.path.exists(base + ".f32"):
        print(r.stdout[-3000:], r.stderr[-1500:])
        raise SystemExit("blender failed")
    print(f"  blender {dt:.0f}s ({tail.splitlines()[-1] if tail else ''})")
    return dt


def make(shot, style, force=False):
    cfg = CONFIG[shot][style]
    src = CONFIG[shot][cfg.get("reuse", style)]
    base = os.path.join(WORK, f"{shot}_{cfg.get('reuse', style)}")
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    print(f"[{shot}-{style}]")
    dt = run_blender(shot, src, base, force)
    out = os.path.join(OUT, f"{shot}-{style}.png")
    t = time.time()
    subprocess.run([sys.executable, "-I", os.path.join(HERE, "epic_post.py"), base, cfg["post_style"], out, json.dumps(cfg["post"])], check=True)
    print(f"  post {time.time() - t:.0f}s -> {out}")
    return dt


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    if not args or args[0] == "all":
        for shot in CONFIG:
            for style in "ABC":
                make(shot, style, force)
        import epic_compare
        epic_compare.run()
    elif args[0] == "compare":
        import epic_compare
        epic_compare.run()
    else:
        make(args[0], args[1], force)
