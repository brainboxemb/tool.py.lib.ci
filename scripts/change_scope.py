#!/usr/bin/env python3
"""Classify changed paths and safe Git comparison context for library CI."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import sys


_SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")
_ZERO_SHA = "0" * 40


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


def valid_base_sha(value: str) -> bool:
    """Return whether one event base is a usable non-zero commit SHA."""

    return bool(_SHA40.fullmatch(value)) and value.lower() != _ZERO_SHA


def comparison_base(
    *,
    event_name: str,
    source_sha_input: str,
    pull_base_sha: str,
    push_before_sha: str,
    push_forced: bool,
) -> str | None:
    """Return the safe event base commit, or None to require full CI."""

    if source_sha_input:
        return None
    if event_name == "pull_request":
        return pull_base_sha if valid_base_sha(pull_base_sha) else None
    if event_name == "push" and not push_forced:
        return push_before_sha if valid_base_sha(push_before_sha) else None
    return None


def parser() -> argparse.ArgumentParser:
    """Build the small command-line surface used by the reusable workflow."""

    value = argparse.ArgumentParser(description=__doc__)
    sub = value.add_subparsers(dest="command", required=True)

    classify = sub.add_parser("classify")
    classify.add_argument("path", type=Path)

    base = sub.add_parser("base")
    base.add_argument("--event", required=True)
    base.add_argument("--source-sha-input", default="")
    base.add_argument("--pull-base-sha", default="")
    base.add_argument("--push-before-sha", default="")
    base.add_argument("--push-forced", choices=("true", "false"), default="false")
    return value


def main() -> int:
    """Print one deterministic scope or comparison-base result."""

    args = parser().parse_args()
    if args.command == "classify":
        print(classify_paths(read_nul_paths(args.path)))
        return 0

    base = comparison_base(
        event_name=args.event,
        source_sha_input=args.source_sha_input,
        pull_base_sha=args.pull_base_sha,
        push_before_sha=args.push_before_sha,
        push_forced=args.push_forced == "true",
    )
    print(base or "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
