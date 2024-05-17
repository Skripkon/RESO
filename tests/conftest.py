import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def pytest_addoption(parser):
    parser.addoption("--ip", action="store", default='127.0.0.1')
    parser.addoption("--port", action="store", default=8000)
    parser.addoption("--max-timeout", action="store", default=10)


@pytest.fixture
def get_ip(pytestconfig):
    ip = pytestconfig.getoption("ip")
    yield ip


@pytest.fixture
def get_port(pytestconfig):
    port = pytestconfig.getoption("port")
    yield int(port)


@pytest.fixture
def get_driver(pytestconfig):
    webdriver_service = Service()
    max_timeout = pytestconfig.getoption("max_timeout")
    driver = webdriver.Chrome(service=webdriver_service)
    driver.set_page_load_timeout(max_timeout)
    yield driver
    print("\nKILLING DRIVER")
    driver.quit()


@pytest.fixture
def get_max_timeout(pytestconfig):
    max_timeout = pytestconfig.getoption("max_timeout")
    yield int(max_timeout)
