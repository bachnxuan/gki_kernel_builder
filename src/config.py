#!/usr/bin/env python3
from pathlib import Path
from typing import Final

# ====== Paths ======
ROOT: Final[Path] = Path(__file__).resolve().parent.parent
WORKSPACE: Final[Path] = ROOT / "kernel"
TOOLCHAIN: Final[Path] = Path("/opt/toolchain")

# ====== Build ======
DEFCONFIG: Final[str] = "esk_defconfig"
BUILD_USER: Final[str] = "gki-builder"
BUILD_HOST: Final[str] = "esk"

# ====== Sources ======
KERNEL: Final[dict[str, str]] = {
    "url": "https://github.com/bachnxuan/android12-5.10-lts",
    "branch": "android12-5.10-lts",
    "to": str(WORKSPACE),
}

ANYKERNEL: Final[dict[str, str]] = {
    "url": "https://github.com/bachnxuan/AnyKernel3",
    "branch": "android12-5.10",
    "to": str(WORKSPACE / "AnyKernel3"),
}

BUILD_TOOL: Final[dict[str, str]] = {
    "url": "https://android.googlesource.com/kernel/prebuilts/build-tools",
    "branch": "main-kernel-build-2024",
    "to": str(TOOLCHAIN / "build_tools"),
}

MKBOOTIMG: Final[dict[str, str]] = {
    "url": "https://android.googlesource.com/platform/system/tools/mkbootimg",
    "branch": "main-kernel-build-2024",
    "to": str(TOOLCHAIN / "mkbootimg"),
}

SOURCES: Final[list[dict[str, str]]] = [KERNEL, ANYKERNEL, BUILD_TOOL, MKBOOTIMG]

# ====== Clang ======
CLANG: Final[Path] = Path("/opt/toolchain/clang")
CLANG_TAR: Final[str] = (
    "https://android.googlesource.com/platform/prebuilts/clang/host/linux-x86/+archive/refs/heads/main/clang-r547379.tar.gz"
)

# ====== Cross Compile ======
CLANG_TRIPLE: Final[str] = "aarch64-linux-gnu-"
CROSS_COMPILE: Final[str] = "aarch64-linux-gnu-"

if __name__ == "__main__":
    raise SystemExit("This file is meant to be imported, not executed.")
