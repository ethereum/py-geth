import os

from gevent import subprocess

from .utils.proc import (
    kill_proc,
)
from .accounts import (
    ensure_account_exists,
    get_accounts,
)
from .wrapper import (
    construct_test_chain_kwargs,
    construct_popen_command,
)
from .chain import (
    get_chain_data_dir,
    get_default_base_dir,
    get_genesis_file_path,
    get_live_data_dir,
    get_testnet_data_dir,
    initialize_chain,
    is_live_chain,
    is_testnet_chain,
)


class BaseGethProcess(object):
    _proc = None

    def __init__(self, geth_kwargs):
        self.geth_kwargs = geth_kwargs
        self.command = construct_popen_command(**geth_kwargs)

    is_running = False

    def start(self):
        if self.is_running:
            raise ValueError("Already running")
        self.is_running = True

        self._proc = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def stop(self):
        if not self.is_running:
            raise ValueError("Not running")

        if self._proc.poll() is None:
            kill_proc(self._proc)

        self.is_running = False

    @property
    def is_alive(self):
        return self.is_running and self._proc.poll() is None

    @property
    def is_stopped(self):
        return self._proc is not None and self._proc.poll() is not None

    @property
    def accounts(self):
        return get_accounts(**self.geth_kwargs)

    @property
    def rpc_enabled(self):
        return self.geth_kwargs.get('rpc_enabled', False)

    @property
    def rpc_host(self):
        return self.geth_kwargs.get('rpc_host', '127.0.0.1')

    @property
    def rpc_port(self):
        return self.geth_kwargs.get('rpc_port', '8545')

    @property
    def ipc_path(self):
        return self.geth_kwargs.get(
            'ipc_path',
            os.path.abspath(os.path.expanduser(os.path.join(
                get_live_data_dir(), 'geth.ipc',
            ))),
        )


class LiveGethProcess(BaseGethProcess):
    def __init__(self, geth_kwargs):
        if 'data_dir' in geth_kwargs:
            raise ValueError("You cannot specify `data_dir` for a LiveGethProcess")

        super(LiveGethProcess, self).__init__(geth_kwargs)

    @property
    def data_dir(self):
        return get_live_data_dir()


class TestnetGethProcess(BaseGethProcess):
    def __init__(self, geth_kwargs):
        if 'data_dir' in geth_kwargs:
            raise ValueError("You cannot specify `data_dir` for a TestnetGethProces")

        extra_kwargs = geth_kwargs.get('extra_kwargs', [])
        extra_kwargs.append('--testnet')

        geth_kwargs['extra_kwargs'] = extra_kwargs

        super(TestnetGethProcess, self).__init__(geth_kwargs)

    @property
    def data_dir(self):
        return get_testnet_data_dir()


class DevGethProcess(BaseGethProcess):
    def __init__(self, chain_name, base_dir=None, overrides=None):
        if overrides is None:
            overrides = {}

        if 'data_dir' in overrides:
            raise ValueError("You cannot specify `data_dir` for a DevGethProcess")

        if base_dir is None:
            base_dir = get_default_base_dir()

        geth_kwargs = construct_test_chain_kwargs(**overrides)
        self.data_dir = get_chain_data_dir(base_dir, chain_name)

        # ensure that an account is present
        coinbase = ensure_account_exists(self.data_dir, **geth_kwargs)

        # ensure that the chain is initialized
        genesis_file_path = get_genesis_file_path(self.data_dir)

        needs_init = tuple((
            not os.path.exists(genesis_file_path),
            not is_live_chain(self.data_dir),
            not is_testnet_chain(self.data_dir),
        ))

        if needs_init or True:
            genesis_data = {
                'alloc': dict([
                    (coinbase, {"balance": "1000000000000000000000000000000"}),  # 1 billion ether.
                ]),
            }
            initialize_chain(genesis_data, self.data_dir, **geth_kwargs)

        geth_kwargs['data_dir'] = self.data_dir

        super(DevGethProcess, self).__init__(geth_kwargs)
