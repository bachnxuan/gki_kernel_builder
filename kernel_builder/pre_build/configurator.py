from pathlib import Path

from sh import Command
from kernel_builder.config.config import VARIANT_JSON, WORKSPACE
from kernel_builder.utils.fs import FileSystem
from kernel_builder.utils.log import log
from kernel_builder.utils.variants_parser import VariantsParser


def _config(
    conf: str, mode: bool, target: Path = WORKSPACE / "out" / ".config"
) -> None:
    config: Command = Command(str(WORKSPACE / "scripts" / "config"))
    config("--file", str(target), "--enable" if mode else "--disable", conf)
    simplified_target: Path = FileSystem.relative_to(WORKSPACE, target)
    log(
        f"{'Enabling' if mode else 'Disabling'} config: {conf} (file={simplified_target})"
    )


def configurator() -> None:
    parser: VariantsParser = VariantsParser(VARIANT_JSON)

    for k, v in parser.config().items():
        _config(k, v)
