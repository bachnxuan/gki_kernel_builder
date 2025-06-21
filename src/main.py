#!/usr/bin/env python3
import tarfile
from os import chdir, cpu_count
from pathlib import Path
from subprocess import CompletedProcess
from typing import Final, TypeAlias
from collections.abc import Sequence

from config import (
    CLANG,
    CLANG_TAR,
    DEFCONFIG,
    SOURCES,
    TOOLCHAIN,
    WORKSPACE,
)
from env import setup_env
from utils import (
    run,
    clone_repo,
    reset_path,
    mkdir,
)

# ====== Typing Aliases ======
Proc: TypeAlias = CompletedProcess[bytes]


# ====== Kernel Builder ======
class KernelBuilder:
    def __init__(
        self,
        workspace: Path = WORKSPACE,
        jobs: int | None = None,
        sources: list[dict[str, str]] = SOURCES,
        defconfig: str = DEFCONFIG,
    ) -> None:
        self.workspace: Final[Path] = workspace
        self.jobs: Final[int] = jobs or (cpu_count() or 1)
        self.sources: Final[list[dict[str, str]]] = sources
        self.defconfig: Final[str] = defconfig

    def _make(
        self, args: Sequence[str] | None = None, *, jobs: int, out: str | Path
    ) -> Proc:
        """Invoke GNU Make with LLVM/Clang flags."""
        return run(
            [
                "make",
                f"-j{jobs}",
                "CC=ccache clang",
                "CXX=ccache clang++",
                *(args or []),
                f"O={out}",
            ]
        )

    def build(
        self,
        jobs: int | None = None,
        *,
        defconfig: str | None = None,
        out: str | Path = "out",
    ) -> tuple[Proc, Proc]:
        """Generate .config via <defconfig> and build the kernel."""
        cfg_run: Proc = self._make(
            [defconfig or self.defconfig], jobs=(jobs or self.jobs), out=out
        )
        build_run: Proc = self._make(jobs=(jobs or self.jobs), out=out)
        return cfg_run, build_run

    def clone_sources(self) -> None:
        """Clone sources based on SOURCES."""
        for source in self.sources:
            _ = clone_repo(source, args=["--recurse-submodules"])

    def run(self) -> None:
        # ====== Setup Environment ======
        setup_env()

        # ====== Create Workspace ======
        reset_path(WORKSPACE)
        reset_path(TOOLCHAIN)

        # ====== Clone Kernel & Toolchain ======
        self.clone_sources()

        # Handle clang download through wget
        _ = run(["wget", "-qO", "clang.tar.gz", CLANG_TAR])
        mkdir(CLANG)
        with tarfile.open("clang.tar.gz") as tar:
            tar.extractall(CLANG)

        # ====== Build  ======
        chdir(WORKSPACE)  # Enter Workspace
        _ = self.build()


if __name__ == "__main__":
    build: KernelBuilder = KernelBuilder()
    build.run()
