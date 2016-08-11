from geth.geth import LiveGethProcess


def test_live_chain_with_no_overrides():
    geth = LiveGethProcess()

    geth.start()

    geth.wait_for_ipc(30)

    assert geth.is_running
    assert geth.is_alive

    geth.stop()

    assert geth.is_stopped
