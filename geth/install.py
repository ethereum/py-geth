"""
Install geth
"""
import contextlib
import functools
import os
import stat
import subprocess
import sys
import tarfile

V1_11_0 = "v1.11.0"
V1_11_1 = "v1.11.1"
V1_11_2 = "v1.11.2"
V1_11_3 = "v1.11.3"
V1_11_4 = "v1.11.4"
V1_11_5 = "v1.11.5"
V1_11_6 = "v1.11.6"
V1_12_0 = "v1.12.0"
V1_12_1 = "v1.12.1"
V1_12_2 = "v1.12.2"
V1_13_0 = "v1.13.0"
V1_13_1 = "v1.13.1"
V1_13_2 = "v1.13.2"
V1_13_3 = "v1.13.3"
V1_13_4 = "v1.13.4"
V1_13_5 = "v1.13.5"
V1_13_6 = "v1.13.6"
V1_13_7 = "v1.13.7"
V1_13_8 = "v1.13.8"
V1_13_9 = "v1.13.9"
V1_13_10 = "v1.13.10"
V1_13_11 = "v1.13.11"
V1_13_12 = "v1.13.12"
V1_13_13 = "v1.13.13"
V1_13_14 = "v1.13.14"


LINUX = "linux"
OSX = "darwin"
WINDOWS = "win32"


#
# System utilities.
#
@contextlib.contextmanager
def chdir(path):
    original_path = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original_path)


def get_platform():
    if sys.platform.startswith("linux"):
        return LINUX
    elif sys.platform == OSX:
        return OSX
    elif sys.platform == WINDOWS:
        return WINDOWS
    else:
        raise KeyError(f"Unknown platform: {sys.platform}")


def is_executable_available(program):
    def is_exe(fpath):
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


def ensure_path_exists(dir_path):
    """
    Make sure that a path exists
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        return True
    return False


def ensure_parent_dir_exists(path):
    ensure_path_exists(os.path.dirname(path))


def check_subprocess_call(
    command, message=None, stderr=subprocess.STDOUT, **proc_kwargs
):
    if message:
        print(message)
    print(f"Executing: {' '.join(command)}")

    return subprocess.check_call(command, stderr=stderr, **proc_kwargs)


def check_subprocess_output(
    command, message=None, stderr=subprocess.STDOUT, **proc_kwargs
):
    if message:
        print(message)
    print(f"Executing: {' '.join(command)}")

    return subprocess.check_output(command, stderr=stderr, **proc_kwargs)


def chmod_plus_x(executable_path):
    current_st = os.stat(executable_path)
    os.chmod(executable_path, current_st.st_mode | stat.S_IEXEC)


def get_go_executable_path():
    return os.environ.get("GO_BINARY", "go")


def is_go_available():
    return is_executable_available(get_go_executable_path())


#
#  Installation filesystem path utilities
#
def get_base_install_path(identifier):
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


def get_source_code_archive_path(identifier):
    return os.path.join(
        get_base_install_path(identifier),
        "release.tar.gz",
    )


def get_source_code_extract_path(identifier):
    return os.path.join(
        get_base_install_path(identifier),
        "source",
    )


def get_source_code_path(identifier):
    return os.path.join(
        get_base_install_path(identifier),
        "source",
        f"go-ethereum-{identifier.lstrip('v')}",
    )


def get_build_path(identifier):
    source_code_path = get_source_code_path(identifier)
    return os.path.join(
        source_code_path,
        "build",
    )


def get_built_executable_path(identifier):
    build_path = get_build_path(identifier)
    return os.path.join(
        build_path,
        "bin",
        "geth",
    )


def get_executable_path(identifier):
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


def download_source_code_release(identifier):
    download_uri = DOWNLOAD_SOURCE_CODE_URI_TEMPLATE.format(identifier)
    source_code_archive_path = get_source_code_archive_path(identifier)

    ensure_parent_dir_exists(source_code_archive_path)

    command = [
        "wget",
        download_uri,
        "-c",  # resume previously incomplete download.
        "-O",
        source_code_archive_path,
    ]

    return check_subprocess_call(
        command,
        message=f"Downloading source code release from {download_uri}",
    )


def extract_source_code_release(identifier):
    source_code_archive_path = get_source_code_archive_path(identifier)

    source_code_extract_path = get_source_code_extract_path(identifier)
    ensure_path_exists(source_code_extract_path)

    print(
        f"Extracting archive: {source_code_archive_path} -> {source_code_extract_path}"
    )

    with tarfile.open(source_code_archive_path, "r:gz") as archive_file:

        def is_within_directory(directory, target):
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)

            prefix = os.path.commonprefix([abs_directory, abs_target])

            return prefix == abs_directory

        def safe_extract(tar, path="."):
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")

            tar.extractall(path)

        safe_extract(archive_file, source_code_extract_path)


def build_from_source_code(identifier):
    if not is_go_available():
        raise OSError(
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
        raise OSError(
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
            raise OSError(f"Non-symlink file already present at `{executable_path}`")
    os.symlink(built_executable_path, executable_path)
    chmod_plus_x(executable_path)


def install_from_source_code_release(identifier):
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


install_v1_11_0 = functools.partial(install_from_source_code_release, V1_11_0)
install_v1_11_1 = functools.partial(install_from_source_code_release, V1_11_1)
install_v1_11_2 = functools.partial(install_from_source_code_release, V1_11_2)
install_v1_11_3 = functools.partial(install_from_source_code_release, V1_11_3)
install_v1_11_4 = functools.partial(install_from_source_code_release, V1_11_4)
install_v1_11_5 = functools.partial(install_from_source_code_release, V1_11_5)
install_v1_11_6 = functools.partial(install_from_source_code_release, V1_11_6)
install_v1_12_0 = functools.partial(install_from_source_code_release, V1_12_0)
install_v1_12_1 = functools.partial(install_from_source_code_release, V1_12_1)
install_v1_12_2 = functools.partial(install_from_source_code_release, V1_12_2)
install_v1_13_0 = functools.partial(install_from_source_code_release, V1_13_0)
install_v1_13_1 = functools.partial(install_from_source_code_release, V1_13_1)
install_v1_13_2 = functools.partial(install_from_source_code_release, V1_13_2)
install_v1_13_3 = functools.partial(install_from_source_code_release, V1_13_3)
install_v1_13_4 = functools.partial(install_from_source_code_release, V1_13_4)
install_v1_13_5 = functools.partial(install_from_source_code_release, V1_13_5)
install_v1_13_6 = functools.partial(install_from_source_code_release, V1_13_6)
install_v1_13_7 = functools.partial(install_from_source_code_release, V1_13_7)
install_v1_13_8 = functools.partial(install_from_source_code_release, V1_13_8)
install_v1_13_9 = functools.partial(install_from_source_code_release, V1_13_9)
install_v1_13_10 = functools.partial(install_from_source_code_release, V1_13_10)
install_v1_13_11 = functools.partial(install_from_source_code_release, V1_13_11)
install_v1_13_12 = functools.partial(install_from_source_code_release, V1_13_12)
install_v1_13_13 = functools.partial(install_from_source_code_release, V1_13_13)
install_v1_13_14 = functools.partial(install_from_source_code_release, V1_13_14)


INSTALL_FUNCTIONS = {
    LINUX: {
        V1_11_0: install_v1_11_0,
        V1_11_1: install_v1_11_1,
        V1_11_2: install_v1_11_2,
        V1_11_3: install_v1_11_3,
        V1_11_4: install_v1_11_4,
        V1_11_5: install_v1_11_5,
        V1_11_6: install_v1_11_6,
        V1_12_0: install_v1_12_0,
        V1_12_1: install_v1_12_1,
        V1_12_2: install_v1_12_2,
        V1_13_0: install_v1_13_0,
        V1_13_1: install_v1_13_1,
        V1_13_2: install_v1_13_2,
        V1_13_3: install_v1_13_3,
        V1_13_4: install_v1_13_4,
        V1_13_5: install_v1_13_5,
        V1_13_6: install_v1_13_6,
        V1_13_7: install_v1_13_7,
        V1_13_8: install_v1_13_8,
        V1_13_9: install_v1_13_9,
        V1_13_10: install_v1_13_10,
        V1_13_11: install_v1_13_11,
        V1_13_12: install_v1_13_12,
        V1_13_13: install_v1_13_13,
        V1_13_14: install_v1_13_14,
    },
    OSX: {
        V1_11_0: install_v1_11_0,
        V1_11_1: install_v1_11_1,
        V1_11_2: install_v1_11_2,
        V1_11_3: install_v1_11_3,
        V1_11_4: install_v1_11_4,
        V1_11_5: install_v1_11_5,
        V1_11_6: install_v1_11_6,
        V1_12_0: install_v1_12_0,
        V1_12_1: install_v1_12_1,
        V1_12_2: install_v1_12_2,
        V1_13_0: install_v1_13_0,
        V1_13_1: install_v1_13_1,
        V1_13_2: install_v1_13_2,
        V1_13_3: install_v1_13_3,
        V1_13_4: install_v1_13_4,
        V1_13_5: install_v1_13_5,
        V1_13_6: install_v1_13_6,
        V1_13_7: install_v1_13_7,
        V1_13_8: install_v1_13_8,
        V1_13_9: install_v1_13_9,
        V1_13_10: install_v1_13_10,
        V1_13_11: install_v1_13_11,
        V1_13_12: install_v1_13_12,
        V1_13_13: install_v1_13_13,
        V1_13_14: install_v1_13_14,
    },
}


def install_geth(identifier, platform=None):
    if platform is None:
        platform = get_platform()

    if platform not in INSTALL_FUNCTIONS:
        raise ValueError(
            "Installation of go-ethereum is not supported on your platform "
            f"({platform}). Supported platforms are: "
            f"{', '.join(sorted(INSTALL_FUNCTIONS.keys()))}"
        )
    elif identifier not in INSTALL_FUNCTIONS[platform]:
        raise ValueError(
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
