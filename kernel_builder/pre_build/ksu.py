from sh import curl, bash
from kernel_builder.utils.log import log
from kernel_builder.utils.net import Net
from kernel_builder.utils.source import SourceManager
from kernel_builder.utils import env


class KSUInstaller:
    VARIANT_URLS: dict[str, str] = {
        "NEXT": "https://raw.githubusercontent.com/KernelSU-Next/KernelSU-Next/next/kernel/setup.sh",
        "SUKI": "https://raw.githubusercontent.com/SukiSU-Ultra/SukiSU-Ultra/main/kernel/setup.sh",
    }

    def __init__(self) -> None:
        self.source: SourceManager = SourceManager()
        self.net: Net = Net()
        self.variant: str = env.ksu_variant()
        self.use_susfs: bool = env.susfs_enabled()

    def _install_ksu(self, url: str, ref: str | None) -> None:
        if not self.source.is_simplified(url):
            url = self.source.git_simplifier(url)

        if not ref:
            user, repo = url.split(":", 1)
            ref = self.net.fetch_latest_tag(user, repo)

        setup_url = f"https://raw.githubusercontent.com/{url.split(':', 1)[1]}/{ref}/kernel/setup.sh"

        log(f"Installing KernelSU from {url} | {ref}")

        bash("-s", ref, _in=curl("-LSs", setup_url))

    def install(self) -> None:
        variant: str = self.variant.upper()

        match variant:
            case "NONE":
                return
            case "NEXT":
                self._install_ksu("github.com:kernelSU-Next/kernelSU-Next", "next")
            case "SUKI":
                self._install_ksu("github.com:SukiSU-Ultra/SukiSU-Ultra", "susfs-main")
            case "RKSU":
                self._install_ksu(
                    "github.com:rsuntk/KernelSU",
                    ("staging/susfs-main" if self.use_susfs else "main"),
                )
            case _:
                return


if __name__ == "__main__":
    raise SystemExit("This file is meant to be imported, not executed.")
