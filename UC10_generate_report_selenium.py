import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta


# =========================
# SCREENSHOT CONFIG
# =========================
SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "UC10_screenshots")

def screenshot_final(driver, tc_id):
    """Take a full-page screenshot of the final state. Saved as TC_UC10_XX.png"""
    try:
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        h = driver.execute_script("return document.body.scrollHeight")
        h = min(max(h, 900), 6000)
        driver.set_window_size(1440, h)
        time.sleep(0.3)
        filename = f"{tc_id}.png"
        path = os.path.join(SCREENSHOT_DIR, filename)
        driver.save_screenshot(path)
        print(f"   📸 Screenshot saved: {filename}")
        driver.maximize_window()
        time.sleep(0.2)
    except Exception as e:
        print(f"   ⚠️  Screenshot failed: {e}")


# =========================
# FIXTURE
# =========================
@pytest.fixture
def driver():
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )
    driver.maximize_window()
    yield driver
    driver.quit()


@pytest.fixture
def driver_offline():
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )
    driver.maximize_window()
    yield driver
    driver.quit()


# =========================
# DATE HELPERS
# =========================
def get_relative_date(day_type="today", fmt="%Y-%m-%d"):
    if day_type == "yesterday":
        delta = -1
    elif day_type == "tomorrow":
        delta = 1
    else:
        delta = 0
    return (datetime.now() + timedelta(days=delta)).strftime(fmt)


# =========================
# LOGIN
# =========================
def login(driver):
    wait = WebDriverWait(driver, 20)
    driver.get("http://localhost:3000")

    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(
        "testuc10@gmail.com"
    )
    driver.find_element(By.ID, "password").send_keys("Test@123")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    wait.until(EC.url_contains("/dashboard"))
    time.sleep(1)


# =========================
# NAVIGATE TO REPORTS
# =========================
def navigate_to_reports(driver):
    wait = WebDriverWait(driver, 20)

    current_url = driver.current_url
    base = current_url.split("/dashboard")[0] if "/dashboard" in current_url else "http://localhost:3000"
    driver.get(f"{base}/reports")

    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(), 'Report Generation')]")
        )
    )
    time.sleep(1)


# =========================
# FILL DATE INPUT
# =========================
def fill_date(driver, index, date_value):
    """
    Fill the date input at position `index` (0 = Start Date, 1 = End Date).
    date_value must be YYYY-MM-DD.
    """
    date_inputs = driver.find_elements(By.XPATH, "//input[@type='date']")
    assert len(date_inputs) > index, (
        f"Expected at least {index + 1} date input(s), found {len(date_inputs)}"
    )
    inp = date_inputs[index]

    driver.execute_script("arguments[0].scrollIntoView(true);", inp)

    driver.execute_script(
        """
        var nativeInputValueSetter = Object.getOwnPropertyDescriptor(
            window.HTMLInputElement.prototype, 'value'
        ).set;
        nativeInputValueSetter.call(arguments[0], arguments[1]);
        arguments[0].dispatchEvent(new Event('input',  {bubbles: true}));
        arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
        """,
        inp,
        date_value,
    )
    time.sleep(0.3)


# =========================
# GENERATE REPORT
# =========================
def click_generate_report(driver):
    wait = WebDriverWait(driver, 15)
    btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[not(@disabled) and contains(., 'Generate Report')]")
        )
    )
    btn.click()


# =========================
# WAIT FOR REPORT TO FINISH
# =========================
def wait_for_report(driver, timeout=130):
    wait = WebDriverWait(driver, timeout)

    wait.until(
        EC.none_of(
            EC.presence_of_element_located(
                (By.XPATH, "//button[contains(., 'Generating...')]")
            )
        )
    )

    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//*[contains(text(), 'Export Options')]")
        )
    )


# =========================
# ASSERT NO BLOCKING ERROR
# =========================
def assert_no_export_error(driver):
    error_elements = driver.find_elements(
        By.XPATH,
        "//*[contains(@class,'text-red') and contains(text(), 'Export failed')]"
    )
    assert not any(e.is_displayed() for e in error_elements), \
        "Unexpected export error banner found"


# =========================
# TC-UC10-01: VALID DATE RANGE
# =========================
def test_tc_uc10_01(driver):
    login(driver)
    navigate_to_reports(driver)

    start = (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    end   = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")

    fill_date(driver, 0, start)
    fill_date(driver, 1, end)

    click_generate_report(driver)
    wait_for_report(driver)

    export_section = driver.find_element(
        By.XPATH, "//*[contains(text(), 'Export Options')]"
    )
    assert export_section.is_displayed(), \
        "Export Options section should appear after valid report generation"

    view_btns = driver.find_elements(
        By.XPATH, "//button[contains(text(), 'View Details')]"
    )
    enabled = [b for b in view_btns if b.is_enabled()]
    assert len(enabled) >= 1, \
        "At least one 'View Details' button should be enabled after report generation"

    screenshot_final(driver, "TC_UC10_01")


# =========================
# TC-UC10-02: INVERTED DATE RANGE
# =========================
def test_tc_uc10_02(driver):
    login(driver)
    navigate_to_reports(driver)

    start = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")
    end   = (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")

    fill_date(driver, 0, start)
    fill_date(driver, 1, end)

    click_generate_report(driver)

    time.sleep(8)

    error_elements = driver.find_elements(
        By.XPATH, "//*[contains(@class,'text-red-600') or contains(@class,'bg-red-100')]"
    )
    export_sections = driver.find_elements(
        By.XPATH, "//*[contains(text(), 'Export Options')]"
    )

    has_error = any(e.is_displayed() for e in error_elements)
    no_export = not any(e.is_displayed() for e in export_sections)

    screenshot_final(driver, "TC_UC10_02")

    assert has_error or no_export, \
        "Inverted date range should either show an error or not produce a valid report"


# =========================
# TC-UC10-03: DATE RANGE UNTIL YESTERDAY
# =========================
def test_tc_uc10_03(driver):
    login(driver)
    navigate_to_reports(driver)

    start = (datetime.today() - timedelta(days=14)).strftime("%Y-%m-%d")
    end   = get_relative_date("yesterday")

    fill_date(driver, 0, start)
    fill_date(driver, 1, end)

    click_generate_report(driver)
    wait_for_report(driver)

    export_section = driver.find_element(
        By.XPATH, "//*[contains(text(), 'Export Options')]"
    )
    assert export_section.is_displayed(), \
        "Export Options should appear for a date range ending yesterday"

    screenshot_final(driver, "TC_UC10_03")


# =========================
# TC-UC10-04: DATE RANGE UNTIL TODAY
# =========================
def test_tc_uc10_04(driver):
    login(driver)
    navigate_to_reports(driver)

    start = (datetime.today() - timedelta(days=14)).strftime("%Y-%m-%d")
    end   = get_relative_date("today")

    fill_date(driver, 0, start)
    fill_date(driver, 1, end)

    click_generate_report(driver)
    wait_for_report(driver)

    export_section = driver.find_element(
        By.XPATH, "//*[contains(text(), 'Export Options')]"
    )
    assert export_section.is_displayed(), \
        "Report with end date = today should generate successfully"

    screenshot_final(driver, "TC_UC10_04")


# =========================
# TC-UC10-05: DATE RANGE UNTIL TOMORROW
# =========================
def test_tc_uc10_05(driver):
    login(driver)
    navigate_to_reports(driver)

    start = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")
    end   = get_relative_date("tomorrow")

    fill_date(driver, 0, start)
    fill_date(driver, 1, end)

    click_generate_report(driver)

    time.sleep(10)

    error_elements = driver.find_elements(
        By.XPATH, "//*[contains(@class,'text-red-600') or contains(@class,'bg-red-100')]"
    )
    export_sections = driver.find_elements(
        By.XPATH, "//*[contains(text(), 'Export Options')]"
    )

    report_ok = any(e.is_displayed() for e in export_sections)
    has_error = any(e.is_displayed() for e in error_elements)

    assert report_ok or has_error, \
        "Future end date should either succeed gracefully or display a validation error"

    screenshot_final(driver, "TC_UC10_05")


# =========================
# TC-UC10-06: WITHOUT END DATE
# =========================
def test_tc_uc10_06(driver):
    login(driver)
    navigate_to_reports(driver)

    start = (datetime.today() - timedelta(days=14)).strftime("%Y-%m-%d")
    fill_date(driver, 0, start)
    # Intentionally skip End Date

    wait = WebDriverWait(driver, 10)
    btn = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//button[contains(., 'Generate Report')]")
        )
    )

    is_disabled = (
        btn.get_attribute("disabled") is not None
        or "opacity-60" in (btn.get_attribute("class") or "")
    )

    if not is_disabled:
        btn.click()
        time.sleep(3)
        error_els = driver.find_elements(
            By.XPATH,
            "//*[contains(@class,'text-red-600') or contains(@class,'bg-red-100')]"
        )
        has_error = any(e.is_displayed() for e in error_els)
        screenshot_final(driver, "TC_UC10_06")
        assert has_error, \
            "Clicking Generate without end date should show an error message"
    else:
        screenshot_final(driver, "TC_UC10_06")
        assert is_disabled, \
            "Generate Report button must be disabled when end date is missing"


# =========================
# TC-UC10-07: WITHOUT START DATE
# =========================
def test_tc_uc10_07(driver):
    login(driver)
    navigate_to_reports(driver)

    end = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    fill_date(driver, 1, end)
    # Intentionally skip Start Date

    wait = WebDriverWait(driver, 10)
    btn = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//button[contains(., 'Generate Report')]")
        )
    )

    is_disabled = (
        btn.get_attribute("disabled") is not None
        or "opacity-60" in (btn.get_attribute("class") or "")
    )

    if not is_disabled:
        btn.click()
        time.sleep(3)
        error_els = driver.find_elements(
            By.XPATH,
            "//*[contains(@class,'text-red-600') or contains(@class,'bg-red-100')]"
        )
        has_error = any(e.is_displayed() for e in error_els)
        screenshot_final(driver, "TC_UC10_07")
        assert has_error, \
            "Clicking Generate without start date should show an error message"
    else:
        screenshot_final(driver, "TC_UC10_07")
        assert is_disabled, \
            "Generate Report button must be disabled when start date is missing"


# =========================
# TC-UC10-08: NO INTERNET CONDITION
# =========================
def test_tc_uc10_08(driver_offline):
    driver = driver_offline
    login(driver)
    navigate_to_reports(driver)

    start = (datetime.today() - timedelta(days=14)).strftime("%Y-%m-%d")
    end   = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    fill_date(driver, 0, start)
    fill_date(driver, 1, end)

    driver.execute_script(
        """
        window._originalFetch = window.fetch;
        window.fetch = function() {
            return Promise.reject(new TypeError('Network request failed - simulated offline'));
        };
        """
    )

    click_generate_report(driver)

    try:
        error_el = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(
                (By.XPATH,
                 "//*["
                 "contains(@class,'text-red-600') or contains(@class,'bg-red-100')"
                 "]")
            )
        )
        assert error_el.is_displayed(), \
            "An error banner should be visible when the network is offline"

        screenshot_final(driver, "TC_UC10_08")
    finally:
        driver.execute_script(
            "if (window._originalFetch) { window.fetch = window._originalFetch; }"
        )


# =========================
# TC-UC10-09: CHANGE EXPORT FORMAT (PDF then JSON)
# =========================
def test_tc_uc10_09(driver):
    login(driver)
    navigate_to_reports(driver)
    wait = WebDriverWait(driver, 15)

    start = (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    end   = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")

    fill_date(driver, 0, start)
    fill_date(driver, 1, end)

    click_generate_report(driver)
    wait_for_report(driver)

    export_section = driver.find_element(
        By.XPATH, "//*[contains(text(), 'Export Options')]"
    )
    assert export_section.is_displayed(), \
        "Export Options must be visible before testing export buttons"

    # Export as PDF
    pdf_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Export as PDF')]")
        )
    )
    pdf_btn.click()
    time.sleep(4)
    assert_no_export_error(driver)

    screenshot_final(driver, "TC_UC10_09_PDF")

    # Export as JSON
    json_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Export as JSON')]")
        )
    )
    json_btn.click()
    time.sleep(3)
    assert_no_export_error(driver)

    screenshot_final(driver, "TC_UC10_09_JSON")
