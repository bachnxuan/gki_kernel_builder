#!/usr/bin/env python3
import os
from typing import Final
from pathlib import Path
from config import BUILD_HOST, BUILD_USER, CLANG, CLANG_TRIPLE, CROSS_COMPILE


def setup_env() -> None:
    """A function to set neccessary env for building kernel."""

    # ====== KBUILD ======
    os.environ["KBUILD_BUILD_USER"] = BUILD_USER
    os.environ["KBUILD_BUILD_HOST"] = BUILD_HOST

    # ====== Paths ======
    CLANG_BIN: Final[Path] = CLANG / "bin"
    os.environ["PATH"] = f"{CLANG_BIN}{os.pathsep}{os.environ.get('PATH', '')}"

    # ====== Cross Compile ======
    os.environ["CLANG_TRIPLE"] = CLANG_TRIPLE
    os.environ["CROSS_COMPILE"] = CROSS_COMPILE

    # ====== LLVM ======
    # Force LLVM binutils and Clang IAS
    os.environ["LLVM"] = "1"
    os.environ["LLVM_IAS"] = "1"

    # Force Thin LTO
    os.environ["CONFIG_LTO_CLANG_THIN"] = "y"
    os.environ["CONFIG_LTO_CLANG_FULL"] = "n"

    # Manually config LD path
    os.environ["LD"] = str(CLANG_BIN / "ld.lld")


if __name__ == "__main__":
    raise SystemExit("This file is meant to be imported, not executed.")
