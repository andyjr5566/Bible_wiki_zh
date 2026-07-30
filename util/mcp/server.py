#!/usr/bin/env python3
"""Hermes Scripture MCP server.

The server exposes the repository's existing workflow; it does not replace its
validators or grant broad filesystem access.  In particular, M3/M6 always use
``util/run_chapter_manual.py`` so invoking this MCP server never triggers a
model endpoint on the user's behalf.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # Allows repository unit tests without the MCP venv.
    MCP_IMPORT_ERROR = exc

    class FastMCP:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs):
            pass

        @staticmethod
        def tool():
            return lambda func: func

        @staticmethod
        def prompt(_name=None):
            return lambda func: func

        def run(self, **_kwargs):
            raise RuntimeError(f"無法載入 MCP 套件：{MCP_IMPORT_ERROR}")
else:
    MCP_IMPORT_ERROR = None


MCP_DIR = Path(__file__).resolve().parent
UTIL_DIR = MCP_DIR.parent
ROOT_DIR = UTIL_DIR.parent

if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

from book_paths import BOOK_NUMBERS, book_directory, canonical_book_name
from check_chapter_files import build_checks
import link_updates
import source_excerpts


mcp = FastMCP("Hermes-Scripture-MCP")

_MAX_READ_CHARS = 24_000
_DEFAULT_READ_CHARS = 12_000
_MAX_SEARCH_RESULTS = 50
_CHAPTER_ARTIFACTS = {
    "source_manifest.md",
    "link_candidates.yaml",
    "candidate_similarity.md",
    "link_plan.yaml",
    "verse_links.yaml",
    "chapter_content.yaml",
    "link_updates.yaml",
    "manual/sources.md",
    "manual/chapter_content.prompt.md",
}
_ENTRY_ARTIFACT_RE = re.compile(r"^entry_content/[^/\\]+\.yaml$")
_MANUAL_ENTRY_PROMPT_RE = re.compile(r"^manual/entry_batch_\d+\.prompt\.md$")


def _error(message: str, **details: Any) -> Dict[str, Any]:
    return {"success": False, "error": message, **details}


def _safe_limit(value: int) -> int:
    if not isinstance(value, int):
        return _DEFAULT_READ_CHARS
    return max(1, min(value, _MAX_READ_CHARS))


def _is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def _relative_to_root(path: Path) -> str:
    return path.resolve().relative_to(ROOT_DIR.resolve()).as_posix()


def _safe_relative_file(relative_path: str, allowed_root: Path, *, suffixes: tuple[str, ...]) -> Path:
    """Resolve a user-facing relative path without accepting traversal or absolute paths."""
    if not isinstance(relative_path, str) or not relative_path.strip():
        raise ValueError("路徑必須是非空相對路徑")
    relative = Path(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("不允許絕對路徑或 .. 路徑跳脫")
    resolved = (ROOT_DIR / relative).resolve()
    if resolved.suffix.lower() not in suffixes or not _is_under(resolved, allowed_root):
        raise ValueError("路徑不在允許的資料夾或副檔名不正確")
    if not resolved.is_file():
        raise FileNotFoundError(f"找不到檔案：{relative_path}")
    return resolved


def _canonical_book(book: str) -> str:
    canonical = canonical_book_name(book)
    if canonical not in BOOK_NUMBERS:
        raise ValueError(f"未知書卷：{book}")
    return canonical


def _chapter_context(book: str, chapter: int) -> tuple[str, Path, Path]:
    canonical = _canonical_book(book)
    if not isinstance(chapter, int) or chapter < 1:
        raise ValueError("chapter 必須是正整數")
    directory = book_directory(ROOT_DIR, canonical)
    return canonical, directory, directory / ".tmp" / f"第{chapter}章"


def _bounded_content(path: Path, max_characters: int) -> Dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    limit = _safe_limit(max_characters)
    return {
        "path": _relative_to_root(path),
        "content": content[:limit],
        "truncated": len(content) > limit,
        "total_characters": len(content),
    }


def _load_entry_index() -> Dict[str, Any]:
    index_path = ROOT_DIR / "util" / "output" / "link_index.json"
    if not index_path.is_file():
        raise FileNotFoundError(
            "找不到 util/output/link_index.json；請先執行 python util/build_link_index.py"
        )
    data = json.loads(index_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("link_index.json 格式無效")
    return data


def _primary_entries(index: Dict[str, Any]) -> List[Dict[str, Any]]:
    entries: Dict[str, Dict[str, Any]] = {}
    link_root = ROOT_DIR / "link_folder"
    for value in index.values():
        if not isinstance(value, dict) or "alias_of" in value:
            continue
        title = value.get("title")
        path = value.get("path")
        if not isinstance(title, str) or not isinstance(path, str):
            continue
        try:
            resolved = _safe_relative_file(path, link_root, suffixes=(".md",))
        except (ValueError, OSError):
            continue
        entry = dict(value)
        entry["path"] = _relative_to_root(resolved)
        entries[title] = entry
    return sorted(entries.values(), key=lambda item: str(item["title"]))


def _entry_for_title(index: Dict[str, Any], title: str) -> Optional[Dict[str, Any]]:
    item = index.get(title)
    if not isinstance(item, dict):
        return None
    if "alias_of" in item:
        item = index.get(item["alias_of"])
    if not isinstance(item, dict) or not item.get("path") or not item.get("title"):
        return None
    return item


def _entry_result(entry: Dict[str, Any], matched_by: str) -> Dict[str, Any]:
    return {
        "title": entry["title"],
        "type": entry.get("type"),
        "secondary_types": entry.get("secondary_types", []),
        "path": entry["path"],
        "aliases": entry.get("aliases", []),
        "matched_by": matched_by,
    }


def _manual_completion(canonical: str, chapter: int) -> List[str]:
    """Check the two omissions that manual ``check`` intentionally treats as warnings."""
    _canonical, _directory, tmp = _chapter_context(canonical, chapter)
    missing = []
    plan_path = tmp / "link_plan.yaml"
    if not plan_path.is_file():
        return ["缺 link_plan.yaml；先執行 prepare_manual_payload_prompts"]
    try:
        plan = yaml.safe_load(plan_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        return [f"link_plan.yaml 無法解析：{exc}"]
    planned = {
        str(item["name"])
        for item in plan.get("C_new_formal", [])
        if isinstance(item, dict) and item.get("name")
    }
    payload_dir = tmp / "entry_content"
    payloads = list(payload_dir.glob("*.yaml")) if payload_dir.is_dir() else []
    if len(payloads) < len(planned):
        missing.append(f"C 類條目 payload 不足：需 {len(planned)}，目前 {len(payloads)}")
    if not (tmp / "chapter_content.yaml").is_file():
        missing.append("缺 chapter_content.yaml（M6 payload）")
    return missing


def _run_manual(command: str, canonical: str, chapter: int, *options: str) -> Dict[str, Any]:
    cmd = [sys.executable, str(UTIL_DIR / "run_chapter_manual.py"), command, *options, canonical, str(chapter)]
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=90,
        )
    except subprocess.TimeoutExpired:
        return _error("manual 流程逾時（90 秒）", command=cmd)
    return {
        "success": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "command": " ".join(cmd),
    }


def _link_update_manifest(canonical: str, chapter: int) -> Path:
    _canonical, _directory, tmp = _chapter_context(canonical, chapter)
    manifest = tmp / "link_updates.yaml"
    if not manifest.is_file():
        raise FileNotFoundError(
            "找不到 link_updates.yaml；先依 raw text 填寫 B 類 summary/relation，"
            "或先執行 python util/link_updates.py prepare"
        )
    return manifest


def _update_preview(canonical: str, chapter: int) -> Dict[str, Any]:
    manifest = _link_update_manifest(canonical, chapter)
    preview = link_updates.preview_updates(manifest)
    if preview["book"] != canonical or preview["chapter"] != chapter:
        raise ValueError(
            "link_updates.yaml 的 book/chapter 與工具參數不一致；拒絕套用跨章更新"
        )
    digest = hashlib.sha256()
    digest.update(manifest.read_bytes())
    changes = []
    for operation in preview["operations"]:
        before = operation["before"]
        after = operation["after"]
        digest.update(operation["relative_path"].encode("utf-8"))
        digest.update(hashlib.sha256(before.encode("utf-8")).digest())
        digest.update(hashlib.sha256(after.encode("utf-8")).digest())
        changes.append({
            "title": operation["title"],
            "path": operation["relative_path"],
            "will_change": before != after,
        })
    return {
        "manifest": _relative_to_root(manifest),
        "book": canonical,
        "chapter": chapter,
        "preview_token": digest.hexdigest(),
        "change_count": sum(item["will_change"] for item in changes),
        "entries": changes,
    }


@mcp.tool()
def get_chapter_status(book: str, chapter: int) -> Dict[str, Any]:
    """Read-only chapter workflow status from the repository's canonical checks.

    This diagnoses missing pipeline artefacts and embeds the exact resume hint.
    It does not execute a model, render files, or alter payloads.
    """
    try:
        canonical, _directory, _tmp = _chapter_context(book, chapter)
        checks = build_checks(canonical, chapter, root=ROOT_DIR)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return _error(str(exc))
    rows = [
        {"name": name, "passed": passed, "resume_hint": "" if passed else hint}
        for name, passed, hint in checks
    ]
    return {
        "success": True,
        "book": canonical,
        "chapter": chapter,
        "passed": all(row["passed"] for row in rows),
        "checks": rows,
    }


@mcp.tool()
def search_wiki_entries(
    query: str,
    entry_type: Optional[str] = None,
    max_results: int = 20,
) -> Dict[str, Any]:
    """Search the canonical link index by title and aliases, with deterministic results.

    ``entry_type`` filters the primary type; aliases and secondary types are
    returned so an agent can make the A/B/C/D decision without inventing names.
    """
    query = query.strip()
    if not query:
        return _error("query 不可為空")
    try:
        index = _load_entry_index()
        entries = _primary_entries(index)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _error(str(exc))
    known_types = sorted({str(entry.get("type")) for entry in entries if entry.get("type")})
    if entry_type is not None and entry_type not in known_types:
        return _error("未知 entry_type", allowed_types=known_types)
    needle = query.casefold()
    matches = []
    for entry in entries:
        if entry_type and entry.get("type") != entry_type:
            continue
        title = str(entry["title"])
        aliases = [str(alias) for alias in entry.get("aliases", [])]
        if title.casefold() == needle:
            rank, matched_by = 0, "exact_title"
        elif any(alias.casefold() == needle for alias in aliases):
            rank, matched_by = 1, "exact_alias"
        elif needle in title.casefold():
            rank, matched_by = 2, "title_substring"
        elif any(needle in alias.casefold() for alias in aliases):
            rank, matched_by = 3, "alias_substring"
        else:
            continue
        matches.append((rank, title, _entry_result(entry, matched_by)))
    limit = max(1, min(max_results, _MAX_SEARCH_RESULTS))
    matches.sort(key=lambda item: (item[0], item[1]))
    return {
        "success": True,
        "query": query,
        "result_count": min(len(matches), limit),
        "truncated": len(matches) > limit,
        "results": [item[2] for item in matches[:limit]],
    }


@mcp.tool()
def read_wiki_entry(path_or_title: str, max_characters: int = _DEFAULT_READ_CHARS) -> Dict[str, Any]:
    """Read one indexed ``link_folder`` Markdown entry only.

    Arbitrary project paths, absolute paths, and ``..`` traversal are rejected.
    Use ``read_chapter_artifact`` for the explicitly allowed `.tmp` payloads.
    """
    try:
        index = _load_entry_index()
        link_root = ROOT_DIR / "link_folder"
        if "/" in path_or_title or "\\" in path_or_title or path_or_title.endswith(".md"):
            path = _safe_relative_file(path_or_title, link_root, suffixes=(".md",))
            rel = _relative_to_root(path)
            entry = next((item for item in _primary_entries(index) if item["path"] == rel), None)
            if entry is None:
                return _error("檔案不是 link_index.json 中的正式條目；請先重建索引", path=rel)
        else:
            entry = _entry_for_title(index, path_or_title.strip())
            if entry is None:
                return _error("查無此條目或 alias；請先用 search_wiki_entries 搜尋")
            path = _safe_relative_file(str(entry["path"]), link_root, suffixes=(".md",))
        result = _bounded_content(path, max_characters)
        result.update({"success": True, "title": entry["title"]})
        return result
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _error(str(exc))


@mcp.tool()
def read_chapter_artifact(
    book: str,
    chapter: int,
    artifact: str,
    max_characters: int = _DEFAULT_READ_CHARS,
) -> Dict[str, Any]:
    """Read a whitelisted `.tmp/第X章` workflow artifact, never an arbitrary file."""
    try:
        canonical, _directory, tmp = _chapter_context(book, chapter)
        normalized = artifact.replace("\\", "/")
        allowed = (
            normalized in _CHAPTER_ARTIFACTS
            or _ENTRY_ARTIFACT_RE.fullmatch(normalized)
            or _MANUAL_ENTRY_PROMPT_RE.fullmatch(normalized)
        )
        if not allowed:
            return _error("artifact 不在允許清單", allowed_artifacts=sorted(_CHAPTER_ARTIFACTS))
        relative = Path(normalized)
        if relative.is_absolute() or ".." in relative.parts:
            return _error("artifact 必須是安全的相對路徑")
        path = (tmp / relative).resolve()
        if not _is_under(path, tmp) or not path.is_file():
            return _error("找不到允許的章節產物", artifact=normalized)
        result = _bounded_content(path, max_characters)
        result.update({"success": True, "book": canonical, "chapter": chapter})
        return result
    except (OSError, ValueError) as exc:
        return _error(str(exc))


@mcp.tool()
def read_chapter_source(
    book: str,
    chapter: int,
    source: str = "scripture",
    max_characters: int = _DEFAULT_READ_CHARS,
) -> Dict[str, Any]:
    """Read local scripture or one source declared ``OK`` by this chapter's manifest.

    ``source='scripture'`` reads the local verses.  For source material, pass
    the source label returned in ``source_manifest.md``; files not declared by
    that manifest are unavailable through this MCP tool.
    """
    try:
        canonical, _directory, tmp = _chapter_context(book, chapter)
        if source.casefold() == "scripture":
            path = ROOT_DIR / "raw_scripture" / canonical / f"第{chapter}章.txt"
            if not path.is_file():
                return _error("找不到本地經文", path=_relative_to_root(path))
            result = _bounded_content(path, max_characters)
            result.update({"success": True, "source": "scripture"})
            return result
        sources = source_excerpts.parse_manifest(tmp / "source_manifest.md", ROOT_DIR)
        allowed_root = ROOT_DIR / "raw_data"
        choices = []
        for label, path in sources:
            resolved = Path(path).resolve()
            choices.append(label)
            if label.casefold() != source.casefold():
                continue
            if not _is_under(resolved, allowed_root) or not resolved.is_file():
                return _error("manifest 指向的來源檔案不在 raw_data/ 或不存在", source=label)
            result = _bounded_content(resolved, max_characters)
            result.update({"success": True, "source": label})
            return result
        return _error("source 不在本章 manifest 的 OK 清單", available_sources=choices)
    except (OSError, ValueError) as exc:
        return _error(str(exc))


@mcp.tool()
def lint_chapter_content(text: str, content_kind: str = "markdown") -> Dict[str, Any]:
    """Advisory M3/M6 format lint for supplied text; it never reads a path.

    This is not a source-faithfulness or schema gate.  Use
    ``check_manual_payloads`` after writing the YAML payloads.
    """
    if content_kind not in {"markdown", "yaml"}:
        return _error("content_kind 只能是 markdown 或 yaml")
    errors, warnings = [], []
    in_mermaid = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```mermaid"):
            in_mermaid = True
            continue
        if in_mermaid and line.strip().startswith("```"):
            in_mermaid = False
            continue
        if in_mermaid and ("[[" in line or "]]" in line):
            errors.append(f"第 {number} 行 Mermaid 圖內不可放 [[wiki-link]]")
    if in_mermaid:
        errors.append("Mermaid 程式碼區塊未關閉")
    if content_kind == "yaml":
        try:
            yaml.safe_load(text)
        except yaml.YAMLError as exc:
            errors.append(f"YAML 解析失敗：{exc}")
    sensational = ["垂涕", "魔劍", "殺成血池", "悲絕痛絕", "血肉橫飛", "超魔幻"]
    found = [word for word in sensational if word in text]
    if found:
        warnings.append("疑似戲劇化用語：" + "、".join(found))
    return {
        "success": True,
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        "advice": "通過只代表此輕量格式檢查；內容仍須逐條回到經文與有效 raw_data 複核。",
    }


@mcp.tool()
def prepare_manual_payload_prompts(
    book: str,
    chapter: int,
    confirm_stale: bool = False,
) -> Dict[str, Any]:
    """Run manual ``prompts`` for M3/M6; it never calls a model endpoint.

    When upstream edits would delete hand-written payloads, first call without
    ``confirm_stale`` to inspect the warning.  Set it to true only after that
    review, exactly matching ``run_chapter_manual.py prompts --confirm-stale``.
    """
    try:
        canonical, _directory, _tmp = _chapter_context(book, chapter)
    except ValueError as exc:
        return _error(str(exc))
    options = ("--confirm-stale",) if confirm_stale else ()
    result = _run_manual("prompts", canonical, chapter, *options)
    result.update({"book": canonical, "chapter": chapter, "zero_api": True})
    return result


@mcp.tool()
def check_manual_payloads(book: str, chapter: int) -> Dict[str, Any]:
    """Read-only M3/M6 validation using ``run_chapter_manual.py check --no-rewrite``.

    Unlike the CLI's informational check, this MCP tool reports missing C-class
    payloads or M6 payloads as incomplete rather than a successful gate.
    """
    try:
        canonical, _directory, _tmp = _chapter_context(book, chapter)
    except ValueError as exc:
        return _error(str(exc))
    result = _run_manual("check", canonical, chapter, "--no-rewrite")
    incomplete = _manual_completion(canonical, chapter)
    result.update({
        "book": canonical,
        "chapter": chapter,
        "complete": not incomplete,
        "incomplete_reasons": incomplete,
        "passed": result["success"] and not incomplete,
        "read_only": True,
    })
    return result


@mcp.tool()
def render_manual_chapter(book: str, chapter: int, keep_chapter: bool = False) -> Dict[str, Any]:
    """Render M3/M6 through manual ``run`` only after the read-only payload gate passes."""
    preflight = check_manual_payloads(book, chapter)
    if not preflight.get("passed"):
        return _error(
            "manual payload gate 未通過，拒絕 render；先依 check_manual_payloads 修正",
            preflight=preflight,
        )
    canonical = preflight["book"]
    options = ("--keep-chapter",) if keep_chapter else ()
    result = _run_manual("run", canonical, chapter, *options)
    result.update({"book": canonical, "chapter": chapter, "zero_api": True})
    return result


@mcp.tool()
def preview_chapter_link_updates(book: str, chapter: int) -> Dict[str, Any]:
    """Validate and preview B-class accumulation updates without modifying files.

    Review ``link_updates.yaml`` against the chapter sources first.  The returned
    token is required by ``apply_chapter_link_updates`` and becomes invalid if
    either the manifest or a target entry changes.
    """
    try:
        canonical = _canonical_book(book)
        preview = _update_preview(canonical, chapter)
        return {"success": True, **preview}
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return _error(str(exc))


@mcp.tool()
def apply_chapter_link_updates(book: str, chapter: int, preview_token: str) -> Dict[str, Any]:
    """Apply the exact B-class preview after token confirmation.

    The underlying update code prevalidates all targets, stages each changed file
    before replacement, and attempts rollback on an operating-system failure.
    """
    try:
        canonical = _canonical_book(book)
        preview = _update_preview(canonical, chapter)
        if preview_token != preview["preview_token"]:
            return _error(
                "preview_token 不符或已過期；請重新 preview、核對內容後再套用",
                current_preview_token=preview["preview_token"],
            )
        logs: List[str] = []
        changed = link_updates.apply_updates(
            ROOT_DIR / preview["manifest"], dry_run=False, reporter=logs.append
        )
        return {
            "success": True,
            "book": canonical,
            "chapter": chapter,
            "changed_files": changed,
            "logs": logs,
            "next_step": "重跑 preview_chapter_link_updates；change_count 必須為 0，之後再做收尾驗證。",
        }
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return _error(str(exc))


@mcp.prompt("biblical_chapter_sop")
def biblical_chapter_sop(book: str = "民數記", chapter: int = 22) -> str:
    """MCP-assisted new-chapter SOP; the repository prompt remains authoritative."""
    return f"""# Hermes Scripture：{book} 第 {chapter} 章（MCP 輔助）

以 `agent_start_prompt.md` 為完整且優先的規格。本 MCP 只降低查找、手寫 M3/M6 驗證與 B 類套用的操作風險，不能取代四來源內容複核或收尾閘門。

1. 先呼叫 `get_chapter_status`；依回傳的 resume hint 完成來源、候選與語義近鄰步驟。
2. 用 `search_wiki_entries` 查既有 title／alias；需要原文時用 `read_wiki_entry`。不可自創名稱、alias 或音譯。
3. M3/M6 **只走人工零 API 流程**：`prepare_manual_payload_prompts` → 讀 manifest 指定的完整來源（`read_chapter_source` 可安全讀取）→ 手寫 entry payload（M3）→ 再 prepare 取得更新後 M6 prompt → 手寫 `chapter_content.yaml` → `check_manual_payloads` → `render_manual_chapter`。不要用 `run_chapter.py` 生成 M3/M6。
4. `lint_chapter_content` 只是格式提示；M3/M6 的真閘門是 `check_manual_payloads`，內容忠實性仍須人工逐條對四來源。
5. B 類累積必須先核對 `link_updates.yaml` 與來源，再 `preview_chapter_link_updates`，使用回傳 token 才可 `apply_chapter_link_updates`；套用後重跑 preview 必須是 0 變更。
6. 最後仍照 `agent_start_prompt.md` 執行 build index／embedding、驗證、稽核與 `check_chapter_files.py`，全部 PASS 才提交。
"""


@mcp.prompt("biblical_maintenance_sop")
def biblical_maintenance_sop(book: str = "民數記", chapter: int = 22) -> str:
    """MCP-assisted maintenance SOP with the same zero-API M3/M6 discipline."""
    return f"""# Hermes Scripture 維護：{book} 第 {chapter} 章（MCP 輔助）

以 `agent_maintenance_prompt.md` 為完整且優先的規格。先讀四來源並逐條勘誤；結構通過不等於內容正確。

- 先用 `get_chapter_status` 看目前管線狀態，用 `read_chapter_artifact` 讀受限的 `.tmp` payload，用 `search_wiki_entries`／`read_wiki_entry` 核對既有條目與 aliases。
- 修改 M3／M6 時固定走零 API：手寫 yaml → `check_manual_payloads`（唯讀，不會重寫 alias）→ `render_manual_chapter`。改 entry payload 且本章整理已同步時，才帶 `keep_chapter=true`。
- 修改 candidates 前先呼叫 `prepare_manual_payload_prompts(confirm_stale=false)` 看作廢清單；確認手寫 payload 可刪後才設為 true，然後補寫 payload、check、render。
- B 類累積只能走 `preview_chapter_link_updates` → 人工核對 source → 使用 token 的 `apply_chapter_link_updates` → 再 preview 必須 0 變更。
- 此 MCP 不授權跳過 `agent_maintenance_prompt.md` 的內容勘誤、link index／embedding 同步、驗證與稽核。
"""


def main() -> None:
    if MCP_IMPORT_ERROR is not None:
        sys.stderr.write(f"❌ 無法啟動 MCP server：{MCP_IMPORT_ERROR}\n")
        raise SystemExit(1)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
