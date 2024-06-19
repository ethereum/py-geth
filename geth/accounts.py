from __future__ import (
    annotations,
)

import os
import re

from typing_extensions import (
    Unpack,
)

from geth.exceptions import (
    PyGethValueError,
)
from geth.types import (
    GethKwargsTypedDict,
)
from geth.utils.validation import (
    validate_geth_kwargs,
)

from .utils.proc import (
    format_error_message,
)
from .wrapper import (
    spawn_geth,
)


def get_accounts(
    **geth_kwargs: Unpack[GethKwargsTypedDict],
) -> tuple[str, ...] | tuple[()]:
    """
    Returns all geth accounts as tuple of hex encoded strings

    >>> get_accounts(data_dir='some/data/dir')
    ... ('0x...', '0x...')
    """
    validate_geth_kwargs(geth_kwargs)

    if not geth_kwargs.get("data_dir"):
        raise PyGethValueError("data_dir is required to get accounts")

    geth_kwargs["suffix_args"] = ["account", "list"]

    command, proc = spawn_geth(geth_kwargs)
    stdoutdata, stderrdata = proc.communicate()

    if proc.returncode:
        if "no keys in store" in stderrdata.decode():
            return tuple()
        else:
            raise PyGethValueError(
                format_error_message(
                    "Error trying to list accounts",
                    command,
                    proc.returncode,
                    stdoutdata.decode(),
                    stderrdata.decode(),
                )
            )
    accounts = parse_geth_accounts(stdoutdata)
    return accounts


account_regex = re.compile(b"([a-f0-9]{40})")


def create_new_account(**geth_kwargs: Unpack[GethKwargsTypedDict]) -> str:
    r"""
    Creates a new Ethereum account on geth.

    This is useful for testing when you want to stress
    interaction (transfers) between Ethereum accounts.

    This command communicates with ``geth`` command over
    terminal interaction. It creates keystore folder and new
    account there.

    This function only works against offline geth processes,
    because geth builds an account cache when starting up.
    If geth process is already running you can create new
    accounts using
    `web3.personal.newAccount()
    <https://geth.ethereum.org/docs/interacting-with-geth/rpc/ns-personal>_`

    RPC API.

    Example pytest fixture for tests:

    .. code-block:: python

        import os

        from geth.wrapper import DEFAULT_PASSWORD_PATH
        from geth.accounts import create_new_account


        @pytest.fixture
        def target_account() -> str:
            '''Create a new Ethereum account on a running Geth node.

            The account can be used as a withdrawal target for tests.

            :return: 0x address of the account
            '''

            # We store keystore files in the current working directory
            # of the test run
            data_dir = os.getcwd()

            # Use the default password "this-is-not-a-secure-password"
            # as supplied in geth/default_blockchain_password file.
            # The supplied password must be bytes, not string,
            # as we only want ASCII characters and do not want to
            # deal encoding problems with passwords
            account = create_new_account(data_dir, DEFAULT_PASSWORD_PATH)
            return account

    :param \**geth_kwargs:
        Command line arguments to pass to geth. See below:

    :Required Keyword Arguments:
        * *data_dir* (``str``) --
          Geth datadir path - where to keep "keystore" folder
        * *password* (``str`` or ``bytes``) --
          Password to use for the new account, either the password as bytes or a str
          path to a file containing the password.

    :return: Account as 0x prefixed hex string
    :rtype: str
    """
    if not geth_kwargs.get("data_dir"):
        raise PyGethValueError("data_dir is required to create a new account")

    if not geth_kwargs.get("password"):
        raise PyGethValueError("password is required to create a new account")

    password = geth_kwargs.get("password")

    geth_kwargs.update({"suffix_args": ["account", "new"]})
    validate_geth_kwargs(geth_kwargs)

    if isinstance(password, str):
        if not os.path.exists(password):
            raise PyGethValueError(f"Password file not found at path: {password}")
    elif not isinstance(password, bytes):
        raise PyGethValueError(
            "Password must be either a str (path to a file) or bytes"
        )

    command, proc = spawn_geth(geth_kwargs)

    if isinstance(password, str):
        stdoutdata, stderrdata = proc.communicate()
    else:
        stdoutdata, stderrdata = proc.communicate(b"\n".join((password, password)))

    if proc.returncode:
        raise PyGethValueError(
            format_error_message(
                "Error trying to create a new account",
                command,
                proc.returncode,
                stdoutdata.decode(),
                stderrdata.decode(),
            )
        )

    match = account_regex.search(stdoutdata)
    if not match:
        raise PyGethValueError(
            format_error_message(
                "Did not find an address in process output",
                command,
                proc.returncode,
                stdoutdata.decode(),
                stderrdata.decode(),
            )
        )

    return "0x" + match.groups()[0].decode()


def ensure_account_exists(**geth_kwargs: Unpack[GethKwargsTypedDict]) -> str:
    if not geth_kwargs.get("data_dir"):
        raise PyGethValueError("data_dir is required to get accounts")

    validate_geth_kwargs(geth_kwargs)
    accounts = get_accounts(**geth_kwargs)
    if not accounts:
        account = create_new_account(**geth_kwargs)
    else:
        account = accounts[0]
    return account


def parse_geth_accounts(raw_accounts_output: bytes) -> tuple[str, ...]:
    accounts = account_regex.findall(raw_accounts_output)
    accounts_set = set(accounts)  # remove duplicates
    return tuple("0x" + account.decode() for account in accounts_set)
