from geth import (
    DevGethProcess,
)


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
