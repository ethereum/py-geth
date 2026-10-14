import subprocess
import sys
import tempfile

import pytest

from geth import install as install_module
from geth.exceptions import (
    PyGethException,
    PyGethOSError,
    PyGethValueError,
)


@pytest.mark.parametrize(
    "platform,executable_name",
    (("linux", "geth"), ("darwin", "geth"), ("win32", "geth.exe")),
)
def test_installation_paths_use_platform_executable_name(
    monkeypatch, tmp_path, platform, executable_name
):
    monkeypatch.setattr(install_module.sys, "platform", platform)
    monkeypatch.setenv("GETH_BASE_INSTALL_PATH", str(tmp_path))

    assert install_module.get_built_executable_path("v1.17.2").endswith(
        str(
            tmp_path.joinpath(
                "geth-v1.17.2",
                "source",
                "go-ethereum-1.17.2",
                "build",
                "bin",
                executable_name,
            )
        )
    )
    assert install_module.get_executable_path("v1.17.2").endswith(
        str(tmp_path.joinpath("geth-v1.17.2", "bin", executable_name))
    )


def test_go_binary_override(monkeypatch):
    monkeypatch.setenv("GO_BINARY", "/custom/go")

    assert install_module.get_go_executable_path() == "/custom/go"


def test_checkout_source_code_release_is_shallow_exact_and_repeatable(
    monkeypatch, tmp_path
):
    repository = tmp_path / "upstream repository"
    repository.mkdir()
    subprocess.check_call(["git", "init", str(repository)])
    subprocess.check_call(
        ["git", "config", "user.email", "test@example.com"], cwd=repository
    )
    subprocess.check_call(["git", "config", "user.name", "Test"], cwd=repository)
    tracked_file = repository / "version.txt"
    tracked_file.write_text("first")
    subprocess.check_call(["git", "add", "version.txt"], cwd=repository)
    subprocess.check_call(["git", "commit", "-m", "first"], cwd=repository)
    subprocess.check_call(["git", "tag", "v1.16.7"], cwd=repository)
    tracked_file.write_text("second")
    subprocess.check_call(["git", "commit", "-am", "second"], cwd=repository)

    install_root = tmp_path / "install path with spaces"
    monkeypatch.setenv("GETH_BASE_INSTALL_PATH", str(install_root))
    monkeypatch.setattr(
        install_module, "SOURCE_CODE_GIT_REPOSITORY", repository.as_uri()
    )
    original_check_call = install_module.check_subprocess_call
    clone_commands = []

    def capture_clone_command(command, **kwargs):
        clone_commands.append(command)
        return original_check_call(command, **kwargs)

    monkeypatch.setattr(install_module, "check_subprocess_call", capture_clone_command)

    install_module.checkout_source_code_release("v1.16.7")
    source_path = install_module.get_source_code_path("v1.16.7")
    first_head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=source_path, text=True
    )
    assert install_module.os.path.isdir(
        install_module.os.path.join(source_path, ".git")
    )
    with open(install_module.os.path.join(source_path, "version.txt")) as version_file:
        assert version_file.read() == "first"
    assert (
        subprocess.check_output(
            ["git", "rev-list", "--count", "HEAD"], cwd=source_path, text=True
        ).strip()
        == "1"
    )
    assert clone_commands[0][0:12] == [
        "git",
        "-c",
        "core.longpaths=true",
        "clone",
        "--config",
        "core.longpaths=true",
        "--depth",
        "1",
        "--branch",
        "v1.16.7",
        "--single-branch",
        repository.as_uri(),
    ]
    assert clone_commands[0][-1].endswith("checkout")
    assert (
        subprocess.check_output(
            ["git", "config", "--get", "core.longpaths"], cwd=source_path, text=True
        ).strip()
        == "true"
    )

    install_module.checkout_source_code_release("v1.16.7")
    assert (
        subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=source_path, text=True
        )
        == first_head
    )


def test_checkout_failure_does_not_publish_partial_source(monkeypatch, tmp_path):
    monkeypatch.setenv("GETH_BASE_INSTALL_PATH", str(tmp_path))

    def fail_clone(command, **kwargs):
        raise subprocess.CalledProcessError(128, command)

    monkeypatch.setattr(install_module, "is_git_available", lambda: True)
    monkeypatch.setattr(install_module, "check_subprocess_call", fail_clone)

    with pytest.raises(PyGethException, match="Unable to check out geth release"):
        install_module.checkout_source_code_release("v0.0.0")

    assert not install_module.os.path.exists(
        install_module.get_source_code_path("v0.0.0")
    )


def test_install_geth_from_github_source(monkeypatch):
    identifier = "v1.16.7"
    with tempfile.TemporaryDirectory(prefix="py-geth ") as temporary_directory:
        install_root = install_module.os.path.join(
            temporary_directory, "installation with spaces"
        )
        monkeypatch.setenv("GETH_BASE_INSTALL_PATH", install_root)

        subprocess.run(
            [sys.executable, "-m", "geth.install", identifier],
            check=True,
            cwd=install_module.os.path.dirname(
                install_module.os.path.dirname(install_module.__file__)
            ),
            env=install_module.os.environ.copy(),
        )

        source = install_module.get_source_code_path(identifier)
        executable = install_module.get_executable_path(identifier)
        assert install_module.os.path.isdir(install_module.os.path.join(source, ".git"))
        assert (
            subprocess.check_output(
                ["git", "rev-parse", "--verify", "HEAD"], cwd=source, text=True
            ).strip()
            == subprocess.check_output(
                ["git", "rev-parse", "--verify", f"refs/tags/{identifier}^{{commit}}"],
                cwd=source,
                text=True,
            ).strip()
        )

        version_output = subprocess.check_output([executable, "version"], text=True)
        assert "Version: 1.16.7" in version_output


@pytest.mark.parametrize("platform", ("linux", "win32"))
def test_build_from_source_code(monkeypatch, tmp_path, platform):
    source_path = tmp_path / "source"
    source_path.mkdir()
    executable_name = "geth.exe" if platform == "win32" else "geth"
    built_executable = source_path / "build" / "bin" / executable_name
    executable = tmp_path / "installed" / "bin" / executable_name
    calls = []

    def build_geth(command, **kwargs):
        calls.append((command, kwargs))
        built_executable.parent.mkdir(parents=True)
        built_executable.write_bytes(b"geth")
        return 0

    monkeypatch.setattr(install_module.sys, "platform", platform)
    monkeypatch.setenv("GO_BINARY", "/custom/go")
    monkeypatch.setattr(install_module, "is_go_available", lambda: True)
    monkeypatch.setattr(
        install_module, "get_source_code_path", lambda identifier: str(source_path)
    )
    monkeypatch.setattr(
        install_module,
        "get_built_executable_path",
        lambda identifier: str(built_executable),
    )
    monkeypatch.setattr(
        install_module, "get_executable_path", lambda identifier: str(executable)
    )
    monkeypatch.setattr(install_module, "check_subprocess_output", build_geth)

    install_module.build_from_source_code("v1.17.2")

    assert len(calls) == 1
    command, kwargs = calls[0]
    assert command == [
        "/custom/go",
        "run",
        "build/ci.go",
        "install",
        "./cmd/geth",
    ]
    assert kwargs["message"] == "Building `geth` binary"
    assert kwargs["env"]["CI"] == "false"
    assert executable.read_bytes() == b"geth"
    assert executable.is_symlink() is (platform != "win32")


def test_build_failure_includes_compiler_output(monkeypatch, tmp_path):
    source_path = tmp_path / "source"
    source_path.mkdir()
    monkeypatch.setattr(install_module, "is_go_available", lambda: True)
    monkeypatch.setattr(
        install_module, "get_source_code_path", lambda identifier: str(source_path)
    )

    def fail_build(command, **kwargs):
        raise subprocess.CalledProcessError(1, command, output=b"compiler error")

    monkeypatch.setattr(install_module, "check_subprocess_output", fail_build)

    with pytest.raises(PyGethException, match="compiler error"):
        install_module.build_from_source_code("v1.16.7")


def test_build_requires_go(monkeypatch):
    monkeypatch.setattr(install_module, "is_go_available", lambda: False)

    with pytest.raises(PyGethOSError, match="`go` runtime was not found"):
        install_module.build_from_source_code("v1.17.2")


def test_install_rejects_unsupported_platform():
    with pytest.raises(PyGethValueError, match="not supported on your platform"):
        install_module.install_geth("v1.17.2", platform="unsupported")


def test_install_rejects_unsupported_version():
    with pytest.raises(PyGethValueError, match="not supported"):
        install_module.install_geth("v0.0.0", platform=install_module.LINUX)


def test_every_platform_supports_the_same_versions():
    linux, osx, windows = (
        install_module.INSTALL_FUNCTIONS[platform]
        for platform in (
            install_module.LINUX,
            install_module.OSX,
            install_module.WINDOWS,
        )
    )
    assert linux.keys() == osx.keys() == windows.keys()
    assert install_module.V1_17_8 in linux
