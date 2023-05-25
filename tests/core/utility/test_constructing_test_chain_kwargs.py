import contextlib
import os
import shutil
import tempfile

from geth.wrapper import (
    construct_test_chain_kwargs,
    get_max_socket_path_length,
)


@contextlib.contextmanager
def tempdir():
    directory = tempfile.mkdtemp()

    try:
        yield directory
    finally:
        shutil.rmtree(directory)


def test_short_data_directory_paths_use_local_geth_ipc_socket():
    with tempdir() as data_dir:
        expected_path = os.path.abspath(os.path.join(data_dir, "geth.ipc"))
        assert len(expected_path) < get_max_socket_path_length()
        chain_kwargs = construct_test_chain_kwargs(data_dir=data_dir)

        assert chain_kwargs["ipc_path"] == expected_path


def test_long_data_directory_paths_use_tempfile_geth_ipc_socket():
    with tempdir() as temp_directory:
        data_dir = os.path.abspath(
            os.path.join(
                temp_directory,
                "this-path-is-longer-than-the-maximum-unix-socket-path-length",
                "and-thus-the-underlying-function-should-not-use-it-for-the",
                "geth-ipc-path",
            )
        )
        data_dir_ipc_path = os.path.abspath(os.path.join(data_dir, "geth.ipc"))
        assert len(data_dir_ipc_path) > get_max_socket_path_length()

        chain_kwargs = construct_test_chain_kwargs(data_dir=data_dir)

        assert chain_kwargs["ipc_path"] != data_dir_ipc_path
