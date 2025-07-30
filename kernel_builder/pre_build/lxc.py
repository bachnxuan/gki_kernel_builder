from pathlib import Path
from typing import override

from kernel_builder.constants import PATCHES
from kernel_builder.interface.patcher import PatcherInterface
from kernel_builder.utils.command import apply_patch
from kernel_builder.utils.log import log


class LXCPatcher(PatcherInterface):
    def __init__(self, lxc: bool) -> None:
        self.lxc: bool = lxc

    @override
    def apply(self) -> None:
        LXC: Path = PATCHES / "lxc.patch"
        if self.lxc:
            log("Applying LXC Patches")
            apply_patch(LXC)
        else:
            return


if __name__ == "__main__":
    raise SystemExit("This file is meant to be imported, not executed.")
