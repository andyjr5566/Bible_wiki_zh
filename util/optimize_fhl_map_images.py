#!/usr/bin/env python3
"""以 JPEG 壓縮 FHL 地圖；只有達到縮減門檻時才採用。"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "appendix" / "fhl_maps"
IMAGES_DIR = DATA_DIR / "images"
METADATA_PATH = DATA_DIR / "metadata.json"
MANIFEST_PATH = DATA_DIR / "image_optimization.json"


def probe_image(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,pix_fmt",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode:
        raise RuntimeError(f"無法檢查圖片 {path}: {result.stderr.strip()}")
    streams = json.loads(result.stdout).get("streams", [])
    if len(streams) != 1:
        raise RuntimeError(f"圖片串流數異常：{path}")
    return streams[0]


def should_adopt(original_size: int, jpeg_size: int, minimum_reduction: float) -> bool:
    return jpeg_size <= original_size * (1 - minimum_reduction)


def encode_jpeg(source: Path, destination: Path, quality: int):
    temporary = destination.with_suffix(".tmp.jpg")
    temporary.unlink(missing_ok=True)
    result = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(source),
            "-frames:v",
            "1",
            "-pix_fmt",
            "yuvj444p",
            "-q:v",
            str(quality),
            str(temporary),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(f"JPEG 編碼失敗 {source}: {result.stderr.strip()}")
    source_info = probe_image(source)
    jpeg_info = probe_image(temporary)
    if (
        source_info["width"],
        source_info["height"],
    ) != (
        jpeg_info["width"],
        jpeg_info["height"],
    ):
        temporary.unlink(missing_ok=True)
        raise RuntimeError(f"轉檔後尺寸改變：{source}")
    if jpeg_info.get("pix_fmt") != "yuvj444p":
        temporary.unlink(missing_ok=True)
        raise RuntimeError(
            f"JPEG 並非 4:4:4 色度取樣：{source} ({jpeg_info.get('pix_fmt')})"
        )
    temporary.replace(destination)


def load_manifest() -> dict[str, dict]:
    if not MANIFEST_PATH.exists():
        return {}
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {item["gid"]: item for item in payload.get("images", [])}


def write_manifest(entries: dict[str, dict], quality: int, minimum_reduction: float):
    payload = {
        "encoder": "ffmpeg",
        "jpeg_quality": quality,
        "pixel_format": "yuvj444p",
        "minimum_reduction_pct": round(minimum_reduction * 100, 2),
        "images": [entries[gid] for gid in sorted(entries)],
    }
    MANIFEST_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gid-from", default="001", help="起始 gid（含）")
    parser.add_argument("--gid-to", default="999", help="結束 gid（含）")
    parser.add_argument("--quality", type=int, default=8, help="ffmpeg -q:v，越低品質越高")
    parser.add_argument("--workers", type=int, default=4, help="同時執行的轉檔數")
    parser.add_argument(
        "--min-reduction",
        type=float,
        default=10.0,
        help="採用 JPEG 所需的最小縮減百分比",
    )
    args = parser.parse_args()

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print("找不到 ffmpeg 或 ffprobe。", file=sys.stderr)
        return 2
    if not 2 <= args.quality <= 31:
        parser.error("--quality 必須介於 2 與 31")
    if not 1 <= args.workers <= 8:
        parser.error("--workers 必須介於 1 與 8")
    if not 0 <= args.min_reduction < 100:
        parser.error("--min-reduction 必須介於 0 與 100")

    records = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    selected = [
        record
        for record in records
        if args.gid_from <= record["gid"] <= args.gid_to
    ]
    entries = load_manifest()
    adopted = 0
    original_total = 0
    selected_total = 0
    minimum_reduction = args.min_reduction / 100

    def optimize_one(record):
        gid = record["gid"]
        source_name = Path(record["local_image"].replace("\\", "/")).name
        source = IMAGES_DIR / source_name
        if not source.exists():
            existing = entries.get(gid)
            if existing and (IMAGES_DIR / existing["chosen_image"]).exists():
                return existing, 0, 0, False, f"{gid} 已採用 {existing['chosen_image']}"
            raise FileNotFoundError(f"找不到原始圖片：{source}")

        destination = IMAGES_DIR / f"{source.stem}.jpg"
        encode_jpeg(source, destination, args.quality)
        original_size = source.stat().st_size
        jpeg_size = destination.stat().st_size
        use_jpeg = should_adopt(original_size, jpeg_size, minimum_reduction)
        if use_jpeg:
            chosen = destination.name
            selected_size = jpeg_size
            image_format = "jpeg"
            is_adopted = True
        else:
            destination.unlink(missing_ok=True)
            chosen = source.name
            selected_size = original_size
            image_format = "gif"
            is_adopted = False

        reduction = (1 - selected_size / original_size) * 100
        entry = {
            "gid": gid,
            "source_image": source.name,
            "chosen_image": chosen,
            "format": image_format,
            "original_bytes": original_size,
            "chosen_bytes": selected_size,
            "reduction_pct": round(reduction, 2),
        }
        message = (
            f"{gid} {image_format.upper()} "
            f"{original_size / 1024:.1f}→{selected_size / 1024:.1f} KB "
            f"(-{reduction:.1f}%)"
        )
        return entry, original_size, selected_size, is_adopted, message

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        results = executor.map(optimize_one, selected)
        for index, result in enumerate(results, 1):
            entry, original_size, selected_size, is_adopted, message = result
            entries[entry["gid"]] = entry
            original_total += original_size
            selected_total += selected_size
            adopted += int(is_adopted)
            print(f"[{index}/{len(selected)}] {message}")

    write_manifest(entries, args.quality, minimum_reduction)
    reduction = (
        (1 - selected_total / original_total) * 100 if original_total else 0
    )
    print(
        f"本批完成 {len(selected)} 張，採用 JPEG {adopted} 張，"
        f"容量縮減 {reduction:.1f}%。"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
