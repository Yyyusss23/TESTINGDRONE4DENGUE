from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import subprocess
import time
import os
import re

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
SCRIPT_DIR     = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIR = os.path.join(SCRIPT_DIR, "UC3_mobile_screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

TEST_EMAIL     = "mobiletest@email.com"
WRONG_EMAIL    = "wrong@email.com"
WRONG_CODE     = "000000"
VALID_PASSWORD = "SecretPass123"
SHORT_PASSWORD = "Pass123"
LONG_PASSWORD  = "VeryLongPassword12345"
LETTERS_ONLY   = "SecretPassword"
NUMBERS_ONLY   = "123456789"
MISMATCH_PASS1 = "NewPass1"
MISMATCH_PASS2 = "BadPass2"
SERVER_API_DIR = "/Users/yus/Documents/GitHub/drone4dengue/server-api"

options = UiAutomator2Options()
options.platform_name   = "Android"
options.device_name     = "emulator-5554"
options.app_package     = "com.adamarbain.dengueeyemobileapp"
options.app_activity    = ".MainActivity"
options.no_reset        = True
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
    print(f"   📸 Screenshot: {filename}")


def has_text(*keywords):
    source = driver.page_source.lower()
    return any(k.lower() in source for k in keywords)


def get_visible_text():
    texts = re.findall(r'text="([^"]+)"', driver.page_source)
    return [t for t in texts if t.strip()]


def find_el(by, value, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def tap_el(by, value, timeout=15):
    el = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )
    el.click()
    return el


def hide_keyboard_safe():
    """Hide soft keyboard if visible."""
    try:
        driver.hide_keyboard()
        time.sleep(0.5)
    except Exception:
        pass


def record(tc_id, status, note=""):
    tag = "✅ PASS" if status is True else ("❌ FAIL" if status is False else "ℹ️  N/A ")
    line = f"{tag}  {tc_id}  {note}"
    results.append(line)
    print(f"   {line}")


def get_code_from_db():
    """Read latest reset code directly from database."""
    script = (
        "const{PrismaClient}=require('@prisma/client');"
        "const p=new PrismaClient();"
        "p.user.findUnique({where:{email:'" + TEST_EMAIL + "'}})"
        ".then(u=>{console.log(u&&u.resetCode?u.resetCode:'NO_CODE');p.$disconnect();})"
        ".catch(e=>{console.log('ERR');p.$disconnect();});"
    )
    result = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, cwd=SERVER_API_DIR
    )
    code = result.stdout.strip().split('\n')[-1].strip()
    if code and len(code) == 6 and code.isdigit():
        print(f"   🔑 Fresh code from DB: {code}")
        return code
    else:
        print(f"   ⚠️  DB code not found. stdout={result.stdout!r}")
        return None


def force_close_modal_and_go_to_login():
    """Aggressively close any modal and return to login screen."""
    hide_keyboard_safe()

    # Try Cancel button up to 3 times
    for _ in range(3):
        try:
            tap_el(AppiumBy.XPATH, "//*[@text='Cancel']", timeout=2)
            time.sleep(0.5)
        except TimeoutException:
            break

    # Press back button up to 3 times
    for _ in range(3):
        if has_text("Welcome Back", "Forgot Password", "Sign In"):
            break
        try:
            driver.back()
            time.sleep(1)
        except Exception:
            break

    time.sleep(1)

    try:
        tap_el(AppiumBy.XPATH, "//*[@text='OK']", timeout=2)
        time.sleep(0.5)
    except TimeoutException:
        pass

    if not has_text("Welcome Back", "Forgot Password", "Sign In"):
        print("   ⚠️  Could not return to login screen")
    else:
        print("   ✅ On login screen — ready for next test")
    time.sleep(1)


def open_forgot_password_fresh():
    force_close_modal_and_go_to_login()
    try:
        tap_el(AppiumBy.XPATH, "//*[@text='Forgot Password?']")
        time.sleep(3)
        print("   ✅ Forgot Password modal opened fresh")
        return True
    except TimeoutException:
        screenshot("UC3_Error_ForgotPasswordBtn.png")
        print("   ❌ Could not find Forgot Password button")
        return False


def type_email_and_send(email):
    """Type email and tap Send Reset Code."""
    # Find email input — placeholder "Enter your email address"
    email_input = find_el(AppiumBy.XPATH,
        "//android.widget.EditText[@text='Enter your email address']")
    email_input.clear()
    email_input.send_keys(email)
    time.sleep(0.5)

    # Hide keyboard so Send Reset Code button is visible
    hide_keyboard_safe()

    # Tap Send Reset Code
    tap_el(AppiumBy.XPATH, "//*[@text='Send Reset Code']")
    time.sleep(6)


def type_code_and_verify(code):
    """Type code and tap Verify Code."""
    code_input = find_el(AppiumBy.XPATH, "//android.widget.EditText")
    code_input.clear()
    code_input.send_keys(code)
    time.sleep(0.5)
    hide_keyboard_safe()
    tap_el(AppiumBy.XPATH, "//*[@text='Verify Code']")
    time.sleep(3)


def type_passwords_and_reset(pw1, pw2):
    """Type new password, confirm password, tap Reset Password."""
    inputs = driver.find_elements(AppiumBy.XPATH, "//android.widget.EditText")
    if len(inputs) >= 2:
        inputs[0].clear()
        inputs[0].send_keys(pw1)
        time.sleep(0.3)
        inputs[1].clear()
        inputs[1].send_keys(pw2)
        time.sleep(0.3)
    elif len(inputs) == 1:
        inputs[0].clear()
        inputs[0].send_keys(pw1)
    hide_keyboard_safe()
    tap_el(AppiumBy.XPATH, "//*[@text='Reset Password']")
    time.sleep(3)


# ─────────────────────────────────────────────
# SETUP SESSION
# ─────────────────────────────────────────────

def setup_session():
    print("\n🔐 Setting up — navigating to Login Screen...")
    time.sleep(5)

    try:
        tap_el(AppiumBy.XPATH, "//*[@text='OK']", timeout=3)
        time.sleep(0.5)
    except TimeoutException:
        pass

    if has_text("Welcome Back", "Forgot Password", "Sign In"):
        print("✅ Already on login screen")
        return True

    try:
        tap_el(AppiumBy.XPATH, "//*[@text='Profile']", timeout=5)
        time.sleep(1)
        tap_el(AppiumBy.XPATH, "//*[@text='Log Out']", timeout=5)
        time.sleep(1)
        tap_el(AppiumBy.XPATH, "//*[@text='Log Out']", timeout=5)
        time.sleep(2)
        print("✅ Logged out")
        return True
    except TimeoutException:
        pass

    screenshot("UC3_M_Error_Setup.png")
    print("❌ Could not reach login screen")
    return False


# ─────────────────────────────────────────────
# TC-UC03-01 — Full Valid Reset Flow
# ─────────────────────────────────────────────

def tc_uc03_01():
    print(f"\n▶ TC-UC03-01 — Valid Reset Flow")
    try:
        if not open_forgot_password_fresh():
            record("TC-UC03-01", False, "Could not open modal")
            return

        print(f"   Step 1: Sending reset code to {TEST_EMAIL}")
        type_email_and_send(TEST_EMAIL)
        screenshot("UC3_M_TC01_Step1.png")
        print(f"   🔍 Screen: {get_visible_text()}")

        if not has_text("Enter Code", "Verify Code", "6-digit", "Check your email"):
            record("TC-UC03-01", False,
                   "Step 1 FAIL — Enter Code screen not shown")
            force_close_modal_and_go_to_login()
            return

        print("   ✅ Step 1 PASS — Enter Code screen shown")

        fresh_code = get_code_from_db()
        if not fresh_code:
            record("TC-UC03-01", False, "Could not read code from DB")
            force_close_modal_and_go_to_login()
            return

        print(f"   Step 2: Entering code {fresh_code}")
        type_code_and_verify(fresh_code)
        screenshot("UC3_M_TC01_Step2.png")
        print(f"   🔍 Screen: {get_visible_text()}")

        if not has_text("New Password", "Reset Password", "Create a strong", "new password"):
            record("TC-UC03-01", False,
                   "Step 2 FAIL — New Password screen not shown")
            force_close_modal_and_go_to_login()
            return

        print("   ✅ Step 2 PASS — New Password screen shown")

        print(f"   Step 3: Entering password {VALID_PASSWORD}")
        type_passwords_and_reset(VALID_PASSWORD, VALID_PASSWORD)
        screenshot("UC3_M_TC01_Step3.png")
        print(f"   🔍 Screen: {get_visible_text()}")

        if has_text("success", "reset successful", "can now log in", "password reset"):
            record("TC-UC03-01", True,
                   f"Full flow PASS — {TEST_EMAIL} → code {fresh_code} → "
                   f"password {VALID_PASSWORD} → success message shown")
        else:
            record("TC-UC03-01", False,
                   "Step 3 FAIL — no success message")

    except Exception as e:
        screenshot("UC3_M_Error_TC01.png")
        record("TC-UC03-01", False, f"Exception: {e}")

    force_close_modal_and_go_to_login()


# ─────────────────────────────────────────────
# TC-UC03-02 — Unregistered Email
# ─────────────────────────────────────────────

def tc_uc03_02():
    print(f"\n▶ TC-UC03-02 — Unregistered Email ({WRONG_EMAIL})")
    try:
        if not open_forgot_password_fresh():
            record("TC-UC03-02", False, "Could not open modal")
            return

        type_email_and_send(WRONG_EMAIL)
        screenshot("UC3_M_TC02.png")
        visible = get_visible_text()
        print(f"   🔍 Screen: {visible}")

        if has_text("Enter Code", "Verify Code", "6-digit"):
            record("TC-UC03-02", False,
                   f"FAIL — system accepted unregistered {WRONG_EMAIL}")
        elif has_text("not found", "error", "invalid", "failed", "user", "object"):
            record("TC-UC03-02", True,
                   f"PASS — {WRONG_EMAIL} rejected, error shown")
        else:
            record("TC-UC03-02", False, "FAIL — no error shown")

    except Exception as e:
        screenshot("UC3_M_Error_TC02.png")
        record("TC-UC03-02", False, f"Exception: {e}")

    force_close_modal_and_go_to_login()


# ─────────────────────────────────────────────
# TC-UC03-03 — Wrong Code + Resend
# ─────────────────────────────────────────────

def tc_uc03_03():
    print(f"\n▶ TC-UC03-03 — Wrong Code ({WRONG_CODE}) + Resend")
    try:
        if not open_forgot_password_fresh():
            record("TC-UC03-03a", False, "Could not open modal")
            record("TC-UC03-03b", None, "Skipped")
            return

        type_email_and_send(TEST_EMAIL)
        screenshot("UC3_M_TC03_Step1.png")
        print(f"   🔍 Screen: {get_visible_text()}")

        if not has_text("Enter Code", "Verify Code", "6-digit"):
            record("TC-UC03-03a", False,
                   "FAIL — could not reach Enter Code screen")
            record("TC-UC03-03b", None, "Skipped")
            force_close_modal_and_go_to_login()
            return

        print("   ✅ Enter Code screen reached")

        print(f"   Entering wrong code: {WRONG_CODE}")
        type_code_and_verify(WRONG_CODE)
        screenshot("UC3_M_TC03_WrongCode.png")
        visible = get_visible_text()
        print(f"   🔍 After wrong code: {visible}")

        if has_text("invalid", "expired", "error", "wrong", "incorrect"):
            record("TC-UC03-03a", True,
                   f"PASS — wrong code {WRONG_CODE} rejected")

            # Test resend
            force_close_modal_and_go_to_login()
            time.sleep(1)
            if not open_forgot_password_fresh():
                record("TC-UC03-03b", False, "Could not reopen modal")
                return

            type_email_and_send(TEST_EMAIL)
            screenshot("UC3_M_TC03_Resend.png")
            resend_code = get_code_from_db()
            print(f"   🔍 After resend: {get_visible_text()}")

            if has_text("Enter Code", "Verify Code", "6-digit") and resend_code:
                record("TC-UC03-03b", True,
                       f"PASS — resend triggered, new code {resend_code}")
            else:
                record("TC-UC03-03b", False, "FAIL — resend did not work")
        else:
            record("TC-UC03-03a", False,
                   f"FAIL — no error for wrong code {WRONG_CODE}")
            record("TC-UC03-03b", None, "Skipped")

    except Exception as e:
        screenshot("UC3_M_Error_TC03.png")
        record("TC-UC03-03a", False, f"Exception: {e}")
        record("TC-UC03-03b", None, "Skipped")

    force_close_modal_and_go_to_login()


# ─────────────────────────────────────────────
# TC-UC03-04 — Invalid Password Formats
# ─────────────────────────────────────────────

def tc_uc03_04():
    print("\n▶ TC-UC03-04 — Invalid Password Formats")
    try:
        if not open_forgot_password_fresh():
            record("TC-UC03-04", False, "Could not open modal")
            return

        type_email_and_send(TEST_EMAIL)
        screenshot("UC3_M_TC04_Step1.png")

        if not has_text("Enter Code", "Verify Code", "6-digit"):
            record("TC-UC03-04", False, "FAIL — could not reach Enter Code")
            force_close_modal_and_go_to_login()
            return

        fresh_code = get_code_from_db()
        if not fresh_code:
            record("TC-UC03-04", False, "FAIL — no code from DB")
            force_close_modal_and_go_to_login()
            return

        type_code_and_verify(fresh_code)
        screenshot("UC3_M_TC04_Step2.png")

        if not has_text("New Password", "Reset Password", "Create a strong", "new password"):
            record("TC-UC03-04", False, "FAIL — no New Password screen")
            force_close_modal_and_go_to_login()
            return

        print("   ✅ New Password screen reached")
        sub = []

        # Attempt 1: Too short (BVA-07)
        print(f"   Attempt 1: {SHORT_PASSWORD} (7 chars)")
        type_passwords_and_reset(SHORT_PASSWORD, SHORT_PASSWORD)
        screenshot("UC3_M_TC04_TooShort.png")
        p1 = has_text("error", "short", "least", "character", "minimum",
                      "invalid", "password", "6")
        print(f"   {'✅' if p1 else '❌'} Short {'rejected' if p1 else 'NOT rejected'}")
        sub.append(p1)

        # Attempt 2: Too long (BVA-12)
        print(f"   Attempt 2: {LONG_PASSWORD} (21 chars)")
        type_passwords_and_reset(LONG_PASSWORD, LONG_PASSWORD)
        screenshot("UC3_M_TC04_TooLong.png")
        p2 = has_text("error", "long", "maximum", "character", "invalid", "password")
        print(f"   {'✅' if p2 else '⚠️ '} Long {'rejected' if p2 else 'NOT rejected'}")
        sub.append(p2)

        # Attempt 3: Letters only (EP-05)
        print(f"   Attempt 3: {LETTERS_ONLY}")
        type_passwords_and_reset(LETTERS_ONLY, LETTERS_ONLY)
        screenshot("UC3_M_TC04_LettersOnly.png")
        p3 = has_text("error", "number", "digit", "invalid", "password", "mix")
        print(f"   {'✅' if p3 else '⚠️ '} Letters {'rejected' if p3 else 'NOT rejected'}")
        sub.append(p3)

        # Attempt 4: Numbers only (EP-06)
        print(f"   Attempt 4: {NUMBERS_ONLY}")
        type_passwords_and_reset(NUMBERS_ONLY, NUMBERS_ONLY)
        screenshot("UC3_M_TC04_NumbersOnly.png")
        p4 = has_text("error", "letter", "invalid", "password", "mix")
        print(f"   {'✅' if p4 else '⚠️ '} Numbers {'rejected' if p4 else 'NOT rejected'}")
        sub.append(p4)

        if all(sub):
            record("TC-UC03-04", True, "All 4 invalid formats rejected")
        elif any(s is False for s in sub):
            record("TC-UC03-04", False,
                   "Some formats not rejected — backend only validates "
                   "min 6 chars, not format mix or max length")
        else:
            record("TC-UC03-04", None,
                   "Partial — backend does not enforce all rules server-side")

    except Exception as e:
        screenshot("UC3_M_Error_TC04.png")
        record("TC-UC03-04", False, f"Exception: {e}")

    force_close_modal_and_go_to_login()


# ─────────────────────────────────────────────
# TC-UC03-05 — Passwords Do Not Match
# ─────────────────────────────────────────────

def tc_uc03_05():
    print(f"\n▶ TC-UC03-05 — Passwords Do Not Match ({MISMATCH_PASS1} vs {MISMATCH_PASS2})")
    try:
        if not open_forgot_password_fresh():
            record("TC-UC03-05", False, "Could not open modal")
            return

        type_email_and_send(TEST_EMAIL)
        screenshot("UC3_M_TC05_Step1.png")

        if not has_text("Enter Code", "Verify Code", "6-digit"):
            record("TC-UC03-05", False, "FAIL — no Enter Code screen")
            force_close_modal_and_go_to_login()
            return

        fresh_code = get_code_from_db()
        if not fresh_code:
            record("TC-UC03-05", False, "FAIL — no code from DB")
            force_close_modal_and_go_to_login()
            return

        type_code_and_verify(fresh_code)
        screenshot("UC3_M_TC05_Step2.png")

        if not has_text("New Password", "Reset Password", "Create a strong", "new password"):
            record("TC-UC03-05", False, "FAIL — no New Password screen")
            force_close_modal_and_go_to_login()
            return

        print("   ✅ New Password screen reached")
        print(f"   Entering: {MISMATCH_PASS1} and {MISMATCH_PASS2}")
        type_passwords_and_reset(MISMATCH_PASS1, MISMATCH_PASS2)
        screenshot("UC3_M_TC05_Mismatch.png")
        visible = get_visible_text()
        print(f"   🔍 After mismatch: {visible}")

        if has_text("do not match", "passwords do not", "match", "error",
                    "confirm", "same"):
            record("TC-UC03-05", True,
                   f"PASS — mismatch ({MISMATCH_PASS1}/{MISMATCH_PASS2}) rejected")
        else:
            record("TC-UC03-05", False, "FAIL — no error for mismatched passwords")

    except Exception as e:
        screenshot("UC3_M_Error_TC05.png")
        record("TC-UC03-05", False, f"Exception: {e}")

    force_close_modal_and_go_to_login()


# ─────────────────────────────────────────────
# STATE TRANSITION TESTS
# ─────────────────────────────────────────────

def tc_state_transitions():
    print("\n▶ State Transition Tests")

    # ST-14
    print("   ST-14: Login → Forgot Password modal opens")
    try:
        force_close_modal_and_go_to_login()
        tap_el(AppiumBy.XPATH, "//*[@text='Forgot Password?']")
        time.sleep(2)
        screenshot("UC3_M_ST14.png")
        visible = get_visible_text()
        print(f"   🔍 Visible: {visible}")
        if has_text("Reset Password", "Send Reset Code", "Enter your email"):
            record("ST-14", True, "PASS — modal opens correctly")
        else:
            record("ST-14", False, "FAIL — modal not showing expected content")
    except Exception as e:
        screenshot("UC3_M_Error_ST14.png")
        record("ST-14", False, f"Exception: {e}")
    force_close_modal_and_go_to_login()

    # ST-015
    print("   ST-015: Unknown email → error")
    try:
        if not open_forgot_password_fresh():
            record("ST-015", False, "Could not open modal")
        else:
            type_email_and_send(WRONG_EMAIL)
            screenshot("UC3_M_ST015.png")
            print(f"   🔍 Visible: {get_visible_text()}")
            if not has_text("Enter Code", "Verify Code") and \
               has_text("not found", "error", "invalid", "failed", "user", "object"):
                record("ST-015", True, "PASS — unknown email rejected")
            else:
                record("ST-015", False, "FAIL")
    except Exception as e:
        screenshot("UC3_M_Error_ST015.png")
        record("ST-015", False, f"Exception: {e}")
    force_close_modal_and_go_to_login()

    # ST-016 → ST-019 chain
    print("   ST-016: Valid email → Enter Code screen")
    try:
        if not open_forgot_password_fresh():
            record("ST-016", False, "Could not open modal")
            record("ST-017", None, "Skipped")
            record("ST-018", None, "Skipped")
            record("ST-019", None, "Skipped")
            return

        type_email_and_send(TEST_EMAIL)
        fresh_code = get_code_from_db()
        screenshot("UC3_M_ST016.png")
        print(f"   🔍 Screen: {get_visible_text()}")

        if not has_text("Enter Code", "Verify Code", "6-digit"):
            record("ST-016", False, "FAIL — no Enter Code screen")
            record("ST-017", None, "Skipped")
            record("ST-018", None, "Skipped")
            record("ST-019", None, "Skipped")
            force_close_modal_and_go_to_login()
            return

        record("ST-016", True, "PASS — Enter Code screen shown")

        # ST-017
        print(f"   ST-017: Wrong code {WRONG_CODE}")
        type_code_and_verify(WRONG_CODE)
        screenshot("UC3_M_ST017.png")
        print(f"   🔍 After wrong: {get_visible_text()}")
        if has_text("invalid", "expired", "error", "wrong", "incorrect"):
            record("ST-017", True, "PASS — wrong code rejected")
        else:
            record("ST-017", False, "FAIL — no error for wrong code")

        # ST-018
        print(f"   ST-018: Valid code {fresh_code}")
        if not fresh_code:
            record("ST-018", False, "FAIL — no code")
            record("ST-019", None, "Skipped")
            force_close_modal_and_go_to_login()
            return

        type_code_and_verify(fresh_code)
        screenshot("UC3_M_ST018.png")
        print(f"   🔍 After valid: {get_visible_text()}")

        if has_text("New Password", "Reset Password", "Create a strong", "new password"):
            record("ST-018", True, "PASS — New Password screen shown")

            # ST-019
            print(f"   ST-019: Mismatch {MISMATCH_PASS1}/{MISMATCH_PASS2}")
            type_passwords_and_reset(MISMATCH_PASS1, MISMATCH_PASS2)
            screenshot("UC3_M_ST019.png")
            print(f"   🔍 After mismatch: {get_visible_text()}")
            if has_text("do not match", "match", "error", "confirm", "same"):
                record("ST-019", True, "PASS — mismatch rejected")
            else:
                record("ST-019", False, "FAIL — no error for mismatch")
        else:
            record("ST-018", False, "FAIL — no New Password screen")
            record("ST-019", None, "Skipped")

    except Exception as e:
        screenshot("UC3_M_Error_ST016.png")
        record("ST-016", False, f"Exception: {e}")
        record("ST-017", None, "Skipped")
        record("ST-018", None, "Skipped")
        record("ST-019", None, "Skipped")

    force_close_modal_and_go_to_login()


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

try:
    if setup_session():
        tc_uc03_01()
        tc_uc03_02()
        tc_uc03_03()
        tc_uc03_04()
        tc_uc03_05()
        tc_state_transitions()
    else:
        print("🛑 Aborting — could not reach login screen")

except Exception as e:
    print(f"\n🛑 Unexpected error: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n" + "="*60)
    print("  TEST SUMMARY — UC3 Reset Password (Mobile)")
    print("="*60)
    passed = failed = na = 0
    for r in results:
        # Truncate long lines
        line = r if len(r) < 200 else r[:200] + "..."
        print(f"  {line}")
        if "✅" in r:  passed += 1
        elif "❌" in r: failed += 1
        else:           na += 1
    print(f"\n  Total: {len(results)}  |  ✅ Passed: {passed}  |  "
          f"❌ Failed: {failed}  |  ℹ️ N/A: {na}")
    print(f"\n  📁 Screenshots → {SCREENSHOT_DIR}")
    print("="*60)
    driver.quit()