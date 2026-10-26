"""風格 A 樣張產生器：渲染（Blender 背景模式）→ 後製（epic_post.py 風格 A）→ 存檔。

用法（PowerShell，從本站根目錄）：
    python -I scripts\\blender\\epic_make.py cover            # 封面 1920x1080（另存 1280x720 縮圖）
    python -I scripts\\blender\\epic_make.py redsea_scene
    python -I scripts\\blender\\epic_make.py all [--force]
    python -I scripts\\blender\\epic_make.py list

畫格定義在 FRAMES；燈光、霧、色調在 style_a.py。輸出：lab/renders/epic/A/<畫格>.png（1280x720），
封面另存 lab/renders/cover/cover-1920.png 與 cover-1280.png。中間檔在 lab/renders/epic/_work/。
"""
import json
import os
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
WORK = os.path.join(ROOT, "lab", "renders", "epic", "_work")
OUT = os.path.join(ROOT, "lab", "renders", "epic", "A")
COVER = os.path.join(ROOT, "lab", "renders", "cover")

import style_a as S  # noqa: E402

# 畫格：script、env（相機等，場景腳本讀環境變數）、post 設定名、尺寸
FRAMES = {
    "cover": dict(script="epic_cover.py", post="cover", size=(1920, 1080), samples=48, env={}),
    "redsea_scene": dict(script="epic_redsea.py", post="redsea", size=S.SIZE, env={}),
    "tent_high": dict(script="epic_river.py", post="river", size=S.SIZE, env=dict(FRAME="tent_high")),
    "tent_descend": dict(script="epic_river.py", post="river", size=S.SIZE, env=dict(FRAME="tent_descend")),
    "tent_scene": dict(script="epic_river.py", post="river", size=S.SIZE, env=dict(FRAME="tent_scene")),
    "ford_high": dict(script="epic_river.py", post="river", size=S.SIZE, env=dict(FRAME="ford_high")),
    "ford_descend": dict(script="epic_river.py", post="river", size=S.SIZE, env=dict(FRAME="ford_descend")),
    "ford_scene": dict(script="epic_river.py", post="river", size=S.SIZE, env=dict(FRAME="ford_scene")),
    "canaan_high": dict(script="epic_canaan.py", post="canaan", size=S.SIZE, env=dict(FRAME="canaan_high")),
    "canaan_descend": dict(script="epic_canaan.py", post="canaan", size=S.SIZE, env=dict(FRAME="canaan_descend")),
    "canaan_scene": dict(script="epic_canaan.py", post="canaan", size=S.SIZE, env=dict(FRAME="canaan_scene")),
}


PAINT_ARG = None


def make(name, force=False, params=None):
    fr = FRAMES[name]
    w, h = fr["size"]
    base = os.path.join(WORK, name)
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    print(f"[{name}]")
    if force or not (os.path.exists(base + ".f32") and os.path.exists(base + "_depth.f32")):
        env = dict(os.environ)
        env.update({k: str(v) for k, v in fr["env"].items()})
        args = [BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, fr["script"]), "--", "--style", "A",
                "--w", str(w), "--h", str(h), "--samples", str(fr.get("samples", S.SAMPLES)), "--out", base]
        t = time.time()
        r = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if not os.path.exists(base + "_depth.f32"):
            print(r.stdout[-3500:], r.stderr[-1500:])
            raise SystemExit("blender failed: " + name)
        print(f"  blender {time.time() - t:.0f}s")
    post = S.post_params(fr["post"], paint=PAINT_ARG)
    if params:
        post.update(params)
    post['out_size'] = [w, h]
    out = os.path.join(OUT, f"{name}.png")
    t = time.time()
    subprocess.run([sys.executable, "-I", os.path.join(HERE, "epic_post.py"), base, "A", out, json.dumps(post)], check=True,
                   env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    print(f"  post {time.time() - t:.0f}s")
    if name == "cover":
        from PIL import Image
        os.makedirs(COVER, exist_ok=True)
        im = Image.open(out).convert("RGB")
        im.save(os.path.join(COVER, "cover-1920.png"))
        im.resize((1280, 720), Image.LANCZOS).save(os.path.join(COVER, "cover-1280.png"))
        print("  cover ->", COVER)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    for a_ in sys.argv:
        if a_.startswith("--paint="):
            PAINT_ARG = a_.split("=")[1]
    if not args or args[0] == "list":
        print("\n".join(FRAMES))
    elif args[0] == "all":
        for n in FRAMES:
            if os.path.exists(os.path.join(HERE, FRAMES[n]["script"])):
                make(n, force)
    else:
        make(args[0], force)
