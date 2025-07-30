import os
import re
import shutil
from pathlib import Path
from typing import override

from kernel_builder.constants import WILD_PATCHES, WORKSPACE
from kernel_builder.interface.patcher import PatcherInterface
from kernel_builder.utils.command import apply_patch
from kernel_builder.utils.log import log


class SUSFSPatcher(PatcherInterface):
    def __init__(self, ksu: str, susfs: bool) -> None:
        self.ksu_variant: str = ksu
        self.susfs: bool = susfs

    def copy(self, src: Path, dest: Path):
        log(f"Copying content from folder {src} to {dest}")
        for entry in os.scandir(src):
            src_path: str = entry.path
            dst_path: str = os.path.join(dest, entry.name)
            if entry.is_dir():
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)

    def _apply_patch_folder(self, path: Path, target: Path) -> None:
        for patch_file in path.iterdir():
            if patch_file.suffix != ".patch":
                continue
            apply_patch(patch_file, check=False, cwd=target)

    @override
    def apply(self) -> None:
        if self.ksu_variant == "NONE" or not self.susfs:
            return

        os.chdir(WORKSPACE)

        SUSFS: Path = WORKSPACE / "susfs4ksu" / "kernel_patches"

        GKI_SUSFS: Path = SUSFS / "50_add_susfs_in_gki-android12-5.10.patch"
        KSU_SUSFS: Path = SUSFS / "KernelSU" / "10_enable_susfs_for_ksu.patch"
        SUSFS_HEADER: str = (SUSFS / "include" / "linux" / "susfs.h").read_text()
        VERSION: str = re.search(r"v\d+\.\d+\.\d+", SUSFS_HEADER).group()  # pyright: ignore[reportOptionalMemberAccess]
        KSUN_SUSFS_FIX: Path = WILD_PATCHES / "next" / "susfs_fix_patches" / VERSION

        log("Applying kernel-side SUSFS patches")
        self.copy(SUSFS / "fs", WORKSPACE / "fs")
        self.copy(SUSFS / "include" / "linux", WORKSPACE / "include" / "linux")

        apply_patch(GKI_SUSFS)

        if self.ksu_variant == "NEXT":
            KSUN_PATH: Path = WORKSPACE / "KernelSU-Next"
            apply_patch(KSU_SUSFS, check=False, cwd=KSUN_PATH)
            self._apply_patch_folder(KSUN_SUSFS_FIX, KSUN_PATH)


if __name__ == "__main__":
    raise SystemExit("This file is meant to be imported, not executed.")
