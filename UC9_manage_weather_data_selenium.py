import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta


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


# =========================
# LOGIN FUNCTION
# =========================
def login(driver):
    wait = WebDriverWait(driver, 15)

    driver.get("http://localhost:3000")

    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(
        "testuc9@gmail.com"
    )

    driver.find_element(By.ID, "password").send_keys("Test@123")

    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    wait.until(EC.url_contains("/dashboard"))

def get_dates():
    today = datetime.today()

    return {
        "today": today.strftime("%d/%m/%Y"),
        "yesterday": (today - timedelta(days=1)).strftime("%d/%m/%Y"),
        "tomorrow": (today + timedelta(days=1)).strftime("%d/%m/%Y"),
    }

def get_relative_date(day_type="today", format="%d/%m/%Y"):
    if day_type == "yesterday":
        delta = -1
    elif day_type == "tomorrow":
        delta = 1
    else:
        delta = 0

    return (datetime.now() + timedelta(days=delta)).strftime(format)

# =========================
# COMMON VALIDATOR CLASS
# =========================
class UploadValidator:

    @staticmethod
    def assert_invalid_upload(driver, wait):
        expected_error = "failed to process csv file. please check the format."

        # =========================
        # WAIT FIXED 5 SECONDS
        # =========================
        time.sleep(2)

        page_text = driver.page_source.lower()

        if "failed to process" not in page_text:
            time.sleep(3)  # extra buffer before failing
            raise AssertionError(
                "FAILED: Expected error message not shown - "
                "'Failed to process CSV file. Please check the format.'"
            )

        assert expected_error in page_text, \
            f"Unexpected error message found: {page_text}"

        print("Invalid upload correctly rejected")


# =========================
# TC-UC9-01: VALID CSV UPLOAD
# =========================
def test_tc_uc9_01(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    csv_path = r"C:\Users\LENOVO\OneDrive - Universiti Malaya\Documents\4 Software Testing\Assignment\Test Data\new_weather.csv"

    file_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input.send_keys(csv_path)

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Upload')]"))
    ).click()

    # WAIT SUCCESS MESSAGE
    success_msg = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(),'successfully')]")
        )
    )

    assert "successfully" in success_msg.text.lower()

    print("CSV uploaded successfully")

    # =========================
    # PAGINATION LOGIC
    # =========================
    target_date = "2/2/2022"
    found = False

    while True:

        # STEP 1: CHECK CURRENT PAGE ROWS
        rows = driver.find_elements(By.XPATH, "//table//tr")

        for row in rows:
            if target_date in row.text:
                found = True
                break

        if found:
            break

        # STEP 2: TRY CLICK NEXT
        try:
            next_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next')]"))
            )

            # STOP if disabled
            if "disabled" in next_btn.get_attribute("class").lower():
                break

            # STEP 3: GET OLD FIRST ROW TEXT (for validation)
            old_first_row = rows[1].text if len(rows) > 1 else ""

            next_btn.click()

            # STEP 4: WAIT UNTIL TABLE ACTUALLY CHANGES
            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.XPATH, "//table//tr")) > 0
                and d.find_elements(By.XPATH, "//table//tr")[1].text != old_first_row
            )

        except TimeoutException:
            break

# =========================
# TC-UC9-02: INVALID CSV FORMAT
# =========================
def test_tc_uc9_02(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    csv_path = r"C:\Users\LENOVO\OneDrive - Universiti Malaya\Documents\4 Software Testing\Assignment\Test Data\new_weather_invalid_column.csv"

    file_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input.send_keys(csv_path)

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Upload')]"))
    ).click()

    UploadValidator.assert_invalid_upload(driver, wait)


# =========================
# TC-UC9-03: INVALID TXT FILE FORMAT
# =========================
def test_tc_uc9_03(driver):
    wait = WebDriverWait(driver, 10)

    login(driver)

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    txt_path = r"C:\Users\LENOVO\OneDrive - Universiti Malaya\Documents\4 Software Testing\Assignment\Test Data\new_weather.txt"

    file_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input.send_keys(txt_path)

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Upload')]"))
    ).click()

    UploadValidator.assert_invalid_upload(driver, wait)
    
# =========================
# TC-UC9-04: INVALID DATE VALUE
# =========================

def test_tc_uc9_04(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    csv_path = r"C:\Users\LENOVO\OneDrive - Universiti Malaya\Documents\4 Software Testing\Assignment\Test Data\new_weather_invalid_date.csv"

    file_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input.send_keys(csv_path)

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Upload')]"))
    ).click()

    UploadValidator.assert_invalid_upload(driver, wait)

# =========================
# TC-UC9-05: VALID YESTERDAY DATE
# =========================

def test_tc_uc9_05(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    csv_path = r"C:\Users\LENOVO\OneDrive - Universiti Malaya\Documents\4 Software Testing\Assignment\Test Data\new_weather_yesterday.csv"

    file_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input.send_keys(csv_path)

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Upload')]"))
    ).click()

    dates = get_dates()
    target_date = dates["yesterday"]
    
    # =========================
    # PAGINATION LOGIC
    # =========================
    found = False

    while True:

        # STEP 1: CHECK CURRENT PAGE ROWS
        rows = driver.find_elements(By.XPATH, "//table//tr")

        for row in rows:
            if target_date in row.text:
                found = True
                break

        if found:
            break

        # STEP 2: TRY CLICK NEXT
        try:
            next_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next')]"))
            )

            # STOP if disabled
            if "disabled" in next_btn.get_attribute("class").lower():
                break

            # STEP 3: GET OLD FIRST ROW TEXT (for validation)
            old_first_row = rows[1].text if len(rows) > 1 else ""

            next_btn.click()

            # STEP 4: WAIT UNTIL TABLE ACTUALLY CHANGES
            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.XPATH, "//table//tr")) > 0
                and d.find_elements(By.XPATH, "//table//tr")[1].text != old_first_row
            )

        except TimeoutException:
            break

# =========================
# TC-UC9-06: VALID TODAY DATE
# =========================

def test_tc_uc9_06(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    csv_path = r"C:\Users\LENOVO\OneDrive - Universiti Malaya\Documents\4 Software Testing\Assignment\Test Data\new_weather_today.csv"

    file_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input.send_keys(csv_path)

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Upload')]"))
    ).click()

    dates = get_dates()
    target_date = dates["today"]

    time.sleep(3)

    # =========================
    # PAGINATION LOGIC
    # =========================
    found = False

    while True:

        # STEP 1: CHECK CURRENT PAGE ROWS
        rows = driver.find_elements(By.XPATH, "//table//tr")

        for row in rows:
            if target_date in row.text:
                found = True
                break

        if found:
            break

        # STEP 2: TRY CLICK NEXT
        try:
            next_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next')]"))
            )

            # STOP if disabled
            if "disabled" in next_btn.get_attribute("class").lower():
                break

            # STEP 3: GET OLD FIRST ROW TEXT (for validation)
            old_first_row = rows[1].text if len(rows) > 1 else ""

            next_btn.click()

            # STEP 4: WAIT UNTIL TABLE ACTUALLY CHANGES
            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.XPATH, "//table//tr")) > 0
                and d.find_elements(By.XPATH, "//table//tr")[1].text != old_first_row
            )

        except TimeoutException:
            break

# =========================
# TC-UC9-07: INVALID TOMORROW DATE
# =========================

def test_tc_uc9_07(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    csv_path = r"C:\Users\LENOVO\OneDrive - Universiti Malaya\Documents\4 Software Testing\Assignment\Test Data\new_weather_tomorrow.csv"

    file_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input.send_keys(csv_path)

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Upload')]"))
    ).click()

    UploadValidator.assert_invalid_upload(driver, wait)

# =========================
# TC-UC9-08: INVALID TEMPERATURE VALUE
# =========================

def test_tc_uc9_08(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    csv_path = r"C:\Users\LENOVO\OneDrive - Universiti Malaya\Documents\4 Software Testing\Assignment\Test Data\new_weather_invalid_temperature.csv"

    file_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input.send_keys(csv_path)

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Upload')]"))
    ).click()

    UploadValidator.assert_invalid_upload(driver, wait)

# =========================
# TC-UC9-09: INVALID HUMIDITY VALUE
# =========================

def test_tc_uc9_09(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    csv_path = r"C:\Users\LENOVO\OneDrive - Universiti Malaya\Documents\4 Software Testing\Assignment\Test Data\new_weather_invalid_humidity.csv"

    file_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input.send_keys(csv_path)

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Upload')]"))
    ).click()

    UploadValidator.assert_invalid_upload(driver, wait)

# =========================
# TC-UC9-10: VALID HUMIDITY VALUE OF 0
# =========================

def test_tc_uc9_10(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    csv_path = r"C:\Users\LENOVO\OneDrive - Universiti Malaya\Documents\4 Software Testing\Assignment\Test Data\new_weather_humidity0.csv"

    file_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input.send_keys(csv_path)

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Upload')]"))
    ).click()

    # =========================
    # PAGINATION LOGIC
    # =========================
    target_value = "0°C"
    found = False

    while True:

        # STEP 1: CHECK CURRENT PAGE ROWS
        rows = driver.find_elements(By.XPATH, "//table//tr")

        for row in rows:
            if target_value in row.text:
                found = True
                break

        if found:
            break

        # STEP 2: TRY CLICK NEXT
        try:
            next_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next')]"))
            )

            # STOP if disabled
            if "disabled" in next_btn.get_attribute("class").lower():
                break

            # STEP 3: GET OLD FIRST ROW TEXT (for validation)
            old_first_row = rows[1].text if len(rows) > 1 else ""

            next_btn.click()

            # STEP 4: WAIT UNTIL TABLE ACTUALLY CHANGES
            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.XPATH, "//table//tr")) > 0
                and d.find_elements(By.XPATH, "//table//tr")[1].text != old_first_row
            )

        except TimeoutException:
            break

# =========================
# TC-UC9-11: VALID HUMIDITY VALUE OF 100
# =========================

def test_tc_uc9_11(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    csv_path = r"C:\Users\LENOVO\OneDrive - Universiti Malaya\Documents\4 Software Testing\Assignment\Test Data\new_weather_humidity100.csv"

    file_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input.send_keys(csv_path)

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Upload')]"))
    ).click()

    # =========================
    # PAGINATION LOGIC
    # =========================
    target_value = "100°C"
    found = False

    while True:

        # STEP 1: CHECK CURRENT PAGE ROWS
        rows = driver.find_elements(By.XPATH, "//table//tr")

        for row in rows:
            if target_value in row.text:
                found = True
                break

        if found:
            break

        # STEP 2: TRY CLICK NEXT
        try:
            next_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next')]"))
            )

            # STOP if disabled
            if "disabled" in next_btn.get_attribute("class").lower():
                break

            # STEP 3: GET OLD FIRST ROW TEXT (for validation)
            old_first_row = rows[1].text if len(rows) > 1 else ""

            next_btn.click()

            # STEP 4: WAIT UNTIL TABLE ACTUALLY CHANGES
            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.XPATH, "//table//tr")) > 0
                and d.find_elements(By.XPATH, "//table//tr")[1].text != old_first_row
            )

        except TimeoutException:
            break

# =========================
# TC-UC9-12: INVALID HUMIDITY VALUE OF -1
# =========================

def test_tc_uc9_12(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    csv_path = r"C:\Users\LENOVO\OneDrive - Universiti Malaya\Documents\4 Software Testing\Assignment\Test Data\new_weather_humidity-1.csv"

    file_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input.send_keys(csv_path)

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Upload')]"))
    ).click()

    UploadValidator.assert_invalid_upload(driver, wait)

# =========================
# TC-UC9-13: INVALID HUMIDITY VALUE OF 101
# =========================

def test_tc_uc9_13(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    csv_path = r"C:\Users\LENOVO\OneDrive - Universiti Malaya\Documents\4 Software Testing\Assignment\Test Data\new_weather_humidity101.csv"

    file_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input.send_keys(csv_path)

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Upload')]"))
    ).click()

    UploadValidator.assert_invalid_upload(driver, wait)

# =========================
# TC-UC9-14: INVALID RAINFALL VALUE
# =========================

def test_tc_uc9_14(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    csv_path = r"C:\Users\LENOVO\OneDrive - Universiti Malaya\Documents\4 Software Testing\Assignment\Test Data\new_weather_invalid_rainfall.csv"

    file_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input.send_keys(csv_path)

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Upload')]"))
    ).click()

    UploadValidator.assert_invalid_upload(driver, wait)

# =========================
# TC-UC9-15: INVALID LOCATION VALUE
# =========================

def test_tc_uc9_15(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    csv_path = r"C:\Users\LENOVO\OneDrive - Universiti Malaya\Documents\4 Software Testing\Assignment\Test Data\new_weather_invalid_location.csv"

    file_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input.send_keys(csv_path)

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Upload')]"))
    ).click()

    UploadValidator.assert_invalid_upload(driver, wait)

# =========================
# TC-UC9-16: CANCEL CSV UPLOAD
# =========================

def test_tc_uc9_16(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    csv_path = r"C:\Users\LENOVO\OneDrive - Universiti Malaya\Documents\4 Software Testing\Assignment\Test Data\new_weather.csv"

    file_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input.send_keys(csv_path)

# =========================
# TC-UC9-17: FORM VALID INPUT
# =========================

def test_tc_uc9_17(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    # Open Weather Data page
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    # Click "Add New Record"
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add New Record')]")
        )
    ).click()

    # Fill Date
    date_field = wait.until(
        EC.presence_of_element_located((By.ID, "date"))
    )

    date_field.clear()
    date_field.send_keys("20/01/2026")

    # Temperature
    driver.find_element(By.ID, "temperature").send_keys("30.9")

    # Humidity
    driver.find_element(By.ID, "humidity").send_keys("70")

    # Rainfall
    driver.find_element(By.ID, "rainfall").send_keys("25.7")

    # Location
    driver.find_element(By.ID, "location").send_keys("Kuala Lumpur")

    # Dropdown (Operational Area)
    select_element = Select(
        driver.find_element(By.ID, "companyLocationId")
    )
    select_element.select_by_index(1)   # or select_by_visible_text(...)
    
    # Submit
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add Record')]")
        )
    ).click()
    
    # wait a bit for toast animation
    time.sleep(2)

    # check any success message
    success_elements = driver.find_elements(
        By.XPATH,
        "//*[contains(., 'successfully')]"
    )
    
    success_msg = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(),'Weather record added successfully')]")
        )
    )

    assert "weather record added successfully" in success_msg.text.lower()

    # =========================
    # PAGINATION LOGIC
    # =========================
    
    target_value = "20/1/2026"
    found = False

    while True:

        # STEP 1: CHECK CURRENT PAGE ROWS
        rows = driver.find_elements(By.XPATH, "//table//tr")

        for row in rows:
            if target_value in row.text:
                found = True
                break

        if found:
            break

        # STEP 2: TRY CLICK NEXT
        try:
            next_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next')]"))
            )

            # STOP if disabled
            if "disabled" in next_btn.get_attribute("class").lower():
                break

            # STEP 3: GET OLD FIRST ROW TEXT (for validation)
            old_first_row = rows[1].text if len(rows) > 1 else ""

            next_btn.click()

            # STEP 4: WAIT UNTIL TABLE ACTUALLY CHANGES
            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.XPATH, "//table//tr")) > 0
                and d.find_elements(By.XPATH, "//table//tr")[1].text != old_first_row
            )

        except TimeoutException:
            break

# =========================
# TC-UC9-18: FORM INCOMPLETE INPUT
# =========================

def test_tc_uc9_18(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    # Open Weather Data page
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    # Click "Add New Record"
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add New Record')]")
        )
    ).click()

    # Fill Date
    date_field = wait.until(
        EC.presence_of_element_located((By.ID, "date"))
    )

    date_field.clear()
    date_field.send_keys("20/01/2026")

    # Humidity
    driver.find_element(By.ID, "humidity").send_keys("70")

    # Rainfall
    driver.find_element(By.ID, "rainfall").send_keys("25.7")

    # Location
    driver.find_element(By.ID, "location").send_keys("Kuala Lumpur")

    # Dropdown (Operational Area)
    select_element = Select(
        driver.find_element(By.ID, "companyLocationId")
    )
    select_element.select_by_index(1)   # or select_by_visible_text(...)
    
    records_before = driver.find_elements(By.CSS_SELECTOR, ".record-row")
    
    # Submit
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add Record')]")
        )
    ).click()
    
    # wait a bit for toast animation
    time.sleep(2)

    records_after = driver.find_elements(By.CSS_SELECTOR, ".record-row")
    assert len(records_after) == len(records_before)
    
# =========================
# TC-UC9-19: FORM INVALID DATE
# =========================

def test_tc_uc9_19(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    # Open Weather Data page
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    # Click "Add New Record"
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add New Record')]")
        )
    ).click()

    # Fill Date
    date_field = wait.until(
        EC.presence_of_element_located((By.ID, "date"))
    )

    date_field.clear()
    date_field.send_keys("2026/01/20") # invalid format
    
    # Temperature
    driver.find_element(By.ID, "temperature").send_keys("30.9")

    # Humidity
    driver.find_element(By.ID, "humidity").send_keys("70")

    # Rainfall
    driver.find_element(By.ID, "rainfall").send_keys("25.7")

    # Location
    driver.find_element(By.ID, "location").send_keys("Kuala Lumpur")

    # Dropdown (Operational Area)
    select_element = Select(
        driver.find_element(By.ID, "companyLocationId")
    )
    select_element.select_by_index(1)   # or select_by_visible_text(...)
    
    records_before = driver.find_elements(By.CSS_SELECTOR, ".record-row")
    
    # Submit
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add Record')]")
        )
    ).click()
    
    # wait a bit for toast animation
    time.sleep(2)

    records_after = driver.find_elements(By.CSS_SELECTOR, ".record-row")
    assert len(records_after) == len(records_before)

# =========================
# TC-UC9-20: FORM YESTERDAY DATE
# =========================

def test_tc_uc9_20(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    # Open Weather Data page
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    # Click "Add New Record"
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add New Record')]")
        )
    ).click()

    # Fill Date
    date_field = wait.until(
        EC.presence_of_element_located((By.ID, "date"))
    )

    date_field.clear()
    date_field.send_keys(get_relative_date("yesterday"))
    
    # Temperature
    driver.find_element(By.ID, "temperature").send_keys("30.9")

    # Humidity
    driver.find_element(By.ID, "humidity").send_keys("70")

    # Rainfall
    driver.find_element(By.ID, "rainfall").send_keys("25.7")

    # Location
    driver.find_element(By.ID, "location").send_keys("Kuala Lumpur")

    # Dropdown (Operational Area)
    select_element = Select(
        driver.find_element(By.ID, "companyLocationId")
    )
    select_element.select_by_index(1)   # or select_by_visible_text(...)
    
    # Submit
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add Record')]")
        )
    ).click()

    # wait a bit for toast animation
    time.sleep(2)

    # check any success message
    success_elements = driver.find_elements(
        By.XPATH,
        "//*[contains(., 'successfully')]"
    )
    
    success_msg = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(),'Weather record added successfully')]")
        )
    )

    assert "weather record added successfully" in success_msg.text.lower()

# =========================
# TC-UC9-21: FORM TODAY DATE
# =========================

def test_tc_uc9_21(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    # Open Weather Data page
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    # Click "Add New Record"
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add New Record')]")
        )
    ).click()

    # Fill Date
    date_field = wait.until(
        EC.presence_of_element_located((By.ID, "date"))
    )

    date_field.clear()
    date_field.send_keys(get_relative_date("today"))
    
    # Temperature
    driver.find_element(By.ID, "temperature").send_keys("30.9")

    # Humidity
    driver.find_element(By.ID, "humidity").send_keys("70")

    # Rainfall
    driver.find_element(By.ID, "rainfall").send_keys("25.7")

    # Location
    driver.find_element(By.ID, "location").send_keys("Kuala Lumpur")

    # Dropdown (Operational Area)
    select_element = Select(
        driver.find_element(By.ID, "companyLocationId")
    )
    select_element.select_by_index(1)   # or select_by_visible_text(...)
    
    # Submit
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add Record')]")
        )
    ).click()

    # wait a bit for toast animation
    time.sleep(2)

    # check any success message
    success_elements = driver.find_elements(
        By.XPATH,
        "//*[contains(., 'successfully')]"
    )
    
    success_msg = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(),'Weather record added successfully')]")
        )
    )

    assert "weather record added successfully" in success_msg.text.lower()

# =========================
# TC-UC9-22: FORM TOMORROW DATE
# =========================

def test_tc_uc9_22(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    # Open Weather Data page
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    # Click "Add New Record"
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add New Record')]")
        )
    ).click()

    # Fill Date
    date_field = wait.until(
        EC.presence_of_element_located((By.ID, "date"))
    )

    date_field.clear()
    date_field.send_keys(get_relative_date("tomorrow"))
    
    # Temperature
    driver.find_element(By.ID, "temperature").send_keys("30.9")

    # Humidity
    driver.find_element(By.ID, "humidity").send_keys("70")

    # Rainfall
    driver.find_element(By.ID, "rainfall").send_keys("25.7")

    # Location
    driver.find_element(By.ID, "location").send_keys("Kuala Lumpur")

    # Dropdown (Operational Area)
    select_element = Select(
        driver.find_element(By.ID, "companyLocationId")
    )
    select_element.select_by_index(1)   # or select_by_visible_text(...)
    
    records_before = driver.find_elements(By.CSS_SELECTOR, ".record-row")
    
    # Submit
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add Record')]")
        )
    ).click()

    # wait a bit for toast animation
    time.sleep(2)

    records_after = driver.find_elements(By.CSS_SELECTOR, ".record-row")
    assert len(records_after) == len(records_before)

# =========================
# TC-UC9-23: FORM INVALID TEMPERATURE
# =========================

def test_tc_uc9_23(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    # Open Weather Data page
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    # Click "Add New Record"
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add New Record')]")
        )
    ).click()

    # Fill Date
    date_field = wait.until(
        EC.presence_of_element_located((By.ID, "date"))
    )

    date_field.clear()
    date_field.send_keys("20/01/2026")
    
    # Temperature
    driver.find_element(By.ID, "temperature").send_keys("low")

    # Humidity
    driver.find_element(By.ID, "humidity").send_keys("70")

    # Rainfall
    driver.find_element(By.ID, "rainfall").send_keys("25.7")

    # Location
    driver.find_element(By.ID, "location").send_keys("Kuala Lumpur")

    # Dropdown (Operational Area)
    select_element = Select(
        driver.find_element(By.ID, "companyLocationId")
    )
    select_element.select_by_index(1)   # or select_by_visible_text(...)
    
    records_before = driver.find_elements(By.CSS_SELECTOR, ".record-row")
    
    # Submit
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add Record')]")
        )
    ).click()
    
    # wait a bit for toast animation
    time.sleep(2)

    records_after = driver.find_elements(By.CSS_SELECTOR, ".record-row")
    assert len(records_after) == len(records_before)

# =========================
# TC-UC9-24: FORM INVALID HUMIDITY
# =========================

def test_tc_uc9_24(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    # Open Weather Data page
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    # Click "Add New Record"
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add New Record')]")
        )
    ).click()

    # Fill Date
    date_field = wait.until(
        EC.presence_of_element_located((By.ID, "date"))
    )

    date_field.clear()
    date_field.send_keys("20/01/2026")
    
    # Temperature
    driver.find_element(By.ID, "temperature").send_keys("30.9")

    # Humidity
    driver.find_element(By.ID, "humidity").send_keys("low")

    # Rainfall
    driver.find_element(By.ID, "rainfall").send_keys("25.7")

    # Location
    driver.find_element(By.ID, "location").send_keys("Kuala Lumpur")

    # Dropdown (Operational Area)
    select_element = Select(
        driver.find_element(By.ID, "companyLocationId")
    )
    select_element.select_by_index(1)   # or select_by_visible_text(...)
    
    records_before = driver.find_elements(By.CSS_SELECTOR, ".record-row")
    
    # Submit
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add Record')]")
        )
    ).click()
    
    # wait a bit for toast animation
    time.sleep(2)

    records_after = driver.find_elements(By.CSS_SELECTOR, ".record-row")
    assert len(records_after) == len(records_before)

# =========================
# TC-UC9-25: FORM HUMIDITY VALUE 0
# =========================

def test_tc_uc9_25(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    # Open Weather Data page
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    # Click "Add New Record"
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add New Record')]")
        )
    ).click()

    # Fill Date
    date_field = wait.until(
        EC.presence_of_element_located((By.ID, "date"))
    )

    date_field.clear()
    date_field.send_keys("20/01/2026")
    
    # Temperature
    driver.find_element(By.ID, "temperature").send_keys("30.9")

    # Humidity
    driver.find_element(By.ID, "humidity").send_keys("0")

    # Rainfall
    driver.find_element(By.ID, "rainfall").send_keys("25.7")

    # Location
    driver.find_element(By.ID, "location").send_keys("Kuala Lumpur")

    # Dropdown (Operational Area)
    select_element = Select(
        driver.find_element(By.ID, "companyLocationId")
    )
    select_element.select_by_index(1)   # or select_by_visible_text(...)
    
    records_before = driver.find_elements(By.CSS_SELECTOR, ".record-row")
    
    # Submit
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add Record')]")
        )
    ).click()
    
    # wait a bit for toast animation
    time.sleep(2)

    # check any success message
    success_elements = driver.find_elements(
        By.XPATH,
        "//*[contains(., 'successfully')]"
    )
    
    success_msg = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(),'Weather record added successfully')]")
        )
    )

    assert "weather record added successfully" in success_msg.text.lower()

# =========================
# TC-UC9-26: FORM HUMIDITY VALUE 100
# =========================

def test_tc_uc9_26(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    # Open Weather Data page
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    # Click "Add New Record"
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add New Record')]")
        )
    ).click()

    # Fill Date
    date_field = wait.until(
        EC.presence_of_element_located((By.ID, "date"))
    )

    date_field.clear()
    date_field.send_keys("20/01/2026")
    
    # Temperature
    driver.find_element(By.ID, "temperature").send_keys("30.9")

    # Humidity
    driver.find_element(By.ID, "humidity").send_keys("100")

    # Rainfall
    driver.find_element(By.ID, "rainfall").send_keys("25.7")

    # Location
    driver.find_element(By.ID, "location").send_keys("Kuala Lumpur")

    # Dropdown (Operational Area)
    select_element = Select(
        driver.find_element(By.ID, "companyLocationId")
    )
    select_element.select_by_index(1)   # or select_by_visible_text(...)
    
    records_before = driver.find_elements(By.CSS_SELECTOR, ".record-row")
    
    # Submit
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add Record')]")
        )
    ).click()
    
    # wait a bit for toast animation
    time.sleep(2)

    # check any success message
    success_elements = driver.find_elements(
        By.XPATH,
        "//*[contains(., 'successfully')]"
    )
    
    success_msg = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(),'Weather record added successfully')]")
        )
    )

    assert "weather record added successfully" in success_msg.text.lower()

# =========================
# TC-UC9-27: FORM INVALID HUMIDITY -1
# =========================

def test_tc_uc9_27(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    # Open Weather Data page
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    # Click "Add New Record"
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add New Record')]")
        )
    ).click()

    # Fill Date
    date_field = wait.until(
        EC.presence_of_element_located((By.ID, "date"))
    )

    date_field.clear()
    date_field.send_keys("20/01/2026")
    
    # Temperature
    driver.find_element(By.ID, "temperature").send_keys("30.9")

    # Humidity
    driver.find_element(By.ID, "humidity").send_keys("-1")

    # Rainfall
    driver.find_element(By.ID, "rainfall").send_keys("25.7")

    # Location
    driver.find_element(By.ID, "location").send_keys("Kuala Lumpur")

    # Dropdown (Operational Area)
    select_element = Select(
        driver.find_element(By.ID, "companyLocationId")
    )
    select_element.select_by_index(1)   # or select_by_visible_text(...)
    
    records_before = driver.find_elements(By.CSS_SELECTOR, ".record-row")
    
    # Submit
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add Record')]")
        )
    ).click()
    
    # wait a bit for toast animation
    time.sleep(2)

    records_after = driver.find_elements(By.CSS_SELECTOR, ".record-row")
    assert len(records_after) == len(records_before)

# =========================
# TC-UC9-28: FORM INVALID HUMIDITY 101
# =========================

def test_tc_uc9_28(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    # Open Weather Data page
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    # Click "Add New Record"
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add New Record')]")
        )
    ).click()

    # Fill Date
    date_field = wait.until(
        EC.presence_of_element_located((By.ID, "date"))
    )

    date_field.clear()
    date_field.send_keys("20/01/2026")
    
    # Temperature
    driver.find_element(By.ID, "temperature").send_keys("30.9")

    # Humidity
    driver.find_element(By.ID, "humidity").send_keys("101")

    # Rainfall
    driver.find_element(By.ID, "rainfall").send_keys("25.7")

    # Location
    driver.find_element(By.ID, "location").send_keys("Kuala Lumpur")

    # Dropdown (Operational Area)
    select_element = Select(
        driver.find_element(By.ID, "companyLocationId")
    )
    select_element.select_by_index(1)   # or select_by_visible_text(...)
    
    records_before = driver.find_elements(By.CSS_SELECTOR, ".record-row")
    
    # Submit
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add Record')]")
        )
    ).click()
    
    # wait a bit for toast animation
    time.sleep(2)

    records_after = driver.find_elements(By.CSS_SELECTOR, ".record-row")
    assert len(records_after) == len(records_before)

# =========================
# TC-UC9-29: FORM INVALID RAINFALL
# =========================

def test_tc_uc9_29(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    # Open Weather Data page
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    # Click "Add New Record"
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add New Record')]")
        )
    ).click()

    # Fill Date
    date_field = wait.until(
        EC.presence_of_element_located((By.ID, "date"))
    )

    date_field.clear()
    date_field.send_keys("20/01/2026")
    
    # Temperature
    driver.find_element(By.ID, "temperature").send_keys("30.9")

    # Humidity
    driver.find_element(By.ID, "humidity").send_keys("70")

    # Rainfall
    driver.find_element(By.ID, "rainfall").send_keys("high")

    # Location
    driver.find_element(By.ID, "location").send_keys("Kuala Lumpur")

    # Dropdown (Operational Area)
    select_element = Select(
        driver.find_element(By.ID, "companyLocationId")
    )
    select_element.select_by_index(1)   # or select_by_visible_text(...)
    
    records_before = driver.find_elements(By.CSS_SELECTOR, ".record-row")
    
    # Submit
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add Record')]")
        )
    ).click()
    
    # wait a bit for toast animation
    time.sleep(2)

    records_after = driver.find_elements(By.CSS_SELECTOR, ".record-row")
    assert len(records_after) == len(records_before)

# =========================
# TC-UC9-30: FORM INVALID LOCATION
# =========================

def test_tc_uc9_30(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    # Open Weather Data page
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    # Click "Add New Record"
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add New Record')]")
        )
    ).click()

    # Fill Date
    date_field = wait.until(
        EC.presence_of_element_located((By.ID, "date"))
    )

    date_field.clear()
    date_field.send_keys("20/01/2026")
    
    # Temperature
    driver.find_element(By.ID, "temperature").send_keys("30.9")

    # Humidity
    driver.find_element(By.ID, "humidity").send_keys("101")

    # Rainfall
    driver.find_element(By.ID, "rainfall").send_keys("25.7")

    # Dropdown (Operational Area)
    select_element = Select(
        driver.find_element(By.ID, "companyLocationId")
    )
    select_element.select_by_index(1)   # or select_by_visible_text(...)
    
    records_before = driver.find_elements(By.CSS_SELECTOR, ".record-row")
    
    # Submit
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add Record')]")
        )
    ).click()
    
    # wait a bit for toast animation
    time.sleep(2)

    records_after = driver.find_elements(By.CSS_SELECTOR, ".record-row")
    assert len(records_after) == len(records_before)

# =========================
# TC-UC9-31: NO DATA AVAILABLE
# =========================

def test_tc_uc9_31(driver):
    wait = WebDriverWait(driver, 15)

    wait = WebDriverWait(driver, 15)

    driver.get("http://localhost:3000")

    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(
        "testuc9.2@gmail.com"
    )

    driver.find_element(By.ID, "password").send_keys("Test@123")

    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    wait.until(EC.url_contains("/dashboard"))
    
    # Open Weather Data page
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()
    
    success_msg = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(),'No Weather Data')]")
        )
    )

    assert "No Weather Data" in success_msg.text

# =========================
# TC-UC9-32: NO INTERNET CONNECTION
# =========================

def test_tc_uc9_32(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    # Open Weather Data page
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    # Click "Add New Record"
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add New Record')]")
        )
    ).click()

    # Fill Date
    date_field = wait.until(
        EC.presence_of_element_located((By.ID, "date"))
    )
    date_field.clear()
    date_field.send_keys("20/01/2026")

    # Temperature
    driver.find_element(By.ID, "temperature").send_keys("30.9")

    # Humidity
    driver.find_element(By.ID, "humidity").send_keys("70")

    # Rainfall
    driver.find_element(By.ID, "rainfall").send_keys("25.7")

    # Location
    driver.find_element(By.ID, "location").send_keys("Kuala Lumpur")

    # Dropdown (Operational Area)
    select_element = Select(driver.find_element(By.ID, "companyLocationId"))
    select_element.select_by_index(1)

    # Go offline BEFORE submitting
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
        "offline": True,
        "latency": 0,
        "downloadThroughput": 0,
        "uploadThroughput": 0
    })

    # Click Add Record
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add Record')]")
        )
    ).click()

    # ASSERT: "Failed to save weather record" message appears
    error_msg = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(), 'Failed to save weather record')]")
        )
    )
    assert "failed to save weather record" in error_msg.text.lower(), \
        f"Expected failure message but got: {error_msg.text!r}"

    # Restore internet
    driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
        "offline": False,
        "latency": 0,
        "downloadThroughput": -1,
        "uploadThroughput": -1
    })


# =========================
# TC-UC9-33: SERVER IS DOWN
# =========================

def test_tc_uc9_33(driver):
    wait = WebDriverWait(driver, 15)

    login(driver)

    # Open Weather Data page
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Weather Data']]")
        )
    ).click()

    # Click "Add New Record"
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add New Record')]")
        )
    ).click()

    # Fill Date
    date_field = wait.until(
        EC.presence_of_element_located((By.ID, "date"))
    )
    date_field.clear()
    date_field.send_keys("20/01/2026")

    # Temperature
    driver.find_element(By.ID, "temperature").send_keys("30.9")

    # Humidity
    driver.find_element(By.ID, "humidity").send_keys("70")

    # Rainfall
    driver.find_element(By.ID, "rainfall").send_keys("25.7")

    # Location
    driver.find_element(By.ID, "location").send_keys("Kuala Lumpur")

    # Dropdown (Operational Area)
    select_element = Select(driver.find_element(By.ID, "companyLocationId"))
    select_element.select_by_index(1)

    # Simulate server down (offline) BEFORE submitting
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
        "offline": True,
        "latency": 0,
        "downloadThroughput": 0,
        "uploadThroughput": 0
    })

    # Click Add Record
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Add Record')]")
        )
    ).click()

    # ASSERT: "Failed to save weather record" message appears
    error_msg = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(), 'Failed to save weather record')]")
        )
    )
    assert "failed to save weather record" in error_msg.text.lower(), \
        f"Expected failure message but got: {error_msg.text!r}"

    # Restore internet
    driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
        "offline": False,
        "latency": 0,
        "downloadThroughput": -1,
        "uploadThroughput": -1
    })