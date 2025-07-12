import shutil
import zipfile
from pathlib import Path

from sh import Command
from kernel_builder.config.config import (
    BOOT_SIGNING_KEY,
    GKI_URL,
    IMAGE_COMP,
    OUTPUT,
    TOOLCHAIN,
    WORKSPACE,
)
from kernel_builder.utils import env
from kernel_builder.utils.fs import FileSystem
from kernel_builder.utils.log import log
from kernel_builder.utils.shell import Shell
from kernel_builder.utils.net import Net


class FlashableBuilder:
    def __init__(self, image_comp: str | None = None) -> None:
        self.shell: Shell = Shell()
        self.fs: FileSystem = FileSystem()
        self.net: Net = Net()
        self.local_run: bool = env.local_run()
        self.image_comp: str = image_comp or IMAGE_COMP
        self.image_path: Path = self._resolve_image_path()

    def _resolve_image_path(self) -> Path:
        boot_dir: Path = WORKSPACE / "out" / "arch" / "arm64" / "boot"
        filename: str = (
            "Image" if self.image_comp == "raw" else f"Image.{self.image_comp}"
        )
        img: Path = boot_dir / filename
        return img

    def _stage_image(self, target: Path) -> None:
        if not self.image_path.exists():
            raise FileNotFoundError(f"Kernel image not found at {self.image_path}")
        shutil.copyfile(self.image_path, target / self.image_path.name)
        log(f"Staged {self.image_path.name} into {target}")

    def build_anykernel3(self) -> None:
        """
        Build a flashable AnyKernel3 ZIP package.
        """
        log("Preparing to build AnyKernel3 package...")

        ak_dir = WORKSPACE / "AnyKernel3"
        self._stage_image(ak_dir)
        shutil.make_archive(
            base_name=str(OUTPUT / "AnyKernel3"),
            format="zip",
            root_dir=ak_dir,
            base_dir=".",
        )

        log(f"Created AnyKernel3.zip at {OUTPUT}")

    def build_boot_image(self) -> None:
        """
        Create and sign the boot image from the GKI release.
        """
        log("Starting boot image creation process...")

        boot_tmp = WORKSPACE / "boot"
        python = Command("python3")

        unpacker: Path = TOOLCHAIN / "mkbootimg" / "unpack_bootimg.py"
        mkbootimg: Path = TOOLCHAIN / "mkbootimg" / "mkbootimg.py"
        avbtool: Command = Command(
            str(TOOLCHAIN / "build-tools" / "linux-x86" / "bin" / "avbtool")
        )

        # Prepare temp directory
        self.fs.reset_path(boot_tmp)
        self.fs.cd(boot_tmp)

        # Download and extract GKI
        log(f"Downloading GKI image from {GKI_URL}...")
        self.net.stream_to_file(GKI_URL, boot_tmp / "gki.zip")
        with zipfile.ZipFile(boot_tmp / "gki.zip", "r") as z:
            z.extractall(boot_tmp)

        log("Unpacking boot image...")
        python(str(unpacker), f"--boot_img={boot_tmp / 'boot-5.10.img'}")

        log("Copying kernel image to boot directory...")
        self._stage_image(boot_tmp)

        log("Rebuilding boot.img with mkbootimg.py...")
        python(
            str(mkbootimg),
            "--header_version",
            "4",
            "--kernel",
            "Image.gz",
            "--output",
            "boot.img",
            "--ramdisk",
            "out/ramdisk",
            "--os_version",
            "12.0.0",
            "--os_patch_level",
            "2025-05",
        )

        # Sign the image
        log("Signing boot.img with avbtool...")
        avbtool(
            "add_hash_footer",
            "--partition_name",
            "boot",
            "--partition_size",
            str(64 * 1024 * 1024),
            "--image",
            "boot.img",
            "--algorithm",
            "SHA256_RSA2048",
            "--key",
            str(BOOT_SIGNING_KEY),
        )

        shutil.move(boot_tmp / "boot.img", OUTPUT / "boot.img")
        log(f"Boot image created at {OUTPUT}")
