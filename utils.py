#!/usr/bin/env python3
import os
import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path
from subprocess import CompletedProcess
from typing import TypeAlias

# ====== Typing Aliases ======
Proc: TypeAlias = CompletedProcess[bytes]


# ====== Command Wrappers ======
def run(command: list[str]) -> Proc:
    """Run cmd with current env."""
    return subprocess.run(command, check=True, env=os.environ)


def patch(patch_file: str | Path) -> Proc:
    """Apply a patch file with --forward/--fuzz=3."""
    return run(["patch", "-p1", "--forward", "--fuzz=3", f"{patch_file}"])


def clone_repo(
    repo: dict[str, str], *, depth: int = 1, args: Sequence[str] | None = None
) -> CompletedProcess[bytes]:
    """Clone a git repository based on repo, branch, dest."""
    return run(
        [
            "git",
            "clone",
            "--depth",
            str(depth),
            "-b",
            repo["branch"],
            *(args or []),
            repo["url"],
            repo["to"],
        ]
    )


def mkdir(path: Path) -> None:
    """Create path and parents if missing (same as mkdir -p)."""
    path.mkdir(parents=True, exist_ok=True)


def reset_path(path: Path) -> None:
    """
    - If path does not exist -> create it.
    - If path is an empty dir or non-empty -> remove & recreate.
    - If path is a file/symlink -> delete it.
    """
    if path.exists():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    mkdir(path)


if __name__ == "__main__":
    raise SystemExit("This file is meant to be imported, not executed.")
