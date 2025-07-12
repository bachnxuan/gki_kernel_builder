from pathlib import Path
from requests.models import Response
import requests
import tarfile

from sh import aria2c
from kernel_builder.config.config import TOOLCHAIN
from kernel_builder.utils.fs import FileSystem
from kernel_builder.utils.log import log
from typing import Any


def fetch_latest_aosp_clang(
    user: str = "bachnxuan",
    repo: str = "aosp_clang_mirror",
    dest: Path = TOOLCHAIN,
) -> None:
    api_url: str = f"https://api.github.com/repos/{user}/{repo}/releases/latest"
    resp: Response = requests.get(api_url)
    resp.raise_for_status()

    data: dict[str, Any] = resp.json()
    release_url: str | None = next(
        (
            asset["browser_download_url"]
            for asset in data.get("assets", [])
            if asset.get("browser_download_url", "").endswith(".tar.gz")
        ),
        None,
    )

    if release_url is None:
        log(f"No .tar.gz asset found for {user}/{repo}", "error")
        return

    log(f"Clang release url: {release_url}")

    filename: str = Path(release_url).name
    download_path: Path = dest / filename

    aria2c(
        "-x16",
        "-s32",
        "-k8M",
        "--file-allocation=falloc",
        "--timeout=60",
        "--retry-wait=5",
        "-d",
        str(dest),
        "-o",
        filename,
        release_url,
    )

    out_dir: Path = dest / "clang"
    FileSystem.reset_path(out_dir)
    with tarfile.open(download_path) as archive:
        archive.extractall(out_dir)

    download_path.unlink()
    log(f"Installed clang to {out_dir}")
