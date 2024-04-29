from __future__ import (
    annotations,
)

import signal
import subprocess
import time
from typing import (
    AnyStr,
)

from .timeout import (
    Timeout,
)


def wait_for_popen(proc: subprocess.Popen[AnyStr], timeout: int = 30) -> None:
    try:
        with Timeout(timeout) as _timeout:
            while proc.poll() is None:
                time.sleep(0.1)
                _timeout.check()
    except Timeout:
        pass


def kill_proc(proc: subprocess.Popen[AnyStr]) -> None:
    try:
        if proc.poll() is None:
            try:
                proc.send_signal(signal.SIGINT)
                wait_for_popen(proc, 30)
            except KeyboardInterrupt:
                print(
                    "Trying to close geth process.  Press Ctrl+C 2 more times "
                    "to force quit"
                )
        if proc.poll() is None:
            try:
                proc.terminate()
                wait_for_popen(proc, 10)
            except KeyboardInterrupt:
                print(
                    "Trying to close geth process.  Press Ctrl+C 1 more times "
                    "to force quit"
                )
        if proc.poll() is None:
            proc.kill()
            wait_for_popen(proc, 2)
    except KeyboardInterrupt:
        proc.kill()


def format_error_message(
    prefix: str, command: list[str], return_code: int, stdoutdata: str, stderrdata: str
) -> str:
    lines = [prefix]

    lines.append(f"Command    : {' '.join(command)}")
    lines.append(f"Return Code: {return_code}")

    if stdoutdata:
        lines.append(f"stdout:\n`{stdoutdata}`")
    else:
        lines.append("stdout: N/A")

    if stderrdata:
        lines.append(f"stderr:\n`{stderrdata}`")
    else:
        lines.append("stderr: N/A")

    return "\n".join(lines)
