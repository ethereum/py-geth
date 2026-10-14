"""
Install geth
"""

from __future__ import (
    annotations,
)

from collections.abc import (
    Generator,
)
import contextlib
import functools
import os
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
from typing import (
    Any,
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

V1_16_0 = "v1.16.0"
V1_16_1 = "v1.16.1"
V1_16_2 = "v1.16.2"
V1_16_3 = "v1.16.3"
V1_16_4 = "v1.16.4"
V1_16_5 = "v1.16.5"
V1_16_6 = "v1.16.6"
V1_16_7 = "v1.16.7"
V1_16_8 = "v1.16.8"
V1_16_9 = "v1.16.9"
V1_17_0 = "v1.17.0"
V1_17_1 = "v1.17.1"
V1_17_2 = "v1.17.2"
V1_17_3 = "v1.17.3"
V1_17_4 = "v1.17.4"
V1_17_5 = "v1.17.5"
V1_17_6 = "v1.17.6"
V1_17_7 = "v1.17.7"
V1_17_8 = "v1.17.8"


LINUX = "linux"
OSX = "darwin"
WINDOWS = "win32"


#
# System utilities.
#
@contextlib.contextmanager
def chdir(path: str) -> Generator[None]:
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
    return shutil.which(program) is not None


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


def is_git_available() -> bool:
    return is_executable_available("git")


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
        "geth.exe" if get_platform() == WINDOWS else "geth",
    )


def get_executable_path(identifier: str) -> str:
    base_install_path = get_base_install_path(identifier)
    return os.path.join(
        base_install_path,
        "bin",
        "geth.exe" if get_platform() == WINDOWS else "geth",
    )


#
# Installation primitives.
#
DOWNLOAD_SOURCE_CODE_URI_TEMPLATE = (
    "https://github.com/ethereum/go-ethereum/archive/{0}.tar.gz"
)
SOURCE_CODE_GIT_REPOSITORY = "https://github.com/ethereum/go-ethereum.git"


def _source_checkout_matches_identifier(source_path: str, identifier: str) -> bool:
    if not os.path.isdir(os.path.join(source_path, ".git")):
        return False

    try:
        head = subprocess.check_output(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=source_path,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        tag = subprocess.check_output(
            ["git", "rev-parse", "--verify", f"refs/tags/{identifier}^{{commit}}"],
            cwd=source_path,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return False

    return head == tag


def checkout_source_code_release(identifier: str) -> None:
    """Shallow-clone *identifier* into the source path used by the builder."""
    if not identifier:
        raise PyGethValueError("The geth release identifier must not be empty")
    if not is_git_available():
        raise PyGethOSError(
            "The `git` executable was not found but is required to install geth "
            "from source."
        )

    source_path = get_source_code_path(identifier)
    if _source_checkout_matches_identifier(source_path, identifier):
        print(f"Using existing source checkout: {source_path}")
        return

    extract_path = get_source_code_extract_path(identifier)
    ensure_path_exists(extract_path)
    staging_path = tempfile.mkdtemp(prefix=".geth-checkout-", dir=extract_path)
    staged_checkout = os.path.join(staging_path, "checkout")
    previous_source = os.path.join(staging_path, "previous-source")

    try:
        check_subprocess_call(
            [
                "git",
                # Git for Windows otherwise uses the legacy MAX_PATH limit
                # while checking out go-ethereum's deeply nested test files.
                "-c",
                "core.longpaths=true",
                "clone",
                # Persist this for subsequent Git commands in this checkout.
                "--config",
                "core.longpaths=true",
                "--depth",
                "1",
                "--branch",
                identifier,
                "--single-branch",
                SOURCE_CODE_GIT_REPOSITORY,
                staged_checkout,
            ],
            message=f"Checking out geth source release {identifier}",
        )
        if not _source_checkout_matches_identifier(staged_checkout, identifier):
            raise PyGethException(
                f"Git checkout did not resolve to requested geth release {identifier}"
            )

        if os.path.lexists(source_path):
            os.replace(source_path, previous_source)
        try:
            os.replace(staged_checkout, source_path)
        except OSError:
            if os.path.lexists(previous_source):
                os.replace(previous_source, source_path)
            raise
    except subprocess.CalledProcessError as err:
        raise PyGethException(
            f"Unable to check out geth release {identifier!r} from "
            f"{SOURCE_CODE_GIT_REPOSITORY}: {err}"
        ) from err
    except OSError as err:
        raise PyGethOSError(
            f"Unable to prepare the source checkout for geth release "
            f"{identifier!r}: {err}"
        ) from err
    finally:
        shutil.rmtree(staging_path, ignore_errors=True)


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
        ) from e


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
        # go-ethereum reads CI-specific commit variables when CI is enabled.
        # Those variables describe py-geth's checkout, not this go-ethereum
        # checkout, so force its build tooling to derive metadata from .git.
        build_environment = os.environ.copy()
        build_environment["CI"] = "false"
        install_command = [
            get_go_executable_path(),
            "run",
            "build/ci.go",
            "install",
            "./cmd/geth",
        ]

        try:
            check_subprocess_output(
                install_command,
                message="Building `geth` binary",
                env=build_environment,
            )
        except subprocess.CalledProcessError as err:
            output = err.output
            if isinstance(output, bytes):
                output = output.decode(errors="replace")
            raise PyGethException(
                "Unable to build geth from source. Build output:\n"
                f"{output or '(no build output was produced)'}"
            ) from err

    built_executable_path = get_built_executable_path(identifier)
    if not os.path.exists(built_executable_path):
        raise PyGethOSError(
            f"Built executable not found in expected location: {built_executable_path}"
        )
    if get_platform() != WINDOWS:
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
    if get_platform() == WINDOWS:
        shutil.copy2(built_executable_path, executable_path)
    else:
        os.symlink(built_executable_path, executable_path)
        chmod_plus_x(executable_path)


def install_from_source_code_release(identifier: str) -> None:
    checkout_source_code_release(identifier)
    build_from_source_code(identifier)

    executable_path = get_executable_path(identifier)
    assert os.path.exists(executable_path), f"Executable not found @ {executable_path}"

    check_version_command = [executable_path, "version"]

    version_output = check_subprocess_output(
        check_version_command,
        message=f"Checking installed executable version @ {executable_path}",
    )

    print(f"geth successfully installed at: {executable_path}\n\n{version_output}\n\n")


install_v1_16_0 = functools.partial(install_from_source_code_release, V1_16_0)
install_v1_16_1 = functools.partial(install_from_source_code_release, V1_16_1)
install_v1_16_2 = functools.partial(install_from_source_code_release, V1_16_2)
install_v1_16_3 = functools.partial(install_from_source_code_release, V1_16_3)
install_v1_16_4 = functools.partial(install_from_source_code_release, V1_16_4)
install_v1_16_5 = functools.partial(install_from_source_code_release, V1_16_5)
install_v1_16_6 = functools.partial(install_from_source_code_release, V1_16_6)
install_v1_16_7 = functools.partial(install_from_source_code_release, V1_16_7)
install_v1_16_8 = functools.partial(install_from_source_code_release, V1_16_8)
install_v1_16_9 = functools.partial(install_from_source_code_release, V1_16_9)
install_v1_17_0 = functools.partial(install_from_source_code_release, V1_17_0)
install_v1_17_1 = functools.partial(install_from_source_code_release, V1_17_1)
install_v1_17_2 = functools.partial(install_from_source_code_release, V1_17_2)
install_v1_17_3 = functools.partial(install_from_source_code_release, V1_17_3)
install_v1_17_4 = functools.partial(install_from_source_code_release, V1_17_4)
install_v1_17_5 = functools.partial(install_from_source_code_release, V1_17_5)
install_v1_17_6 = functools.partial(install_from_source_code_release, V1_17_6)
install_v1_17_7 = functools.partial(install_from_source_code_release, V1_17_7)
install_v1_17_8 = functools.partial(install_from_source_code_release, V1_17_8)

INSTALL_FUNCTIONS = {
    LINUX: {
        V1_16_0: install_v1_16_0,
        V1_16_1: install_v1_16_1,
        V1_16_2: install_v1_16_2,
        V1_16_3: install_v1_16_3,
        V1_16_4: install_v1_16_4,
        V1_16_5: install_v1_16_5,
        V1_16_6: install_v1_16_6,
        V1_16_7: install_v1_16_7,
        V1_16_8: install_v1_16_8,
        V1_16_9: install_v1_16_9,
        V1_17_0: install_v1_17_0,
        V1_17_1: install_v1_17_1,
        V1_17_2: install_v1_17_2,
        V1_17_3: install_v1_17_3,
        V1_17_4: install_v1_17_4,
        V1_17_5: install_v1_17_5,
        V1_17_6: install_v1_17_6,
        V1_17_7: install_v1_17_7,
        V1_17_8: install_v1_17_8,
    },
    OSX: {
        V1_16_0: install_v1_16_0,
        V1_16_1: install_v1_16_1,
        V1_16_2: install_v1_16_2,
        V1_16_3: install_v1_16_3,
        V1_16_4: install_v1_16_4,
        V1_16_5: install_v1_16_5,
        V1_16_6: install_v1_16_6,
        V1_16_7: install_v1_16_7,
        V1_16_8: install_v1_16_8,
        V1_16_9: install_v1_16_9,
        V1_17_0: install_v1_17_0,
        V1_17_1: install_v1_17_1,
        V1_17_2: install_v1_17_2,
        V1_17_3: install_v1_17_3,
        V1_17_4: install_v1_17_4,
        V1_17_5: install_v1_17_5,
        V1_17_6: install_v1_17_6,
        V1_17_7: install_v1_17_7,
        V1_17_8: install_v1_17_8,
    },
    WINDOWS: {
        V1_16_0: install_v1_16_0,
        V1_16_1: install_v1_16_1,
        V1_16_2: install_v1_16_2,
        V1_16_3: install_v1_16_3,
        V1_16_4: install_v1_16_4,
        V1_16_5: install_v1_16_5,
        V1_16_6: install_v1_16_6,
        V1_16_7: install_v1_16_7,
        V1_16_8: install_v1_16_8,
        V1_16_9: install_v1_16_9,
        V1_17_0: install_v1_17_0,
        V1_17_1: install_v1_17_1,
        V1_17_2: install_v1_17_2,
        V1_17_3: install_v1_17_3,
        V1_17_4: install_v1_17_4,
        V1_17_5: install_v1_17_5,
        V1_17_6: install_v1_17_6,
        V1_17_7: install_v1_17_7,
        V1_17_8: install_v1_17_8,
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
