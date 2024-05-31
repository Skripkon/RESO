from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from .utils import clear_generated_data, try_editing, try_generation


EXTENSIONS = ['.mid', '.musicxml', '.pdf', '.mp3']


def test_algo_1(get_ip: str, get_port: int, get_driver: webdriver.Chrome):
    ip, port, driver = get_ip, get_port, get_driver

    driver.get(f'http://{ip}:{port}/')
    driver.find_element(by=By.ID, value="startButton").click()
    driver.find_element(by=By.ID, value="algoEngine").click()

    generate_button = driver.find_element(by=By.ID, value="GenerateAlgorithmicMusic")
    duration_select = Select(driver.find_element(by=By.ID, value="DurationOfTheTrack"))
    tempo_select = Select(driver.find_element(by=By.ID, value="TempoOfTheTrack"))
    scale_select = Select(driver.find_element(by=By.ID, value="ScaleOfTheTrack"))

    wait = WebDriverWait(driver, 50)
    clear_generated_data()
    try_generation(generate_button, wait, EXTENSIONS)
    clear_generated_data()

    duration_select.select_by_visible_text("00:30")
    tempo_select.select_by_visible_text("Slow")
    scale_select.select_by_visible_text("F#")

    try_generation(generate_button, wait, EXTENSIONS)
    clear_generated_data()


def test_algo_2(get_ip: str, get_port: int, get_driver: webdriver.Chrome):
    ip, port, driver = get_ip, get_port, get_driver
    driver.get(f'http://{ip}:{port}/generate/algorithmic')

    generate_button = driver.find_element(by=By.ID, value="GenerateAlgorithmicMusic")
    generator_select = Select(driver.find_element(by=By.ID, value="AlgoGenerator"))
    duration_select = Select(driver.find_element(by=By.ID, value="DurationOfTheTrack"))
    tempo_select = Select(driver.find_element(by=By.ID, value="TempoOfTheTrack"))
    scale_select = Select(driver.find_element(by=By.ID, value="ScaleOfTheTrack"))

    generator_select.select_by_visible_text("Waltz")
    duration_select.select_by_visible_text("02:00")
    tempo_select.select_by_visible_text("Fast")
    scale_select.select_by_visible_text("Eb")

    clear_generated_data()
    try_generation(generate_button, WebDriverWait(driver, 50), EXTENSIONS)


def test_algo_3(get_ip: str, get_port: int, get_driver: webdriver.Chrome):
    ip, port, driver = get_ip, get_port, get_driver
    driver.get(f'http://{ip}:{port}/generate/algorithmic')

    generate_button = driver.find_element(by=By.ID, value="GenerateAlgorithmicMusic")
    generator_select = Select(driver.find_element(by=By.ID, value="AlgoGenerator"))
    duration_select = Select(driver.find_element(by=By.ID, value="DurationOfTheTrack"))
    tempo_select = Select(driver.find_element(by=By.ID, value="TempoOfTheTrack"))
    scale_select = Select(driver.find_element(by=By.ID, value="ScaleOfTheTrack"))

    generator_select.select_by_visible_text("Waltz")
    duration_select.select_by_visible_text("00:30")
    tempo_select.select_by_visible_text("Slow")
    scale_select.select_by_visible_text("F#")

    clear_generated_data()
    try_generation(generate_button, WebDriverWait(driver, 50), EXTENSIONS)


def test_algo_4(get_ip: str, get_port: int, get_driver: webdriver.Chrome):
    ip, port, driver = get_ip, get_port, get_driver
    driver.get(f'http://{ip}:{port}/generate/algorithmic')

    generate_button = driver.find_element(by=By.ID, value="GenerateAlgorithmicMusic")
    generator_select = Select(driver.find_element(by=By.ID, value="AlgoGenerator"))
    duration_select = Select(driver.find_element(by=By.ID, value="DurationOfTheTrack"))
    tempo_select = Select(driver.find_element(by=By.ID, value="TempoOfTheTrack"))
    scale_select = Select(driver.find_element(by=By.ID, value="ScaleOfTheTrack"))

    generator_select.select_by_visible_text("Calm Melody")
    duration_select.select_by_visible_text("02:00")
    tempo_select.select_by_visible_text("Normal")
    scale_select.select_by_visible_text("G#")

    clear_generated_data()
    try_generation(generate_button, WebDriverWait(driver, 50), EXTENSIONS)

    edit_button = driver.find_element(by=By.ID, value="EditAlgoTrackButton")
    start_time = driver.find_element(by=By.ID, value="AlgoStartTime")
    end_time = driver.find_element(by=By.ID, value="AlgoEndTime")
    add_fades = driver.find_element(by=By.ID, value="AlgoAddFades")
    fade_in = driver.find_element(by=By.ID, value="AlgoFadeInTime")
    fade_out = driver.find_element(by=By.ID, value="AlgoFadeOutTime")
    render_button = driver.find_element(by=By.ID, value="EditAlgoRenderButton")
    edit_button.click()

    start_time.send_keys(Keys.BACKSPACE * 2 + "05")
    end_time.send_keys(Keys.BACKSPACE * 2 + "25")
    add_fades.click()

    fade_in.send_keys(Keys.BACKSPACE + "3")
    fade_out.send_keys(Keys.BACKSPACE + "6")

    try_editing(render_button, WebDriverWait(driver, 50))


def test_algo_5(get_ip: str, get_port: int, get_driver: webdriver.Chrome):
    ip, port, driver = get_ip, get_port, get_driver
    driver.get(f'http://{ip}:{port}/generate/algorithmic')

    generate_button = driver.find_element(by=By.ID, value="GenerateAlgorithmicMusic")
    generator_select = Select(driver.find_element(by=By.ID, value="AlgoGenerator"))
    duration_select = Select(driver.find_element(by=By.ID, value="DurationOfTheTrack"))
    tempo_select = Select(driver.find_element(by=By.ID, value="TempoOfTheTrack"))
    scale_select = Select(driver.find_element(by=By.ID, value="ScaleOfTheTrack"))

    generator_select.select_by_visible_text("Etude")
    duration_select.select_by_visible_text("02:00")
    tempo_select.select_by_visible_text("Fast")
    scale_select.select_by_visible_text("B")

    clear_generated_data()
    try_generation(generate_button, WebDriverWait(driver, 50), EXTENSIONS)
    sleep(3)
    clear_generated_data()
