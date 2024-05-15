import pytest


def pytest_addoption(parser):
    parser.addoption("--port", action="store", default=8000)


@pytest.fixture
def get_port(pytestconfig):
    port = int(pytestconfig.getoption("port"))
    yield port
