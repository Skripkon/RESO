from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from .utils import clear_generated_data, try_editing, try_generation


EXTENSIONS = ['.mid', '.mp3']


def test_lstm_1(get_ip: str, get_port: int, get_driver: webdriver.Chrome):
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
    try_generation(generate_button, WebDriverWait(driver, 90), EXTENSIONS)


def test_lstm_2(get_ip: str, get_port: int, get_driver: webdriver.Chrome):
    ip, port, driver = get_ip, get_port, get_driver
    driver.get(f'http://{ip}:{port}/generate/neural')

    generate_button = driver.find_element(by=By.ID, value="GenerateNeuralMusic")
    duration_select = Select(driver.find_element(by=By.ID, value="DurationOfTheTrack"))
    tempo_select = Select(driver.find_element(by=By.ID, value="TempoOfTheTrack"))
    composer_select = Select(driver.find_element(by=By.ID, value="Composer"))
    correct_scale = driver.find_element(by=By.ID, value="NeuroCorrectScale")

    duration_select.select_by_visible_text("00:30")
    tempo_select.select_by_visible_text("Slow")
    composer_select.select_by_visible_text("Chopin")
    correct_scale.click()

    clear_generated_data()
    try_generation(generate_button, WebDriverWait(driver, 90), EXTENSIONS)


def test_lstm_3(get_ip: str, get_port: int, get_driver: webdriver.Chrome):
    ip, port, driver = get_ip, get_port, get_driver
    driver.get(f'http://{ip}:{port}/generate/neural')

    generate_button = driver.find_element(by=By.ID, value="GenerateNeuralMusic")
    composer_select = Select(driver.find_element(by=By.ID, value="Composer"))
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
    composer_select.select_by_visible_text("Bach")
    correct_scale.click()

    clear_generated_data()
    try_generation(generate_button, WebDriverWait(driver, 90), EXTENSIONS)

    edit_button.click()
    start_time.send_keys(Keys.BACKSPACE * 2 + "05")
    end_time.send_keys(Keys.BACKSPACE * 2 + "25")
    add_fades.click()
    fade_in.send_keys(Keys.BACKSPACE + "3")
    fade_out.send_keys(Keys.BACKSPACE + "6")

    try_editing(render_button, WebDriverWait(driver, 20))
    sleep(3)
    clear_generated_data()
