import pytest
import os

from geth.chain import is_ropsten_chain


@pytest.mark.parametrize(
    'platform,data_dir,should_be_ropsten',
    (
        ("darwin", "~", False),
        ("darwin", "~/Library/Ethereum/ropsten", True),
        ("linux2", "~", False),
        ("linux2", "~/.ethereum/ropsten", True),
    ),
)
def test_is_ropsten_chain(monkeypatch, platform, data_dir, should_be_ropsten):
    monkeypatch.setattr('sys.platform', platform)
    if platform == "win32":
        monkeypatch.setattr('os.path.sep', '\\')

    expanded_data_dir = os.path.expanduser(data_dir)
    relative_data_dir = os.path.relpath(expanded_data_dir)

    assert is_ropsten_chain(data_dir) is should_be_ropsten
    assert is_ropsten_chain(expanded_data_dir) is should_be_ropsten
    assert is_ropsten_chain(relative_data_dir) is should_be_ropsten

