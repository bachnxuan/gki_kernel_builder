import pytest
from pytest import MonkeyPatch


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: MonkeyPatch):
    for key in ("KSU", "SUSFS", "LXC", "LOCAL_RUN"):
        monkeypatch.delenv(key, raising=False)
