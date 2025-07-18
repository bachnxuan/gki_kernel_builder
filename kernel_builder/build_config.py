from dataclasses import dataclass


@dataclass
class BuildConfig:
    ksu: str
    susfs: bool
    lxc: bool
    verbose: bool
