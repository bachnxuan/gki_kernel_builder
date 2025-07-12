import sh
from pathlib import Path
from kernel_builder.utils.fs import FileSystem
from kernel_builder.utils.log import log
from kernel_builder.config.config import ROOT


class Shell:
    """Helper class for interacting with the shell."""

    def __init__(self):
        self.fs: FileSystem = FileSystem()

    def patch(
        self, patch: Path, *, check: bool = True, cwd: Path | None = None
    ) -> None:
        log(f"Patching file: {self.fs.relative_to(ROOT, patch)}")
        cwd = cwd or Path.cwd()
        data: bytes = patch.read_bytes()
        sh.patch("-p1", "--forward", "--fuzz=3", _in=data, _cwd=str(cwd), _ok=not check)


if __name__ == "__main__":
    raise SystemExit("This file is meant to be imported, not executed.")
