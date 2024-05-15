from multiprocessing import Process
import os
import subprocess
from time import sleep

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


LOG_PATH = os.path.join('tests', 'tmp.txt')
IP = '127.0.0.1'


def background_server(port):
    print(f"\nSTARTING THE SERVER ON PORT {port}...")
    f_err = open(LOG_PATH, 'a', os.O_NONBLOCK)
    command = ['uvicorn', 'main:app', '--host', IP, '--port', str(port)]
    subprocess.run(command, input=b'n', stderr=f_err)


@pytest.fixture(scope='session')
def start_server(pytestconfig):
    port = int(pytestconfig.getoption("port"))
    os.system(f'touch {LOG_PATH}')

    proc = Process(target=background_server, args=(port,), daemon=True)
    proc.start()

    f_err = open(LOG_PATH, 'r', os.O_NONBLOCK)
    log = ''
    while True:
        sleep(2)
        new_log = f_err.read()
        log += new_log
        if new_log:
            print(new_log, end='')
        if "Application shutdown complete." in log:
            print("ERROR")
            port = -1
            break
        if "Application startup complete." in log and "Application shutdown complete." not in log:
            print("SERVER STARTED")
            break
    yield port
    print(f"KILLING SERVER (pid={proc.pid})")
    os.system(f'kill -s INT {proc.pid}')
    sleep(2)
    os.remove(LOG_PATH)


@pytest.fixture
def clear_generated_data():
    for file in [f for f in os.listdir('generated_data') if not f.startswith('.')]:
        os.remove(os.path.join('generated_data', file))


@pytest.fixture
def get_driver():
    chrome_driver_path = os.path.join('tests', 'chromedriver')
    webdriver_service = Service()
    driver = webdriver.Chrome(service=webdriver_service)
    yield driver
    print("\nKILLING DRIVER")
    driver.quit()


@pytest.mark.run_server
def test_algo_1(start_server, clear_generated_data, get_driver):
    port = start_server
    assert port >= 0
    print("STARTING TEST")
    driver: webdriver.Chrome = get_driver
    driver.get(f'http://{IP}:{port}/')


def test_algo_2(get_port, clear_generated_data, get_driver):
    port = get_port
    assert port >= 0
    print("\nSTARTING TEST")
    driver: webdriver.Chrome = get_driver
    driver.get(f'http://{IP}:{port}/')
