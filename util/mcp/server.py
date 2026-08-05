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
import urllib.parse
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

# --- lint_chapter_content rules -------------------------------------------------
# Each rule below was measured against the whole corpus (2,694 rendered md files)
# before being promoted to an error: mechanically decidable rules with zero false
# positives become errors, heuristics stay warnings.
_ALIAS_LINK_RE = re.compile(r"\[\[[^\]\[|]+\|[^\]\[|]+\]\]")
_EMBED_RE = re.compile(r"!\[\[")
_HASHTAG_RE = re.compile(r"(?:(?<=\s)|^)#[^\s#\[\]()（）,，。、]{1,30}")
_REFERENCE_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s*參考(?:資料|書目)\s*$")
_HTML_TAG_RE = re.compile(
    r"</?(?:div|span|br|img|table|tr|td|th|p|b|i|u|font|center|hr)\b[^>]*>", re.I
)
_PROCESS_NOTE_RE = re.compile(r"舊版|本次維護|先前版本|待確認事項|本次補上|應並陳")
_SELF_WRAPPED_NODE_RE = re.compile(r"^\s*-\s*\[\[.+\]\]\s*$")
_MERMAID_OPEN_RE = re.compile(r"^\s*```\s*mermaid\b")
_FENCE_RE = re.compile(r"^\s*```")
_MERMAID_BARE_LABEL_RE = re.compile(
    r"[A-Za-z_][A-Za-z0-9_]*\s*[\[(]\s*(?!\")[^\"\]\)]*[　-鿿][^\"\]\)]*[\])]"
)

# --- scan_unsourced_tokens patterns ---------------------------------------------
_HEBREW_RUN_RE = re.compile(r"[֐-׿]+")
_NIQQUD_RE = re.compile(r"[֑-ׇ]")
_PAREN_LATIN_RE = re.compile(r"[（(]\s*([A-Za-z][A-Za-z'’\-./ ]{1,34})\s*[)）]")
_ITALIC_LATIN_RE = re.compile(r"\*([A-Za-z][A-Za-z'’\-]{2,24})\*")
# Source labels and translation sigla are not transliterations.
_TRANSLITERATION_IGNORE = {
    "CT", "GT", "KC", "BH", "BibleHub", "BibleHub Study", "KingComments",
    "ESV", "KJV", "NIV", "NASB", "NKJV", "RSV", "ASV", "LXX", "MT",
}
# Frequent simplified-only characters; the corpus is Traditional Chinese throughout.
_SIMPLIFIED_CHARS = set(
    "贯东车马门问间见觉学国图书写与来对时机样条种类经过还这发现产业内长关无爱应变风飞"
    "离归乡个们么为没说话让给头买卖乐会体点热当权义军师杀击斗农岁职员团结灵进电记讲论"
    "证据历称举义乱亲价众优伟传伤伦优侧俭债倾偿储儿"
)


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


def _run_util_command(script: str, *args: str, timeout: int = 300) -> Dict[str, Any]:
    """Run one existing util CLI without exposing its stdout to MCP stdio."""
    script_path = UTIL_DIR / script
    if not script_path.is_file():
        return _error(f"找不到 util 程式：{script}")
    cmd = [sys.executable, str(script_path), *(str(arg) for arg in args)]
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=max(1, min(int(timeout), 900)),
        )
    except subprocess.TimeoutExpired:
        return _error(
            f"{script} 執行逾時（{timeout} 秒）",
            command=" ".join(cmd),
        )
    except OSError as exc:
        return _error(f"無法執行 {script}：{exc}", command=" ".join(cmd))
    return {
        "success": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip()[-30_000:],
        "stderr": proc.stderr.strip()[-10_000:],
        "command": " ".join(cmd),
    }


def _safe_subdir(relative_path: str, allowed_root: Path) -> Path:
    """Resolve a user-provided directory while keeping it below ``allowed_root``."""
    if not isinstance(relative_path, str) or not relative_path.strip():
        raise ValueError("資料夾路徑不可為空")
    relative = Path(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("不允許絕對路徑或 .. 路徑跳脫")
    resolved = (ROOT_DIR / relative).resolve()
    if not _is_under(resolved, allowed_root):
        raise ValueError(f"資料夾必須位於 {_relative_to_root(allowed_root)} 之下")
    return resolved


def _safe_repo_path(raw_path: str, *, must_exist: bool = False) -> Path:
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise ValueError("路徑不可為空")
    path = Path(raw_path)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("不允許絕對路徑或 .. 路徑跳脫")
    resolved = (ROOT_DIR / path).resolve()
    if not _is_under(resolved, ROOT_DIR):
        raise ValueError("路徑不可超出專案根目錄")
    if must_exist and not resolved.exists():
        raise FileNotFoundError(f"找不到檔案或資料夾：{raw_path}")
    return resolved


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
def crawl_bible_source(
    url: str,
    output_filename: str,
    output_path: str = "raw_data",
    overwrite: bool = False,
    timeout: int = 30,
) -> Dict[str, Any]:
    """Fetch one explicit source URL into a safe ``raw_data`` subdirectory.

    This is the MCP equivalent of ``crawl_bible_text.py URL --output_path
    raw_data --output_filename ...``.  It never crawls a site broadly and does
    not overwrite an existing file unless ``overwrite`` is explicitly true.
    """
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("url 必須是完整的 http(s) URL")
        if not isinstance(output_filename, str) or not output_filename.strip():
            raise ValueError("output_filename 不可為空")
        filename = Path(output_filename)
        if filename.name != output_filename or filename.name in {"", ".", ".."}:
            raise ValueError("output_filename 必須是單一檔名，不可包含路徑")
        if filename.suffix.lower() != ".txt":
            filename = filename.with_name(filename.name + ".txt")
        output_dir = _safe_subdir(output_path, ROOT_DIR / "raw_data")
        target = output_dir / filename.name
        if target.exists() and not overwrite:
            return _error(
                f"輸出檔已存在：{_relative_to_root(target)}；需要 overwrite=true 才會覆寫",
                path=_relative_to_root(target),
            )
        args = [url, "--output_path", output_path, "--output_filename", filename.name]
        if overwrite:
            args.append("--overwrite")
        result = _run_util_command(
            "crawl_bible_text.py", *args, timeout=max(10, min(int(timeout), 180))
        )
        result.update({"url": url, "path": _relative_to_root(target)})
        return result
    except (TypeError, ValueError, OSError) as exc:
        return _error(str(exc))


@mcp.tool()
def build_source_manifest(book: str, chapter: int, check_only: bool = False) -> Dict[str, Any]:
    """Generate or validate the canonical four-source ``source_manifest.md``."""
    try:
        canonical, _directory, tmp = _chapter_context(book, chapter)
        args = [canonical, str(chapter)]
        if check_only:
            args.append("--check")
        result = _run_util_command("build_source_manifest.py", *args)
        result.update({
            "book": canonical,
            "chapter": chapter,
            "manifest": _relative_to_root(tmp / "source_manifest.md"),
            "check_only": check_only,
        })
        return result
    except (TypeError, ValueError, OSError) as exc:
        return _error(str(exc))


@mcp.tool()
def build_candidate_similarity(book: str, chapter: int, top: int = 3) -> Dict[str, Any]:
    """Run ``semantic_lookup.py --candidates`` and write the human-review report."""
    try:
        canonical, _directory, tmp = _chapter_context(book, chapter)
        bounded_top = max(3, min(int(top), 10))
        result = _run_util_command(
            "semantic_lookup.py", "--candidates", canonical, str(chapter),
            "--top", str(bounded_top), timeout=300,
        )
        result.update({
            "book": canonical,
            "chapter": chapter,
            "report": _relative_to_root(tmp / "candidate_similarity.md"),
            "top": bounded_top,
        })
        return result
    except (TypeError, ValueError, OSError) as exc:
        return _error(str(exc))


@mcp.tool()
def model_client(
    action: str,
    endpoint: Optional[str] = None,
    task: Optional[str] = None,
    confirm: bool = False,
) -> Dict[str, Any]:
    """List, test, or explicitly select a configured model endpoint.

    ``use`` changes ``_config/model_endpoints.yaml`` and therefore requires
    ``confirm=true``.  This tool never runs generation; ``test`` only performs
    the endpoint smoke test implemented by ``util/model_client.py``.
    """
    if action not in {"list", "test", "use"}:
        return _error("action 必須是 list、test 或 use")
    if action == "use" and not confirm:
        return _error("切換 active endpoint 會寫入設定，請明確傳入 confirm=true")
    if action == "use" and not endpoint:
        return _error("action=use 必須提供 endpoint")
    if action == "list" and (endpoint or task):
        return _error("action=list 不接受 endpoint 或 task")
    if action == "use" and task:
        return _error("action=use 不接受 task")
    args = [action]
    if endpoint:
        args.append(endpoint)
    if task:
        args.extend(["--task", task])
    result = _run_util_command("model_client.py", *args, timeout=120)
    result.update({"action": action, "endpoint": endpoint, "task": task})
    return result


@mcp.tool()
def sync_link_index(check_only: bool = False) -> Dict[str, Any]:
    """Build or reproducibility-check the canonical link index."""
    args = ["--check"] if check_only else []
    return _run_util_command("build_link_index.py", *args)


@mcp.tool()
def check_existing_links(book: str, chapter: int, missing_only: bool = True) -> Dict[str, Any]:
    """Check chapter links against existing entries and optional chapter data."""
    try:
        canonical, directory, _tmp = _chapter_context(book, chapter)
        chapter_file = directory / f"第{chapter}章.md"
        if not _is_under(chapter_file, ROOT_DIR):
            raise ValueError("章節檔案不可超出專案根目錄")
        args = [_relative_to_root(chapter_file)]
        if missing_only:
            args.append("--missing")
        result = _run_util_command("check_existing_links.py", *args)
        result.update({"book": canonical, "chapter": chapter, "missing_only": missing_only})
        return result
    except (TypeError, ValueError, OSError) as exc:
        return _error(str(exc))


@mcp.tool()
def sync_embedding_index(
    rebuild: bool = False,
    check_only: bool = False,
    status_only: bool = False,
) -> Dict[str, Any]:
    """Incrementally build, rebuild, check, or inspect the embedding index."""
    if sum(bool(value) for value in (rebuild, check_only, status_only)) > 1:
        return _error("rebuild、check_only、status_only 只能選一個")
    args: List[str] = []
    if rebuild:
        args.append("--rebuild")
    elif check_only:
        args.append("--check")
    elif status_only:
        args.append("--status")
    return _run_util_command("build_embedding_index.py", *args, timeout=600)


@mcp.tool()
def build_appendix_links(check_only: bool = False) -> Dict[str, Any]:
    """Synchronize rendered appendix blocks, or check whether they are stale."""
    args = ["--check"] if check_only else []
    return _run_util_command("build_appendix_links.py", *args, timeout=300)


@mcp.tool()
def validate_knowledge_base(base: Optional[str] = None, report: Optional[str] = None) -> Dict[str, Any]:
    """Run the structural knowledge-base validator and optionally write its JSON report."""
    args: List[str] = []
    if base:
        if any(char in base for char in "\r\n"):
            return _error("base 不可包含換行")
        args.append(f"--base={base}")
    if report:
        report_path = Path(report)
        if report_path.is_absolute() or ".." in report_path.parts or report_path.name != report:
            return _error("report 只能是 util/output 下的單一檔名")
        args.append(f"--report={report}")
    return _run_util_command("validate_knowledge_base.py", *args, timeout=300)


@mcp.tool()
def check_link_quality(book: Optional[str] = None) -> Dict[str, Any]:
    """Run the link-quality report for the whole vault or one canonical book."""
    try:
        args = [] if book is None else [_canonical_book(book)]
    except ValueError as exc:
        return _error(str(exc))
    return _run_util_command("link_quality_check.py", *args, timeout=300)


@mcp.tool()
def verify_links(book: Optional[str] = None) -> Dict[str, Any]:
    """Run the offline broken-link and scripture-reference verifier."""
    try:
        args = [] if book is None else [_canonical_book(book)]
    except ValueError as exc:
        return _error(str(exc))
    return _run_util_command("verify_links.py", *args, timeout=300)


@mcp.tool()
def audit_knowledge_base(
    mode: str = "check_due",
    book: Optional[str] = None,
    checkpoint: int = 10,
    confirm: bool = False,
) -> Dict[str, Any]:
    """Check audit cadence, or explicitly generate a book/full-vault audit report."""
    if mode not in {"check_due", "book", "all"}:
        return _error("mode 必須是 check_due、book 或 all")
    if mode == "check_due":
        if book is not None:
            return _error("mode=check_due 不接受 book")
        args = ["--check-due"]
    elif not confirm:
        return _error("產生稽核報告會寫入檔案，請明確傳入 confirm=true")
    elif mode == "book":
        if not book:
            return _error("mode=book 必須提供 book")
        try:
            args = ["--book", _canonical_book(book)]
        except ValueError as exc:
            return _error(str(exc))
    else:
        if book is not None:
            return _error("mode=all 不接受 book")
        try:
            checkpoint_value = int(checkpoint)
        except (TypeError, ValueError):
            return _error("checkpoint 必須是正整數")
        if checkpoint_value < 1:
            return _error("checkpoint 必須是正整數")
        args = ["--all", "--checkpoint", str(checkpoint_value)]
    return _run_util_command("audit_knowledge_base.py", *args, timeout=600)


@mcp.tool()
def check_chapter_files(book: str, chapter: int) -> Dict[str, Any]:
    """Check that every required artefact in the start workflow exists."""
    try:
        canonical, _directory, _tmp = _chapter_context(book, chapter)
        result = _run_util_command("check_chapter_files.py", canonical, str(chapter), timeout=180)
        result.update({"book": canonical, "chapter": chapter})
        return result
    except (TypeError, ValueError, OSError) as exc:
        return _error(str(exc))


@mcp.tool()
def prepare_chapter_link_updates(book: str, chapter: int) -> Dict[str, Any]:
    """Create the B-category ``link_updates.yaml`` skeleton without applying edits."""
    try:
        canonical, _directory, tmp = _chapter_context(book, chapter)
        manifest = tmp / "link_updates.yaml"
        if manifest.exists():
            return _error(
                f"link_updates.yaml 已存在，拒絕覆蓋：{_relative_to_root(manifest)}",
                path=_relative_to_root(manifest),
            )
        result = _run_util_command("link_updates.py", "prepare", canonical, str(chapter), timeout=180)
        result.update({"book": canonical, "chapter": chapter, "manifest": _relative_to_root(manifest)})
        return result
    except (TypeError, ValueError, OSError) as exc:
        return _error(str(exc))


@mcp.tool()
def run_chapter(book: str, chapter: int, keep_chapter: bool = False) -> Dict[str, Any]:
    """Compatibility entry point that always runs ``run_chapter_manual.py run``.

    The model-powered ``util/run_chapter.py`` is intentionally not exposed by
    MCP.  M3/M6 remain a human-written, zero-API workflow.
    """
    return render_manual_chapter(book, chapter, keep_chapter=keep_chapter)


@mcp.tool()
def rename_markdown(
    source: str,
    destination: str,
    dry_run: bool = True,
    confirm: bool = False,
) -> Dict[str, Any]:
    """Preview or explicitly perform safe Markdown/WikiLink renaming.

    A real rename requires both ``dry_run=false`` and ``confirm=true``.  This
    covers the maintenance boundary command while preventing accidental bulk
    rewrites from an ambiguous agent call.
    """
    if not dry_run and not confirm:
        return _error("正式改名會修改 vault，請同時傳入 dry_run=false、confirm=true")
    try:
        source_path = _safe_repo_path(source, must_exist=True)
        destination_path = _safe_repo_path(destination)
        if destination_path == ROOT_DIR:
            raise ValueError("destination 不可為專案根目錄")
        if not _is_under(destination_path, ROOT_DIR):
            raise ValueError("destination 不可超出專案根目錄")
        result = _run_util_command(
            "rename_markdown.py", source, destination,
            *( ["--dry-run"] if dry_run else [] ), timeout=600,
        )
        result.update({"source": _relative_to_root(source_path), "destination": _relative_to_root(destination_path), "dry_run": dry_run})
        return result
    except (TypeError, ValueError, OSError) as exc:
        return _error(str(exc))


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
    in_fence = False
    in_knowledge_nodes = False
    for number, line in enumerate(text.splitlines(), 1):
        if _MERMAID_OPEN_RE.match(line):
            in_mermaid = True
            in_fence = True
            continue
        if in_fence and _FENCE_RE.match(line):
            in_fence = False
            in_mermaid = False
            continue
        if in_mermaid:
            if "[[" in line or "]]" in line:
                errors.append(f"第 {number} 行 Mermaid 圖內不可放 [[wiki-link]]")
            elif _MERMAID_BARE_LABEL_RE.search(line):
                warnings.append(
                    f'第 {number} 行 Mermaid 節點標籤未加引號，建議寫成 A["標籤"]'
                )
            continue
        if in_fence:
            continue

        if _EMBED_RE.search(line):
            errors.append(f"第 {number} 行不可使用 ![[ ]] 嵌入語法")
        if _HTML_TAG_RE.search(line):
            errors.append(f"第 {number} 行不可使用 HTML 標籤")
        if _REFERENCE_HEADING_RE.match(line):
            errors.append(f"第 {number} 行不可放參考資料／參考書目清單")
        stripped = line.strip()
        is_table_row = stripped.startswith("|") and stripped.count("|") >= 2
        if is_table_row and _ALIAS_LINK_RE.search(line):
            errors.append(f"第 {number} 行表格內不可放帶別名連結（| 會斷開儲存格）")
        if _PROCESS_NOTE_RE.search(line):
            errors.append(
                f"第 {number} 行出現流程註記（舊版／本次維護／先前版本／待確認事項／應並陳），"
                "正文只寫研經內容，勘誤依據寫在 commit 訊息或 relation"
            )
        for match in _HASHTAG_RE.finditer(line):
            token = match.group(0)
            if re.fullmatch(r"#+", token):
                continue
            errors.append(f"第 {number} 行不可使用 #標籤（{token}）")
            break

        if content_kind == "yaml":
            if re.match(r"^knowledge_nodes\s*:", line):
                in_knowledge_nodes = True
                continue
            if in_knowledge_nodes:
                if line and not line.startswith((" ", "\t", "-")):
                    in_knowledge_nodes = False
                elif _SELF_WRAPPED_NODE_RE.match(line):
                    errors.append(
                        f"第 {number} 行 knowledge_nodes 不可自己包 [[ ]]（雙重括號 bug），"
                        "寫裸名或 名稱|小標題"
                    )

    if in_mermaid or in_fence:
        errors.append("程式碼區塊未關閉")
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


def _chapter_node_files(canonical: str, chapter: int) -> tuple[List[Path], List[str]]:
    """Resolve a chapter's knowledge_nodes to rendered entry files plus the chapter md."""
    _canonical, directory, tmp = _chapter_context(canonical, chapter)
    payload = tmp / "chapter_content.yaml"
    if not payload.is_file():
        raise FileNotFoundError("缺 chapter_content.yaml；先完成 M6 payload 再掃描")
    data = yaml.safe_load(payload.read_text(encoding="utf-8")) or {}
    names = [
        str(node).split("|")[0].strip()
        for group in (data.get("knowledge_nodes") or {}).values()
        for node in (group or [])
    ]
    index = {
        path.stem: path
        for path in (ROOT_DIR / "link_folder").glob("*/*.md")
    }
    files, missing = [], []
    for name in names:
        target = index.get(name)
        if target is None:
            missing.append(name)
        else:
            files.append(target)
    chapter_md = directory / f"第{chapter}章.md"
    if chapter_md.is_file():
        files.append(chapter_md)
    return files, missing


def _raw_corpus() -> str:
    parts = []
    for path in sorted((ROOT_DIR / "raw_data").glob("*.txt")):
        parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "".join(parts)


@mcp.tool()
def scan_unsourced_tokens(book: str, chapter: int, include_warnings: bool = True) -> Dict[str, Any]:
    """Globally flag Hebrew letters, Latin transliterations and simplified characters.

    Every token found in this chapter's knowledge_node entries and its rendered
    markdown is checked against the whole ``raw_data/`` corpus, not only the
    source files for this chapter or entry. Hebrew runs are compared after
    stripping niqqud; Latin tokens use word-boundary matching so that ``perat``
    does not falsely match ``temperate``. A flag means the token appears nowhere
    in the local corpus and is a strong removal signal. No flag does *not* prove
    the token came from this entry's actual accumulated sources. This tool reads
    only; it never edits.
    """
    try:
        canonical = _canonical_book(book)
        files, missing_nodes = _chapter_node_files(canonical, chapter)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return _error(str(exc))

    raw = _raw_corpus()
    if not raw:
        return _error("raw_data/ 讀不到任何來源檔，無法判斷出處")

    hebrew, latin, simplified = [], [], []
    for path in files:
        relative = _relative_to_root(path)
        text = path.read_text(encoding="utf-8", errors="ignore")
        for run in sorted(set(_HEBREW_RUN_RE.findall(text))):
            stripped = _NIQQUD_RE.sub("", run)
            if stripped and stripped not in raw:
                hebrew.append({"file": relative, "token": run})
        candidates = set(_PAREN_LATIN_RE.findall(text)) | set(_ITALIC_LATIN_RE.findall(text))
        for token in sorted(candidates):
            token = token.strip()
            if not token or token in _TRANSLITERATION_IGNORE:
                continue
            if re.search(r"\b" + re.escape(token) + r"\b", raw, re.IGNORECASE):
                continue
            # A compound such as "Peniel / Penuel" is sourced when every word is.
            words = [word for word in re.split(r"[^A-Za-z']+", token) if word]
            if words and all(
                re.search(r"\b" + re.escape(word) + r"\b", raw, re.IGNORECASE) for word in words
            ):
                if include_warnings:
                    simplified_note = {
                        "file": relative,
                        "token": token,
                        "note": "整串查無出處，但每個字詞單獨都有出處（多為 raw 換行造成），請人工確認寫法",
                    }
                    latin.append(simplified_note)
                continue
            latin.append({"file": relative, "token": token})
        found = sorted(set(text) & _SIMPLIFIED_CHARS)
        if found:
            simplified.append({"file": relative, "characters": "".join(found)})

    hard = [item for item in latin if "note" not in item]
    return {
        "success": True,
        "book": canonical,
        "chapter": chapter,
        "files_scanned": len(files),
        "nodes_without_markdown": missing_nodes,
        "unsourced_hebrew": hebrew,
        "unsourced_latin": hard,
        "latin_needing_review": [item for item in latin if "note" in item],
        "simplified_characters": simplified,
        "flag_count": len(hebrew) + len(hard) + len(simplified),
        "advice": (
            "查無出處＝刪除音譯或希伯來字母，改用來源實際給的中文字義；"
            "未報出不等於本章／該條目實際來源有出處，仍須依 manifest 與累積章節人工核對；"
            "護欄只掃 .tmp payload，本工具補掃已渲染的 link_folder 條目。"
        ),
    }


def _run_gate(script: str, *args: str, timeout: int = 300) -> Dict[str, Any]:
    cmd = [sys.executable, str(UTIL_DIR / script), *args]
    try:
        proc = subprocess.run(
            cmd, cwd=ROOT_DIR, capture_output=True, text=True, encoding="utf-8", timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return {"gate": script, "passed": False, "error": f"逾時（{timeout} 秒）"}
    stdout = proc.stdout.strip()
    tail = "\n".join(stdout.splitlines()[-6:])
    passed = proc.returncode == 0 and "結論：FAIL" not in stdout
    return {
        "gate": " ".join([script, *args]),
        "passed": passed,
        "returncode": proc.returncode,
        "tail": tail,
        "stderr": proc.stderr.strip()[-500:],
    }


@mcp.tool()
def run_gates(book: str, chapter: Optional[int] = None, rebuild_index: bool = False) -> Dict[str, Any]:
    """Run the repository's closing gates and report each verdict separately.

    Covers ``validate_knowledge_base``, ``verify_links``, ``check_accumulation_orphans``
    and — when ``chapter`` is given — ``check_existing_links --missing``.  Set
    ``rebuild_index`` to run ``build_link_index`` then ``build_embedding_index``
    first, which is required after adding, renaming or deleting entries because a
    stale index makes the orphan check report false failures.  Passing gates prove
    structure only; content faithfulness still needs a source-by-source review.
    """
    try:
        canonical = _canonical_book(book)
    except ValueError as exc:
        return _error(str(exc))

    results: List[Dict[str, Any]] = []
    if rebuild_index:
        results.append(_run_gate("build_link_index.py"))
        results.append(_run_gate("build_embedding_index.py"))
    results.append(_run_gate("validate_knowledge_base.py"))
    results.append(_run_gate("verify_links.py", canonical))
    if chapter is not None:
        try:
            _canonical, directory, _tmp = _chapter_context(canonical, chapter)
        except ValueError as exc:
            return _error(str(exc))
        chapter_md = f"{directory.name}/第{chapter}章.md"
        results.append(_run_gate("check_existing_links.py", chapter_md, "--missing"))
    results.append(_run_gate("check_accumulation_orphans.py", canonical))

    failed = [item["gate"] for item in results if not item["passed"]]
    return {
        "success": not failed,
        "book": canonical,
        "chapter": chapter,
        "passed": not failed,
        "failed_gates": failed,
        "results": results,
        "advice": (
            "閘門全綠只是可以開始檢查內容的前提，不是完工判準；"
            "工作內容 1（擴充候選）與 2（逐條目對 rawdata 勘誤）不會讓閘門變色。"
        ),
    }


@mcp.prompt("biblical_chapter_sop")
def biblical_chapter_sop(book: str = "民數記", chapter: int = 22) -> str:
    """MCP-assisted new-chapter SOP; the repository prompt remains authoritative."""
    return f"""# Hermes Scripture：{book} 第 {chapter} 章（MCP 輔助）

以 `agent_start_prompt.md` 為完整且優先的規格。本 MCP 只降低查找、手寫 M3/M6 驗證與 B 類套用的操作風險，不能取代四來源內容複核或收尾閘門。

1. 先呼叫 `get_chapter_status`；依回傳的 resume hint 完成來源、候選與語義近鄰步驟。
2. 來源準備可用 `crawl_bible_source`、`build_source_manifest`、`build_candidate_similarity`；模型端點可用 `model_client`，但 `use` 必須明確確認。
3. 收尾可依序呼叫 `build_appendix_links`、`check_existing_links`、`sync_link_index`、`sync_embedding_index`、`validate_knowledge_base`、`check_link_quality`、`verify_links`、`audit_knowledge_base`、`check_chapter_files`。
4. 用 `search_wiki_entries` 查既有 title／alias；需要原文時用 `read_wiki_entry`。不可自創名稱、alias 或音譯。
5. M3/M6 **只走人工零 API 流程**：`prepare_manual_payload_prompts` → 讀 manifest 指定的完整來源（`read_chapter_source` 可安全讀取）→ 手寫 entry payload（M3）→ 再 prepare 取得更新後 M6 prompt → 手寫 `chapter_content.yaml` → `check_manual_payloads` → `render_manual_chapter`。不要用 `run_chapter.py` 生成 M3/M6。
6. `lint_chapter_content` 驗格式硬規（Mermaid `[[ ]]`、`![[ ]]`、HTML、`#標籤`、參考資料清單、表格內帶別名連結、正文流程註記、`knowledge_nodes` 自包 `[[ ]]`）；M3/M6 的真閘門是 `check_manual_payloads`，內容忠實性仍須人工逐條對四來源。
6b. 渲染後可跑 `scan_unsourced_tokens`——它以**整個** raw_data 語料補掃 `link_folder` 條目裡查無出處的希伯來字母與拉丁音譯（詞界比對）。報出＝強力刪除線索；未報出**不**證明它出自本章／該條目實際來源，仍須人工核對 manifest 與累積章節。
7. B 類累積先用 `prepare_chapter_link_updates`，再核對 `link_updates.yaml` 與來源，接著 `preview_chapter_link_updates`，使用回傳 token 才可 `apply_chapter_link_updates`；套用後重跑 preview 必須是 0 變更。
8. 收尾可用 `run_gates(book, chapter, rebuild_index=True)` 作核心機械閘門；它不取代上述完整收尾工具或人工內容複核。**閘門全綠只是可以開始檢查內容的前提，不是完工判準。**
"""


@mcp.prompt("biblical_maintenance_sop")
def biblical_maintenance_sop(book: str = "民數記", chapter: int = 22) -> str:
    """MCP-assisted maintenance SOP with the same zero-API M3/M6 discipline."""
    return f"""# Hermes Scripture 維護：{book} 第 {chapter} 章（MCP 輔助）

以 `agent_maintenance_prompt.md` 為完整且優先的規格。先讀四來源並逐條勘誤；結構通過不等於內容正確。

- 先用 `get_chapter_status` 看目前管線狀態，用 `read_chapter_artifact` 讀受限的 `.tmp` payload，用 `search_wiki_entries`／`read_wiki_entry` 核對既有條目與 aliases。
- 收尾或單獨檢查可用 `check_existing_links`、`sync_link_index`、`sync_embedding_index`、`validate_knowledge_base`、`check_link_quality`、`verify_links`、`audit_knowledge_base`、`check_chapter_files`；需要建立 B 類骨架時用 `prepare_chapter_link_updates`。
- 修改 M3／M6 時固定走零 API：手寫 yaml → `check_manual_payloads`（唯讀，不會重寫 alias）→ `render_manual_chapter`。改 entry payload 且本章整理已同步時，才帶 `keep_chapter=true`。
- 修改 candidates 前先呼叫 `prepare_manual_payload_prompts(confirm_stale=false)` 看作廢清單；確認手寫 payload 可刪後才設為 true，然後補寫 payload、check、render。
- B 類累積只能走 `preview_chapter_link_updates` → 人工核對 source → 使用 token 的 `apply_chapter_link_updates` → 再 preview 必須 0 變更。
- 渲染後可跑 `scan_unsourced_tokens`：護欄（`_unsourced_hebrew_errors`）只掃 `.tmp` payload，舊版遷移的 A 類條目沒有 entry_content、一次都沒被驗過；這一支以**整個** raw_data 語料補掃。報出＝查無任何本地來源的強力刪除線索；未報出**不**證明它在本章／該條目實際累積來源出現，仍要按 manifest 與累積章節核對。
- 收尾用 `run_gates(book, chapter, rebuild_index=True)` 一次跑完索引重建與四道閘門。**閘門全綠不是完工判準，只是可以開始檢查內容的前提**——工作內容 1（擴充候選）與 2（逐條目對 rawdata 勘誤）不會讓任何閘門變色；一章若 `link_folder/` 改動數為 0，回報要明寫「本章 N 個條目全部讀過、無錯可改」。
- 此 MCP 不授權跳過 `agent_maintenance_prompt.md` 的內容勘誤、link index／embedding 同步、驗證與稽核。
"""


def main() -> None:
    if MCP_IMPORT_ERROR is not None:
        sys.stderr.write(f"❌ 無法啟動 MCP server：{MCP_IMPORT_ERROR}\n")
        raise SystemExit(1)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
