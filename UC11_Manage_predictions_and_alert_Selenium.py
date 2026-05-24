
# ================================================================
# DRONE4DENGUE SYSTEM
# UC11 - PREDICTION & ALERT
# SELENIUM AUTOMATED TESTING
# ================================================================

# ================================================================
# IMPORT REQUIRED LIBRARIES
# ================================================================

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import time
import os

# ================================================================
# CONFIGURATION VARIABLES
# ================================================================

BASE_URL = "http://localhost:3000"

VALID_EMAIL = "admin@email.com"
VALID_PASSWORD = "Admin123!"

# ================================================================
# GLOBAL RESULT STORAGE
# ================================================================

test_results = []
test_defects = []

# ================================================================
# INITIALIZE CHROME DRIVER
# ================================================================

driver = webdriver.Chrome()

driver.maximize_window()

wait = WebDriverWait(driver, 15)

# ================================================================
# HELPER FUNCTION : LOGIN SYSTEM
# ================================================================

def login_system():

    print("Opening Drone4Dengue website...")

    driver.get(BASE_URL)

    time.sleep(3)

    print("Locating email input field...")

    email_field = wait.until(
        EC.presence_of_element_located(
            (By.NAME, "email")
        )
    )

    print("Entering email address...")

    email_field.clear()

    email_field.send_keys(VALID_EMAIL)

    print("Locating password field...")

    password_field = driver.find_element(
        By.NAME,
        "password"
    )

    print("Entering password...")

    password_field.clear()

    password_field.send_keys(VALID_PASSWORD)

    print("Locating login button...")

    login_button = driver.find_element(
        By.XPATH,
        "//button[contains(text(),'Login')]"
    )

    print("Clicking login button...")

    login_button.click()

    time.sleep(3)

# ================================================================
# TEST CASE : TC-UC11-001
# VERIFY PREDICTION MAP DISPLAY
# ================================================================

def tc_uc11_001():

    try:

        print("\nExecuting TC-UC11-001")

        login_system()

        print("Opening Prediction & Alert module...")

        prediction_module = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//span[contains(text(),'Prediction & Alert')]"
                )
            )
        )

        prediction_module.click()

        time.sleep(3)

        print("Selecting state filter...")

        state_filter = driver.find_element(
            By.NAME,
            "state"
        )

        state_filter.send_keys("Selangor")

        print("Selecting risk level...")

        risk_filter = driver.find_element(
            By.NAME,
            "riskLevel"
        )

        risk_filter.send_keys("High")

        print("Applying prediction filter...")

        apply_button = driver.find_element(
            By.XPATH,
            "//button[contains(text(),'Apply')]"
        )

        apply_button.click()

        time.sleep(5)

        print("Checking prediction map visibility...")

        prediction_map = driver.find_elements(
            By.XPATH,
            "//div[contains(@class,'prediction')]"
        )

        if len(prediction_map) > 0:

            test_results.append(
                "TC-UC11-001 : PASS"
            )

        else:

            test_results.append(
                "TC-UC11-001 : FAIL"
            )

            test_defects.append(
                "Prediction map was not displayed correctly."
            )

    except Exception as e:

        test_results.append(
            "TC-UC11-001 : FAIL"
        )

        test_defects.append(str(e))

# ================================================================
# TEST CASE : TC-UC11-002
# VERIFY PREDICTION FILTER UPDATE
# ================================================================

def tc_uc11_002():

    try:

        print("\nExecuting TC-UC11-002")

        login_system()

        prediction_module = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//span[contains(text(),'Prediction & Alert')]"
                )
            )
        )

        prediction_module.click()

        time.sleep(3)

        print("Filtering Kuala Lumpur prediction records...")

        state_filter = driver.find_element(
            By.NAME,
            "state"
        )

        state_filter.send_keys("Kuala Lumpur")

        apply_button = driver.find_element(
            By.XPATH,
            "//button[contains(text(),'Apply')]"
        )

        apply_button.click()

        time.sleep(5)

        prediction_rows = driver.find_elements(
            By.XPATH,
            "//table//tr"
        )

        if len(prediction_rows) > 0:

            test_results.append(
                "TC-UC11-002 : PASS"
            )

        else:

            test_results.append(
                "TC-UC11-002 : FAIL"
            )

            test_defects.append(
                "Prediction records were not updated correctly."
            )

    except Exception as e:

        test_results.append(
            "TC-UC11-002 : FAIL"
        )

        test_defects.append(str(e))

# ================================================================
# TEST CASE : TC-UC11-003
# VERIFY ALERT VALIDATION
# ================================================================

def tc_uc11_003():

    try:

        print("\nExecuting TC-UC11-003")

        login_system()

        prediction_module = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//span[contains(text(),'Prediction & Alert')]"
                )
            )
        )

        prediction_module.click()

        time.sleep(3)

        threshold_input = driver.find_element(
            By.NAME,
            "threshold"
        )

        threshold_input.send_keys("80")

        save_button = driver.find_element(
            By.XPATH,
            "//button[contains(text(),'Save')]"
        )

        save_button.click()

        time.sleep(3)

        validation_message = driver.find_elements(
            By.XPATH,
            "//*[contains(text(),'recipient')]"
        )

        if len(validation_message) > 0:

            test_results.append(
                "TC-UC11-003 : PASS"
            )

        else:

            test_results.append(
                "TC-UC11-003 : FAIL"
            )

            test_defects.append(
                "System accepted alert configuration without recipient."
            )

    except Exception as e:

        test_results.append(
            "TC-UC11-003 : FAIL"
        )

        test_defects.append(str(e))

# ================================================================
# TEST CASE : TC-UC11-004
# VERIFY VALID ALERT CONFIGURATION
# ================================================================

def tc_uc11_004():

    try:

        print("\nExecuting TC-UC11-004")

        login_system()

        prediction_module = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//span[contains(text(),'Prediction & Alert')]"
                )
            )
        )

        prediction_module.click()

        time.sleep(3)

        threshold_input = driver.find_element(
            By.NAME,
            "threshold"
        )

        threshold_input.send_keys("70")

        recipient_group = driver.find_element(
            By.NAME,
            "recipientGroup"
        )

        recipient_group.send_keys(
            "Health Officer Group"
        )

        save_button = driver.find_element(
            By.XPATH,
            "//button[contains(text(),'Save')]"
        )

        save_button.click()

        time.sleep(3)

        success_message = driver.find_elements(
            By.XPATH,
            "//*[contains(text(),'success')]"
        )

        if len(success_message) > 0:

            test_results.append(
                "TC-UC11-004 : PASS"
            )

        else:

            test_results.append(
                "TC-UC11-004 : FAIL"
            )

            test_defects.append(
                "Alert configuration failed to save."
            )

    except Exception as e:

        test_results.append(
            "TC-UC11-004 : FAIL"
        )

        test_defects.append(str(e))

# ================================================================
# EXECUTE ALL TEST CASES
# ================================================================

tc_uc11_001()
tc_uc11_002()
tc_uc11_003()
tc_uc11_004()

# ================================================================
# DISPLAY TEST SUMMARY
# ================================================================

print("\n================================================")
print("UC11 SELENIUM TEST EXECUTION SUMMARY")
print("================================================")

for result in test_results:

    print(result)

print("\n================================================")
print("DEFECT LOG")
print("================================================")

for defect in test_defects:

    print(defect)

# ================================================================
# CLOSE DRIVER
# ================================================================

time.sleep(2)

driver.quit()
