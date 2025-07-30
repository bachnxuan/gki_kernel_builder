import tarfile
from pathlib import Path

from kernel_builder.config.config import (
    CLANG_URL,
    CLANG_VARIANT,
    IMAGE_COMP,
    KERNEL_NAME,
)
from kernel_builder.constants import OUTPUT, TOOLCHAIN, WORKSPACE
from kernel_builder.post_build.export_env import GithubExportEnv
from kernel_builder.post_build.flashable import FlashableBuilder
from kernel_builder.post_build.kpm import KPMPatcher
from kernel_builder.pre_build.ksu import KSUInstaller
from kernel_builder.pre_build.lxc import LXCPatcher
from kernel_builder.pre_build.susfs import SUSFSPatcher
from kernel_builder.pre_build.variants import Variants
from kernel_builder.utils.build import Builder
from kernel_builder.utils.clang import fetch_clang_url
from kernel_builder.utils.command import aria2c
from kernel_builder.utils.fs import FileSystem
from kernel_builder.utils.log import log
from kernel_builder.utils.source import SourceManager


class KernelBuilder:
    def __init__(self, ksu: str, susfs: bool, lxc: bool) -> None:
        self.ksu_variant: str = ksu
        self.use_susfs: bool = susfs
        self.use_lxc: bool = lxc

        self.kpm: KPMPatcher = KPMPatcher(ksu)
        self.ksu: KSUInstaller = KSUInstaller(ksu, susfs)
        self.susfs: SUSFSPatcher = SUSFSPatcher(ksu, susfs)
        self.lxc: LXCPatcher = LXCPatcher(lxc)
        self.export_env: GithubExportEnv = GithubExportEnv(ksu, susfs, lxc)
        self.variants: Variants = Variants(ksu, susfs, lxc)

        self.builder: Builder = Builder()
        self.fs: FileSystem = FileSystem()
        self.source: SourceManager = SourceManager()
        self.flashable: FlashableBuilder = FlashableBuilder()

        boot_dir: Path = WORKSPACE / "out" / "arch" / "arm64" / "boot"
        image: Path = boot_dir / "Image"
        self.image_path: Path = (
            image if IMAGE_COMP == "raw" else image.with_suffix(f".{IMAGE_COMP}")
        )

    def run_build(self) -> None:
        """
        Run the complete build process.
        """
        log(f"Build Config: {self.ksu_variant=}, {self.use_susfs=}, {self.use_lxc=}")

        # Reset paths
        reset_paths = [WORKSPACE, TOOLCHAIN, OUTPUT]
        log(f"Resetting paths: {', '.join(map(str, reset_paths))}")
        for path in reset_paths:
            self.fs.reset_path(path)

        # Clone sources
        log("Cloning kernel and toolchain repositories...")
        self.source.clone_sources()

        # Clone Clang
        clang_url: str = CLANG_URL or fetch_clang_url(CLANG_VARIANT)
        dest: Path = TOOLCHAIN
        tarball: Path = dest / "tarball"
        clang: Path = dest / "clang"

        aria2c("-d", str(dest), "-o", "tarball", clang_url)
        FileSystem.reset_path(clang)

        with tarfile.open(tarball, "r:*") as tar:
            tar.extractall(clang)

        tarball.unlink()

        # Enter workspace
        self.fs.cd(WORKSPACE)

        # Pre-build steps
        self.ksu.install()
        self.susfs.apply()
        self.lxc.apply()

        # Main build steps
        self.builder.build()

        # Post build
        self.kpm.patch()
        self.export_env.export_github_env()

        # Build flashable
        self.flashable.build_anykernel3()
        self.flashable.build_boot_image()

        # Rename artifacts
        log("Renaming build artifacts...")
        version: str | None = self.builder.get_kernel_version()
        suffix: str = self.variants.suffix
        anykernel_src: Path = OUTPUT / "AnyKernel3.zip"
        boot_src: Path = OUTPUT / "boot.img"

        anykernel_dest: Path = (
            OUTPUT / f"{KERNEL_NAME}-{version}{suffix}-AnyKernel3.zip"
        )
        boot_dest: Path = OUTPUT / f"{KERNEL_NAME}-{version}{suffix}-boot.img"

        anykernel_src.rename(anykernel_dest)
        boot_src.rename(boot_dest)
