"""A+C 強度比較圖：同一個紅海畫格，A 原版與 A+C 輕／中／強，並排。輸出 lab/renders/style/redsea-AC-compare.png。"""
import json, os, subprocess, sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
import style_a as S
from PIL import Image, ImageDraw, ImageFont

shot = sys.argv[1] if len(sys.argv) > 1 else "redsea_scene"
post_key = {"redsea_scene": "redsea", "cover": "cover"}.get(shot, "redsea")
base = os.path.join(ROOT, "lab", "renders", "epic", "_work", shot)
outdir = os.path.join(ROOT, "lab", "renders", "style")
os.makedirs(outdir, exist_ok=True)
panels = []
for label, choice in (("A 原版（無繪畫層）", None), ("A+C 輕（amount 0.35）", "light"), ("A+C 中（amount 0.60）", "medium"), ("A+C 強（amount 0.85）", "strong")):
    p = S.post_params(post_key, paint="" if choice is None else choice) if choice else dict(S.POST[post_key])
    out = os.path.join(outdir, f"{shot.split('_')[0]}-AC-{choice or 'none'}.png")
    subprocess.run([sys.executable, "-I", os.path.join(HERE, "epic_post.py"), base, "A", out, json.dumps(p)], check=True, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    panels.append((label, Image.open(out).convert("RGB")))
def font(sz):
    for f in ("msjh.ttc", "msjhbd.ttc"):
        pth = os.path.join(r"C:\Windows\Fonts", f)
        if os.path.exists(pth):
            return ImageFont.truetype(pth, sz)
    return ImageFont.load_default()
tw, th, pad, head = 640, 360, 8, 50
canvas = Image.new("RGB", (tw * 2 + pad * 3, (th + head) * 2 + pad * 3), (18, 18, 20))
d = ImageDraw.Draw(canvas)
ft = font(26)
for i, (label, im) in enumerate(panels):
    x = pad + (i % 2) * (tw + pad)
    y = pad + (i // 2) * (th + head + pad)
    d.text((x + 4, y + 8), label, font=ft, fill=(240, 236, 226))
    canvas.paste(im.resize((tw, th), Image.LANCZOS), (x, y + head))
path = os.path.join(outdir, f"{shot.split('_')[0]}-AC-compare.png")
canvas.save(path)
print("比較圖", path)
