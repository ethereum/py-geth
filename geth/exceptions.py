from __future__ import (
    annotations,
)

import textwrap

from .utils.encoding import (
    force_text,
)


def force_text_maybe(value: str | bytes | bytearray | None) -> str | None:
    if value is not None:
        return force_text(value, "utf8")
    return None


DEFAULT_MESSAGE = "An error occurred during execution"


class GethError(Exception):
    message = DEFAULT_MESSAGE

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
