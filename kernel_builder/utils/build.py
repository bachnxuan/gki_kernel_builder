import os
import re
import sys
from dataclasses import dataclass, field
from os import cpu_count
from pathlib import Path
from typing import ClassVar

from sh import make

from kernel_builder.config.config import DEFCONFIG, IMAGE_COMP
from kernel_builder.constants import WORKSPACE
from kernel_builder.pre_build.configurator import configurator
from kernel_builder.utils import env
from kernel_builder.utils.fs import FileSystem
from kernel_builder.utils.log import log


@dataclass(slots=True)
class Builder:
    fs: FileSystem = field(default_factory=FileSystem)

    workspace: ClassVar[Path] = WORKSPACE
    defconfig: ClassVar[str] = DEFCONFIG
    image_comp: ClassVar[str] = IMAGE_COMP
    jobs: int = field(default_factory=lambda: cpu_count() or 1)
    ksu_variant: str = field(default_factory=env.ksu_variant)
    use_susfs: bool = field(default_factory=env.susfs_enabled)

    def _make(
        self, args: list[str] | None = None, *, jobs: int, out: str | Path
    ) -> None:
        make(
            f"-j{jobs}",
            *(args or []),
            f"O={out}",
            _cwd=Path.cwd(),
            _env={**os.environ, "CC": "ccache clang", "CXX": "ccache clang++"},
            _out=sys.stdout,
            _err=sys.stderr,
        )

    def build(
        self,
        jobs: int | None = None,
        *,
        out: str | Path = "out",
    ) -> None:
        target: str = (
            "Image" if self.image_comp == "raw" else f"Image.{self.image_comp}"
        )
        jobs = jobs or self.jobs
        log(
            f"Start build: {self.defconfig=}, {out=}, {jobs or self.jobs=}, {self.image_comp=}"
        )
        self._make([self.defconfig], jobs=jobs, out=out)

        configurator()

        log("Making olddefconfig")
        self._make(["olddefconfig"], jobs=jobs, out=out)

        log("Defconfig completed. Starting full build.")
        self._make([target, "modules"], jobs=jobs, out=out)
        log("Build completed successfully.")

    def get_kernel_version(self) -> str:
        log("Fetching kernel version...")
        makefile: str = (self.workspace / "Makefile").read_text()
        version = re.findall(
            r"^(?:VERSION|PATCHLEVEL|SUBLEVEL)\s*=\s*(\d+)$", makefile, re.MULTILINE
        )
        assert version, "Unable to determine kernel version"
        return ".".join(version[:3])


if __name__ == "__main__":
    raise SystemExit("This file is meant to be imported, not executed.")
