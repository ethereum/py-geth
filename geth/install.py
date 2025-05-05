"""
Install geth
"""
from __future__ import (
    annotations,
)

import contextlib
import functools
import os
import stat
import subprocess
import sys
import tarfile
from typing import (
    Any,
    Generator,
)

import requests
from requests.exceptions import (
    ConnectionError,
    HTTPError,
    Timeout,
)

from geth.exceptions import (
    PyGethException,
    PyGethKeyError,
    PyGethOSError,
    PyGethValueError,
)
from geth.types import (
    IO_Any,
)

V1_14_0 = "v1.14.0"
V1_14_2 = "v1.14.2"
V1_14_3 = "v1.14.3"
V1_14_4 = "v1.14.4"
V1_14_5 = "v1.14.5"
V1_14_6 = "v1.14.6"
V1_14_7 = "v1.14.7"
V1_14_8 = "v1.14.8"
V1_14_9 = "v1.14.9"
V1_14_10 = "v1.14.10"
V1_14_11 = "v1.14.11"
V1_14_12 = "v1.14.12"
V1_14_13 = "v1.14.13"
V1_15_0 = "v1.15.0"
V1_15_1 = "v1.15.1"
V1_15_2 = "v1.15.2"
V1_15_3 = "v1.15.3"
V1_15_4 = "v1.15.4"
V1_15_5 = "v1.15.5"
V1_15_6 = "v1.15.6"
V1_15_7 = "v1.15.7"
V1_15_8 = "v1.15.8"
V1_15_9 = "v1.15.9"
V1_15_10 = "v1.15.10"
V1_15_11 = "v1.15.11"


LINUX = "linux"
OSX = "darwin"
WINDOWS = "win32"


#
# System utilities.
#
@contextlib.contextmanager
def chdir(path: str) -> Generator[None, None, None]:
    original_path = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original_path)


def get_platform() -> str:
    if sys.platform.startswith("linux"):
        return LINUX
    elif sys.platform == OSX:
        return OSX
    elif sys.platform == WINDOWS:
        return WINDOWS
    else:
        raise PyGethKeyError(f"Unknown platform: {sys.platform}")


def is_executable_available(program: str) -> bool:
    def is_exe(fpath: str) -> bool:
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath = os.path.dirname(program)
    if fpath:
        if is_exe(program):
            return True
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return True

    return False


def ensure_path_exists(dir_path: str) -> bool:
    """
    Make sure that a path exists
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        return True
    return False


def ensure_parent_dir_exists(path: str) -> None:
    ensure_path_exists(os.path.dirname(path))


def check_subprocess_call(
    command: list[str],
    message: str | None = None,
    stderr: IO_Any = subprocess.STDOUT,
    **proc_kwargs: Any,
) -> int:
    if message:
        print(message)
    print(f"Executing: {' '.join(command)}")

    return subprocess.check_call(command, stderr=stderr, **proc_kwargs)


def check_subprocess_output(
    command: list[str],
    message: str | None = None,
    stderr: IO_Any = subprocess.STDOUT,
    **proc_kwargs: Any,
) -> Any:
    if message:
        print(message)
    print(f"Executing: {' '.join(command)}")

    return subprocess.check_output(command, stderr=stderr, **proc_kwargs)


def chmod_plus_x(executable_path: str) -> None:
    current_st = os.stat(executable_path)
    os.chmod(executable_path, current_st.st_mode | stat.S_IEXEC)


def get_go_executable_path() -> str:
    return os.environ.get("GO_BINARY", "go")


def is_go_available() -> bool:
    return is_executable_available(get_go_executable_path())


#
#  Installation filesystem path utilities
#
def get_base_install_path(identifier: str) -> str:
    if "GETH_BASE_INSTALL_PATH" in os.environ:
        return os.path.join(
            os.environ["GETH_BASE_INSTALL_PATH"],
            f"geth-{identifier}",
        )
    else:
        return os.path.expanduser(
            os.path.join(
                "~",
                ".py-geth",
                f"geth-{identifier}",
            )
        )


def get_source_code_archive_path(identifier: str) -> str:
    return os.path.join(
        get_base_install_path(identifier),
        "release.tar.gz",
    )


def get_source_code_extract_path(identifier: str) -> str:
    return os.path.join(
        get_base_install_path(identifier),
        "source",
    )


def get_source_code_path(identifier: str) -> str:
    return os.path.join(
        get_base_install_path(identifier),
        "source",
        f"go-ethereum-{identifier.lstrip('v')}",
    )


def get_build_path(identifier: str) -> str:
    source_code_path = get_source_code_path(identifier)
    return os.path.join(
        source_code_path,
        "build",
    )


def get_built_executable_path(identifier: str) -> str:
    build_path = get_build_path(identifier)
    return os.path.join(
        build_path,
        "bin",
        "geth",
    )


def get_executable_path(identifier: str) -> str:
    base_install_path = get_base_install_path(identifier)
    return os.path.join(
        base_install_path,
        "bin",
        "geth",
    )


#
# Installation primitives.
#
DOWNLOAD_SOURCE_CODE_URI_TEMPLATE = (
    "https://github.com/ethereum/go-ethereum/archive/{0}.tar.gz"
)


def download_source_code_release(identifier: str) -> None:
    download_uri = DOWNLOAD_SOURCE_CODE_URI_TEMPLATE.format(identifier)
    source_code_archive_path = get_source_code_archive_path(identifier)

    ensure_parent_dir_exists(source_code_archive_path)
    try:
        response = requests.get(download_uri)
        response.raise_for_status()
        with open(source_code_archive_path, "wb") as f:
            f.write(response.content)

        print(f"Downloading source code release from {download_uri}")

    except (HTTPError, Timeout, ConnectionError) as e:
        raise PyGethException(
            f"An error occurred while downloading from {download_uri}: {e}"
        )


def extract_source_code_release(identifier: str) -> None:
    source_code_archive_path = get_source_code_archive_path(identifier)
    source_code_extract_path = get_source_code_extract_path(identifier)
    ensure_path_exists(source_code_extract_path)

    print(
        f"Extracting archive: {source_code_archive_path} -> {source_code_extract_path}"
    )

    with tarfile.open(source_code_archive_path, "r:gz") as archive_file:

        def is_within_directory(directory: str, target: str) -> bool:
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)

            prefix = os.path.commonprefix([abs_directory, abs_target])

            return prefix == abs_directory

        def safe_extract(tar: tarfile.TarFile, path: str = ".") -> None:
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise PyGethException("Attempted Path Traversal in Tar File")

            tar.extractall(path)

        safe_extract(archive_file, source_code_extract_path)


def build_from_source_code(identifier: str) -> None:
    if not is_go_available():
        raise PyGethOSError(
            "The `go` runtime was not found but is required to build geth.  If "
            "the `go` executable is not in your $PATH you can specify the path "
            "using the environment variable GO_BINARY to specify the path."
        )
    source_code_path = get_source_code_path(identifier)

    with chdir(source_code_path):
        make_command = ["make", "geth"]

        check_subprocess_call(
            make_command,
            message="Building `geth` binary",
        )

    built_executable_path = get_built_executable_path(identifier)
    if not os.path.exists(built_executable_path):
        raise PyGethOSError(
            "Built executable not found in expected location: "
            f"{built_executable_path}"
        )
    print(f"Making built binary executable: chmod +x {built_executable_path}")
    chmod_plus_x(built_executable_path)

    executable_path = get_executable_path(identifier)
    ensure_parent_dir_exists(executable_path)
    if os.path.exists(executable_path):
        if os.path.islink(executable_path):
            os.remove(executable_path)
        else:
            raise PyGethOSError(
                f"Non-symlink file already present at `{executable_path}`"
            )
    os.symlink(built_executable_path, executable_path)
    chmod_plus_x(executable_path)


def install_from_source_code_release(identifier: str) -> None:
    download_source_code_release(identifier)
    extract_source_code_release(identifier)
    build_from_source_code(identifier)

    executable_path = get_executable_path(identifier)
    assert os.path.exists(executable_path), f"Executable not found @ {executable_path}"

    check_version_command = [executable_path, "version"]

    version_output = check_subprocess_output(
        check_version_command,
        message=f"Checking installed executable version @ {executable_path}",
    )

    print(f"geth successfully installed at: {executable_path}\n\n{version_output}\n\n")


install_v1_14_0 = functools.partial(install_from_source_code_release, V1_14_0)
install_v1_14_2 = functools.partial(install_from_source_code_release, V1_14_2)
install_v1_14_3 = functools.partial(install_from_source_code_release, V1_14_3)
install_v1_14_4 = functools.partial(install_from_source_code_release, V1_14_4)
install_v1_14_5 = functools.partial(install_from_source_code_release, V1_14_5)
install_v1_14_6 = functools.partial(install_from_source_code_release, V1_14_6)
install_v1_14_7 = functools.partial(install_from_source_code_release, V1_14_7)
install_v1_14_8 = functools.partial(install_from_source_code_release, V1_14_8)
install_v1_14_9 = functools.partial(install_from_source_code_release, V1_14_9)
install_v1_14_10 = functools.partial(install_from_source_code_release, V1_14_10)
install_v1_14_11 = functools.partial(install_from_source_code_release, V1_14_11)
install_v1_14_12 = functools.partial(install_from_source_code_release, V1_14_12)
install_v1_14_13 = functools.partial(install_from_source_code_release, V1_14_13)
install_v1_15_0 = functools.partial(install_from_source_code_release, V1_15_0)
install_v1_15_1 = functools.partial(install_from_source_code_release, V1_15_1)
install_v1_15_2 = functools.partial(install_from_source_code_release, V1_15_2)
install_v1_15_3 = functools.partial(install_from_source_code_release, V1_15_3)
install_v1_15_4 = functools.partial(install_from_source_code_release, V1_15_4)
install_v1_15_5 = functools.partial(install_from_source_code_release, V1_15_5)
install_v1_15_6 = functools.partial(install_from_source_code_release, V1_15_6)
install_v1_15_7 = functools.partial(install_from_source_code_release, V1_15_7)
install_v1_15_8 = functools.partial(install_from_source_code_release, V1_15_8)
install_v1_15_9 = functools.partial(install_from_source_code_release, V1_15_9)
install_v1_15_10 = functools.partial(install_from_source_code_release, V1_15_10)
install_v1_15_11 = functools.partial(install_from_source_code_release, V1_15_11)

INSTALL_FUNCTIONS = {
    LINUX: {
        V1_14_0: install_v1_14_0,
        V1_14_2: install_v1_14_2,
        V1_14_3: install_v1_14_3,
        V1_14_4: install_v1_14_4,
        V1_14_5: install_v1_14_5,
        V1_14_6: install_v1_14_6,
        V1_14_7: install_v1_14_7,
        V1_14_8: install_v1_14_8,
        V1_14_9: install_v1_14_9,
        V1_14_10: install_v1_14_10,
        V1_14_11: install_v1_14_11,
        V1_14_12: install_v1_14_12,
        V1_14_13: install_v1_14_13,
        V1_15_0: install_v1_15_0,
        V1_15_1: install_v1_15_1,
        V1_15_2: install_v1_15_2,
        V1_15_3: install_v1_15_3,
        V1_15_4: install_v1_15_4,
        V1_15_5: install_v1_15_5,
        V1_15_6: install_v1_15_6,
        V1_15_7: install_v1_15_7,
        V1_15_8: install_v1_15_8,
        V1_15_9: install_v1_15_9,
        V1_15_10: install_v1_15_10,
        V1_15_11: install_v1_15_11,
    },
    OSX: {
        V1_14_0: install_v1_14_0,
        V1_14_2: install_v1_14_2,
        V1_14_3: install_v1_14_3,
        V1_14_4: install_v1_14_4,
        V1_14_5: install_v1_14_5,
        V1_14_6: install_v1_14_6,
        V1_14_7: install_v1_14_7,
        V1_14_8: install_v1_14_8,
        V1_14_9: install_v1_14_9,
        V1_14_10: install_v1_14_10,
        V1_14_11: install_v1_14_11,
        V1_14_12: install_v1_14_12,
        V1_14_13: install_v1_14_13,
        V1_15_0: install_v1_15_0,
        V1_15_1: install_v1_15_1,
        V1_15_2: install_v1_15_2,
        V1_15_3: install_v1_15_3,
        V1_15_4: install_v1_15_4,
        V1_15_5: install_v1_15_5,
        V1_15_6: install_v1_15_6,
        V1_15_7: install_v1_15_7,
        V1_15_8: install_v1_15_8,
        V1_15_9: install_v1_15_9,
        V1_15_10: install_v1_15_10,
        V1_15_11: install_v1_15_11,
    },
}


def install_geth(identifier: str, platform: str | None = None) -> None:
    if platform is None:
        platform = get_platform()

    if platform not in INSTALL_FUNCTIONS:
        raise PyGethValueError(
            "Installation of go-ethereum is not supported on your platform "
            f"({platform}). Supported platforms are: "
            f"{', '.join(sorted(INSTALL_FUNCTIONS.keys()))}"
        )
    elif identifier not in INSTALL_FUNCTIONS[platform]:
        raise PyGethValueError(
            f"Installation of geth=={identifier} is not supported. Must be one of "
            f"{', '.join(sorted(INSTALL_FUNCTIONS[platform].keys()))}"
        )

    install_fn = INSTALL_FUNCTIONS[platform][identifier]
    install_fn()


if __name__ == "__main__":
    try:
        identifier = sys.argv[1]
    except IndexError:
        print(
            "Invocation error. Should be invoked as `python -m geth.install <release-tag>`"  # noqa: E501
        )
        sys.exit(1)

    install_geth(identifier)
