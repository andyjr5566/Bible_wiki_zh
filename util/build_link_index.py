#!/usr/bin/env python3
"""建立並驗證 link_folder 全域索引。"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

import yaml

UTIL_DIR = Path(__file__).resolve().parent
ROOT = UTIL_DIR.parent
LINK_FOLDER = ROOT / "link_folder"
OUTPUT_DIR = UTIL_DIR / "output"
INDEX_FILE = OUTPUT_DIR / "link_index.json"
RESOLUTION_FILE = ROOT / "_config" / "link_conflict_resolutions.yaml"
EXCLUDE_PARTS = {"_index", "_管理", "_待分類", "_template"}


def normalize_name(value):
    """只正規化 Unicode 與空白，不刪除具有語義的括號內容。"""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(value))).strip()


def extract_frontmatter(text):
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    data = yaml.safe_load(match.group(1))
    return data if isinstance(data, dict) else {}


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def collect_entries(link_folder=LINK_FOLDER, root=ROOT):
    entries = []
    errors = []
    for md in sorted(link_folder.rglob("*.md")):
        if EXCLUDE_PARTS & set(md.parts):
            continue
        try:
            fm = extract_frontmatter(md.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            errors.append(f"{md}: 無法解析：{exc}")
            continue

        category = md.parent.name
        entry_type = fm.get("type", category)
        aliases = [normalize_name(x) for x in _as_list(fm.get("aliases")) if str(x).strip()]
        secondary = [
            normalize_name(x) for x in _as_list(fm.get("secondary_types")) if str(x).strip()
        ]
        title = md.stem
        if entry_type != category:
            errors.append(f"{md}: type={entry_type} 與資料夾分類 {category} 不一致")
        if len(aliases) != len(set(aliases)):
            errors.append(f"{md}: aliases 內有重複值")
        entries.append({
            "path": str(md.relative_to(root)).replace("\\", "/"),
            "type": entry_type,
            "secondary_types": secondary,
            "title": title,
            "status": fm.get("status", "candidate"),
            "aliases": aliases,
        })
    return entries, errors


def load_resolutions(path=RESOLUTION_FILE):
    if not path.exists():
        return {"titles": {}, "aliases": {}}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {
        "titles": data.get("titles", {}),
        "aliases": data.get("aliases", {}),
    }


def make_index(entries, resolutions=None):
    """建立索引；名稱歧義一律回報，不能由掃描順序決定勝負。"""
    resolutions = resolutions or {"titles": {}, "aliases": {}}
    index = {}
    owners = {}
    errors = []

    for entry in entries:
        title = entry["title"]
        key = normalize_name(title)
        if key in owners:
            chosen = resolutions["titles"].get(title)
            paths = {owners[key], entry["path"]}
            if chosen not in paths:
                errors.append(f"重複條目名稱：{title} → {owners[key]} / {entry['path']}")
                continue
            if entry["path"] == chosen:
                index[title] = entry
                owners[key] = entry["path"]
            continue
        owners[key] = entry["path"]
        index[title] = entry

    alias_owners = {}
    normalized_titles = {normalize_name(e["title"]): e["title"] for e in entries}
    for entry in entries:
        for alias in entry["aliases"]:
            normalized = normalize_name(alias)
            resolved_target = resolutions["aliases"].get(alias)
            if normalized in normalized_titles and normalized_titles[normalized] != entry["title"]:
                if resolved_target:
                    continue
                errors.append(
                    f"alias 與正式名稱衝突：{alias} → {entry['title']} / "
                    f"{normalized_titles[normalized]}"
                )
                continue
            previous = alias_owners.get(normalized)
            if previous and previous != entry["title"]:
                if resolved_target in {previous, entry["title"]}:
                    alias_owners[normalized] = resolved_target
                    index[alias] = {"alias_of": resolved_target}
                    continue
                errors.append(f"alias 多重指向：{alias} → {previous} / {entry['title']}")
                continue
            alias_owners[normalized] = entry["title"]
            if alias not in index:
                index[alias] = {"alias_of": entry["title"]}

    # secondary_types 是分類資訊，絕不可成為 alias。
    return index, errors


def build_index(link_folder=LINK_FOLDER, index_file=INDEX_FILE, root=ROOT, check=False):
    entries, errors = collect_entries(link_folder, root)
    # 舊式 type 值先作相容性警告；新檔由 validator 嚴格阻擋。
    type_errors = [e for e in errors if "與資料夾分類" in e]
    errors = [e for e in errors if e not in type_errors]
    for warning in type_errors:
        print(f"⚠️ {warning}")
    index, index_errors = make_index(entries, load_resolutions())
    errors.extend(index_errors)
    if errors:
        for error in errors:
            print(f"❌ {error}")
        return False

    rendered = json.dumps(index, ensure_ascii=False, indent=2) + "\n"
    if check:
        if not index_file.exists() or index_file.read_text(encoding="utf-8") != rendered:
            print(f"❌ link index 不是最新：{index_file}")
            return False
        print(f"✅ link index 已是最新：{index_file}")
    else:
        index_file.parent.mkdir(parents=True, exist_ok=True)
        index_file.write_text(rendered, encoding="utf-8")
        print(f"✅ link index 已建立：{index_file}")

    formal = sum(e["status"] == "formal" for e in entries)
    candidate = sum(e["status"] == "candidate" for e in entries)
    aliases = sum(1 for value in index.values() if "alias_of" in value)
    print(f"   共 {len(entries)} 個條目、{aliases} 個 alias")
    print(f"   ├─ 正式條目：{formal}")
    print(f"   └─ 候選條目：{candidate}")
    return True


def main():
    # 輸出含中文與 emoji；Windows cp1252 stdout 直接 print 會 UnicodeEncodeError，
    # 須在 argparse（--help 也會印字）之前重設編碼。
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="只確認索引可重現且為最新")
    args = parser.parse_args()
    sys.exit(0 if build_index(check=args.check) else 1)


if __name__ == "__main__":
    main()
