import pytest
import os

import semantic_version

from geth import (
    get_geth_version,
)
from geth.install import (
    INSTALL_FUNCTIONS,
    get_executable_path,
    get_platform,
    install_geth,
)

INSTALLATION_TEST_PARAMS = tuple(
    (platform, version)
    for platform, platform_install_functions in INSTALL_FUNCTIONS.items()
    for version in platform_install_functions.keys()
)


@pytest.mark.skipif(
    "GETH_RUN_INSTALL_TESTS" not in os.environ,
    reason=(
        "Installation tests will not run unless `GETH_RUN_INSTALL_TESTS` "
        "environment variable is set"
    ),
)
@pytest.mark.parametrize(
    "platform,version",
    INSTALLATION_TEST_PARAMS,
)
def test_geth_installation_as_function_call(monkeypatch, tmpdir, platform, version):
    if get_platform() != platform:
        pytest.skip("Wrong platform for install script")

    base_install_path = str(tmpdir.mkdir("temporary-dir"))
    monkeypatch.setenv("GETH_BASE_INSTALL_PATH", base_install_path)

    # sanity check that it's not already installed.
    executable_path = get_executable_path(version)
    assert not os.path.exists(executable_path)

    install_geth(identifier=version, platform=platform)

    assert os.path.exists(executable_path)
    monkeypatch.setenv("GETH_BINARY", executable_path)

    actual_version = get_geth_version()
    expected_version = semantic_version.Spec(version.lstrip("v"))

    assert actual_version in expected_version
