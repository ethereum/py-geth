import pytest

from geth import (
    get_geth_version
)


@pytest.fixture
def _amend_geth_overrides_for_1_9(overrides=None):
    version = get_geth_version()

    if version.major == 1:
        if version.minor == 9 or version.minor == 10:
            return {'allow_insecure_unlock': True}
    elif version.major != 1 or version.minor < 9:
        raise Exception('Unsupported geth version. Please choose a version between 1.9.14 and 2.0.0')
