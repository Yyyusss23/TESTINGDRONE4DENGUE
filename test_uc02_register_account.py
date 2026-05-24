import os
import time

import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


BASE_URL = "http://localhost:3000"
SCREENSHOT_DIR = "screenshots"
VALID_PASSWORD = "Password1"
VALID_PHONE = "60123456789"
DUPLICATE_EMAIL = "admin1@drone4dengue.com"
WINDOW_WIDTH = 1440
WINDOW_HEIGHT = 1800
EVIDENCE_SETTLE_SECONDS = 0.2


def save_evidence(driver, filename):
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    time.sleep(EVIDENCE_SETTLE_SECONDS)
    driver.execute_script("window.scrollTo(0, 0);")
    driver.save_screenshot(os.path.join(SCREENSHOT_DIR, filename))


def save_evidence_if_possible(driver, filename):
    try:
        save_evidence(driver, filename)
        return True
    except WebDriverException:
        return False


def open_register_page(driver):
    driver.get(f"{BASE_URL}/signup")
    wait = WebDriverWait(driver, 20)
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[contains(., 'Create Account')]")))
    wait.until_not(EC.text_to_be_present_in_element((By.ID, "company"), "Loading companies"))


def clear_and_type(driver, field_id, value):
    field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, field_id)))
    field.clear()
    driver.execute_script("arguments[0].value = '';", field)
    field.send_keys(value)


def select_first_company(driver):
    company = Select(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "company"))))
    options = [option for option in company.options if option.get_attribute("value")]
    if not options:
        pytest.fail("No company option is available for registration.")
    company.select_by_value(options[0].get_attribute("value"))


def accept_terms(driver):
    terms_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Accept Terms and Privacy Policy']"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", terms_button)
    driver.execute_script("arguments[0].click();", terms_button)


def fill_register_form(driver, email, username, name="UC Two User", phone=VALID_PHONE):
    clear_and_type(driver, "email", email)
    clear_and_type(driver, "name", name)
    clear_and_type(driver, "username", username)
    clear_and_type(driver, "phone", phone)
    select_first_company(driver)
    clear_and_type(driver, "password", VALID_PASSWORD)
    clear_and_type(driver, "confirmPassword", VALID_PASSWORD)
    accept_terms(driver)


def submit_register_form(driver):
    button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(., 'SIGN UP') or contains(., 'Create Account')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
    driver.execute_script("arguments[0].click();", button)


def page_has_text(driver, *texts):
    lowered = driver.find_element(By.TAG_NAME, "body").text.lower()
    return any(text.lower() in lowered for text in texts)


def wait_for_duplicate_email_error(driver):
    WebDriverWait(driver, 15).until(
        lambda d: page_has_text(d, "already registered", "already exists", "email already")
    )


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument(f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
    driver.implicitly_wait(2)
    yield driver
    driver.quit()


def test_tc_uc02_04_invalid_email_missing_at(driver):
    open_register_page(driver)
    fill_register_form(driver, "newuser.drone4dengue.com", "uc02user04")
    submit_register_form(driver)
    WebDriverWait(driver, 10).until(
        lambda d: page_has_text(d, "please enter a valid email address", "invalid email", "invalid email format")
        or d.execute_script("return document.getElementById('email')?.validationMessage || ''")
    )
    save_evidence(driver, "TC-UC02-04_invalid_email_rejected_web.png")
    assert "/signup" in driver.current_url


def test_tc_uc02_05_duplicate_email(driver):
    open_register_page(driver)
    fill_register_form(driver, DUPLICATE_EMAIL, "uc02dup05", phone="60123456788")
    submit_register_form(driver)
    wait_for_duplicate_email_error(driver)
    save_evidence(driver, "TC-UC02-05_duplicate_email_rejected_web.png")
    assert "/signup" in driver.current_url


def test_tc_uc02_06_username_boundary_values(driver):
    attempts = [
        ("ab", "TC-UC02-06_attempt1_username_2_chars_rejected_web.png", True),
        ("abc", "TC-UC02-06_attempt2_username_3_chars_accepted_web.png", False),
        ("abcd", "TC-UC02-06_attempt3_username_4_chars_accepted_web.png", False),
    ]

    for username, screenshot, should_show_username_error in attempts:
        open_register_page(driver)
        fill_register_form(driver, DUPLICATE_EMAIL, username, phone="60123456787")
        submit_register_form(driver)

        if should_show_username_error:
            WebDriverWait(driver, 10).until(
                lambda d: page_has_text(d, "username must be at least 3 characters")
            )
            save_evidence(driver, screenshot)
            assert page_has_text(driver, "username must be at least 3 characters")
        else:
            wait_for_duplicate_email_error(driver)
            save_evidence(driver, screenshot)
            assert not page_has_text(driver, "username must be at least 3 characters")
