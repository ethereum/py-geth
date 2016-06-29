import pytest
import json
import requests


@pytest.fixture
def open_port():
    from pygeth.utils import get_open_port
    return get_open_port()


@pytest.fixture()
def rpc_client(open_port):
    from pygeth.utils.encoding import force_obj_to_text
    endpoint = "http://127.0.0.1:{port}".format(port=open_port)

    def make_request(method, params=None, raise_on_error=True):
        global nonce
        nonce += 1  # NOQA
        payload = {
            "id": nonce,
            "jsonrpc": "2.0",
            "method": method,
            "params": params or [],
        }
        payload_data = json.dumps(force_obj_to_text(payload))
        response = requests.post(endpoint, data=payload_data)

        if raise_on_error:
            assert response.status_code == 200

            result = response.json()

            if 'error' in result:
                raise AssertionError(result['error'])

            assert set(result.keys()) == {"id", "jsonrpc", "result"}
        return response.json()['result']

    return make_request


@pytest.fixture()
def data_dir(tmpdir):
    return str(tmpdir.mkdir("data-dir"))


@pytest.fixture()
def base_dir(tmpdir):
    return str(tmpdir.mkdir("base-dir"))
