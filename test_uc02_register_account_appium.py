import os
import time

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


APPIUM_SERVER = "http://127.0.0.1:4723"
SCREENSHOT_DIR = os.path.abspath(os.path.join(os.getcwd(), "screenshots"))
APP_PACKAGE = "com.adamarbain.dengueeyemobileapp"
APP_ACTIVITY = ".MainActivity"
VALID_PASSWORD = "Password1"
DUPLICATE_EMAIL = "admin1@drone4dengue.com"


def save_evidence(driver, filename):
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    driver.save_screenshot(os.path.join(SCREENSHOT_DIR, filename))


def find_text(driver, text, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((AppiumBy.XPATH, f"//*[contains(@text, '{text}')]"))
    )


def tap_text(driver, text, timeout=10):
    find_text(driver, text, timeout).click()


def get_inputs(driver):
    return driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")


def open_register_screen(driver):
    time.sleep(2)
    if driver.find_elements(AppiumBy.XPATH, "//*[contains(@text, 'Create Account')]"):
        return
    if driver.find_elements(AppiumBy.XPATH, "//*[contains(@text, 'Sign Up')]"):
        tap_text(driver, "Sign Up")
    find_text(driver, "Create Account", timeout=15)


def clear_and_type(element, value):
    element.click()
    element.clear()
    element.send_keys(value)


def fill_mobile_register_form(driver, email):
    inputs = get_inputs(driver)
    if len(inputs) < 3:
        pytest.fail(f"Expected at least 3 registration fields, found {len(inputs)}.")
    clear_and_type(inputs[0], email)
    clear_and_type(inputs[1], VALID_PASSWORD)
    clear_and_type(inputs[2], VALID_PASSWORD)
    tap_text(driver, "I agree")


def submit_mobile_register_form(driver):
    tap_text(driver, "Create Account")


@pytest.fixture
def driver():
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = "emulator-5554"
    options.app_package = APP_PACKAGE
    options.app_activity = APP_ACTIVITY
    options.no_reset = True
    driver = webdriver.Remote(APPIUM_SERVER, options=options)
    yield driver
    driver.quit()


def test_tc_uc02_04_invalid_email_missing_at_mobile(driver):
    open_register_screen(driver)
    fill_mobile_register_form(driver, "newuser.drone4dengue.com")
    submit_mobile_register_form(driver)
    find_text(driver, "Please enter a valid email address", timeout=10)
    save_evidence(driver, "TC-UC02-04_invalid_email_rejected_mobile.png")
    assert driver.find_elements(AppiumBy.XPATH, "//*[contains(@text, 'Create Account')]")


def test_tc_uc02_05_duplicate_email_mobile(driver):
    open_register_screen(driver)
    fill_mobile_register_form(driver, DUPLICATE_EMAIL)
    submit_mobile_register_form(driver)
    find_text(driver, "Email already exists", timeout=20)
    save_evidence(driver, "TC-UC02-05_duplicate_email_rejected_mobile.png")
    assert driver.find_elements(AppiumBy.XPATH, "//*[contains(@text, 'Create Account')]")


def test_tc_uc02_06_username_boundary_values_mobile(driver):
    open_register_screen(driver)
    inputs = get_inputs(driver)
    save_evidence(driver, "TC-UC02-06_username_field_missing_mobile.png")
    if len(inputs) < 4:
        pytest.xfail("Mobile registration screen has no username field, so TC-UC02-06 cannot be executed on mobile.")
    pytest.fail("Unexpected username field found. Update this script to execute username boundary attempts.")

