import os
from time import sleep

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def clear_generated_data():
    for file in [f for f in os.listdir('generated_data') if not f.startswith('.')]:
        os.remove(os.path.join('generated_data', file))


def check_generated_files(extensions: list[str], wait_mp3_file_time: int = 40):
    """
    Checks whether all 2 files generated. Since wav to mp3 conversion take quite some time,
    function check_iteration() that actually checks all 2 files is invoked in a loop with a
    cooldown of ITERATION_TIME seconds until wait_mp3_file_time has passed (fails the test)
    or the mp3 file has been found.
    """
    def check_iteration():
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
            raise Exception("Didn't find some generated files.")
        tries += 1
        sleep(ITERATION_TIME)


def check_edited_file():
    """Check whether the edited mp3 file has been saved."""
    for file in os.listdir('generated_data'):
        if file.startswith('edited_') and file.endswith('.mp3'):
            return
    raise Exception("Track editing failed.")


def try_generation(generate_button: WebElement, wait: WebDriverWait, extensions: list[str]):
    """Try to edit a track and raise an exception if failed."""
    generate_button.click()
    wait.until(EC.element_to_be_clickable(generate_button))
    check_generated_files(extensions)
    sleep(2)


def try_editing(render_button: WebElement, wait: WebDriverWait):
    """Try to edit a track and raise an exception if failed."""
    render_button.click()
    wait.until(EC.element_to_be_clickable(render_button))
    check_edited_file()
