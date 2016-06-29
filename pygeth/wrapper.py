import os
import functools
import tempfile

from gevent import subprocess

from .utils.networking import (
    is_port_open,
    get_open_port,
)
from .utils.filesystem import (
    is_executable_available,
)


is_nice_available = functools.partial(is_executable_available, 'nice')


PYGETH_DIR = os.path.abspath(os.path.dirname(__file__))


DEFAULT_PASSWORD_PATH = os.path.join(PYGETH_DIR, 'default_blockchain_password')
DEFAULT_GENESIS_PATH = os.path.join(PYGETH_DIR, 'genesis.json')


def construct_test_chain_kwargs(**overrides):
    overrides.setdefault('genesis_path', DEFAULT_GENESIS_PATH)
    overrides.setdefault('unlock', '0')
    overrides.setdefault('password', DEFAULT_PASSWORD_PATH)
    overrides.setdefault('mine', True)
    overrides.setdefault('miner_threads', '1')
    overrides.setdefault('no_discover', True)
    overrides.setdefault('max_peers', '0')
    overrides.setdefault('network_id', '1234')

    if is_port_open(30303):
        overrides.setdefault('port', '30303')
    else:
        overrides.setdefault('port', get_open_port())

    overrides.setdefault('rpc_enabled', True)
    overrides.setdefault('rpc_addr', '127.0.0.1')
    if is_port_open(8545):
        overrides.setdefault('rpc_port', '8545')
    else:
        overrides.setdefault('rpc_port', get_open_port())

    overrides.setdefault('ipc_path', tempfile.NamedTemporaryFile().name)

    overrides.setdefault('verbosity', '5')
    return overrides


def construct_popen_command(data_dir=None,
                            geth_executable="geth",
                            genesis_path=None,
                            max_peers=None,
                            network_id=None,
                            no_discover=None,
                            mine=False,
                            miner_threads=None,
                            nice=True,
                            unlock=None,
                            password=None,
                            port=None,
                            verbosity=None,
                            ipc_path=None,
                            rpc_enabled=None,
                            rpc_addr=None,
                            rpc_port=None,
                            prefix_cmd=None,
                            suffix_args=None,
                            suffix_kwargs=None):
    command = []

    if nice and is_nice_available():
        command.extend(('nice', '-n', '20'))

    command.append(geth_executable)

    if rpc_enabled:
        command.append('--rpc')

    if rpc_addr is not None:
        command.extend(('--rpcaddr', rpc_addr))

    if rpc_port is not None:
        command.extend(('--rpcport', rpc_port))

    if genesis_path is not None:
        command.extend(('--genesis', genesis_path))

    if data_dir is not None:
        command.extend(('--datadir', data_dir))

    if max_peers is not None:
        command.extend(('--maxpeers', max_peers))

    if network_id is not None:
        command.extend(('--networkid', network_id))

    if port is not None:
        command.extend(('--port', port))

    if ipc_path is not None:
        command.extend(('--ipcpath', ipc_path))

    if verbosity is not None:
        command.extend((
            '--verbosity', verbosity,
        ))

    if unlock is not None:
        command.extend((
            '--unlock', unlock,
        ))

    if password is not None:
        command.extend((
            '--password', password,
        ))

    if no_discover:
        command.append('--nodiscover')

    if mine:
        if unlock is None:
            raise ValueError("Cannot mine without an unlocked account")
        command.append('--mine')

    if miner_threads is not None:
        if not mine:
            raise ValueError("`mine` must be truthy when specifying `miner_threads`")
        command.extend(('--minerthreads', miner_threads))

    if suffix_kwargs:
        command.extend(suffix_kwargs)

    if suffix_args:
        command.extend(suffix_args)

    return command


def spawn_geth(geth_kwargs,
               stdin=subprocess.PIPE,
               stdout=subprocess.PIPE,
               stderr=subprocess.PIPE):
    command = construct_popen_command(**geth_kwargs)

    proc = subprocess.Popen(
        command,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        bufsize=1,
    )

    return command, proc
