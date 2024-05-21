import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
    options = Options()
    options.add_argument('--headless=new')  # not to show visual interface
    options.add_argument("window-size=1000,1500")  # to have all buttons 'visible' on screen
    options.add_argument('--no-sandbox')  # to execute as root
    options.add_argument('--disable-dev-shm-usage')  # to avoid memory shortage problem
    webdriver_service = Service()
    max_timeout = pytestconfig.getoption("max_timeout")
    driver = webdriver.Chrome(service=webdriver_service, options=options)
    driver.set_page_load_timeout(max_timeout)
    yield driver
    # print("\nKILLING DRIVER")
    driver.quit()


@pytest.fixture
def get_max_timeout(pytestconfig):
    max_timeout = pytestconfig.getoption("max_timeout")
    yield int(max_timeout)
