from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / ".tmp-shots/shechem-env"
STATES = [
    ("02 聚集", "02-gather-{device}-32"),
    ("05 女兒提問", "05-family-1-{device}-25"),
    ("05 爺爺回答", "05-family-1-{device}-80"),
    ("15 至於我和我家", "15-my-house-{device}-32"),
    ("18 不能事奉", "18-cannot-{device}-32"),
    ("24 立約", "24-covenant-{device}-32"),
    ("26 躺石", "26-raise-{device}-down"),
    ("26 立石", "26-raise-{device}-up"),
    ("28 散去32%", "28-dismiss-{device}-32"),
    ("28 散去起點", "28-dismiss-{device}-start"),
    ("28 散去60%", "28-dismiss-{device}-departing"),
    ("28 約書亞獨行", "28-dismiss-{device}-joshua"),
    ("28 約書亞末段", "28-dismiss-{device}-last"),
    ("31 白天", "31-elders-{device}-day"),
    ("31 夜間", "31-elders-{device}-night"),
    ("36 終幕", "36-epilogue-stone-{device}-32"),
    ("約旦河岸", "jordan-jericho-{device}-shoreline"),
]


def main():
    metrics = {}
    for device in ('desktop', 'mobile'):
        report = json.loads((SHOTS / f'report-{device}.json').read_text(encoding='utf-8'))
        metrics.update({item['name']:item.get('pixels', {}) for item in report['samples']})
    cell_w, image_w, image_h = 800, 384, 230
    label_h, gap, cols = 36, 32, 3
    rows = (len(STATES) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell_w + gap, rows * (image_h + label_h + gap) + gap), "#171a1e")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", 19)
    except OSError:
        font = ImageFont.load_default()

    for index, (label, stem) in enumerate(STATES):
        col, row = index % cols, index // cols
        x0 = gap + col * cell_w
        y0 = gap + row * (image_h + label_h + gap)
        draw.text((x0, y0), label, fill="#f2e7d1", font=font)
        for offset, device in enumerate(("desktop", "mobile")):
            full_stem = stem.replace("{device}", device)
            path = SHOTS / (full_stem + ".png")
            if not path.is_file():
                continue
            image = Image.open(path).convert("RGB")
            image.thumbnail((image_w, image_h), Image.Resampling.LANCZOS)
            x = x0 + offset * (image_w + 8) + (image_w - image.width) // 2
            y = y0 + label_h + (image_h - image.height) // 2
            sheet.paste(image, (x, y))
            measurement = metrics.get(full_stem, {})
            device_name = '桌機' if device == 'desktop' else '手機橫擺'
            caption = f"{device_name}  L*={measurement.get('meanL', '?')}  人物={measurement.get('detectedFigures', '?')}"
            draw.text((x, y0 + label_h + image_h + 2), caption, fill="#d5c5a8", font=font)

    target = SHOTS / "shechem-env-contact.png"
    sheet.save(target, optimize=True)
    printable_target = str(target).encode("ascii", "backslashreplace").decode("ascii")
    print(printable_target)


if __name__ == "__main__":
    main()
