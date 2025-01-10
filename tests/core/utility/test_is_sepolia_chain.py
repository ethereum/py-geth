import pytest
import os

from geth.chain import (
    is_sepolia_chain,
)


@pytest.mark.parametrize(
    "platform,data_dir,should_be_sepolia",
    (
        ("darwin", "~", False),
        ("darwin", "~/Library/Ethereum/sepolia", True),
        ("linux2", "~", False),
        ("linux2", "~/.ethereum/sepolia", True),
    ),
)
def test_is_sepolia_chain(monkeypatch, platform, data_dir, should_be_sepolia):
    monkeypatch.setattr("sys.platform", platform)
    if platform == "win32":
        monkeypatch.setattr("os.path.sep", "\\")

    expanded_data_dir = os.path.expanduser(data_dir)
    relative_data_dir = os.path.relpath(expanded_data_dir)

    assert is_sepolia_chain(data_dir) is should_be_sepolia
    assert is_sepolia_chain(expanded_data_dir) is should_be_sepolia
    assert is_sepolia_chain(relative_data_dir) is should_be_sepolia
