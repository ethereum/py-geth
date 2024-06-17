from __future__ import (
    annotations,
)

import codecs
import textwrap
from typing import (
    Any,
)


def force_text_maybe(value: bytes | bytearray | str | None) -> str | None:
    if isinstance(value, (bytes, bytearray)):
        return codecs.decode(value, "utf8")
    elif isinstance(value, str) or value is None:
        return value
    else:
        raise PyGethTypeError(f"Unsupported type: {type(value)}")


class PyGethException(Exception):
    """
    Exception mixin inherited by all exceptions of py-geth

    This allows::

        try:
            some_call()
        except PyGethException:
            # deal with py-geth exception
        except:
            # deal with other exceptions
    """

    user_message: str | None = None

    def __init__(
        self,
        *args: Any,
        user_message: str | None = None,
    ):
        super().__init__(*args)

        # Assign properties of PyGethException
        self.user_message = user_message


class GethError(Exception):
    message = "An error occurred during execution"

    def __init__(
        self,
        command: list[str],
        return_code: int,
        stdin_data: str | bytes | bytearray | None = None,
        stdout_data: str | bytes | bytearray | None = None,
        stderr_data: str | bytes | bytearray | None = None,
        message: str | None = None,
    ):
        if message is not None:
            self.message = message
        self.command = command
        self.return_code = return_code
        self.stdin_data = force_text_maybe(stdin_data)
        self.stderr_data = force_text_maybe(stderr_data)
        self.stdout_data = force_text_maybe(stdout_data)

    def __str__(self) -> str:
        return textwrap.dedent(
            f"""
        {self.message}
        > command: `{" ".join(self.command)}`
        > return code: `{self.return_code}`
        > stderr:
        {self.stdout_data}
        > stdout:
        {self.stderr_data}
        """
        ).strip()


class PyGethGethError(PyGethException, GethError):
    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ):
        GethError.__init__(*args, **kwargs)


class PyGethAttributeError(PyGethException, AttributeError):
    pass


class PyGethKeyError(PyGethException, KeyError):
    pass


class PyGethTypeError(PyGethException, TypeError):
    pass


class PyGethValueError(PyGethException, ValueError):
    pass


class PyGethOSError(PyGethException, OSError):
    pass


class PyGethNotImplementedError(PyGethException, NotImplementedError):
    pass


class PyGethFileNotFoundError(PyGethException, FileNotFoundError):
    pass
