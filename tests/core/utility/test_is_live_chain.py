import pytest
import os

from geth.chain import (
    is_live_chain,
)


@pytest.mark.parametrize(
    "platform,data_dir,should_be_live",
    (
        ("darwin", "~", False),
        ("darwin", "~/Library/Ethereum", True),
        ("linux2", "~", False),
        ("linux2", "~/.ethereum", True),
    ),
)
def test_is_live_chain(monkeypatch, platform, data_dir, should_be_live):
    monkeypatch.setattr("sys.platform", platform)
    if platform == "win32":
        monkeypatch.setattr("os.path.sep", "\\")

    expanded_data_dir = os.path.expanduser(data_dir)
    relative_data_dir = os.path.relpath(expanded_data_dir)

    assert is_live_chain(data_dir) is should_be_live
    assert is_live_chain(expanded_data_dir) is should_be_live
    assert is_live_chain(relative_data_dir) is should_be_live
