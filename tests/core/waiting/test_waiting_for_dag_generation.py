import os
import time

import pytest

from geth.utils.dag import (
    is_dag_generated,
)
from geth.utils.timeout import (
    Timeout,
)
from geth.wrapper import (
    spawn_geth,
)


@pytest.mark.skipif(
    "TEST_DAG_WAIT" not in os.environ,
    reason="'TEST_DAG_WAIT' environment variable is not set",
)
def test_waiting_for_dag_generation(base_dir):
    assert not is_dag_generated(base_dir=base_dir)

    command, proc = spawn_geth(
        dict(
            data_dir=base_dir,
            suffix_args=["makedag", "0", base_dir],
        )
    )

    assert not is_dag_generated(base_dir=base_dir)

    with Timeout(600) as timeout:
        while True:
            if is_dag_generated(base_dir=base_dir):
                break
            time(0.1)
            timeout.check()

    assert proc.poll() is not None
    assert proc.returncode == 0
