import os
import re

from .wrapper import spawn_geth
from .utils.proc import format_error_message
from .chain import (
    get_genesis_file_path,
    is_live_chain,
    is_testnet_chain,
    write_genesis_file,
)


def get_accounts(data_dir, **geth_kwargs):
    """
    Returns all geth accounts as tuple of hex encoded strings

    >>> geth_accounts()
    ... ('0x...', '0x...')
    """
    command, proc = spawn_geth(dict(
        data_dir=data_dir,
        suffix_args=['account', 'list'],
        **geth_kwargs
    ))
    stdoutdata, stderrdata = proc.communicate()

    if proc.returncode:
        if "no keys in store" in stderrdata:
            return tuple()
        else:
            raise ValueError(format_error_message(
                "Error trying to list accounts",
                command,
                proc.returncode,
                stdoutdata,
                stderrdata,
            ))
    accounts = parse_geth_accounts(stdoutdata)
    return accounts


account_regex = re.compile(b'\{([a-f0-9]{40})\}')


def create_new_account(data_dir, password, **geth_kwargs):
    if os.path.exists(password):
        geth_kwargs['password'] = password

    command, proc = spawn_geth(dict(
        data_dir=data_dir,
        suffix_args=['account', 'new'],
        **geth_kwargs
    ))

    if os.path.exists(password):
        stdoutdata, stderrdata = proc.communicate()
    else:
        stdoutdata, stderrdata = proc.communicate(b"\n".join((password, password)))

    if proc.returncode:
        raise ValueError(format_error_message(
            "Error trying to create a new account",
            command,
            proc.returncode,
            stdoutdata,
            stderrdata,
        ))

    match = account_regex.search(stdoutdata)
    if not match:
        raise ValueError(format_error_message(
            "Did not find an address in process output",
            command,
            proc.returncode,
            stdoutdata,
            stderrdata,
        ))

    return b'0x' + match.groups()[0]


def ensure_account_exists(data_dir, **geth_kwargs):
    accounts = get_accounts(data_dir, **geth_kwargs)
    if not accounts:
        account = create_new_account(data_dir, **geth_kwargs)
        genesis_file_path = get_genesis_file_path(data_dir)

        should_write_genesis = not any((
            os.path.exists(genesis_file_path),
            is_live_chain(data_dir),
            is_testnet_chain(data_dir),
        ))
        if should_write_genesis:
            write_genesis_file(
                genesis_file_path,
                alloc=dict([
                    (account, "1000000000000000000000000000"),  # 1 billion ether.
                ]),
            )
    else:
        account = accounts[0]
    return account


def parse_geth_accounts(raw_accounts_output):
    accounts = account_regex.findall(raw_accounts_output)
    return tuple(b'0x' + account for account in accounts)
