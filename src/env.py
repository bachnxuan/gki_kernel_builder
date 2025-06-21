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
    os.environ["LLVM"] = "1"  # Force uses of LLVM binutils
    os.environ["LLVM_IAS"] = "1"  # Force Clang IAS
    os.environ["LD"] = str(CLANG_BIN / "ld.lld")


if __name__ == "__main__":
    raise SystemExit("This file is meant to be imported, not executed.")
