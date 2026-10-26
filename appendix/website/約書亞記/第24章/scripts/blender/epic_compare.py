"""把三種風格並排成比較圖，上方標 A／B／C（用 C:\\Windows\\Fonts 的中文字型）。"""
import os
import sys as _sys
try:
    _sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "lab", "renders", "style")
LABELS = {"A": "A  史詩剪影", "B": "B  寫實人物", "C": "C  繪畫風"}


def font(size):
    for f in ("msjh.ttc", "msjhbd.ttc", "mingliu.ttc", "kaiu.ttf"):
        p = os.path.join(r"C:\Windows\Fonts", f)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def run():
    for shot in ("cover", "redsea"):
        ims = []
        for s in "ABC":
            p = os.path.join(OUT, f"{shot}-{s}.png")
            if not os.path.exists(p):
                print("缺", p)
                return
            ims.append(Image.open(p).convert("RGB"))
        tw, th = 640, 360
        pad, head = 8, 54
        canvas = Image.new("RGB", (tw * 3 + pad * 4, th + head + pad * 2), (18, 18, 20))
        d = ImageDraw.Draw(canvas)
        ft = font(30)
        for i, (s, im) in enumerate(zip("ABC", ims)):
            x = pad + i * (tw + pad)
            canvas.paste(im.resize((tw, th), Image.LANCZOS), (x, head + pad))
            d.text((x + 6, 8), LABELS[s], font=ft, fill=(240, 236, 226))
        path = os.path.join(OUT, f"{shot}-compare.png")
        canvas.save(path)
        print("比較圖", path)


if __name__ == "__main__":
    run()
