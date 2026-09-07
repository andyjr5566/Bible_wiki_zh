#!/usr/bin/env python3
"""Atomic YAML writes: serialize first, then replace the file in one step.

A direct ``open(path, "w")`` (which ``Path.write_text`` also does) truncates the
target the moment it opens. If serialization then raises, or the process is
killed mid-write, or the disk fills, the file is left at 0 bytes with no backup.
Hand-written M3/M6 payloads have been lost exactly this way
(see ``[[yaml-roundtrip-truncates-on-dump-error]]``).

Route every ``.tmp/**/*.yaml`` write through :func:`write_yaml_atomic`:
the dump happens before any file is touched, the bytes land in a sibling
``<name>.<pid>.tmp`` file, and ``os.replace`` moves it into place atomically
(on the same filesystem). On any failure the temp file is removed and the
original is byte-for-byte intact.
"""
from __future__ import annotations

import os
from pathlib import Path

import yaml

# The house defaults every call site already passed by hand.
_DEFAULTS = {"allow_unicode": True, "sort_keys": False}


def dump_yaml(data, **kwargs) -> str:
    """``yaml.safe_dump`` with the project defaults; kwargs override them."""
    return yaml.safe_dump(data, **{**_DEFAULTS, **kwargs})


def write_yaml_atomic(path, data, **dump_kwargs) -> Path:
    """Serialize ``data`` and atomically replace ``path``.

    Serialization runs first — a failure there leaves ``path`` untouched. The
    text is then written to ``<path>.<pid>.tmp`` and ``os.replace``d over the
    target. Any error during the write removes the temp file and re-raises.
    """
    path = Path(path)
    text = dump_yaml(data, **dump_kwargs)  # may raise; nothing touched yet
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    try:
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)
    except BaseException:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise
    return path
