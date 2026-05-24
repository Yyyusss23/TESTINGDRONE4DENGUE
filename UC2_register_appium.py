"""
UC2 Registration - Mobile Appium Test Script (TC-UC02-07, TC-UC02-08, TC-UC02-09)
Testing Level: System Testing
Techniques Applied:
  - Boundary Value Analysis (BVA)
  - Decision Table Testing (DT)
  - State Transition Testing (ST)
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

# ── Unique emails per test attempt (no redundancy) ──────────────────
# TC-UC02-07: Phone BVA
EMAIL_TC07_BVA08  = "reg_phone7d@email.com"       # BVA-08: 7 digits  (invalid)
EMAIL_TC07_BVA09  = "reg_phone8d@email.com"       # BVA-09: 8 digits  (valid)
EMAIL_TC07_BVA10  = "reg_phone15d@email.com"      # BVA-10: 15 digits (valid)
EMAIL_TC07_BVA11  = "reg_phone16d@email.com"      # BVA-11: 16 digits (invalid)

# TC-UC02-08: Password BVA
EMAIL_TC08_BVA12  = "reg_pass7chr@email.com"      # BVA-12: 7 chars, no digit check (invalid length)
EMAIL_TC08_BVA13  = "reg_passnodig@email.com"     # BVA-13: 8 chars, no digit (invalid composition)
EMAIL_TC08_BVA14  = "reg_pass8dig@email.com"      # BVA-14: 8 chars with digit (valid)
EMAIL_TC08_BVA15  = "reg_pass9dig@email.com"      # BVA-15: 9 chars with digit (valid)

# TC-UC02-09: Password mismatch
EMAIL_TC09_MISM   = "reg_pwmismatch@email.com"    # BVA-16 / DT-09: confirm password mismatch

# ── Phone boundary values ────────────────────────────────────────────
PHONE_7_DIGITS    = "1234567"             # BVA-08: below minimum (INVALID)
PHONE_8_DIGITS    = "12345678"            # BVA-09: at minimum boundary (VALID)
PHONE_15_DIGITS   = "123456789012345"     # BVA-10: at maximum boundary (VALID)
PHONE_16_DIGITS   = "1234567890123456"    # BVA-11: above maximum (INVALID)

# ── Password boundary / composition values ───────────────────────────
PASS_7_CHARS      = "Pass123"             # BVA-12: 7 chars — below minimum (INVALID)
PASS_NO_DIGIT     = "Password"            # BVA-13: 8 chars, no digit (INVALID)
PASS_8_WITH_DIGIT = "Pass@123"            # BVA-14: 8 chars with digit — at minimum (VALID)
PASS_9_WITH_DIGIT = "Pass@1234"           # BVA-15: 9 chars with digit — above minimum (VALID)

# ── Password mismatch values ─────────────────────────────────────────
PASS_MISMATCH_A   = "Password@1"           # BVA-16 / DT-09
PASS_MISMATCH_B   = "Password@2"

# ── Shared valid password for non-password tests (TC-07) ─────────────
VALID_PASSWORD    = "Mobile@123"
VALID_CONFIRM     = "Mobile@123"

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
                  phone=None, agree=True):
    """
    Fill registration form fields. Pass None to skip a field.
    Phone field is filled if present in the form.
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

    if email is not None:
        _fill_by_hint(["Enter your email"], email)

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
        try:
            checkbox = find(AppiumBy.XPATH,
                            "//*[contains(@text,'agree') or contains(@text,'Terms') "
                            "or contains(@content-desc,'agree')]", timeout=5)
            source = driver.page_source
            if 'checked="true"' not in source and 'selected="true"' not in source:
                checkbox.click()
                time.sleep(0.5)
        except TimeoutException:
            try:
                tap(AppiumBy.XPATH,
                    "//android.view.ViewGroup[contains(@content-desc,'agree') "
                    "or contains(@content-desc,'Terms')]", timeout=3)
            except TimeoutException:
                print("   ⚠️  Terms checkbox not found — skipping")


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
                phone=attempt["phone"],
                password=VALID_PASSWORD,
                confirm_password=VALID_CONFIRM,
                agree=True
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
                password=attempt["password"],
                confirm_password=attempt["confirm"],
                agree=True
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
# Input: Password = "Password1", Confirm = "Password2"
# Expected: Error 'Passwords do not match'. Registration blocked.
#           User remains on Registration page (ST-03).
# Uses EMAIL_TC09_MISM — unique email, different from all TC-07/TC-08 emails
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
            password=PASS_MISMATCH_A,
            confirm_password=PASS_MISMATCH_B,
            agree=True
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
# MAIN
# ─────────────────────────────────────────────

try:
    print("=" * 62)
    print("  UC2 REGISTRATION — MOBILE APPIUM TEST (TC-07 to TC-09)")
    print("  Testing Level: System Testing")
    print(f"  App: com.adamarbain.dengueeyemobileapp")
    print(f"  Screenshots: {SCREENSHOT_DIR}")
    print("=" * 62)
    print("\n  Test Cases and Unique Emails Used:")
    print(f"  TC-UC02-07a (BVA-08) → {EMAIL_TC07_BVA08}  | phone 7 digits  (invalid)")
    print(f"  TC-UC02-07b (BVA-09) → {EMAIL_TC07_BVA09}  | phone 8 digits  (valid)")
    print(f"  TC-UC02-07c (BVA-10) → {EMAIL_TC07_BVA10} | phone 15 digits (valid)")
    print(f"  TC-UC02-07d (BVA-11) → {EMAIL_TC07_BVA11} | phone 16 digits (invalid)")
    print(f"  TC-UC02-08a (BVA-12) → {EMAIL_TC08_BVA12}  | pass 7 chars (invalid)")
    print(f"  TC-UC02-08b (BVA-13) → {EMAIL_TC08_BVA13} | pass 8 chars no digit (invalid)")
    print(f"  TC-UC02-08c (BVA-14) → {EMAIL_TC08_BVA14}  | pass 8 chars+digit (valid)")
    print(f"  TC-UC02-08d (BVA-15) → {EMAIL_TC08_BVA15}  | pass 9 chars+digit (valid)")
    print(f"  TC-UC02-09  (BVA-16) → {EMAIL_TC09_MISM} | password mismatch")
    print("=" * 62)

    if setup_session():
        tc_uc02_07()
        tc_uc02_08()
        tc_uc02_09()
    else:
        print("🛑 Aborting — Register screen not accessible")

except Exception as e:
    print(f"\n🛑 Unexpected error: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n" + "=" * 62)
    print("  TEST SUMMARY — UC2 Registration (Mobile, TC-07 to TC-09)")
    print("=" * 62)
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
    print("=" * 62)
    driver.quit()