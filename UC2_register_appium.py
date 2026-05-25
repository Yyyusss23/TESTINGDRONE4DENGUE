"""
UC2 Registration - Mobile Appium Test Script
TC-UC02-01 through TC-UC02-12 (TC-01 to TC-06 and TC-10 to TC-12 added)
Testing Level: System Testing
Techniques Applied:
  - Boundary Value Analysis (BVA)
  - Decision Table Testing (DT)
  - State Transition Testing (ST)
  - Use Case Testing (UCT)
Tool: Appium + UiAutomator2 (Android)
"""

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os

# ─────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────
SCRIPT_DIR     = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIR = os.path.join(SCRIPT_DIR, "UC2_mobile_screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# ── TC-UC02-01: Valid registration (Admin Web — simulated on mobile) ──
EMAIL_TC01_VALID      = "webuser_uc02@drone4dengue.com"

# ── TC-UC02-02: Valid registration (Mobile App) ───────────────────────
EMAIL_TC02_VALID      = "mobileuser_uc02@drone4dengue.com"

# ── TC-UC02-03: Empty required fields ────────────────────────────────
EMAIL_TC03_VALID      = "reg_emptyfield@email.com"   # used for attempt-2 (full name empty)

# ── TC-UC02-04: Invalid email format ─────────────────────────────────
EMAIL_TC04_INVALID    = "newuser.drone4dengue.com"   # missing '@'

# ── TC-UC02-05: Duplicate / already-registered email ─────────────────
EMAIL_TC05_DUPLICATE  = "admin1@drone4dengue.com"    # confirmed already in DB

# ── TC-UC02-06: Username length BVA (BVA-05, BVA-06, BVA-07) ─────────
EMAIL_TC06_BVA05      = "reg_user2chr@email.com"     # BVA-05: 2-char username (invalid)
EMAIL_TC06_BVA06      = "reg_user3chr@email.com"     # BVA-06: 3-char username (valid)
EMAIL_TC06_BVA07      = "reg_user4chr@email.com"     # BVA-07: 4-char username (valid)

# ── TC-UC02-07: Phone number length BVA ──────────────────────────────
EMAIL_TC07_BVA08      = "reg_phone7d@email.com"      # BVA-08: 7 digits  (invalid)
EMAIL_TC07_BVA09      = "reg_phone8d@email.com"      # BVA-09: 8 digits  (valid)
EMAIL_TC07_BVA10      = "reg_phone15d@email.com"     # BVA-10: 15 digits (valid)
EMAIL_TC07_BVA11      = "reg_phone16d@email.com"     # BVA-11: 16 digits (invalid)

# ── TC-UC02-08: Password length & composition BVA ────────────────────
EMAIL_TC08_BVA12      = "reg_pass7chr@email.com"     # BVA-12: 7 chars, has digit (invalid len)
EMAIL_TC08_BVA13      = "reg_passnodig@email.com"    # BVA-13: 8 chars, no digit (invalid comp)
EMAIL_TC08_BVA14      = "reg_pass8dig@email.com"     # BVA-14: 8 chars with digit (valid)
EMAIL_TC08_BVA15      = "reg_pass9dig@email.com"     # BVA-15: 9 chars with digit (valid)

# ── TC-UC02-09: Password mismatch ────────────────────────────────────
EMAIL_TC09_MISM       = "reg_pwmismatch@email.com"   # BVA-16 / DT-09

# ── TC-UC02-10: Terms & Conditions unchecked ─────────────────────────
EMAIL_TC10_TERMS      = "reg_noterms@email.com"

# ── TC-UC02-11: 'Log In' link navigation ─────────────────────────────
# No email needed — navigation test only

# ── TC-UC02-12: 'Terms and Conditions Policy' link ───────────────────
# No email needed — navigation test only

# ── Phone boundary values ────────────────────────────────────────────
PHONE_7_DIGITS        = "1234567"             # BVA-08: below minimum (INVALID)
PHONE_8_DIGITS        = "12345678"            # BVA-09: at minimum boundary (VALID)
PHONE_15_DIGITS       = "123456789012345"     # BVA-10: at maximum boundary (VALID)
PHONE_16_DIGITS       = "1234567890123456"    # BVA-11: above maximum (INVALID)
PHONE_VALID           = "60123456789"         # shared valid phone for TC-01

# ── Password boundary / composition values ───────────────────────────
PASS_7_CHARS          = "Pass123"             # BVA-12: 7 chars — below minimum (INVALID)
PASS_NO_DIGIT         = "Password"            # BVA-13: 8 chars, no digit (INVALID)
PASS_8_WITH_DIGIT     = "Pass@123"            # BVA-14: 8 chars with digit — at minimum (VALID)
PASS_9_WITH_DIGIT     = "Pass@1234"           # BVA-15: 9 chars with digit — above minimum (VALID)

# ── Password mismatch values ─────────────────────────────────────────
PASS_MISMATCH_A       = "Password@1"
PASS_MISMATCH_B       = "Password@2"

# ── Shared valid credentials ──────────────────────────────────────────
VALID_PASSWORD        = "Mobile@123"
VALID_CONFIRM         = "Mobile@123"
VALID_PHONE           = "60123456789"
VALID_FULLNAME        = "Test User"
VALID_USERNAME        = "testuser01"

options = UiAutomator2Options()
options.platform_name   = "Android"
options.device_name     = "emulator-5554"
options.app_package     = "com.adamarbain.dengueeyemobileapp"
options.app_activity    = ".MainActivity"
options.no_reset        = False
options.automation_name = "UiAutomator2"

driver  = webdriver.Remote("http://127.0.0.1:4723", options=options)
wait    = WebDriverWait(driver, 20)
results = []


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def screenshot(filename):
    path = os.path.join(SCREENSHOT_DIR, filename)
    driver.save_screenshot(path)
    print(f"   📸 Screenshot saved: {filename}")


def find(by, value, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def tap(by, value, timeout=15):
    el = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )
    el.click()
    return el


def has_text(*keywords):
    source = driver.page_source.lower()
    return any(k.lower() in source for k in keywords)


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


def dismiss_ok():
    try:
        tap(AppiumBy.XPATH, "//*[@text='OK']", timeout=3)
        time.sleep(0.5)
    except TimeoutException:
        pass


def go_to_register():
    """Navigate to the Registration screen from any state."""
    driver.terminate_app("com.adamarbain.dengueeyemobileapp")
    time.sleep(1)
    driver.activate_app("com.adamarbain.dengueeyemobileapp")
    time.sleep(3)
    dismiss_ok()

    try:
        tap(AppiumBy.XPATH,
            "//*[@text='Sign Up' or contains(@text,'Sign Up') "
            "or @text='Register' or @text='Create Account']",
            timeout=10)
        time.sleep(2)
    except TimeoutException:
        print("   ⚠️  Sign Up button not found — may already be on Register screen")

    try:
        find(AppiumBy.XPATH,
             "//android.widget.EditText[@hint='Enter your email' "
             "or @text='Enter your email']", timeout=10)
        print("   ✅ Registration screen ready")
    except TimeoutException:
        print("   ⚠️  Could not confirm Registration screen")


def fill_register(email=None, password=None, confirm_password=None,
                  phone=None, full_name=None, username=None, agree=True):
    """
    Fill registration form fields. Pass None to skip a field.
    agree=False leaves the Terms & Conditions checkbox unchecked.
    """
    all_inputs = driver.find_elements(AppiumBy.XPATH, "//android.widget.EditText")
    print(f"   ℹ️  Found {len(all_inputs)} input field(s) on screen")

    def _fill_by_hint(hint_texts, value):
        for hint in hint_texts:
            try:
                field = find(AppiumBy.XPATH,
                             f"//android.widget.EditText[@hint='{hint}' "
                             f"or @text='{hint}']", timeout=5)
                field.clear()
                field.send_keys(value)
                return True
            except TimeoutException:
                continue
        return False

    if full_name is not None:
        filled = _fill_by_hint(
            ["Full Name", "Enter your full name", "Name"], full_name
        )
        if not filled:
            print("   ⚠️  Full Name field not found")

    if email is not None:
        _fill_by_hint(["Enter your email"], email)

    if username is not None:
        filled = _fill_by_hint(
            ["Username", "Enter your username", "User Name"], username
        )
        if not filled:
            print("   ⚠️  Username field not found")

    if phone is not None:
        filled = _fill_by_hint(
            ["Enter your phone number", "Phone number", "Phone"], phone
        )
        if not filled:
            print("   ⚠️  Phone field not found — may not exist in this form version")

    if password is not None:
        _fill_by_hint(["Create a password", "Enter your password", "Password"], password)

    if confirm_password is not None:
        _fill_by_hint(["Confirm your password", "Confirm Password"], confirm_password)

    if agree:
        # The register screen's T&C row is a Pressable wrapping:
        #   • a View (the visible checkbox square)
        #   • a Text: "I agree to DengueEye's Terms & Conditions and Privacy Policy"
        #     with two nested tappable Text spans ("Terms & Conditions", "Privacy Policy")
        #
        # We MUST tap the OUTER Pressable/ViewGroup (the checkbox row), NOT any inner
        # Text span — tapping the inner spans navigates to the T&C page instead of ticking.
        #
        # XPath priority order:
        #   1. content-desc on the outer Pressable (set by some RN builds)
        #   2. Clickable element containing the "I agree" sentence text
        #   3. Clickable ViewGroup ancestor of the "I agree" TextView
        _ticked = False

        # Attempt 1 — content-desc on the outer Pressable
        for cd in ["agree", "terms checkbox", "accept terms"]:
            try:
                el = find(AppiumBy.XPATH,
                          f"//*[contains(@content-desc,'{cd}')]", timeout=3)
                el.click()
                time.sleep(0.5)
                _ticked = True
                break
            except TimeoutException:
                continue

        # Attempt 2 — clickable element whose text starts with "I agree"
        if not _ticked:
            try:
                el = find(AppiumBy.XPATH,
                          "//*[contains(@text,'I agree') and @clickable='true']",
                          timeout=3)
                el.click()
                time.sleep(0.5)
                _ticked = True
            except TimeoutException:
                pass

        # Attempt 3 — clickable ViewGroup ancestor of the "I agree" TextView
        if not _ticked:
            try:
                el = find(AppiumBy.XPATH,
                          "//android.view.ViewGroup[@clickable='true' and "
                          ".//android.widget.TextView[contains(@text,'I agree')]]",
                          timeout=3)
                el.click()
                time.sleep(0.5)
                _ticked = True
            except TimeoutException:
                pass

        if not _ticked:
            print("   ⚠️  Terms & Conditions checkbox row not found — skipping tick")
    # If agree=False, intentionally skip — leave checkbox unchecked


def click_create_account():
    """Tap the Create Account / Register / Submit button."""
    tap(AppiumBy.XPATH,
        "//*[@text='Create Account' or @text='Register' "
        "or @text='Sign Up' or @text='Submit']")
    time.sleep(3)


# ─────────────────────────────────────────────
# SESSION SETUP
# ─────────────────────────────────────────────

def setup_session():
    print("\n📋 Verifying app launches and Register screen is reachable...")
    time.sleep(5)
    dismiss_ok()
    go_to_register()

    try:
        find(AppiumBy.XPATH,
             "//android.widget.EditText[@hint='Enter your email' "
             "or @text='Enter your email']", timeout=15)
        print("✅ Register screen is ready")
        return True
    except TimeoutException:
        screenshot("UC2_M_Error_AppLaunch.png")
        print("❌ Register screen not accessible")
        return False


# ─────────────────────────────────────────────
# TC-UC02-01 — Valid Registration (All Fields Correct)
# Techniques: TCOV-02-010, BVA-17, DT-06, UCT-02, ST-05
# Platform: Admin Web (simulated via mobile app)
# Expected: Success message shown, redirected to Login page
# ─────────────────────────────────────────────

def tc_uc02_01():
    print(f"\n▶ TC-UC02-01 — Valid Registration with All Required Fields")
    print("   Technique: BVA-17, DT-06, UCT-02, ST-05")
    print(f"   email='{EMAIL_TC01_VALID}' | phone='{PHONE_VALID}' | "
          f"username='{VALID_USERNAME}'")
    try:
        go_to_register()
        fill_register(
            full_name=VALID_FULLNAME,
            email=EMAIL_TC01_VALID,
            username=VALID_USERNAME,
            phone=PHONE_VALID,
            password="Test@123",
            confirm_password="Test@123",
            agree=True
        )
        screenshot("UC2_M_TC01_BeforeSubmit.png")
        click_create_account()
        screenshot("UC2_M_TC01_AfterSubmit.png")

        success_shown = has_text(
            "registration successful", "account created",
            "successfully registered", "success", "created"
        )
        on_login_page = has_text(
            "login", "log in", "sign in", "welcome back"
        )

        if success_shown or on_login_page:
            record("TC-UC02-01", True,
                   f"PASS — Valid registration accepted [email: {EMAIL_TC01_VALID}]. "
                   "Success message displayed and/or redirected to Login page (ST-05).")
        else:
            record("TC-UC02-01", False,
                   f"FAIL — Registration did not succeed [email: {EMAIL_TC01_VALID}]. "
                   "No success message or Login page redirect observed.")
    except Exception as e:
        screenshot("UC2_M_Error_TC01.png")
        record("TC-UC02-01", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC02-02 — Valid Registration (Mobile App)
# Techniques: TCOV-02-010, UCT-01, ST-05
# Expected: Account created, success message, redirect to Login
# ─────────────────────────────────────────────

def tc_uc02_02():
    print(f"\n▶ TC-UC02-02 — Valid Registration on Mobile App")
    print("   Technique: UCT-01, ST-05")
    print(f"   email='{EMAIL_TC02_VALID}'")
    try:
        go_to_register()
        fill_register(
            email=EMAIL_TC02_VALID,
            password="Mobile@123",
            confirm_password="Mobile@123",
            agree=True
            # phone, username, full_name omitted — not under test in TC-02
        )
        screenshot("UC2_M_TC02_BeforeSubmit.png")
        click_create_account()
        screenshot("UC2_M_TC02_AfterSubmit.png")

        success_shown = has_text(
            "registration successful", "account created",
            "successfully registered", "success", "created"
        )
        on_login_page = has_text(
            "login", "log in", "sign in", "welcome back"
        )

        if success_shown or on_login_page:
            record("TC-UC02-02", True,
                   f"PASS — Valid mobile registration accepted [email: {EMAIL_TC02_VALID}]. "
                   "Success message shown and/or redirected to Login page (ST-05).")
        else:
            record("TC-UC02-02", False,
                   f"FAIL — Mobile registration did not succeed [email: {EMAIL_TC02_VALID}]. "
                   "No success message or Login page redirect observed.")
    except Exception as e:
        screenshot("UC2_M_Error_TC02.png")
        record("TC-UC02-02", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC02-03 — Empty Required Fields Validation
# Techniques: TCOV-02-001, BVA-01, BVA-02, UCT-06, ST-01
# Attempt 1: Email empty, all other fields valid
# Attempt 2: Full Name empty, all other fields valid
# Expected: Each attempt blocked with field-specific error
# ─────────────────────────────────────────────

def tc_uc02_03():
    print(f"\n▶ TC-UC02-03 — Empty Required Fields Validation")
    print("   Technique: BVA-01, BVA-02, UCT-06, ST-01")

    # ── Attempt 1: Empty email ───────────────────────────────────────
    print(f"\n   [Attempt 1] Email empty — all other fields valid")
    try:
        go_to_register()
        fill_register(
            email="",              # intentionally empty — field under test
            password=VALID_PASSWORD,
            confirm_password=VALID_CONFIRM,
            agree=True
            # phone, username, full_name omitted — not under test in TC-03a
        )
        click_create_account()
        screenshot("UC2_M_TC03a_EmptyEmail.png")

        email_error = has_text(
            "email is required", "email cannot be empty",
            "enter your email", "email field", "required"
        )
        still_on_register = has_text(
            "create account", "register", "sign up", "enter your email"
        )

        if email_error and still_on_register:
            record("TC-UC02-03a", True,
                   "PASS — Empty email rejected (BVA-01). "
                   "Error: 'Email is required'. Registration blocked. "
                   "User remains on Registration page (ST-01).")
        elif email_error:
            record("TC-UC02-03a", True,
                   "PASS — Empty email error shown (BVA-01). Registration blocked.")
        else:
            record("TC-UC02-03a", False,
                   "FAIL — Empty email NOT rejected. "
                   "Defect: email required-field validation missing.")
    except Exception as e:
        screenshot("UC2_M_Error_TC03a.png")
        record("TC-UC02-03a", False, f"Exception: {e}")

    # ── Attempt 2: Empty Full Name ───────────────────────────────────
    print(f"\n   [Attempt 2] Full Name empty — all other fields valid "
          f"[email: {EMAIL_TC03_VALID}]")
    try:
        go_to_register()
        fill_register(
            email=EMAIL_TC03_VALID,
            full_name="",          # intentionally empty — field under test
            password=VALID_PASSWORD,
            confirm_password=VALID_CONFIRM,
            agree=True
            # phone, username omitted — not under test in TC-03b
        )
        click_create_account()
        screenshot("UC2_M_TC03b_EmptyFullName.png")

        name_error = has_text(
            "full name is required", "name is required",
            "name cannot be empty", "enter your name",
            "name field", "required"
        )
        still_on_register = has_text(
            "create account", "register", "sign up", "enter your email"
        )

        if name_error and still_on_register:
            record("TC-UC02-03b", True,
                   f"PASS — Empty Full Name rejected (BVA-02) "
                   f"[email: {EMAIL_TC03_VALID}]. "
                   "Error: 'Full Name is required'. Registration blocked. "
                   "User remains on Registration page (ST-01).")
        elif name_error:
            record("TC-UC02-03b", True,
                   f"PASS — Empty Full Name error shown (BVA-02) "
                   f"[email: {EMAIL_TC03_VALID}].")
        else:
            record("TC-UC02-03b", False,
                   f"FAIL — Empty Full Name NOT rejected [email: {EMAIL_TC03_VALID}]. "
                   "Defect: Full Name required-field validation missing.")
    except Exception as e:
        screenshot("UC2_M_Error_TC03b.png")
        record("TC-UC02-03b", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC02-04 — Invalid Email Format (Missing '@')
# Techniques: TCOV-02-003, DT-07, ST (stays on Registration)
# Input: 'newuser.drone4dengue.com' (no '@')
# Expected: Error 'Invalid email address'. Registration blocked.
# ─────────────────────────────────────────────

def tc_uc02_04():
    print(f"\n▶ TC-UC02-04 — Invalid Email Format (Missing '@')")
    print("   Technique: DT-07, ST")
    print(f"   email='{EMAIL_TC04_INVALID}'")
    try:
        go_to_register()
        fill_register(
            email=EMAIL_TC04_INVALID,
            password=VALID_PASSWORD,
            confirm_password=VALID_CONFIRM,
            agree=True
            # phone, username, full_name omitted — not under test in TC-04
        )
        click_create_account()
        screenshot("UC2_M_TC04_InvalidEmailFormat.png")

        format_error = has_text(
            "invalid email", "valid email", "email format",
            "enter a valid email", "invalid email address",
            "please enter a valid"
        )
        still_on_register = has_text(
            "create account", "register", "sign up", "enter your email"
        )

        if format_error and still_on_register:
            record("TC-UC02-04", True,
                   f"PASS — Invalid email format '{EMAIL_TC04_INVALID}' rejected (DT-07). "
                   "Error: 'Invalid email address'. Registration blocked. "
                   "User remains on Registration page.")
        elif format_error:
            record("TC-UC02-04", True,
                   f"PASS — Invalid email format error shown (DT-07) "
                   f"for '{EMAIL_TC04_INVALID}'.")
        else:
            record("TC-UC02-04", False,
                   f"FAIL — Invalid email '{EMAIL_TC04_INVALID}' NOT rejected. "
                   "Defect: email format validation missing.")
    except Exception as e:
        screenshot("UC2_M_Error_TC04.png")
        record("TC-UC02-04", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC02-05 — Duplicate / Already-Registered Email
# Techniques: TCOV-02-004, DT-10, UCT-05, ST-04
# Input: admin1@drone4dengue.com (confirmed already in DB)
# Expected: Error 'Email already registered'. Registration blocked.
# ─────────────────────────────────────────────

def tc_uc02_05():
    print(f"\n▶ TC-UC02-05 — Duplicate Email Registration Attempt")
    print("   Technique: DT-10, UCT-05, ST-04")
    print(f"   email='{EMAIL_TC05_DUPLICATE}' (already registered)")
    try:
        go_to_register()
        fill_register(
            email=EMAIL_TC05_DUPLICATE,
            password=VALID_PASSWORD,
            confirm_password=VALID_CONFIRM,
            agree=True
            # phone, username, full_name omitted — not under test in TC-05
        )
        click_create_account()
        screenshot("UC2_M_TC05_DuplicateEmail.png")

        duplicate_error = has_text(
            "already registered", "already exists", "email already",
            "email is taken", "account already", "already in use",
            "email already registered", "already have an account"
        )
        still_on_register = has_text(
            "create account", "register", "sign up", "enter your email"
        )

        if duplicate_error and still_on_register:
            record("TC-UC02-05", True,
                   f"PASS — Duplicate email '{EMAIL_TC05_DUPLICATE}' rejected (DT-10, ST-04). "
                   "Error: 'Email already registered'. Registration blocked. "
                   "User remains on Registration page.")
        elif duplicate_error:
            record("TC-UC02-05", True,
                   f"PASS — Duplicate email error shown (DT-10) "
                   f"for '{EMAIL_TC05_DUPLICATE}'.")
        else:
            record("TC-UC02-05", False,
                   f"FAIL — Duplicate email '{EMAIL_TC05_DUPLICATE}' NOT rejected. "
                   "Defect: duplicate email validation missing (DT-10, UCT-05).")
    except Exception as e:
        screenshot("UC2_M_Error_TC05.png")
        record("TC-UC02-05", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC02-06 — Username Length BVA
# BVA-05: 2 chars → INVALID (below minimum)
# BVA-06: 3 chars → VALID   (at minimum boundary)
# BVA-07: 4 chars → VALID   (above minimum boundary)
# Rule: Username must be at least 3 characters
# Each attempt uses a DIFFERENT email address
# ─────────────────────────────────────────────

def tc_uc02_06():
    print(f"\n▶ TC-UC02-06 — Username Length Boundary Value Analysis")
    print("   Technique: BVA-05, BVA-06, BVA-07 | Rule: minimum 3 characters")

    attempts = [
        {
            "label":    "BVA-05",
            "email":    EMAIL_TC06_BVA05,
            "username": "ab",
            "chars":    2,
            "expect":   "invalid",
            "tc_id":    "TC-UC02-06a (BVA-05)",
            "shot":     "UC2_M_TC06a_BVA05_2chars.png",
            "pass_msg": f"PASS — 2-char username 'ab' rejected (BVA-05) "
                        f"[email: {EMAIL_TC06_BVA05}]. "
                        "Error: 'Username must be at least 3 characters'. "
                        "Registration blocked.",
            "fail_msg": f"FAIL — 2-char username 'ab' NOT rejected [email: {EMAIL_TC06_BVA05}]. "
                        "Defect: minimum username length validation missing.",
        },
        {
            "label":    "BVA-06",
            "email":    EMAIL_TC06_BVA06,
            "username": "abc",
            "chars":    3,
            "expect":   "valid",
            "tc_id":    "TC-UC02-06b (BVA-06)",
            "shot":     "UC2_M_TC06b_BVA06_3chars.png",
            "pass_msg": f"PASS — 3-char username 'abc' accepted (BVA-06) "
                        f"[email: {EMAIL_TC06_BVA06}]. "
                        "At minimum boundary. No username length error shown.",
            "fail_msg": f"FAIL — 3-char username 'abc' incorrectly rejected "
                        f"[email: {EMAIL_TC06_BVA06}]. "
                        "Defect: minimum boundary validation too strict.",
        },
        {
            "label":    "BVA-07",
            "email":    EMAIL_TC06_BVA07,
            "username": "abcd",
            "chars":    4,
            "expect":   "valid",
            "tc_id":    "TC-UC02-06c (BVA-07)",
            "shot":     "UC2_M_TC06c_BVA07_4chars.png",
            "pass_msg": f"PASS — 4-char username 'abcd' accepted (BVA-07) "
                        f"[email: {EMAIL_TC06_BVA07}]. "
                        "Above minimum boundary. No username length error.",
            "fail_msg": f"FAIL — 4-char username 'abcd' incorrectly rejected "
                        f"[email: {EMAIL_TC06_BVA07}]. "
                        "Defect: username length validation logic incorrect.",
        },
    ]

    for attempt in attempts:
        print(f"\n   [{attempt['label']}] email='{attempt['email']}' | "
              f"username='{attempt['username']}' ({attempt['chars']} chars — "
              f"expect {attempt['expect'].upper()})")
        try:
            go_to_register()
            fill_register(
                email=attempt["email"],
                username=attempt["username"],   # field under test
                password=VALID_PASSWORD,
                confirm_password=VALID_CONFIRM,
                agree=True
                # phone, full_name omitted — not under test in TC-06
            )
            click_create_account()
            screenshot(attempt["shot"])

            username_error_shown = has_text(
                "username", "3 character", "at least 3",
                "too short", "minimum", "username must"
            )

            if attempt["expect"] == "invalid":
                if username_error_shown:
                    record(attempt["tc_id"], True, attempt["pass_msg"])
                else:
                    record(attempt["tc_id"], False, attempt["fail_msg"])
            else:
                if not username_error_shown:
                    record(attempt["tc_id"], True, attempt["pass_msg"])
                else:
                    record(attempt["tc_id"], False, attempt["fail_msg"])

        except Exception as e:
            screenshot(f"UC2_M_Error_TC06_{attempt['label']}.png")
            record(attempt["tc_id"], False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC02-07 — Phone Number Length BVA
# BVA-08: 7 digits  → INVALID (below min)
# BVA-09: 8 digits  → VALID   (at minimum boundary)
# BVA-10: 15 digits → VALID   (at maximum boundary)
# BVA-11: 16 digits → INVALID (above max)
# Rule: Phone must be 8–15 digits
# Each attempt uses a DIFFERENT email address
# ─────────────────────────────────────────────

def tc_uc02_07():
    print(f"\n▶ TC-UC02-07 — Phone Number Length Boundary Value Analysis")
    print("   Technique: BVA-08, BVA-09, BVA-10, BVA-11 | Rule: 8–15 digits")

    attempts = [
        {
            "label":    "BVA-08",
            "email":    EMAIL_TC07_BVA08,
            "phone":    PHONE_7_DIGITS,
            "digits":   7,
            "expect":   "invalid",
            "tc_id":    "TC-UC02-07a (BVA-08)",
            "shot":     "UC2_M_TC07a_BVA08_7digits.png",
            "pass_msg": f"PASS — 7-digit phone '{PHONE_7_DIGITS}' rejected (BVA-08) "
                        f"[email: {EMAIL_TC07_BVA08}]. "
                        "Error: phone must be at least 8 digits. Registration blocked.",
            "fail_msg": f"FAIL — 7-digit phone NOT rejected [email: {EMAIL_TC07_BVA08}]. "
                        "Defect: minimum phone length validation missing.",
        },
        {
            "label":    "BVA-09",
            "email":    EMAIL_TC07_BVA09,
            "phone":    PHONE_8_DIGITS,
            "digits":   8,
            "expect":   "valid",
            "tc_id":    "TC-UC02-07b (BVA-09)",
            "shot":     "UC2_M_TC07b_BVA09_8digits.png",
            "pass_msg": f"PASS — 8-digit phone '{PHONE_8_DIGITS}' accepted by length rule (BVA-09) "
                        f"[email: {EMAIL_TC07_BVA09}]. "
                        "No phone length error. Proceeds to server validation.",
            "fail_msg": f"FAIL — 8-digit phone incorrectly rejected [email: {EMAIL_TC07_BVA09}]. "
                        "Defect: minimum boundary validation too strict.",
        },
        {
            "label":    "BVA-10",
            "email":    EMAIL_TC07_BVA10,
            "phone":    PHONE_15_DIGITS,
            "digits":   15,
            "expect":   "valid",
            "tc_id":    "TC-UC02-07c (BVA-10)",
            "shot":     "UC2_M_TC07c_BVA10_15digits.png",
            "pass_msg": f"PASS — 15-digit phone accepted by length rule (BVA-10) "
                        f"[email: {EMAIL_TC07_BVA10}]. "
                        "At maximum boundary. No phone length error.",
            "fail_msg": f"FAIL — 15-digit phone incorrectly rejected [email: {EMAIL_TC07_BVA10}]. "
                        "Defect: maximum boundary validation too strict.",
        },
        {
            "label":    "BVA-11",
            "email":    EMAIL_TC07_BVA11,
            "phone":    PHONE_16_DIGITS,
            "digits":   16,
            "expect":   "invalid",
            "tc_id":    "TC-UC02-07d (BVA-11)",
            "shot":     "UC2_M_TC07d_BVA11_16digits.png",
            "pass_msg": f"PASS — 16-digit phone '{PHONE_16_DIGITS}' rejected (BVA-11) "
                        f"[email: {EMAIL_TC07_BVA11}]. "
                        "Error: phone cannot exceed 15 digits.",
            "fail_msg": f"FAIL — 16-digit phone NOT rejected [email: {EMAIL_TC07_BVA11}]. "
                        "Defect: maximum phone length validation missing.",
        },
    ]

    for attempt in attempts:
        print(f"\n   [{attempt['label']}] email='{attempt['email']}' | "
              f"phone='{attempt['phone']}' ({attempt['digits']} digits — "
              f"expect {attempt['expect'].upper()})")
        try:
            go_to_register()
            fill_register(
                email=attempt["email"],
                phone=attempt["phone"],         # field under test
                password=VALID_PASSWORD,
                confirm_password=VALID_CONFIRM,
                agree=True
                # username, full_name omitted — not under test in TC-07
            )
            click_create_account()
            screenshot(attempt["shot"])

            phone_error_shown = has_text(
                "phone", "digit", "8 digit", "15 digit",
                "at least 8", "exceed 15", "invalid phone",
                "phone number", "minimum", "maximum"
            )

            if attempt["expect"] == "invalid":
                if phone_error_shown:
                    record(attempt["tc_id"], True, attempt["pass_msg"])
                else:
                    record(attempt["tc_id"], False, attempt["fail_msg"])
            else:
                if not phone_error_shown:
                    record(attempt["tc_id"], True, attempt["pass_msg"])
                else:
                    record(attempt["tc_id"], False, attempt["fail_msg"])

        except Exception as e:
            screenshot(f"UC2_M_Error_TC07_{attempt['label']}.png")
            record(attempt["tc_id"], False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC02-08 — Password Length & Composition BVA
# BVA-12: 7 chars              → INVALID (below minimum length)
# BVA-13: 8 chars, no digit   → INVALID (composition rule violated)
# BVA-14: 8 chars with digit  → VALID   (at minimum, composition satisfied)
# BVA-15: 9 chars with digit  → VALID   (above minimum, composition satisfied)
# Rule: min 8 characters, must contain at least one digit
# Each attempt uses a DIFFERENT email address
# ─────────────────────────────────────────────

def tc_uc02_08():
    print(f"\n▶ TC-UC02-08 — Password Length & Composition Boundary Value Analysis")
    print("   Technique: BVA-12, BVA-13, BVA-14, BVA-15, DT-08")
    print("   Rule: minimum 8 characters AND must contain at least one digit")

    attempts = [
        {
            "label":        "BVA-12",
            "email":        EMAIL_TC08_BVA12,
            "password":     PASS_7_CHARS,
            "confirm":      PASS_7_CHARS,
            "desc":         "7 chars, has digit — BELOW minimum length",
            "expect":       "invalid",
            "reject_check": lambda: has_text(
                "at least 8", "8 character", "minimum", "too short",
                "password must be", "least 8"
            ),
            "tc_id":        "TC-UC02-08a (BVA-12)",
            "shot":         "UC2_M_TC08a_BVA12_7chars.png",
            "pass_msg":     f"PASS — 7-char password '{PASS_7_CHARS}' rejected (BVA-12) "
                            f"[email: {EMAIL_TC08_BVA12}]. "
                            "Error: 'Password must be at least 8 characters'.",
            "fail_msg":     f"FAIL — 7-char password NOT rejected [email: {EMAIL_TC08_BVA12}]. "
                            "Defect: minimum length validation missing.",
        },
        {
            "label":        "BVA-13",
            "email":        EMAIL_TC08_BVA13,
            "password":     PASS_NO_DIGIT,
            "confirm":      PASS_NO_DIGIT,
            "desc":         "8 chars, NO digit — composition rule violated",
            "expect":       "invalid",
            "reject_check": lambda: has_text(
                "digit", "number", "one number", "contain a number",
                "must contain", "at least one"
            ),
            "tc_id":        "TC-UC02-08b (BVA-13)",
            "shot":         "UC2_M_TC08b_BVA13_nodigit.png",
            "pass_msg":     f"PASS — '{PASS_NO_DIGIT}' (no digit) rejected (BVA-13) "
                            f"[email: {EMAIL_TC08_BVA13}]. "
                            "Error: 'Password must contain at least one number'.",
            "fail_msg":     f"FAIL — No-digit password NOT rejected [email: {EMAIL_TC08_BVA13}]. "
                            "Defect: composition (digit) rule missing.",
        },
        {
            "label":        "BVA-14",
            "email":        EMAIL_TC08_BVA14,
            "password":     PASS_8_WITH_DIGIT,
            "confirm":      PASS_8_WITH_DIGIT,
            "desc":         "8 chars WITH digit — at minimum boundary, VALID",
            "expect":       "valid",
            "reject_check": lambda: has_text(
                "at least 8", "8 character", "minimum", "too short",
                "digit", "one number"
            ),
            "tc_id":        "TC-UC02-08c (BVA-14)",
            "shot":         "UC2_M_TC08c_BVA14_8chardigit.png",
            "pass_msg":     f"PASS — 8-char password '{PASS_8_WITH_DIGIT}' accepted (BVA-14) "
                            f"[email: {EMAIL_TC08_BVA14}]. "
                            "At minimum boundary with digit. No password validation error.",
            "fail_msg":     f"FAIL — 8-char password with digit incorrectly rejected "
                            f"[email: {EMAIL_TC08_BVA14}]. "
                            "Defect: minimum boundary or composition validation too strict.",
        },
        {
            "label":        "BVA-15",
            "email":        EMAIL_TC08_BVA15,
            "password":     PASS_9_WITH_DIGIT,
            "confirm":      PASS_9_WITH_DIGIT,
            "desc":         "9 chars WITH digit — above minimum, VALID",
            "expect":       "valid",
            "reject_check": lambda: has_text(
                "at least 8", "8 character", "minimum", "too short",
                "digit", "one number"
            ),
            "tc_id":        "TC-UC02-08d (BVA-15)",
            "shot":         "UC2_M_TC08d_BVA15_9chardigit.png",
            "pass_msg":     f"PASS — 9-char password '{PASS_9_WITH_DIGIT}' accepted (BVA-15) "
                            f"[email: {EMAIL_TC08_BVA15}]. "
                            "Above minimum — no password validation error raised.",
            "fail_msg":     f"FAIL — 9-char password with digit incorrectly rejected "
                            f"[email: {EMAIL_TC08_BVA15}]. "
                            "Defect: boundary validation logic incorrect.",
        },
    ]

    for attempt in attempts:
        print(f"\n   [{attempt['label']}] email='{attempt['email']}' | "
              f"password='{attempt['password']}' — {attempt['desc']}")
        try:
            go_to_register()
            fill_register(
                email=attempt["email"],
                password=attempt["password"],   # field under test
                confirm_password=attempt["confirm"],
                agree=True
                # phone, username, full_name omitted — not under test in TC-08
            )
            click_create_account()
            screenshot(attempt["shot"])

            password_error_shown = attempt["reject_check"]()

            if attempt["expect"] == "invalid":
                if password_error_shown:
                    record(attempt["tc_id"], True, attempt["pass_msg"])
                else:
                    record(attempt["tc_id"], False, attempt["fail_msg"])
            else:
                if not password_error_shown:
                    record(attempt["tc_id"], True, attempt["pass_msg"])
                else:
                    record(attempt["tc_id"], False, attempt["fail_msg"])

        except Exception as e:
            screenshot(f"UC2_M_Error_TC08_{attempt['label']}.png")
            record(attempt["tc_id"], False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC02-09 — Password Mismatch (Confirm Password)
# Techniques: BVA-16, DT-09, ST-03
# Input: Password = "Password@1", Confirm = "Password@2"
# Expected: Error 'Passwords do not match'. Registration blocked.
#           User remains on Registration page (ST-03).
# ─────────────────────────────────────────────

def tc_uc02_09():
    print(f"\n▶ TC-UC02-09 — Password and Confirm Password Mismatch")
    print("   Technique: BVA-16, DT-09, ST-03")
    print(f"   email='{EMAIL_TC09_MISM}' | "
          f"Password='{PASS_MISMATCH_A}', Confirm='{PASS_MISMATCH_B}'")
    try:
        go_to_register()
        fill_register(
            email=EMAIL_TC09_MISM,
            password=PASS_MISMATCH_A,           # fields under test
            confirm_password=PASS_MISMATCH_B,
            agree=True
            # phone, username, full_name omitted — not under test in TC-09
        )
        screenshot("UC2_M_TC09_BeforeSubmit.png")
        click_create_account()
        screenshot("UC2_M_TC09_AfterSubmit.png")

        mismatch_error = has_text(
            "passwords do not match",
            "password confirmation does not match",
            "do not match",
            "doesn't match",
            "confirm password",
            "match"
        )
        still_on_register = has_text(
            "create account", "register", "sign up",
            "confirm your password", "confirm password"
        )

        if mismatch_error and still_on_register:
            record("TC-UC02-09", True,
                   f"PASS — Mismatched passwords rejected (BVA-16, DT-09) "
                   f"[email: {EMAIL_TC09_MISM}]. "
                   "Error: 'Passwords do not match' displayed. "
                   "Registration blocked. User remains on Registration page (ST-03).")
        elif mismatch_error and not still_on_register:
            record("TC-UC02-09", False,
                   f"FAIL — Mismatch error shown but user navigated away "
                   f"[email: {EMAIL_TC09_MISM}]. "
                   "Defect: state transition incorrect (ST-03 violated).")
        elif not mismatch_error and still_on_register:
            record("TC-UC02-09", False,
                   f"FAIL — User on Register page but no mismatch error shown "
                   f"[email: {EMAIL_TC09_MISM}]. "
                   "Defect: 'Passwords do not match' validation message missing.")
        else:
            record("TC-UC02-09", False,
                   f"FAIL — Mismatched passwords NOT rejected. Registration proceeded "
                   f"[email: {EMAIL_TC09_MISM}]. "
                   "Defect: confirm password validation completely missing (DT-09).")

    except Exception as e:
        screenshot("UC2_M_Error_TC09.png")
        record("TC-UC02-09", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC02-10 — Terms & Conditions Checkbox Not Checked
# Techniques: TCOV-02-009, BVA-04, ST-02
# Input: All fields valid, Terms & Conditions: UNCHECKED
# Expected: Error 'You must agree to the Terms and Conditions'.
#           Registration blocked. User remains on Registration page.
# ─────────────────────────────────────────────

def tc_uc02_10():
    print(f"\n▶ TC-UC02-10 — Terms & Conditions Unchecked")
    print("   Technique: BVA-04, ST-02")
    print(f"   email='{EMAIL_TC10_TERMS}' | Terms & Conditions: UNCHECKED")
    try:
        go_to_register()
        # agree=False intentionally leaves the checkbox unchecked
        fill_register(
            email=EMAIL_TC10_TERMS,
            password=VALID_PASSWORD,
            confirm_password=VALID_CONFIRM,
            agree=False                         # field under test — leave unchecked
            # phone, username, full_name omitted — not under test in TC-10
        )
        screenshot("UC2_M_TC10_BeforeSubmit.png")
        click_create_account()
        screenshot("UC2_M_TC10_AfterSubmit.png")

        terms_error = has_text(
            "must agree", "agree to the terms", "terms and conditions",
            "please accept", "accept the terms", "terms required",
            "agree to terms"
        )
        still_on_register = has_text(
            "create account", "register", "sign up",
            "enter your email", "confirm password"
        )

        if terms_error and still_on_register:
            record("TC-UC02-10", True,
                   f"PASS — Unchecked T&C rejected (BVA-04, ST-02) "
                   f"[email: {EMAIL_TC10_TERMS}]. "
                   "Error: 'You must agree to the Terms and Conditions'. "
                   "Registration blocked. User remains on Registration page.")
        elif terms_error:
            record("TC-UC02-10", True,
                   f"PASS — Terms & Conditions error shown (BVA-04) "
                   f"[email: {EMAIL_TC10_TERMS}]. Registration blocked.")
        else:
            record("TC-UC02-10", False,
                   f"FAIL — Unchecked T&C NOT rejected [email: {EMAIL_TC10_TERMS}]. "
                   "Defect: Terms & Conditions required validation missing (BVA-04, ST-02).")
    except Exception as e:
        screenshot("UC2_M_Error_TC10.png")
        record("TC-UC02-10", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC02-11 — 'Log In' Link Redirects to Login Page
# Techniques: UCT-03, ST-06
# Action: Click 'Log In' / 'Already have an account? Log In' link
# Expected: User is redirected to Login page. Login page displays correctly.
# ─────────────────────────────────────────────

def tc_uc02_11():
    print(f"\n▶ TC-UC02-11 — 'Log In' Link Navigation from Registration Page")
    print("   Technique: UCT-03, ST-06")
    try:
        go_to_register()
        screenshot("UC2_M_TC11_OnRegisterPage.png")

        # Attempt to tap the Log In link (various possible label texts)
        tapped = False
        for text in ["Log In", "Login", "Sign In",
                     "Already have an account", "Already have an account? Log In"]:
            try:
                tap(AppiumBy.XPATH,
                    f"//*[@text='{text}' or contains(@text,'{text}')]",
                    timeout=5)
                tapped = True
                print(f"   ✅ Tapped link with text containing: '{text}'")
                break
            except TimeoutException:
                continue

        if not tapped:
            record("TC-UC02-11", False,
                   "FAIL — 'Log In' / 'Already have an account' link not found on "
                   "Registration page. Defect: navigation link missing (UCT-03).")
            return

        time.sleep(2)
        screenshot("UC2_M_TC11_AfterLoginTap.png")

        on_login_page = has_text(
            "login", "log in", "sign in",
            "welcome back", "forgot password", "enter your password"
        )

        if on_login_page:
            record("TC-UC02-11", True,
                   "PASS — 'Log In' link correctly redirects to Login page (UCT-03, ST-06). "
                   "Login page displayed successfully.")
        else:
            record("TC-UC02-11", False,
                   "FAIL — Tapped 'Log In' link but Login page not shown. "
                   "Defect: incorrect navigation target (ST-06 violated).")
    except Exception as e:
        screenshot("UC2_M_Error_TC11.png")
        record("TC-UC02-11", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC02-12 — 'Terms & Conditions' Hyperlink Text Navigation
# Techniques: UCT-04, ST-06
# Action: Tap the 'Terms & Conditions' or 'Privacy Policy' inline text link
#         inside the checkbox row (NOT the checkbox itself).
#         In the app, these are nested Text nodes with onPress → router.push('/(auth)/terms').
# Expected: T&C page opens and displays content correctly.
# ─────────────────────────────────────────────

def tc_uc02_12():
    print(f"\n▶ TC-UC02-12 — 'Terms & Conditions' Text Link Opens T&C Page")
    print("   Technique: UCT-04, ST-06")
    print("   Action: Tap the 'Terms & Conditions' or 'Privacy Policy' hyperlink text,")
    print("           NOT the checkbox. The link is a nested Text element inside the")
    print("           checkbox Pressable (router.push('/(auth)/terms')).")
    try:
        go_to_register()
        screenshot("UC2_M_TC12_OnRegisterPage.png")

        # The register screen has two tappable Text nodes nested inside the agree Pressable:
        #   • "Terms & Conditions"  → router.push('/(auth)/terms')
        #   • "Privacy Policy"      → router.push('/(auth)/terms')
        # Both navigate to the same T&C page.
        # We target only those specific label texts so we tap the hyperlink,
        # not the surrounding checkbox Pressable (which would just tick the box).
        tapped = False
        for link_text in ["Terms & Conditions", "Privacy Policy",
                          "Terms and Conditions", "Terms of Service"]:
            try:
                tap(AppiumBy.XPATH,
                    f"//*[@text='{link_text}']",
                    timeout=5)
                tapped = True
                print(f"   ✅ Tapped hyperlink text: '{link_text}'")
                break
            except TimeoutException:
                continue

        if not tapped:
            record("TC-UC02-12", False,
                   "FAIL — 'Terms & Conditions' / 'Privacy Policy' hyperlink text not found "
                   "on Registration page. Defect: T&C navigation link missing (UCT-04).")
            return

        time.sleep(2)
        screenshot("UC2_M_TC12_AfterTCTap.png")

        on_tc_page = has_text(
            "terms and conditions", "terms of service",
            "terms of use", "privacy policy",
            "agreement", "conditions of use"
        )

        if on_tc_page:
            record("TC-UC02-12", True,
                   "PASS — 'Terms & Conditions' hyperlink correctly opens T&C page "
                   "(UCT-04, ST-06). T&C content displayed successfully.")
        else:
            record("TC-UC02-12", False,
                   "FAIL — Tapped 'Terms & Conditions' link but T&C page not shown. "
                   "Defect: T&C page not loaded or navigation target incorrect (ST-06 violated).")
    except Exception as e:
        screenshot("UC2_M_Error_TC12.png")
        record("TC-UC02-12", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

try:
    print("=" * 66)
    print("  UC2 REGISTRATION — MOBILE APPIUM TEST (TC-01 to TC-12)")
    print("  Testing Level: System Testing")
    print(f"  App: com.adamarbain.dengueeyemobileapp")
    print(f"  Screenshots: {SCREENSHOT_DIR}")
    print("=" * 66)
    print("\n  Test Cases and Inputs:")
    print(f"  TC-UC02-01              → {EMAIL_TC01_VALID}   | valid registration (Admin Web)")
    print(f"  TC-UC02-02              → {EMAIL_TC02_VALID}  | valid registration (Mobile)")
    print(f"  TC-UC02-03a             → email empty             | required field check")
    print(f"  TC-UC02-03b             → {EMAIL_TC03_VALID}      | full name empty")
    print(f"  TC-UC02-04              → {EMAIL_TC04_INVALID}    | missing '@'")
    print(f"  TC-UC02-05              → {EMAIL_TC05_DUPLICATE}     | duplicate email")
    print(f"  TC-UC02-06a (BVA-05)    → {EMAIL_TC06_BVA05}     | username 2 chars (invalid)")
    print(f"  TC-UC02-06b (BVA-06)    → {EMAIL_TC06_BVA06}     | username 3 chars (valid)")
    print(f"  TC-UC02-06c (BVA-07)    → {EMAIL_TC06_BVA07}     | username 4 chars (valid)")
    print(f"  TC-UC02-07a (BVA-08)    → {EMAIL_TC07_BVA08}      | phone 7 digits (invalid)")
    print(f"  TC-UC02-07b (BVA-09)    → {EMAIL_TC07_BVA09}      | phone 8 digits (valid)")
    print(f"  TC-UC02-07c (BVA-10)    → {EMAIL_TC07_BVA10}     | phone 15 digits (valid)")
    print(f"  TC-UC02-07d (BVA-11)    → {EMAIL_TC07_BVA11}     | phone 16 digits (invalid)")
    print(f"  TC-UC02-08a (BVA-12)    → {EMAIL_TC08_BVA12}      | pass 7 chars (invalid)")
    print(f"  TC-UC02-08b (BVA-13)    → {EMAIL_TC08_BVA13}     | pass 8 chars no digit (invalid)")
    print(f"  TC-UC02-08c (BVA-14)    → {EMAIL_TC08_BVA14}      | pass 8 chars+digit (valid)")
    print(f"  TC-UC02-08d (BVA-15)    → {EMAIL_TC08_BVA15}      | pass 9 chars+digit (valid)")
    print(f"  TC-UC02-09  (BVA-16)    → {EMAIL_TC09_MISM}   | password mismatch")
    print(f"  TC-UC02-10              → {EMAIL_TC10_TERMS}     | T&C unchecked")
    print(f"  TC-UC02-11              → (navigation test)        | Log In link")
    print(f"  TC-UC02-12              → (navigation test)        | T&C Policy link")
    print("=" * 66)

    if setup_session():
        tc_uc02_01()
        tc_uc02_02()
        tc_uc02_03()
        tc_uc02_04()
        tc_uc02_05()
        tc_uc02_06()
        tc_uc02_07()
        tc_uc02_08()
        tc_uc02_09()
        tc_uc02_10()
        tc_uc02_11()
        tc_uc02_12()
    else:
        print("🛑 Aborting — Register screen not accessible")

except Exception as e:
    print(f"\n🛑 Unexpected error: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n" + "=" * 66)
    print("  TEST SUMMARY — UC2 Registration (Mobile, TC-01 to TC-12)")
    print("=" * 66)
    passed = failed = na = 0
    for r in results:
        print(f"  {r}")
        if "✅" in r:    passed += 1
        elif "❌" in r:  failed += 1
        else:             na += 1
    print(f"\n  Total: {len(results)}  |  "
          f"✅ Passed: {passed}  |  "
          f"❌ Failed: {failed}  |  "
          f"ℹ️  N/A: {na}")
    print(f"\n  📁 Screenshots → {SCREENSHOT_DIR}")
    print("=" * 66)
    driver.quit()
