import os
import sys
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


ALL_APIS = "admin,debug,eth,miner,net,personal,shh,txpool,web3,ws"


def get_max_socket_path_length():
    if 'UNIX_PATH_MAX' in os.environ:
        return int(os.environ['UNIX_PATH_MAX'])
    if sys.platform.startswith('darwin'):
        return 104
    elif sys.platform.startswith('linux'):
        return 108
    elif sys.platform.startswith('win'):
        return 260


def construct_test_chain_kwargs(**overrides):
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

    overrides.setdefault('ws_enabled', True)
    overrides.setdefault('ws_addr', '127.0.0.1')
    overrides.setdefault('ws_api', ALL_APIS)

    if is_port_open(8546):
        overrides.setdefault('ws_port', '8546')
    else:
        overrides.setdefault('ws_port', get_open_port())

    overrides.setdefault('rpc_enabled', True)
    overrides.setdefault('rpc_addr', '127.0.0.1')
    overrides.setdefault('rpc_api', ALL_APIS)
    if is_port_open(8545):
        overrides.setdefault('rpc_port', '8545')
    else:
        overrides.setdefault('rpc_port', get_open_port())

    if 'ipc_path' not in overrides:
        # try to use a `geth.ipc` within the provided data_dir if the path is
        # short enough.
        if 'data_dir' in overrides:
            max_path_length = get_max_socket_path_length()
            geth_ipc_path = os.path.abspath(os.path.join(
                overrides['data_dir'],
                'geth.ipc'
            ))
            if len(geth_ipc_path) <= max_path_length:
                overrides.setdefault('ipc_path', geth_ipc_path)

        # Otherwise default to a tempfile based ipc path.
        overrides.setdefault(
            'ipc_path',
            os.path.join(tempfile.mkdtemp(), 'geth.ipc'),
        )

    overrides.setdefault('ipc_api', ALL_APIS)

    overrides.setdefault('verbosity', '5')
    return overrides


def construct_popen_command(data_dir=None,
                            geth_executable="geth",
                            max_peers=None,
                            network_id=None,
                            no_discover=None,
                            mine=False,
                            autodag=False,
                            miner_threads=None,
                            nice=True,
                            unlock=None,
                            password=None,
                            port=None,
                            verbosity=None,
                            ipc_disable=None,
                            ipc_path=None,
                            ipc_api=None,
                            rpc_enabled=None,
                            rpc_addr=None,
                            rpc_port=None,
                            rpc_api=None,
                            ws_enabled=None,
                            ws_addr=None,
                            ws_origins=None,
                            ws_port=None,
                            ws_api=None,
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

    if rpc_api is not None:
        command.extend(('--rpcapi', rpc_api))

    if ws_enabled:
        command.append('--ws')

    if ws_addr is not None:
        command.extend(('--wsaddr', ws_addr))

    if ws_origins is not None:
        command.extend(('--wsorigins', ws_port))

    if ws_port is not None:
        command.extend(('--wsport', ws_port))

    if ws_api is not None:
        command.extend(('--wsapi', ws_api))

    if data_dir is not None:
        command.extend(('--datadir', data_dir))

    if max_peers is not None:
        command.extend(('--maxpeers', max_peers))

    if network_id is not None:
        command.extend(('--networkid', network_id))

    if port is not None:
        command.extend(('--port', port))

    if ipc_disable:
        command.append('--ipcdisable')

    if ipc_path is not None:
        command.extend(('--ipcpath', ipc_path))

    if ipc_api is not None:
        command.extend(('--ipcapi', ipc_api))

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

    if autodag:
        command.append('--autodag')

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
