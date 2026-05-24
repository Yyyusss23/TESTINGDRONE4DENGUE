"""
UC2 Register - Web Selenium Test Script
Testing Level: System Testing
Techniques Applied:
  - Boundary Value Analysis (BVA)
  - Decision Table Testing (DT)
  - State Transition Testing (ST)
Test Cases:
  TC-UC02-07 — Phone Number Length Boundary Validation
  TC-UC02-08 — Password Length Boundary + Composition Validation
  TC-UC02-09 — Password vs Confirm Password Mismatch
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
BASE_URL       = "http://localhost:3000"
REGISTER_PATH  = "/signup"
SCRIPT_DIR     = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIR = os.path.join(SCRIPT_DIR, "UC2_screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# ── Shared valid field data (non-email fields) ───────────────────────
VALID_NAME     = "Test User"
VALID_USERNAME = "testuser_bva"

# ── Unique emails per attempt (no redundancy across all test cases) ──
# TC-UC02-07: Phone BVA
EMAIL_TC07_BVA08 = "reg_phone7d@drone4dengue.com"    # BVA-08: 7 digits  (invalid)
EMAIL_TC07_BVA09 = "reg_phone8d@drone4dengue.com"    # BVA-09: 8 digits  (valid)
EMAIL_TC07_BVA10 = "reg_phone15d@drone4dengue.com"   # BVA-10: 15 digits (valid)
EMAIL_TC07_BVA11 = "reg_phone16d@drone4dengue.com"   # BVA-11: 16 digits (invalid)

# TC-UC02-08: Password BVA
EMAIL_TC08_BVA12 = "reg_pass7chr@drone4dengue.com"   # BVA-12: 7 chars (invalid length)
EMAIL_TC08_BVA13 = "reg_passnodig@drone4dengue.com"  # BVA-13: 8 chars no digit (invalid composition)
EMAIL_TC08_BVA14 = "reg_pass8dig@drone4dengue.com"   # BVA-14: 8 chars + digit (valid)
EMAIL_TC08_BVA15 = "reg_pass9dig@drone4dengue.com"   # BVA-15: 9 chars + digit (valid)

# TC-UC02-09: Password mismatch
EMAIL_TC09_MISM  = "reg_pwmismatch@drone4dengue.com" # BVA-16 / DT-09: confirm password mismatch

# ── Phone boundary values ────────────────────────────────────────────
PHONE_7_DIGITS  = "1234567"           # BVA-08: below minimum (INVALID)
PHONE_8_DIGITS  = "12345678"          # BVA-09: at minimum boundary (VALID)
PHONE_15_DIGITS = "123456789012345"   # BVA-10: at maximum boundary (VALID)
PHONE_16_DIGITS = "1234567890123456"  # BVA-11: above maximum (INVALID)

# ── Password boundary / composition values ───────────────────────────
PASS_7_CHARS      = "Pass123"    # BVA-12: 7 chars — below minimum (INVALID)
PASS_8_NO_DIGIT   = "Password"   # BVA-13: 8 chars, no digit — composition violation (INVALID)
PASS_8_WITH_DIGIT = "Pass@123"   # BVA-14: 8 chars with digit — at minimum boundary (VALID)
PASS_9_WITH_DIGIT = "Pass@1234"  # BVA-15: 9 chars with digit — above minimum (VALID)

# ── Password mismatch values ─────────────────────────────────────────
MISMATCH_PASSWORD         = "Password@1"   # BVA-16 / DT-09
MISMATCH_CONFIRM_PASSWORD = "Password@2"

# ─────────────────────────────────────────────
# DRIVER & WAIT SETUP
# ─────────────────────────────────────────────
driver  = webdriver.Chrome()
driver.maximize_window()
wait    = WebDriverWait(driver, 15)
results = []


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def screenshot_full(filename):
    try:
        h = driver.execute_script("return document.body.scrollHeight")
        h = min(max(h, 900), 6000)
        driver.set_window_size(1440, h)
        time.sleep(0.3)
        path = os.path.join(SCREENSHOT_DIR, filename)
        driver.save_screenshot(path)
        print(f"   📸 Screenshot: {filename}")
        driver.maximize_window()
        time.sleep(0.2)
    except Exception as e:
        print(f"   ⚠️  Screenshot failed: {e}")


def find_el(by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def tap_el(by, value, timeout=10):
    el = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )
    el.click()
    return el


def has_text(*keywords):
    src = driver.page_source.lower()
    return any(k.lower() in src for k in keywords)


def has_error(keywords=None):
    if keywords is None:
        keywords = ["text-red", "border-red", "error", "invalid",
                    "incorrect", "required", "denied"]
    return has_text(*keywords)


def record(tc_id, status, note=""):
    if status is True:
        tag = "✅ PASS"
    elif status is False:
        tag = "❌ FAIL"
    else:
        tag = "ℹ️  N/A "
    line = f"{tag}  {tc_id}  {note}"
    results.append(line)
    print(f"   {line}")


def go_to_register():
    driver.get(f"{BASE_URL}{REGISTER_PATH}")
    time.sleep(1)
    wait.until(EC.presence_of_element_located((By.ID, "email")))
    time.sleep(0.5)


def fill_register_form(email=None, name=None, username=None,
                        phone=None, password=None, confirm_password=None,
                        select_first_company=True):
    if email is not None:
        field = wait.until(EC.presence_of_element_located((By.ID, "email")))
        field.clear()
        driver.execute_script("arguments[0].value = '';", field)
        field.send_keys(email)

    if name is not None:
        field = wait.until(EC.presence_of_element_located((By.ID, "name")))
        field.clear()
        driver.execute_script("arguments[0].value = '';", field)
        field.send_keys(name)

    if username is not None:
        field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        field.clear()
        driver.execute_script("arguments[0].value = '';", field)
        field.send_keys(username)

    if phone is not None:
        field = wait.until(EC.presence_of_element_located((By.ID, "phone")))
        field.clear()
        driver.execute_script("arguments[0].value = '';", field)
        field.send_keys(phone)

    if select_first_company:
        try:
            company_select = wait.until(
                EC.presence_of_element_located((By.ID, "company"))
            )
            options = company_select.find_elements(By.TAG_NAME, "option")
            for opt in options:
                if opt.get_attribute("value"):
                    opt.click()
                    break
        except (TimeoutException, NoSuchElementException):
            print("   ⚠️  Company dropdown not found or no options available.")

    if password is not None:
        field = wait.until(EC.presence_of_element_located((By.ID, "password")))
        field.clear()
        driver.execute_script("arguments[0].value = '';", field)
        field.send_keys(password)

    if confirm_password is not None:
        field = wait.until(EC.presence_of_element_located((By.ID, "confirmPassword")))
        field.clear()
        driver.execute_script("arguments[0].value = '';", field)
        field.send_keys(confirm_password)


def accept_terms():
    try:
        terms_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@aria-label='Accept Terms and Privacy Policy']")
            )
        )
        terms_btn.click()
        time.sleep(0.3)
    except TimeoutException:
        print("   ⚠️  Terms checkbox button not found.")


def click_submit():
    tap_el(By.CSS_SELECTOR, "button[type='submit']")
    time.sleep(2)


def trigger_blur(field_id):
    try:
        field = driver.find_element(By.ID, field_id)
        driver.execute_script("arguments[0].dispatchEvent(new Event('blur'));", field)
        time.sleep(0.5)
    except NoSuchElementException:
        pass


# ─────────────────────────────────────────────
# SESSION SETUP
# ─────────────────────────────────────────────

def setup_session():
    print("\n📋 Verifying registration page is accessible...")
    try:
        go_to_register()
        email_ok    = find_el(By.ID, "email")
        phone_ok    = find_el(By.ID, "phone")
        password_ok = find_el(By.ID, "password")
        confirm_ok  = find_el(By.ID, "confirmPassword")
        if email_ok and phone_ok and password_ok and confirm_ok:
            print(f"✅ Registration page loaded → {driver.current_url}")
            return True
        else:
            screenshot_full("UC2_Error_PageLoad.png")
            print("❌ Required form fields not found")
            return False
    except TimeoutException:
        screenshot_full("UC2_Error_PageLoad.png")
        print("❌ Registration page not reachable — is localhost:3000 running?")
        return False


# ─────────────────────────────────────────────
# TC-UC02-07 — Phone Number Length BVA
# BVA-08: 7 digits  → INVALID (below min)
# BVA-09: 8 digits  → VALID   (at minimum boundary)
# BVA-10: 15 digits → VALID   (at maximum boundary)
# BVA-11: 16 digits → INVALID (above max)
# Coverage: TCOV-02-006, TCOV-UC02-BVA-08 to BVA-11
# Rule: Phone must be 8–15 digits
# Each attempt uses a DIFFERENT email address
# ─────────────────────────────────────────────

def tc_uc02_07():
    print(f"\n▶ TC-UC02-07 — Phone Number Length Boundary Value Analysis")
    print("   Technique: BVA-08, BVA-09, BVA-10, BVA-11")
    print("   Rule: Phone must be between 8 and 15 digits (inclusive)")

    # ── Attempt 1: BVA-08 — 7 digits (below minimum, INVALID) ──
    print(f"\n   [BVA-08] email='{EMAIL_TC07_BVA08}' | "
          f"phone='{PHONE_7_DIGITS}' (7 digits — BELOW minimum, invalid)")
    try:
        go_to_register()
        fill_register_form(
            email=EMAIL_TC07_BVA08, name=VALID_NAME, username=VALID_USERNAME,
            phone=PHONE_7_DIGITS, password=PASS_8_WITH_DIGIT,
            confirm_password=PASS_8_WITH_DIGIT, select_first_company=True
        )
        accept_terms()
        trigger_blur("phone")
        screenshot_full("UC2_TC07a_Phone7Digits.png")

        if has_error(["8 digits", "at least 8", "minimum", "invalid phone",
                      "valid phone", "text-red", "border-red", "yellow-200"]):
            record("TC-UC02-07a (BVA-08)", True,
                   f"PASS — '{PHONE_7_DIGITS}' (7 digits) rejected (BVA-08) "
                   f"[email: {EMAIL_TC07_BVA08}]. "
                   "Error: phone below minimum length shown. Registration blocked.")
        else:
            record("TC-UC02-07a (BVA-08)", False,
                   f"FAIL — '{PHONE_7_DIGITS}' (7 digits) NOT rejected "
                   f"[email: {EMAIL_TC07_BVA08}]. "
                   "Defect: minimum phone length validation missing.")
    except Exception as e:
        screenshot_full("UC2_Error_TC07a.png")
        record("TC-UC02-07a (BVA-08)", False, f"Exception: {e}")

    # ── Attempt 2: BVA-09 — 8 digits (at minimum boundary, VALID) ──
    print(f"\n   [BVA-09] email='{EMAIL_TC07_BVA09}' | "
          f"phone='{PHONE_8_DIGITS}' (8 digits — AT minimum boundary, valid)")
    try:
        go_to_register()
        fill_register_form(
            email=EMAIL_TC07_BVA09, name=VALID_NAME, username=VALID_USERNAME,
            phone=PHONE_8_DIGITS, password=PASS_8_WITH_DIGIT,
            confirm_password=PASS_8_WITH_DIGIT, select_first_company=True
        )
        accept_terms()
        trigger_blur("phone")
        screenshot_full("UC2_TC07b_Phone8Digits.png")

        phone_rejected = has_error(["8 digits", "at least 8", "minimum",
                                    "invalid phone", "valid phone"])
        if not phone_rejected:
            record("TC-UC02-07b (BVA-09)", True,
                   f"PASS — '{PHONE_8_DIGITS}' (8 digits) accepted by phone length rule (BVA-09) "
                   f"[email: {EMAIL_TC07_BVA09}]. "
                   "At minimum boundary. Proceeds to server validation.")
        else:
            record("TC-UC02-07b (BVA-09)", False,
                   f"FAIL — '{PHONE_8_DIGITS}' (8 digits) incorrectly rejected "
                   f"[email: {EMAIL_TC07_BVA09}]. "
                   "Defect: minimum boundary validation too strict.")
    except Exception as e:
        screenshot_full("UC2_Error_TC07b.png")
        record("TC-UC02-07b (BVA-09)", False, f"Exception: {e}")

    # ── Attempt 3: BVA-10 — 15 digits (at maximum boundary, VALID) ──
    print(f"\n   [BVA-10] email='{EMAIL_TC07_BVA10}' | "
          f"phone='{PHONE_15_DIGITS}' (15 digits — AT maximum boundary, valid)")
    try:
        go_to_register()
        fill_register_form(
            email=EMAIL_TC07_BVA10, name=VALID_NAME, username=VALID_USERNAME,
            phone=PHONE_15_DIGITS, password=PASS_8_WITH_DIGIT,
            confirm_password=PASS_8_WITH_DIGIT, select_first_company=True
        )
        accept_terms()
        trigger_blur("phone")
        screenshot_full("UC2_TC07c_Phone15Digits.png")

        phone_rejected = has_error(["exceed", "maximum", "too long",
                                    "invalid phone", "valid phone", "15"])
        if not phone_rejected:
            record("TC-UC02-07c (BVA-10)", True,
                   f"PASS — '{PHONE_15_DIGITS}' (15 digits) accepted by phone length rule (BVA-10) "
                   f"[email: {EMAIL_TC07_BVA10}]. "
                   "At maximum boundary. Proceeds to server validation.")
        else:
            record("TC-UC02-07c (BVA-10)", False,
                   f"FAIL — '{PHONE_15_DIGITS}' (15 digits) incorrectly rejected "
                   f"[email: {EMAIL_TC07_BVA10}]. "
                   "Defect: maximum boundary validation too strict.")
    except Exception as e:
        screenshot_full("UC2_Error_TC07c.png")
        record("TC-UC02-07c (BVA-10)", False, f"Exception: {e}")

    # ── Attempt 4: BVA-11 — 16 digits (above maximum, INVALID) ──
    print(f"\n   [BVA-11] email='{EMAIL_TC07_BVA11}' | "
          f"phone='{PHONE_16_DIGITS}' (16 digits — ABOVE maximum, invalid)")
    try:
        go_to_register()
        fill_register_form(
            email=EMAIL_TC07_BVA11, name=VALID_NAME, username=VALID_USERNAME,
            phone=PHONE_16_DIGITS, password=PASS_8_WITH_DIGIT,
            confirm_password=PASS_8_WITH_DIGIT, select_first_company=True
        )
        accept_terms()
        trigger_blur("phone")
        screenshot_full("UC2_TC07d_Phone16Digits.png")

        if has_error(["exceed", "maximum", "15 digits", "too long",
                      "invalid phone", "valid phone", "text-red",
                      "border-red", "yellow-200"]):
            record("TC-UC02-07d (BVA-11)", True,
                   f"PASS — '{PHONE_16_DIGITS}' (16 digits) rejected (BVA-11) "
                   f"[email: {EMAIL_TC07_BVA11}]. "
                   "Error: phone exceeds maximum length shown. Registration blocked.")
        else:
            record("TC-UC02-07d (BVA-11)", False,
                   f"FAIL — '{PHONE_16_DIGITS}' (16 digits) NOT rejected "
                   f"[email: {EMAIL_TC07_BVA11}]. "
                   "Defect: maximum phone length validation missing.")
    except Exception as e:
        screenshot_full("UC2_Error_TC07d.png")
        record("TC-UC02-07d (BVA-11)", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC02-08 — Password Length BVA + Composition Rule
# BVA-12: 7 chars              → INVALID (below minimum length)
# BVA-13: 8 chars, no digit   → INVALID (composition rule violated)
# BVA-14: 8 chars with digit  → VALID   (at minimum boundary)
# BVA-15: 9 chars with digit  → VALID   (above minimum)
# Coverage: TCOV-02-007, TCOV-UC02-BVA-12 to BVA-15, TCOV-UC01-DT-08
# Rule: Password ≥ 8 chars AND must contain at least one digit
# Each attempt uses a DIFFERENT email address
# ─────────────────────────────────────────────

def tc_uc02_08():
    print(f"\n▶ TC-UC02-08 — Password Length BVA + Composition Rule")
    print("   Technique: BVA-12, BVA-13, BVA-14, BVA-15, DT-08")
    print("   Rule: Password must be ≥ 8 characters AND contain at least one digit")

    # ── Attempt 1: BVA-12 — 7 chars (below minimum, INVALID) ──
    print(f"\n   [BVA-12] email='{EMAIL_TC08_BVA12}' | "
          f"password='{PASS_7_CHARS}' (7 chars — BELOW minimum, invalid)")
    try:
        go_to_register()
        fill_register_form(
            email=EMAIL_TC08_BVA12, name=VALID_NAME, username=VALID_USERNAME,
            phone=PHONE_8_DIGITS, password=PASS_7_CHARS,
            confirm_password=PASS_7_CHARS, select_first_company=True
        )
        accept_terms()
        trigger_blur("password")
        screenshot_full("UC2_TC08a_Pass7Chars.png")

        if has_error(["at least 8", "8 characters", "minimum",
                      "too short", "text-red", "border-red", "light-bg"]):
            record("TC-UC02-08a (BVA-12)", True,
                   f"PASS — '{PASS_7_CHARS}' (7 chars) rejected (BVA-12) "
                   f"[email: {EMAIL_TC08_BVA12}]. "
                   "Error: password below minimum 8-character rule shown. "
                   "Registration blocked.")
        else:
            record("TC-UC02-08a (BVA-12)", False,
                   f"FAIL — '{PASS_7_CHARS}' (7 chars) NOT rejected "
                   f"[email: {EMAIL_TC08_BVA12}]. "
                   "Defect: minimum password length validation missing.")
    except Exception as e:
        screenshot_full("UC2_Error_TC08a.png")
        record("TC-UC02-08a (BVA-12)", False, f"Exception: {e}")

    # ── Attempt 2: BVA-13 — 8 chars, no digit (composition violation, INVALID) ──
    print(f"\n   [BVA-13] email='{EMAIL_TC08_BVA13}' | "
          f"password='{PASS_8_NO_DIGIT}' (8 chars, no digit — composition violation)")
    try:
        go_to_register()
        fill_register_form(
            email=EMAIL_TC08_BVA13, name=VALID_NAME, username=VALID_USERNAME,
            phone=PHONE_8_DIGITS, password=PASS_8_NO_DIGIT,
            confirm_password=PASS_8_NO_DIGIT, select_first_company=True
        )
        accept_terms()
        trigger_blur("password")
        screenshot_full("UC2_TC08b_Pass8NoDigit.png")

        if has_error(["number", "digit", "include a number", "contain",
                      "text-red", "border-red", "light-bg"]):
            record("TC-UC02-08b (BVA-13)", True,
                   f"PASS — '{PASS_8_NO_DIGIT}' (8 chars, no digit) rejected (BVA-13, DT-08) "
                   f"[email: {EMAIL_TC08_BVA13}]. "
                   "Error: password must contain at least one number shown. "
                   "Registration blocked.")
        else:
            record("TC-UC02-08b (BVA-13)", False,
                   f"FAIL — '{PASS_8_NO_DIGIT}' (no digit) NOT rejected "
                   f"[email: {EMAIL_TC08_BVA13}]. "
                   "Defect: password composition rule (digit required) not enforced.")
    except Exception as e:
        screenshot_full("UC2_Error_TC08b.png")
        record("TC-UC02-08b (BVA-13)", False, f"Exception: {e}")

    # ── Attempt 3: BVA-14 — 8 chars with digit (at minimum boundary, VALID) ──
    print(f"\n   [BVA-14] email='{EMAIL_TC08_BVA14}' | "
          f"password='{PASS_8_WITH_DIGIT}' (8 chars with digit — AT minimum boundary, valid)")
    try:
        go_to_register()
        fill_register_form(
            email=EMAIL_TC08_BVA14, name=VALID_NAME, username=VALID_USERNAME,
            phone=PHONE_8_DIGITS, password=PASS_8_WITH_DIGIT,
            confirm_password=PASS_8_WITH_DIGIT, select_first_company=True
        )
        accept_terms()
        trigger_blur("password")
        screenshot_full("UC2_TC08c_Pass8WithDigit.png")

        pass_rejected = has_error(["at least 8", "8 characters", "minimum",
                                   "too short", "number", "digit", "include a number"])
        if not pass_rejected:
            record("TC-UC02-08c (BVA-14)", True,
                   f"PASS — '{PASS_8_WITH_DIGIT}' (8 chars + digit) accepted (BVA-14) "
                   f"[email: {EMAIL_TC08_BVA14}]. "
                   "At minimum boundary. No password validation error raised. "
                   "Proceeds to server validation.")
        else:
            record("TC-UC02-08c (BVA-14)", False,
                   f"FAIL — '{PASS_8_WITH_DIGIT}' incorrectly rejected "
                   f"[email: {EMAIL_TC08_BVA14}]. "
                   "Defect: minimum boundary validation too strict.")
    except Exception as e:
        screenshot_full("UC2_Error_TC08c.png")
        record("TC-UC02-08c (BVA-14)", False, f"Exception: {e}")

    # ── Attempt 4: BVA-15 — 9 chars with digit (above minimum, VALID) ──
    print(f"\n   [BVA-15] email='{EMAIL_TC08_BVA15}' | "
          f"password='{PASS_9_WITH_DIGIT}' (9 chars with digit — above minimum, valid)")
    try:
        go_to_register()
        fill_register_form(
            email=EMAIL_TC08_BVA15, name=VALID_NAME, username=VALID_USERNAME,
            phone=PHONE_8_DIGITS, password=PASS_9_WITH_DIGIT,
            confirm_password=PASS_9_WITH_DIGIT, select_first_company=True
        )
        accept_terms()
        trigger_blur("password")
        screenshot_full("UC2_TC08d_Pass9WithDigit.png")

        pass_rejected = has_error(["at least 8", "8 characters", "minimum",
                                   "too short", "number", "digit", "include a number"])
        if not pass_rejected:
            record("TC-UC02-08d (BVA-15)", True,
                   f"PASS — '{PASS_9_WITH_DIGIT}' (9 chars + digit) accepted (BVA-15) "
                   f"[email: {EMAIL_TC08_BVA15}]. "
                   "Above minimum. No password validation error raised.")
        else:
            record("TC-UC02-08d (BVA-15)", False,
                   f"FAIL — '{PASS_9_WITH_DIGIT}' (9 chars + digit) incorrectly rejected "
                   f"[email: {EMAIL_TC08_BVA15}]. "
                   "Defect: boundary validation logic incorrect.")
    except Exception as e:
        screenshot_full("UC2_Error_TC08d.png")
        record("TC-UC02-08d (BVA-15)", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC02-09 — Password vs Confirm Password Mismatch
# Techniques: BVA-16, DT-09, ST-03
# Coverage: TCOV-02-008, TCOV-UC02-BVA-16, TCOV-UC01-DT-09, TCOV-UC02-ST-03
# Rule: Password and Confirm Password must match exactly
# Uses EMAIL_TC09_MISM — unique, different from all TC-07/TC-08 emails
# ─────────────────────────────────────────────

def tc_uc02_09():
    print(f"\n▶ TC-UC02-09 — Password vs Confirm Password Mismatch")
    print("   Technique: BVA-16, DT-09, ST-03")
    print(f"   email='{EMAIL_TC09_MISM}' | "
          f"password='{MISMATCH_PASSWORD}', confirmPassword='{MISMATCH_CONFIRM_PASSWORD}'")
    print("   Expected: Error message shown, registration blocked, user stays on page")
    try:
        go_to_register()
        screenshot_full("UC2_TC09_BeforeSubmit.png")

        fill_register_form(
            email=EMAIL_TC09_MISM, name=VALID_NAME, username=VALID_USERNAME,
            phone=PHONE_8_DIGITS,
            password=MISMATCH_PASSWORD,
            confirm_password=MISMATCH_CONFIRM_PASSWORD,
            select_first_company=True
        )
        accept_terms()

        trigger_blur("confirmPassword")
        screenshot_full("UC2_TC09_AfterBlur.png")

        click_submit()
        screenshot_full("UC2_TC09_AfterSubmit.png")

        still_on_register = (
            REGISTER_PATH in driver.current_url or
            "/" == driver.current_url.replace(BASE_URL, "") or
            "register" in driver.current_url
        )

        mismatch_error_shown = has_error(
            ["do not match", "does not match", "passwords do not match",
             "confirmation does not match", "match", "text-red",
             "border-red", "light-bg", "yellow-200"]
        )

        if mismatch_error_shown and still_on_register:
            record("TC-UC02-09", True,
                   f"PASS — Password mismatch detected (BVA-16, DT-09) "
                   f"[email: {EMAIL_TC09_MISM}]. "
                   "Error: 'The passwords do not match.' shown. "
                   "Registration blocked. User remains on Registration page (ST-03).")
        elif mismatch_error_shown and not still_on_register:
            record("TC-UC02-09", False,
                   f"FAIL — Mismatch error shown BUT user was redirected away "
                   f"[email: {EMAIL_TC09_MISM}]. "
                   "Defect: form submission not fully blocked on mismatch.")
        elif not mismatch_error_shown and still_on_register:
            record("TC-UC02-09", False,
                   f"FAIL — User stayed on page but NO mismatch error message shown "
                   f"[email: {EMAIL_TC09_MISM}]. "
                   "Defect: confirm password validation error message missing.")
        else:
            record("TC-UC02-09", False,
                   f"FAIL — No mismatch error shown AND user was redirected "
                   f"[email: {EMAIL_TC09_MISM}]. "
                   "Defect: password confirmation validation completely missing.")
    except Exception as e:
        screenshot_full("UC2_Error_TC09.png")
        record("TC-UC02-09", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

try:
    print("=" * 66)
    print("  UC2 REGISTER — WEB SELENIUM TEST")
    print("  Testing Level: System Testing")
    print("  Test Cases: TC-UC02-07, TC-UC02-08, TC-UC02-09")
    print(f"  URL: {BASE_URL}{REGISTER_PATH}")
    print(f"  Screenshots: {SCREENSHOT_DIR}")
    print("=" * 66)
    print("\n  Test Cases and Unique Emails Used:")
    print(f"  TC-UC02-07a (BVA-08) → {EMAIL_TC07_BVA08}   | phone 7 digits  (invalid)")
    print(f"  TC-UC02-07b (BVA-09) → {EMAIL_TC07_BVA09}   | phone 8 digits  (valid)")
    print(f"  TC-UC02-07c (BVA-10) → {EMAIL_TC07_BVA10}  | phone 15 digits (valid)")
    print(f"  TC-UC02-07d (BVA-11) → {EMAIL_TC07_BVA11}  | phone 16 digits (invalid)")
    print(f"  TC-UC02-08a (BVA-12) → {EMAIL_TC08_BVA12}   | pass 7 chars (invalid)")
    print(f"  TC-UC02-08b (BVA-13) → {EMAIL_TC08_BVA13}  | pass 8 chars no digit (invalid)")
    print(f"  TC-UC02-08c (BVA-14) → {EMAIL_TC08_BVA14}   | pass 8 chars+digit (valid)")
    print(f"  TC-UC02-08d (BVA-15) → {EMAIL_TC08_BVA15}   | pass 9 chars+digit (valid)")
    print(f"  TC-UC02-09  (BVA-16) → {EMAIL_TC09_MISM}  | password mismatch")
    print("=" * 66)

    if setup_session():
        tc_uc02_07()   # BVA-08, BVA-09, BVA-10, BVA-11
        tc_uc02_08()   # BVA-12, BVA-13, BVA-14, BVA-15, DT-08
        tc_uc02_09()   # BVA-16, DT-09, ST-03
    else:
        print("🛑 Aborting — registration page not accessible")

except Exception as e:
    print(f"\n🛑 Unexpected error: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n" + "=" * 66)
    print("  TEST SUMMARY — UC2 Register (Web) | TC-UC02-07 to TC-UC02-09")
    print("=" * 66)
    passed = failed = na = 0
    for r in results:
        line = r if len(r) < 220 else r[:220] + "..."
        print(f"  {line}")
        if "✅" in r:    passed += 1
        elif "❌" in r:  failed += 1
        else:             na += 1
    print(f"\n  Total: {len(results)}  |  "
          f"✅ Passed: {passed}  |  "
          f"❌ Failed: {failed}  |  "
          f"ℹ️  N/A: {na}")
    print(f"\n  📁 Screenshots → {SCREENSHOT_DIR}")
    print("=" * 66)
    input("\nPress Enter to close browser...")
    driver.quit()