from multiprocessing import Process
import os
import subprocess
from time import sleep

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait


LOG_PATH = os.path.join('tests', 'tmp.txt')


def background_server(ip, port):
    print(f"\nSTARTING THE SERVER ON PORT {port}...")
    f_err = open(LOG_PATH, 'a', os.O_NONBLOCK)
    command = ['uvicorn', 'main:app', '--host', ip, '--port', str(port)]
    subprocess.run(command, input=b'n', stderr=f_err)


@pytest.fixture(scope='session')
def start_server(pytestconfig):
    ip = pytestconfig.getoption("ip")
    port = int(pytestconfig.getoption("port"))
    os.system(f'touch {LOG_PATH}')

    proc = Process(target=background_server, args=(ip, port), daemon=True)
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
    yield ip, port
    print(f"KILLING SERVER (pid={proc.pid})")
    os.system(f'kill -s INT {proc.pid}')
    sleep(2)
    os.remove(LOG_PATH)





def clear_generated_data():
    for file in [f for f in os.listdir('generated_data') if not f.startswith('.')]:
        os.remove(os.path.join('generated_data', file))


def check_generated_files(wait_mp3_file_time: int = 30):
    def check_iteration():
        extensions = ['.mid', '.musicxml', '.pdf', '.mp3']
        generated_files = os.listdir('generated_data')
        for ext in extensions:
            for f in generated_files:
                if f.endswith(ext):
                    break
            else:
                return False
        return True

    ITERATION_TIME = 1
    tries = 0
    while not check_iteration():
        if tries == wait_mp3_file_time // ITERATION_TIME:
            raise FileNotFoundError
        tries += 1
        sleep(ITERATION_TIME)


def check_edited_file():
    for file in os.listdir('generated_data'):
        if file.startswith('edited_') and file.endswith('.mp3'):
            return
    raise FileNotFoundError


def try_generation(generate_button: WebElement, wait: WebDriverWait):
    generate_button.click()
    wait.until(EC.element_to_be_clickable(generate_button))
    check_generated_files()
    sleep(2)


def try_edit(render_button: WebElement, wait: WebDriverWait):
    render_button.click()
    wait.until(EC.element_to_be_clickable(render_button))
    check_edited_file()


@pytest.mark.run_server
def test_algo_1(start_server, clear_generated_data, get_driver: webdriver.Chrome):
    ip, port = start_server
    assert port >= 0
    print("STARTING TEST")
    driver: webdriver.Chrome = get_driver
    driver.get(f'http://{ip}:{port}/')


def test_algo_2(get_port, get_ip, get_driver: webdriver.Chrome):
    print("\nSTARTING TEST")
    ip, port, driver = get_ip, get_port, get_driver

    driver.get(f'http://{ip}:{port}/')
    driver.find_element(by=By.ID, value="startButton").click()
    driver.find_element(by=By.ID, value="algoEngine").click()

    generate_button = driver.find_element(by=By.ID, value="GenerateAlgorithmicMusic")
    generator_select = Select(driver.find_element(by=By.ID, value="AlgoGenerator"))
    duration_select = Select(driver.find_element(by=By.ID, value="DurationOfTheTrack"))
    tempo_select = Select(driver.find_element(by=By.ID, value="TempoOfTheTrack"))
    scale_select = Select(driver.find_element(by=By.ID, value="ScaleOfTheTrack"))
    edit_button = driver.find_element(by=By.ID, value="EditAlgoTrackButton")
    start_time = driver.find_element(by=By.ID, value="AlgoStartTime")
    end_time = driver.find_element(by=By.ID, value="AlgoEndTime")
    add_fades = driver.find_element(by=By.ID, value="AlgoAddFades")
    fade_in = driver.find_element(by=By.ID, value="AlgoFadeInTime")
    fade_out = driver.find_element(by=By.ID, value="AlgoFadeOutTime")
    render_button = driver.find_element(by=By.ID, value="EditAlgoRenderButton")

    wait = WebDriverWait(driver, 50)

    clear_generated_data()
    try_generation(generate_button, wait)

    generator_select.select_by_visible_text("Waltz")
    duration_select.select_by_visible_text("02:00")
    tempo_select.select_by_visible_text("Fast")
    scale_select.select_by_visible_text("Eb")

    clear_generated_data()
    try_generation(generate_button, wait)

    duration_select.select_by_visible_text("00:30")
    tempo_select.select_by_visible_text("Slow")
    scale_select.select_by_visible_text("F#")

    clear_generated_data()
    try_generation(generate_button, wait)

    edit_button.click()
    start_time.send_keys(Keys.BACKSPACE * 2 + "05")
    end_time.send_keys(Keys.BACKSPACE * 2 + "25")
    add_fades.click()
    fade_in.send_keys(Keys.BACKSPACE + "3")
    fade_out.send_keys(Keys.BACKSPACE + "6")

    try_edit(render_button, wait)
    clear_generated_data()
