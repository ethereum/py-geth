from geth import (
    DevGethProcess,
)


def test_using_as_a_context_manager(base_dir):
    geth = DevGethProcess("testing", base_dir=base_dir)

    assert not geth.is_running
    assert not geth.is_alive

    with geth:
        assert geth.is_running
        assert geth.is_alive

    assert geth.is_stopped
