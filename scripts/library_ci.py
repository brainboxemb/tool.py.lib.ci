#!/usr/bin/env python3
"""Build and test one Python library from its installed wheel.

This script intentionally owns only ordinary Python package verification.
It has no CAD-CI, SCons, repository-selection or cache behavior.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import os
import shlex
import shutil
import subprocess
import sys
import venv


DEFAULT_TEST_COMMAND = (
    "{python} -m unittest discover -s {repo}/tests -p test_*.py -v"
)


class PipelineError(RuntimeError):
    """One explicit package-CI stage failed."""

    def __init__(self, stage: str, message: str) -> None:
        super().__init__(f"{stage}: {message}")
        self.stage = stage
        self.message = message


def run_checked(
    command: list[str],
    *,
    cwd: Path,
    stage: str,
    env: dict[str, str] | None = None,
) -> None:
    """Run one command and raise a stage-labelled error on failure."""

    print("+ " + shlex.join(command), flush=True)
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=False,
    )
    if completed.returncode:
        raise PipelineError(
            stage,
            f"command exited with status {completed.returncode}",
        )


def single_wheel(directory: Path) -> Path:
    """Return the only wheel in a directory."""

    wheels = tuple(sorted(directory.glob("*.whl")))
    if len(wheels) != 1:
        raise PipelineError(
            "build",
            f"expected exactly one wheel, found {len(wheels)}",
        )
    return wheels[0]


def build_wheel(repo: Path, work: Path) -> Path:
    """Build exactly one wheel from the library repository."""

    wheel_dir = work / "wheel"
    if wheel_dir.exists():
        shutil.rmtree(wheel_dir)
    wheel_dir.mkdir(parents=True)

    run_checked(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--wheel-dir",
            str(wheel_dir),
            str(repo),
        ],
        cwd=work,
        stage="build",
    )
    return single_wheel(wheel_dir)


def create_environment(work: Path) -> Path:
    """Create a clean virtual environment and return its Python executable."""

    environment = work / "venv"
    if environment.exists():
        shutil.rmtree(environment)
    venv.EnvBuilder(with_pip=True, clear=True).create(environment)
    if os.name == "nt":
        python = environment / "Scripts" / "python.exe"
    else:
        python = environment / "bin" / "python"
    if not python.is_file():
        raise PipelineError("environment", "virtualenv Python is missing")
    return python


def install_wheel(python: Path, wheel: Path, *, work: Path) -> None:
    """Install the wheel and all of its declared dependencies."""

    run_checked(
        [str(python), "-m", "pip", "install", str(wheel)],
        cwd=work,
        stage="install",
    )


def test_command(
    value: str,
    *,
    python: Path,
    repo: Path,
) -> list[str]:
    """Expand the documented test-command placeholders without using a shell."""

    text = value.strip() or DEFAULT_TEST_COMMAND
    try:
        parts = shlex.split(text)
    except ValueError as exc:
        raise PipelineError("test", f"invalid test command: {exc}") from exc

    if not parts:
        raise PipelineError("test", "test command may not be empty")

    replacements = {
        "{python}": str(python),
        "{repo}": str(repo),
    }
    expanded = []
    for part in parts:
        for marker, replacement in replacements.items():
            part = part.replace(marker, replacement)
        expanded.append(part)
    return expanded


def run_tests(
    python: Path,
    repo: Path,
    work: Path,
    command_text: str,
) -> None:
    """Run library tests outside the library source tree."""

    test_root = work / "test"
    test_root.mkdir(parents=True, exist_ok=True)
    command = test_command(
        command_text,
        python=python,
        repo=repo,
    )
    run_checked(command, cwd=test_root, stage="test")


def source_commit(repo: Path) -> str:
    """Return the exact checked-out library source commit when available."""

    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if completed.returncode:
        return "not-a-git-checkout"
    return completed.stdout.strip()


def run_pipeline(
    repo: Path,
    work: Path,
    *,
    command_text: str = "",
) -> Path:
    """Build, clean-install and test one library package."""

    repo = repo.resolve()
    work = work.resolve()
    work.mkdir(parents=True, exist_ok=True)

    print(f"source_commit={source_commit(repo)}")
    print(f"build_python={sys.version.split()[0]}")

    wheel = build_wheel(repo, work)
    print(f"wheel={wheel.name}")

    python = create_environment(work)
    install_wheel(python, wheel, work=work)
    print(f"installed_wheel={wheel.name}")

    command = test_command(command_text, python=python, repo=repo)
    print("test_command=" + shlex.join(command))
    run_tests(python, repo, work, command_text)

    print("result=pass")
    return wheel


def main() -> int:
    """Run the package-CI pipeline for one library repository."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--test-command", default="")
    args = parser.parse_args()

    try:
        run_pipeline(
            args.repo,
            args.work,
            command_text=args.test_command,
        )
    except (OSError, PipelineError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
