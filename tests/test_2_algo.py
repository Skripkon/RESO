import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait


def clear_generated_data():
    for file in [f for f in os.listdir('generated_data') if not f.startswith('.')]:
        os.remove(os.path.join('generated_data', file))


def check_generated_files(wait_mp3_file_time: int = 30):
    """
    Checks whether all 4 files generated. Since wav to mp3 conversion take quite some time,
    function check_iteration() that actually checks all 4 files is invoked in a loop with a
    cooldown of ITERATION_TIME seconds until wait_mp3_file_time has passed (fails the test)
    or the mp3 file has been found.
    """
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
    """Check whether the edited mp3 file has been saved."""
    for file in os.listdir('generated_data'):
        if file.startswith('edited_') and file.endswith('.mp3'):
            return
    raise FileNotFoundError


def try_generation(generate_button: WebElement, wait: WebDriverWait):
    generate_button.click()
    wait.until(EC.element_to_be_clickable(generate_button))
    check_generated_files()
    sleep(2)


def try_editing(render_button: WebElement, wait: WebDriverWait):
    render_button.click()
    wait.until(EC.element_to_be_clickable(render_button))
    check_edited_file()


def test_algo_ok(get_ip: str, get_port: int, get_driver: webdriver.Chrome):
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

    try_editing(render_button, wait)
    clear_generated_data()
