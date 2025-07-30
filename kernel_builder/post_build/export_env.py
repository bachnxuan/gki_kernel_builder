import os
import re
from datetime import datetime, timezone
from pathlib import Path

import sh
from dotenv import set_key
from sh import Command, head, sed

from kernel_builder.config.config import KERNEL_NAME, RELEASE_BRANCH, RELEASE_REPO
from kernel_builder.constants import OUTPUT, ROOT, TOOLCHAIN, WORKSPACE
from kernel_builder.pre_build.variants import Variants
from kernel_builder.utils.build import Builder
from kernel_builder.utils.github import GithubAPI
from kernel_builder.utils.log import log


class GithubExportEnv:
    def __init__(self, ksu: str, susfs: bool, lxc: bool) -> None:
        self.builder: Builder = Builder()
        self.variants: Variants = Variants(ksu, susfs, lxc)
        self.gh_api: GithubAPI = GithubAPI()
        self.env_file: Path = ROOT / "github.env"

    def _write_env(self, env_map: dict[str, str]) -> None:
        self.env_file.touch()
        for k, v in env_map.items():
            set_key(self.env_file, k.strip(), v.strip())

    def export_github_env(self) -> None:
        # Get Clang version
        clang: Command = sh.Command(str(TOOLCHAIN / "clang" / "bin" / "clang"))
        raw_toolchain = head("-n", "1", _in=clang("-v", _err_to_out=True))
        toolchain: str = str(
            sed("s/(https..*//; s/ version//", _in=raw_toolchain)
        ).strip()

        # Get SUSFS version
        susfs_version: str | None = re.search(
            r"v\d+\.\d+\.\d+",
            (
                WORKSPACE
                / "susfs4ksu"
                / "kernel_patches"
                / "include"
                / "linux"
                / "susfs.h"
            ).read_text(),
        ).group()  # pyright: ignore[reportOptionalMemberAccess]

        # Get KernelSU version
        official_version: str = self.gh_api.fetch_latest_tag(
            "https://api.github.com/repos/tiann/KernelSU/releases/latest"
        )
        suki_version: str = self.gh_api.fetch_latest_tag(
            "https://api.github.com/repos/SukiSU-Ultra/SukiSU-Ultra/releases/latest"
        )
        next_version: str = self.gh_api.fetch_latest_tag(
            "https://api.github.com/repos/KernelSU-Next/KernelSU-Next/releases/latest"
        )
        ksu_version: str = os.getenv("KSU_VERSION", "Unknown")

        # Get build timestamp
        now: datetime = datetime.now(timezone.utc)
        current_time: str = now.strftime("%a %b %d %H:%M:%S %Y")

        # Writing Env
        env_map: dict[str, str] = {
            "output": str(OUTPUT),
            "version": self.builder.get_kernel_version(),
            "variant": self.variants.suffix,
            "susfs_version": susfs_version,
            "ksu_version": ksu_version,
            "official_version": official_version,
            "suki_version": suki_version,
            "next_version": next_version,
            "toolchain": toolchain,
            "build_time": current_time,
            "release_repo": RELEASE_REPO,
            "release_branch": RELEASE_BRANCH,
            "kernel_name": KERNEL_NAME,
        }
        log(f"Environment map to export: {env_map}")
        self._write_env(env_map)
