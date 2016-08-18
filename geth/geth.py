import os
import random

import gevent
from gevent import subprocess
from gevent import socket
from gevent import monkey

# required for urllib use
monkey.patch_socket()

try:
    from urllib.request import (
        urlopen,
        URLError,
    )
except ImportError:
    from urllib2 import (
        urlopen,
        URLError,
    )

from .utils.networking import (  # noqa: E402
    get_ipc_socket,
)
from .utils.dag import (  # noqa: E402
    is_dag_generated,
)
from .utils.proc import (  # noqa: E402
    kill_proc,
)
from .accounts import (  # noqa: E402
    ensure_account_exists,
    get_accounts,
)
from .wrapper import (  # noqa: E402
    construct_test_chain_kwargs,
    construct_popen_command,
)
from .chain import (  # noqa: E402
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

        self.proc = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def __enter__(self):
        self.start()
        return self

    def stop(self):
        if not self.is_running:
            raise ValueError("Not running")

        if self.proc.poll() is None:
            kill_proc(self.proc)

        self.is_running = False

    def __exit__(self, *exc_info):
        self.stop()

    @property
    def is_alive(self):
        return self.is_running and self.proc.poll() is None

    @property
    def is_stopped(self):
        return self.proc is not None and self.proc.poll() is not None

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
    def is_rpc_ready(self):
        try:
            urlopen("http://{0}:{1}".format(
                self.rpc_host,
                self.rpc_port,
            ))
        except URLError:
            return False
        else:
            return True

    def wait_for_rpc(self, timeout=0):
        if not self.rpc_enabled:
            raise ValueError("RPC interface is not enabled")

        with gevent.Timeout(timeout):
            while True:
                if self.is_rpc_ready:
                    break
                gevent.sleep(random.random())

    @property
    def ipc_enabled(self):
        return not self.geth_kwargs.get('ipc_disable', None)

    @property
    def ipc_path(self):
        return self.geth_kwargs.get(
            'ipc_path',
            os.path.abspath(os.path.expanduser(os.path.join(
                self.data_dir, 'geth.ipc',
            )))
        )

    @property
    def is_ipc_ready(self):
        try:
            with get_ipc_socket(self.ipc_path):
                pass
        except socket.error:
            return False
        else:
            return True

    def wait_for_ipc(self, timeout=0):
        if not self.ipc_enabled:
            raise ValueError("IPC interface is not enabled")

        with gevent.Timeout(timeout):
            while True:
                if self.is_ipc_ready:
                    break
                gevent.sleep(random.random())

    @property
    def is_dag_generated(self):
        return is_dag_generated()

    @property
    def is_mining(self):
        return self.geth_kwargs.get('mine', False)

    def wait_for_dag(self, timeout=0):
        if not self.is_mining and not self.geth_kwargs.get('autodag', False):
            raise ValueError("Geth not configured to generate DAG")

        with gevent.Timeout(timeout):
            while True:
                if self.is_dag_generated:
                    break
                gevent.sleep(random.random())


class LiveGethProcess(BaseGethProcess):
    def __init__(self, geth_kwargs=None):
        if geth_kwargs is None:
            geth_kwargs = {}

        if 'data_dir' in geth_kwargs:
            raise ValueError("You cannot specify `data_dir` for a LiveGethProcess")

        super(LiveGethProcess, self).__init__(geth_kwargs)

    @property
    def data_dir(self):
        return get_live_data_dir()


class TestnetGethProcess(BaseGethProcess):
    def __init__(self, geth_kwargs=None):
        if geth_kwargs is None:
            geth_kwargs = {}

        if 'data_dir' in geth_kwargs:
            raise ValueError("You cannot specify `data_dir` for a TestnetGethProces")

        suffix_kwargs = geth_kwargs.get('suffix_kwargs', [])
        suffix_kwargs.append('--testnet')

        geth_kwargs['suffix_kwargs'] = suffix_kwargs

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

        self.data_dir = get_chain_data_dir(base_dir, chain_name)
        geth_kwargs = construct_test_chain_kwargs(
            data_dir=self.data_dir,
            **overrides
        )

        # ensure that an account is present
        coinbase = ensure_account_exists(**geth_kwargs)

        # ensure that the chain is initialized
        genesis_file_path = get_genesis_file_path(self.data_dir)

        needs_init = all((
            not os.path.exists(genesis_file_path),
            not is_live_chain(self.data_dir),
            not is_testnet_chain(self.data_dir),
        ))

        if needs_init:
            genesis_data = {
                'alloc': dict([
                    (coinbase, {"balance": "1000000000000000000000000000000"}),  # 1 billion ether.
                ]),
            }
            initialize_chain(genesis_data, **geth_kwargs)

        super(DevGethProcess, self).__init__(geth_kwargs)
