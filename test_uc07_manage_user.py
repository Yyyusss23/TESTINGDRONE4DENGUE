import json
import os
import tempfile
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


ADMIN_BASE_URL = os.getenv("ADMIN_BASE_URL", "http://localhost:3000")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:4000")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin1@drone4dengue.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "adminpass1")

SCREENSHOT_DIR = Path(__file__).resolve().parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)

RUN_ID = str(int(time.time()))
UC7_EXISTING_EMAIL = os.getenv("UC7_EXISTING_EMAIL", "automation.user@test.com")
UC7_UPDATE_EMAIL = f"uc07.update.{RUN_ID}@example.com"
UC7_DELETE_EMAIL = f"uc07.delete.{RUN_ID}@example.com"
UC7_ADD_EMAIL = f"uc07.add.{RUN_ID}@example.com"
UC7_SEARCH_MISSING = f"uc07.notfound.{RUN_ID}@example.com"

UC7_ORIGINAL_NAME = f"UC7 Original {RUN_ID}"
UC7_UPDATED_NAME = f"UC7 Updated {RUN_ID}"
UC7_CANCEL_NAME = f"UC7 Cancelled {RUN_ID}"
UC7_UPDATED_PHONE = "60123456789"
UC7_UPDATED_ADDRESS = f"UC7 Test Address {RUN_ID}"


def get_chrome_service():
    try:
        return Service(ChromeDriverManager().install())
    except PermissionError:
        driver_root = Path.home() / ".wdm" / "drivers" / "chromedriver" / "win64"
        candidates = sorted(
            driver_root.glob("*/chromedriver-win64/chromedriver.exe"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        if candidates:
            return Service(str(candidates[0]))
        raise


@pytest.fixture
def driver():
    profile_dir = tempfile.TemporaryDirectory()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,982")
    options.add_argument("--force-device-scale-factor=1.5")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-data-dir={profile_dir.name}")

    browser = webdriver.Chrome(service=get_chrome_service(), options=options)
    yield browser
    browser.quit()
    profile_dir.cleanup()


def save_screenshot(driver, evidence_id):
    driver.save_screenshot(str(SCREENSHOT_DIR / f"{evidence_id}.png"))


def api_request(method, path, token=None, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(f"{API_BASE_URL}{path}", data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=30) as response:
            content = response.read().decode("utf-8")
            return response.status, json.loads(content) if content else {}
    except HTTPError as err:
        content = err.read().decode("utf-8")
        return err.code, json.loads(content) if content else {}
    except URLError as err:
        return 0, {"error": str(err)}


def admin_token():
    status, data = api_request(
        "POST",
        "/auth/admin-login",
        body={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    if status == 0:
        pytest.skip(f"API server is not reachable at {API_BASE_URL}: {data.get('error')}")
    assert status == 200, f"Admin API login failed: {status} {data}"
    return data["token"]


def create_seed_user(email, name=UC7_ORIGINAL_NAME, status="Pending"):
    token = admin_token()
    delete_user_by_email(email)
    status_code, data = api_request(
        "POST",
        "/users",
        token=token,
        body={
            "email": email,
            "password": "Password1!",
            "name": name,
            "role": "user",
            "status": status,
        },
    )
    assert status_code == 201, f"Failed to seed user: {status_code} {data}"


def delete_user_by_email(email):
    token = admin_token()
    query = urlencode({"search": email, "limit": 10000, "page": 1})
    status, data = api_request("GET", f"/users?{query}", token=token)
    if status != 200:
        return

    for user in data.get("users", []):
        if user.get("email") == email:
            api_request("DELETE", f"/users/{user['id']}", token=token)


@pytest.fixture(autouse=True)
def cleanup_uc7_users():
    for email in [UC7_UPDATE_EMAIL, UC7_DELETE_EMAIL, UC7_ADD_EMAIL]:
        delete_user_by_email(email)
    yield
    for email in [UC7_UPDATE_EMAIL, UC7_DELETE_EMAIL, UC7_ADD_EMAIL]:
        delete_user_by_email(email)


def body_text(driver):
    return driver.find_element(By.TAG_NAME, "body").text


def wait_for_text(driver, text, timeout=30):
    return WebDriverWait(driver, timeout).until(lambda d: text.lower() in body_text(d).lower())


def wait_until_not_loading(driver):
    WebDriverWait(driver, 30).until(lambda d: "Loading users..." not in body_text(d))


def login_as_admin(driver):
    driver.get(ADMIN_BASE_URL)
    wait = WebDriverWait(driver, 20)

    email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
    password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")))

    email_input.clear()
    email_input.send_keys(ADMIN_EMAIL)
    password_input.clear()
    password_input.send_keys(ADMIN_PASSWORD)

    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "form button[type='submit']"))).click()
    wait.until(lambda d: d.execute_script("return localStorage.getItem('token');"))


def open_user_management(driver):
    driver.get(f"{ADMIN_BASE_URL}/user-management")
    wait = WebDriverWait(driver, 30)
    wait.until(EC.presence_of_element_located((By.XPATH, "//h1[normalize-space()='User Management']")))
    wait.until(EC.presence_of_element_located((By.XPATH, "//*[normalize-space()='User List']")))
    wait_until_not_loading(driver)


def search_user(driver, keyword):
    search_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Search users...']"))
    )
    search_input.send_keys(Keys.CONTROL, "a")
    search_input.send_keys(keyword)
    wait_until_not_loading(driver)


def row_for_email(driver, email, timeout=20):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, f"//tr[.//*[contains(normalize-space(), '{email}')]]"))
    )


def row_absent_for_email(driver, email, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.invisibility_of_element_located((By.XPATH, f"//tr[.//*[contains(normalize-space(), '{email}')]]"))
    )


def open_add_user_modal(driver):
    wait = WebDriverWait(driver, 20)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(), 'Add New User')]"))).click()
    wait.until(EC.presence_of_element_located((By.XPATH, "//h2[normalize-space()='Add New User']")))


def add_user_modal(driver):
    return WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, "//h2[normalize-space()='Add New User']/ancestor::div[contains(@class,'fixed')]")
        )
    )


def fill_add_user_form(driver, email, role="user"):
    modal = add_user_modal(driver)
    email_input = modal.find_element(By.CSS_SELECTOR, "input[type='email']")
    email_input.clear()
    email_input.send_keys(email)
    Select(modal.find_element(By.TAG_NAME, "select")).select_by_value(role)


def submit_add_user(driver):
    modal = add_user_modal(driver)
    button = modal.find_element(By.XPATH, ".//button[contains(normalize-space(), 'Create User')]")
    button.click()


def close_success_dialog(driver):
    wait = WebDriverWait(driver, 20)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Great!']"))).click()
    wait.until_not(EC.presence_of_element_located((By.XPATH, "//h3[normalize-space()='Success!']")))


def open_edit_modal_for_email(driver, email):
    row = row_for_email(driver, email)
    edit_button = row.find_elements(By.CSS_SELECTOR, "td:last-child button")[0]
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", edit_button)
    edit_button.click()
    return WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, "//h2[normalize-space()='Update User']/ancestor::div[contains(@class,'fixed')]")
        )
    )


def set_edit_field(modal, placeholder, value):
    field = modal.find_element(By.XPATH, f".//input[@placeholder='{placeholder}']")
    field.send_keys(Keys.CONTROL, "a")
    field.send_keys(Keys.BACKSPACE)
    if value:
        field.send_keys(value)


def submit_edit_modal(modal):
    modal.find_element(By.XPATH, ".//button[contains(normalize-space(), 'Update User')]").click()


def cancel_modal(modal):
    modal.find_element(By.XPATH, ".//button[normalize-space()='Cancel']").click()


def verify_user(driver, email):
    row = row_for_email(driver, email)
    verify_buttons = row.find_elements(By.XPATH, ".//button[contains(normalize-space(), 'Verify')]")
    assert verify_buttons, f"No Verify button found for {email}"
    verify_buttons[0].click()
    wait_for_text(driver, "Verified")


def open_delete_dialog_for_email(driver, email):
    row = row_for_email(driver, email)
    delete_button = row.find_elements(By.CSS_SELECTOR, "td:last-child button")[-1]
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", delete_button)
    delete_button.click()
    return WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, "//h2[normalize-space()='Delete User']/ancestor::div[contains(@class,'fixed')]")
        )
    )


def confirm_delete(driver):
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//h2[normalize-space()='Delete User']/ancestor::div[contains(@class,'fixed')]"
                "//button[normalize-space()='Delete']",
            )
        )
    ).click()
    wait_for_text(driver, "Success!")
    close_success_dialog(driver)


def test_tc_uc7_01_open_user_management_page(driver):
    login_as_admin(driver)
    open_user_management(driver)
    save_screenshot(driver, "EV-TC-UC7-01-user-management-opened")

    page = body_text(driver)
    assert "User Management" in page
    assert "User List" in page
    assert "Total Users" in page
    assert driver.find_element(By.CSS_SELECTOR, "table").is_displayed()


def test_tc_uc7_02_search_existing_user(driver):
    create_seed_user(UC7_EXISTING_EMAIL, name=f"Automation User {RUN_ID}", status="Verified")
    login_as_admin(driver)
    open_user_management(driver)

    search_user(driver, UC7_EXISTING_EMAIL)
    row_for_email(driver, UC7_EXISTING_EMAIL)
    save_screenshot(driver, "EV-TC-UC7-02-search-existing-user")

    assert UC7_EXISTING_EMAIL in body_text(driver)


def test_tc_uc7_03_search_non_existing_user(driver):
    login_as_admin(driver)
    open_user_management(driver)

    search_user(driver, UC7_SEARCH_MISSING)
    time.sleep(1)
    save_screenshot(driver, "EV-TC-UC7-03-search-no-result")

    page = body_text(driver)
    assert UC7_SEARCH_MISSING not in page
    assert "No users found" in page or "Showing" not in page


def test_tc_uc7_04_add_new_user_with_valid_details(driver):
    login_as_admin(driver)
    open_user_management(driver)

    open_add_user_modal(driver)
    fill_add_user_form(driver, UC7_ADD_EMAIL, role="user")
    submit_add_user(driver)
    wait_for_text(driver, "Success!")
    close_success_dialog(driver)

    search_user(driver, UC7_ADD_EMAIL)
    row_for_email(driver, UC7_ADD_EMAIL)
    save_screenshot(driver, "EV-TC-UC7-04-add-valid-user")

    assert UC7_ADD_EMAIL in body_text(driver)


def test_tc_uc7_05_cancel_add_user_does_not_create_user(driver):
    login_as_admin(driver)
    open_user_management(driver)

    open_add_user_modal(driver)
    fill_add_user_form(driver, UC7_ADD_EMAIL, role="user")
    cancel_modal(add_user_modal(driver))
    WebDriverWait(driver, 20).until_not(
        EC.presence_of_element_located((By.XPATH, "//h2[normalize-space()='Add New User']"))
    )

    search_user(driver, UC7_ADD_EMAIL)
    row_absent_for_email(driver, UC7_ADD_EMAIL)
    save_screenshot(driver, "EV-TC-UC7-05-cancel-add-keeps-list")

    assert UC7_ADD_EMAIL not in body_text(driver)


def test_tc_uc7_06_edit_cancel_then_save_valid_changes(driver):
    create_seed_user(UC7_UPDATE_EMAIL)
    login_as_admin(driver)
    open_user_management(driver)
    search_user(driver, UC7_UPDATE_EMAIL)

    modal = open_edit_modal_for_email(driver, UC7_UPDATE_EMAIL)
    set_edit_field(modal, "Enter full name", UC7_CANCEL_NAME)
    cancel_modal(modal)
    WebDriverWait(driver, 20).until_not(
        EC.presence_of_element_located((By.XPATH, "//h2[normalize-space()='Update User']"))
    )

    search_user(driver, UC7_UPDATE_EMAIL)
    row_for_email(driver, UC7_UPDATE_EMAIL)
    assert UC7_ORIGINAL_NAME in body_text(driver)
    assert UC7_CANCEL_NAME not in body_text(driver)

    modal = open_edit_modal_for_email(driver, UC7_UPDATE_EMAIL)
    set_edit_field(modal, "Enter full name", UC7_UPDATED_NAME)
    set_edit_field(modal, "Enter phone number", UC7_UPDATED_PHONE)
    set_edit_field(modal, "Enter address", UC7_UPDATED_ADDRESS)
    submit_edit_modal(modal)
    WebDriverWait(driver, 20).until_not(
        EC.presence_of_element_located((By.XPATH, "//h2[normalize-space()='Update User']"))
    )

    search_user(driver, UC7_UPDATE_EMAIL)
    wait_for_text(driver, UC7_UPDATED_NAME)
    save_screenshot(driver, "EV-TC-UC7-06-edit-cancel-then-save")

    page = body_text(driver)
    assert UC7_CANCEL_NAME not in page
    assert UC7_UPDATED_NAME in page
    assert UC7_UPDATED_ADDRESS in page
    assert UC7_UPDATED_PHONE in page


def test_tc_uc7_07_required_field_validation(driver):
    create_seed_user(UC7_UPDATE_EMAIL)
    login_as_admin(driver)
    open_user_management(driver)
    search_user(driver, UC7_UPDATE_EMAIL)

    modal = open_edit_modal_for_email(driver, UC7_UPDATE_EMAIL)
    set_edit_field(modal, "Enter full name", "")
    update_button = modal.find_element(By.XPATH, ".//button[contains(normalize-space(), 'Update User')]")
    save_screenshot(driver, "EV-TC-UC7-07-required-field-validation")

    assert not update_button.is_enabled()
    cancel_modal(modal)
    row_for_email(driver, UC7_UPDATE_EMAIL)
    assert UC7_ORIGINAL_NAME in body_text(driver)


def test_tc_uc7_08_invalid_email_validation(driver):
    login_as_admin(driver)
    open_user_management(driver)

    open_add_user_modal(driver)
    fill_add_user_form(driver, "invalidemail", role="user")
    submit_add_user(driver)
    wait_for_text(driver, "Please enter a valid email address")
    save_screenshot(driver, "EV-TC-UC7-08-invalid-email-validation")

    assert "Please enter a valid email address" in body_text(driver)


def test_tc_uc7_09_duplicate_email_validation(driver):
    create_seed_user(UC7_EXISTING_EMAIL, name=f"Automation User {RUN_ID}", status="Verified")
    login_as_admin(driver)
    open_user_management(driver)

    open_add_user_modal(driver)
    fill_add_user_form(driver, UC7_EXISTING_EMAIL, role="user")
    submit_add_user(driver)
    wait_for_text(driver, "Email already registered")
    save_screenshot(driver, "EV-TC-UC7-09-duplicate-email-validation")

    assert "Email already registered" in body_text(driver)


def test_tc_uc7_10_delete_cancel_then_confirm_delete(driver):
    create_seed_user(UC7_DELETE_EMAIL, name=f"UC7 Delete {RUN_ID}")
    login_as_admin(driver)
    open_user_management(driver)
    search_user(driver, UC7_DELETE_EMAIL)

    dialog = open_delete_dialog_for_email(driver, UC7_DELETE_EMAIL)
    cancel_modal(dialog)
    WebDriverWait(driver, 20).until_not(
        EC.presence_of_element_located((By.XPATH, "//h2[normalize-space()='Delete User']"))
    )
    row_for_email(driver, UC7_DELETE_EMAIL)
    assert UC7_DELETE_EMAIL in body_text(driver)

    open_delete_dialog_for_email(driver, UC7_DELETE_EMAIL)
    confirm_delete(driver)
    search_user(driver, UC7_DELETE_EMAIL)
    row_absent_for_email(driver, UC7_DELETE_EMAIL)
    save_screenshot(driver, "EV-TC-UC7-10-delete-cancel-then-confirm")

    assert UC7_DELETE_EMAIL not in body_text(driver)
