import os
import random

import pytest

import gevent

from geth.wrapper import spawn_geth

from geth.utils.dag import is_dag_generated


@pytest.mark.skipif(
    'TEST_DAG_WAIT' not in os.environ,
    reason="'TEST_DAG_WAIT' environment variable is not set",
)
def test_waiting_for_dag_generation(base_dir):
    assert not is_dag_generated(base_dir=base_dir)

    command, proc = spawn_geth(dict(
        data_dir=base_dir,
        suffix_args=['makedag', '0', base_dir],
    ))

    assert not is_dag_generated(base_dir=base_dir)

    with gevent.Timeout(600):
        while True:
            if is_dag_generated(base_dir=base_dir):
                break
            gevent.sleep(random.random())

    assert proc.poll() is not None
    assert proc.returncode == 0
