from kernel_builder.utils import env
from kernel_builder.config.config import PATCHES
from kernel_builder.utils.shell import Shell
from kernel_builder.utils.log import log
from pathlib import Path


class LXCPatcher:
    def __init__(self) -> None:
        self.shell: Shell = Shell()
        self.lxc: bool = env.lxc_enabled()
        self.susfs: bool = env.susfs_enabled()

    def apply(self) -> None:
        LXC: Path = PATCHES / "lxc.patch"
        if self.lxc:
            log("Applying LXC Patches")
            return self.shell.patch(LXC)
        else:
            return


if __name__ == "__main__":
    raise SystemExit("This file is meant to be imported, not executed.")
