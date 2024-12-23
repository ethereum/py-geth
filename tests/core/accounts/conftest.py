import pytest
import os

PROJECTS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "projects")


@pytest.fixture
def one_account_data_dir():
    data_dir = os.path.join(PROJECTS_DIR, "test-01")
    return data_dir


@pytest.fixture
def three_account_data_dir():
    data_dir = os.path.join(PROJECTS_DIR, "test-02")
    return data_dir


@pytest.fixture
def no_account_data_dir():
    data_dir = os.path.join(PROJECTS_DIR, "test-03")
    return data_dir
