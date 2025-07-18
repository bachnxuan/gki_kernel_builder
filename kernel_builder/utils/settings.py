from kernel_builder.build_config import BuildConfig
import os


class BuildSettings:
    def __init__(self, cfg: BuildConfig) -> None:
        self.cfg: BuildConfig = cfg

    @property
    def ksu_variant(self) -> str:
        return self.cfg.ksu

    @property
    def susfs_enabled(self) -> bool:
        return self.cfg.susfs

    @property
    def lxc_enabled(self) -> bool:
        return self.cfg.lxc

    @property
    def verbose_enabled(self) -> bool:
        return self.cfg.verbose


def github_token() -> str | None:
    return os.getenv("GH_TOKEN", None)
