from kernel_builder.utils.log import log


class Variants:
    def __init__(self, ksu: str, susfs: bool, lxc: bool) -> None:
        self.ksu: str = ksu
        self.lxc: bool = susfs
        self.susfs: bool = lxc

    @property
    def variant_name(self) -> list[str]:
        result: list[str] = []
        k: str = self.ksu.upper()

        if k == "NONE":
            result = ["Non-KSU"]
        elif k == "OFFICIAL":
            result = ["KSU"]
        elif k == "NEXT":
            result = ["KSUN"]
        elif k == "SUKI":
            result = ["SUKISU"]
        else:
            log(f"Unknown KernelSU variant {self.ksu!r}", "error")
            return ["UNKNOWN"]

        if self.susfs:
            result.append("SUSFS")

        if self.lxc:
            result.append("LXC")
        return result

    @property
    def suffix(self) -> str:
        return f"-{'-'.join(self.variant_name)}" if self.variant_name else "-UNKNOWN"


if __name__ == "__main__":
    raise SystemExit("This file is meant to be imported, not executed.")
