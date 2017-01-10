import os
import json
import contextlib

if 'GETH_ASYNC_GEVENT' in os.environ:
    from gevent import monkey
    monkey.patch_socket()

import pytest  # noqa: E402

from geth.utils.encoding import (  # noqa: E402
    force_text,
)


@pytest.fixture
def open_port():
    from geth.utils import get_open_port
    return get_open_port()


@pytest.fixture()
def rpc_client(open_port):
    from testrpc.client.utils import force_obj_to_text

    endpoint = "http://127.0.0.1:{port}".format(port=open_port)

    def make_request(method, params=None):
        global nonce
        nonce += 1  # NOQA
        payload = {
            "id": nonce,
            "jsonrpc": "2.0",
            "method": method,
            "params": params or [],
        }
        payload_data = json.dumps(force_obj_to_text(payload, True))

        if 'GETH_ASYNC_GEVENT' in os.environ:
            from geventhttpclient import HTTPClient
            client = HTTPClient(
                host='127.0.0.1',
                port=open_port,
                connection_timeout=10,
                network_timeout=10,
                headers={
                    'Content-Type': 'application/json',
                },
            )
            with contextlib.closing(client):
                response = client.post('/', body=payload_data)
                response_body = response.read()

            result = json.loads(force_text(response_body))
        else:
            import requests
            response = requests.post(
                endpoint,
                data=payload_data,
                headers={
                    'Content-Type': 'application/json',
                },
            )

            result = response.json()

        if 'error' in result:
            raise AssertionError(result['error'])

        return result['result']

    return make_request


@pytest.fixture()
def data_dir(tmpdir):
    return str(tmpdir.mkdir("data-dir"))


@pytest.fixture()
def base_dir(tmpdir):
    return str(tmpdir.mkdir("base-dir"))
