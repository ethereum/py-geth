import json

import pytest
import requests


@pytest.fixture
def open_port():
    from geth.utils import (
        get_open_port,
    )

    return get_open_port()


@pytest.fixture()
def rpc_client(open_port):
    from testrpc.client.utils import (
        force_obj_to_text,
    )

    endpoint = f"http://127.0.0.1:{open_port}"

    def make_request(method, params=None):
        global nonce
        nonce += 1
        payload = {
            "id": nonce,
            "jsonrpc": "2.0",
            "method": method,
            "params": params or [],
        }
        payload_data = json.dumps(force_obj_to_text(payload, True))

        response = requests.post(
            endpoint,
            data=payload_data,
            headers={
                "Content-Type": "application/json",
            },
        )

        result = response.json()

        if "error" in result:
            raise AssertionError(result["error"])

        return result["result"]

    return make_request


@pytest.fixture()
def data_dir(tmpdir):
    return str(tmpdir.mkdir("data-dir"))


@pytest.fixture()
def base_dir(tmpdir):
    return str(tmpdir.mkdir("base-dir"))
