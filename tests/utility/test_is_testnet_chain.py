import pytest
import os

from pygeth.chain import is_testnet_chain


@pytest.mark.parametrize(
    'platform,data_dir,should_be_testnet',
    (
        ("darwin", "~", False),
        ("darwin", "~/Library/Ethereum/testnet", True),
        ("linux2", "~", False),
        ("linux2", "~/.ethereum/testnet", True),
    ),
)
def test_is_testnet_chain(monkeypatch, platform, data_dir, should_be_testnet):
    monkeypatch.setattr('sys.platform', platform)
    if platform == "win32":
        monkeypatch.setattr('os.path.sep', '\\')

    expanded_data_dir = os.path.expanduser(data_dir)
    relative_data_dir = os.path.relpath(expanded_data_dir)

    assert is_testnet_chain(data_dir) is should_be_testnet
    assert is_testnet_chain(expanded_data_dir) is should_be_testnet
    assert is_testnet_chain(relative_data_dir) is should_be_testnet

