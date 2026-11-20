#!/usr/bin/env python3
"""Classify one changed-path set for reusable Python-library CI."""

from __future__ import annotations

import os
from pathlib import Path
import sys


def classify_paths(paths: list[str]) -> str:
    """Return docs-only only for a non-empty set entirely below docs/."""

    if not paths:
        return "full"
    return "docs-only" if all(path.startswith("docs/") for path in paths) else "full"


def read_nul_paths(path: Path) -> list[str]:
    """Read one NUL-delimited Git path list without losing unusual bytes."""

    raw = path.read_bytes()
    return [
        os.fsdecode(value)
        for value in raw.split(b"\0")
        if value
    ]


def main() -> int:
    """Print the classification for one NUL-delimited path file."""

    if len(sys.argv) != 2:
        print("usage: change_scope.py <nul-delimited-path-file>", file=sys.stderr)
        return 2
    print(classify_paths(read_nul_paths(Path(sys.argv[1]))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
