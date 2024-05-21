import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait


class NeuroGenerationError(Exception):
    pass


def clear_generated_data():
    for file in [f for f in os.listdir('generated_data') if not f.startswith('.')]:
        os.remove(os.path.join('generated_data', file))


def check_generated_files(wait_mp3_file_time: int = 40):
    """
    Checks whether all 2 files generated. Since wav to mp3 conversion take quite some time,
    function check_iteration() that actually checks all 2 files is invoked in a loop with a
    cooldown of ITERATION_TIME seconds until wait_mp3_file_time has passed (fails the test)
    or the mp3 file has been found.
    """
    def check_iteration():
        extensions = ['.mid', '.mp3']
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
            raise NeuroGenerationError("Didn't find some generated files.")
        tries += 1
        sleep(ITERATION_TIME)


def check_edited_file():
    """Check whether the edited mp3 file has been saved."""
    for file in os.listdir('generated_data'):
        if file.startswith('edited_') and file.endswith('.mp3'):
            return
    raise NeuroGenerationError("Track editing failed.")


def try_generation(generate_button: WebElement, wait: WebDriverWait):
    """Try to edit a track and raise an exception if failed."""
    generate_button.click()
    wait.until(EC.element_to_be_clickable(generate_button))
    check_generated_files()
    sleep(2)


def try_editing(render_button: WebElement, wait: WebDriverWait):
    """Try to edit a track and raise an exception if failed."""
    render_button.click()
    wait.until(EC.element_to_be_clickable(render_button))
    check_edited_file()


def test_neuro_1(get_ip: str, get_port: int, get_driver: webdriver.Chrome):
    ip, port, driver = get_ip, get_port, get_driver

    driver.get(f'http://{ip}:{port}/')
    driver.find_element(by=By.ID, value="startButton").click()
    driver.find_element(by=By.ID, value="neuroEngine").click()

    generate_button = driver.find_element(by=By.ID, value="GenerateNeuralMusic")
    duration_select = Select(driver.find_element(by=By.ID, value="DurationOfTheTrack"))
    tempo_select = Select(driver.find_element(by=By.ID, value="TempoOfTheTrack"))

    duration_select.select_by_visible_text("00:30")
    tempo_select.select_by_visible_text("Slow")

    clear_generated_data()
    try_generation(generate_button, WebDriverWait(driver, 90))


def test_neuro_2(get_ip: str, get_port: int, get_driver: webdriver.Chrome):
    ip, port, driver = get_ip, get_port, get_driver
    driver.get(f'http://{ip}:{port}/generate/neural')

    generate_button = driver.find_element(by=By.ID, value="GenerateNeuralMusic")
    duration_select = Select(driver.find_element(by=By.ID, value="DurationOfTheTrack"))
    tempo_select = Select(driver.find_element(by=By.ID, value="TempoOfTheTrack"))
    generator_select = Select(driver.find_element(by=By.ID, value="NeuralGenerator"))
    correct_scale = driver.find_element(by=By.ID, value="NeuroCorrectScale")

    duration_select.select_by_visible_text("00:30")
    tempo_select.select_by_visible_text("Slow")
    generator_select.select_by_visible_text("Chopin")
    correct_scale.click()

    clear_generated_data()
    try_generation(generate_button, WebDriverWait(driver, 90))


def test_neuro_3(get_ip: str, get_port: int, get_driver: webdriver.Chrome):
    ip, port, driver = get_ip, get_port, get_driver
    driver.get(f'http://{ip}:{port}/generate/neural')

    generate_button = driver.find_element(by=By.ID, value="GenerateNeuralMusic")
    generator_select = Select(driver.find_element(by=By.ID, value="NeuralGenerator"))
    duration_select = Select(driver.find_element(by=By.ID, value="DurationOfTheTrack"))
    tempo_select = Select(driver.find_element(by=By.ID, value="TempoOfTheTrack"))
    correct_scale = driver.find_element(by=By.ID, value="NeuroCorrectScale")
    edit_button = driver.find_element(by=By.ID, value="EditNeuroTrackButton")
    start_time = driver.find_element(by=By.ID, value="NeuroStartTime")
    end_time = driver.find_element(by=By.ID, value="NeuroEndTime")
    add_fades = driver.find_element(by=By.ID, value="NeuroAddFades")
    fade_in = driver.find_element(by=By.ID, value="NeuroFadeInTime")
    fade_out = driver.find_element(by=By.ID, value="NeuroFadeOutTime")
    render_button = driver.find_element(by=By.ID, value="EditNeuroRenderButton")

    duration_select.select_by_visible_text("00:30")
    tempo_select.select_by_visible_text("Slow")
    generator_select.select_by_visible_text("Bach")
    correct_scale.click()

    clear_generated_data()
    try_generation(generate_button, WebDriverWait(driver, 90))

    edit_button.click()
    start_time.send_keys(Keys.BACKSPACE * 2 + "05")
    end_time.send_keys(Keys.BACKSPACE * 2 + "25")
    add_fades.click()
    fade_in.send_keys(Keys.BACKSPACE + "3")
    fade_out.send_keys(Keys.BACKSPACE + "6")

    try_editing(render_button, WebDriverWait(driver, 20))
    sleep(3)
    clear_generated_data()
