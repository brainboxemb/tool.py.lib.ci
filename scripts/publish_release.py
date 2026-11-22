#!/usr/bin/env python3
"""Publish exact GitHub releases and the tool's own VERSION release."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
_VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
_SHA = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class ReleaseResult:
    tag: str
    target_sha: str
    url: str
    created: bool


def exact_sha(value: str, name: str = "SHA") -> str:
    value = value.strip()
    if _SHA.fullmatch(value) is None:
        raise ValueError(f"{name} must contain exactly 40 lowercase hex characters")
    return value


def release_version(root: Path = ROOT) -> str:
    """Return the declared self-release version after source checks."""

    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not _VERSION.fullmatch(version):
        raise ValueError(f"VERSION is not a release version: {version}")

    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    if re.search(
        rf"^## {re.escape(version)}(?:\s|$)",
        changelog,
        re.MULTILINE,
    ) is None:
        raise ValueError(f"CHANGELOG.md has no {version} release section")
    return version


def version_changed(root: Path = ROOT) -> bool:
    """Return whether VERSION changed in the current commit."""

    parent = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD^"],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if parent.returncode != 0:
        return True

    changed = subprocess.run(
        ["git", "diff", "--quiet", "HEAD^", "HEAD", "--", "VERSION"],
        cwd=root,
        check=False,
    )
    if changed.returncode == 0:
        return False
    if changed.returncode == 1:
        return True
    raise ValueError("could not determine whether VERSION changed")


def _request(
    url: str,
    token: str,
    *,
    method: str = "GET",
    data: dict | None = None,
):
    """Send one authenticated GitHub REST request."""

    payload = None if data is None else json.dumps(data).encode("utf-8")
    request = Request(
        url,
        data=payload,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urlopen(request) as response:
        body = response.read().decode("utf-8")
        return {} if not body else json.loads(body)


def _tag_commit(base: str, tag: str, token: str) -> str | None:
    """Resolve lightweight or annotated tag to its immutable commit."""

    try:
        reference = _request(f"{base}/git/ref/tags/{quote(tag, safe='')}", token)
    except HTTPError as exc:
        if exc.code == 404:
            return None
        raise

    target = reference.get("object") or {}
    for _ in range(5):
        kind = target.get("type")
        sha = target.get("sha")
        if not isinstance(sha, str) or _SHA.fullmatch(sha) is None:
            raise ValueError(f"release tag {tag} has an invalid target")
        if kind == "commit":
            return sha
        if kind != "tag":
            raise ValueError(
                f"release tag {tag} targets unsupported object {kind!r}"
            )
        value = _request(f"{base}/git/tags/{sha}", token)
        target = value.get("object") or {}

    raise ValueError(f"release tag {tag} has excessive tag indirection")


def stable_head(repository: str, ref: str, token: str) -> str:
    """Return exact current SHA for one required stable branch."""

    ref = ref.strip()
    if not ref or ref.startswith("/") or ".." in ref.split("/"):
        raise ValueError("stable_ref must be a safe non-empty branch name")
    base = f"https://api.github.com/repos/{repository}"
    value = _request(f"{base}/git/ref/heads/{quote(ref, safe='')}", token)
    target = (value.get("object") or {}).get("sha")
    return exact_sha(str(target or ""), f"{ref} head")


def publish_exact_release(
    repository: str,
    version: str,
    sha: str,
    token: str,
    *,
    stable_ref: str = "main",
    notes: str = "",
) -> ReleaseResult:
    """Publish or verify one exact SemVer release at the stable branch head."""

    repository = repository.strip()
    if repository.count("/") != 1:
        raise ValueError("repository must be owner/name")
    if _VERSION.fullmatch(version) is None:
        raise ValueError("version must be plain X.Y.Z SemVer")
    sha = exact_sha(sha, "target SHA")
    if not token:
        raise ValueError("GitHub token is required")

    head = stable_head(repository, stable_ref, token)
    if sha != head:
        raise ValueError(
            f"release target must equal {stable_ref} HEAD: {head}"
        )

    tag = f"v{version}"
    base = f"https://api.github.com/repos/{repository}"
    tag_sha = _tag_commit(base, tag, token)
    if tag_sha is not None and tag_sha != sha:
        raise ValueError(
            f"{tag} already points to {tag_sha}; refusing to relabel {sha}"
        )

    try:
        existing = _request(f"{base}/releases/tags/{quote(tag, safe='')}", token)
    except HTTPError as exc:
        if exc.code != 404:
            raise
    else:
        if tag_sha is None:
            raise ValueError(f"release {tag} exists but tag reference is missing")
        url = str(existing.get("html_url") or "")
        if not url:
            raise ValueError(f"release {tag} has no html_url")
        return ReleaseResult(tag, sha, url, False)

    data = {
        "tag_name": tag,
        "target_commitish": sha,
        "name": tag,
        "draft": False,
        "prerelease": False,
    }
    if notes.strip():
        data["body"] = notes
    else:
        data["generate_release_notes"] = True

    created = _request(f"{base}/releases", token, method="POST", data=data)
    actual = _tag_commit(base, tag, token)
    if actual != sha:
        raise ValueError(
            f"published {tag} resolves to {actual!r}, expected {sha}"
        )
    url = str(created.get("html_url") or "")
    if not url:
        raise ValueError(f"published release {tag} has no html_url")
    return ReleaseResult(tag, sha, url, True)


def publish(repository: str, sha: str, token: str, root: Path = ROOT) -> str:
    """Publish this tool's declared VERSION only when VERSION changed."""

    if not version_changed(root):
        return "VERSION unchanged; no release"

    version = release_version(root)
    result = publish_exact_release(repository, version, sha, token)
    state = "published release" if result.created else "release already exists"
    return f"{state}: {result.tag} at {result.target_sha}"


def main() -> int:
    """Publish this repository using GitHub Actions environment values."""

    repository = os.environ.get("GITHUB_REPOSITORY", "")
    sha = os.environ.get("GITHUB_SHA", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    if not repository or not sha or not token:
        print(
            "ERROR: GITHUB_REPOSITORY, GITHUB_SHA and GITHUB_TOKEN are required",
            file=sys.stderr,
        )
        return 2
    try:
        print(publish(repository, sha, token))
    except (ValueError, HTTPError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
