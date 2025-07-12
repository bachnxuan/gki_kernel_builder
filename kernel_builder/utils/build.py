from sh import Command
import os
import re
import sh
from os import cpu_count
from pathlib import Path
from dataclasses import dataclass, field
from kernel_builder.pre_build.configurator import configurator
from kernel_builder.config.config import WORKSPACE, DEFCONFIG
from kernel_builder.utils import env
from kernel_builder.utils.fs import FileSystem
from kernel_builder.utils.shell import Shell
from kernel_builder.utils.log import log
from typing import ClassVar

make: Command = sh.Command("make").bake(
    _env={**os.environ, "CC": "ccache clang", "CXX": "ccache clang++"},
)


@dataclass(slots=True)
class Builder:
    shell: Shell = field(default_factory=Shell)
    fs: FileSystem = field(default_factory=FileSystem)

    workspace: ClassVar[Path] = WORKSPACE
    defconfig: ClassVar[str] = DEFCONFIG
    jobs: int = field(default_factory=lambda: cpu_count() or 1)
    ksu_variant: str = field(default_factory=env.ksu_variant)
    use_susfs: bool = field(default_factory=env.susfs_enabled)

    def _make(
        self, args: list[str] | None = None, *, jobs: int, out: str | Path
    ) -> None:
        make(f"-j{jobs}", *(args or []), f"O={out}", _cwd=Path.cwd())

    def build(
        self,
        jobs: int | None = None,
        *,
        out: str | Path = "out",
    ) -> None:
        log(
            f"Start build: defconfig={self.defconfig}, out={out}, jobs={jobs or self.jobs}"
        )
        self._make([self.defconfig], jobs=(jobs or self.jobs), out=out)

        configurator()

        log("Making oldefconfig")
        make("olddefconfig", f"O={out}")

        log("Defconfig completed. Starting full build.")
        self._make(jobs=(jobs or self.jobs), out=out)
        log("Build completed successfully.")

    def get_kernel_version(self) -> str | None:
        log("Fetching kernel version...")
        makefile: str = (self.workspace / "Makefile").read_text()
        version = re.findall(
            r"^(?:VERSION|PATCHLEVEL|SUBLEVEL)\s*=\s*(\d+)$", makefile, re.MULTILINE
        )
        return ".".join(version[:3]) if version else None


if __name__ == "__main__":
    raise SystemExit("This file is meant to be imported, not executed.")
