import json
import os

from geth import (
    DevGethProcess,
)

# open genesis.json file from geth main directory
MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

with open(os.path.join(MAIN_DIR, "geth", "genesis.json")) as genesis_file:
    GENESIS_JSON = json.load(genesis_file)


def test_with_no_overrides(base_dir):
    geth = DevGethProcess("testing", base_dir=base_dir)

    geth.start()
    assert geth.is_running
    assert geth.is_alive
    geth.stop()
    assert geth.is_stopped


def test_dev_geth_process_generates_accounts(base_dir):
    geth = DevGethProcess("testing", base_dir=base_dir)
    assert len(set(geth.accounts)) == 1


def test_dev_geth_process_generates_genesis_json_from_genesis_data(base_dir):
    shanghai_genesis = GENESIS_JSON.copy()
    config = shanghai_genesis.pop("config")

    # stop at Shanghai, drop any keys in config after `shanghaiTime`
    shanghai_config = {}
    for key, _value in config.items():
        shanghai_config[key] = config[key]
        if key == "shanghaiTime":
            break

    assert "cancunTime" not in shanghai_config
    shanghai_genesis["config"] = shanghai_config

    geth = DevGethProcess("testing", base_dir=base_dir, genesis_data=shanghai_genesis)

    # assert genesis.json exists and has the correct data
    assert os.path.exists(os.path.join(geth.data_dir, "genesis.json"))
    with open(os.path.join(geth.data_dir, "genesis.json")) as genesis_file:
        genesis_data = json.load(genesis_file)

    assert genesis_data == shanghai_genesis

    geth.start()
    assert geth.is_running
    assert geth.is_alive
    geth.stop()
    assert geth.is_stopped
