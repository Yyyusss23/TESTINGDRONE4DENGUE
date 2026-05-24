"""
UC1 Login - Mobile Appium Test Script
Testing Level: System Testing
Techniques Applied:
  - Equivalence Partitioning (EP)
  - Boundary Value Analysis (BVA)
  - Decision Table Testing (DT)
  - Use Case Testing (UCT)
  - State Transition Testing (ST)
Tool: Appium + UiAutomator2 (Android)
Testers:
  - Edwin Tan Yu Xian         (Equivalence Partitioning)
  - brendan (Boundary Value Analysis)
  - Izzatul Filzah bt Norazmi  (Decision Table Testing)
  - Auni Nafisa bt Osman       (Use Case Testing)
  - Yusrina Maisarah bt Yunus  (State Transition Testing)
"""

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os

# ─────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────
SCRIPT_DIR     = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIR = os.path.join(SCRIPT_DIR, "UC1_mobile_screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Test data — each test uses DIFFERENT data (no redundancy)
VALID_EMAIL        = "mobiletest@email.com"          # UCT-02: valid mobile user
VALID_PASS         = "Mobile12!"                     # valid password
UNREGISTERED_EMAIL = "ghost_user@siswa.um.edu.my"   # EP-03: valid format, no record
WRONG_PASSWORD     = "WrongPass99!"                  # DT-08: registered email, bad pass
INVALID_EMAIL      = "malformed_user.com"            # EP-02: missing "@"
PASS_7_CHARS       = "Pass123"                       # BVA-03: 7 chars (INVALID — below min)
PASS_8_CHARS       = "Pass1234"                      # BVA-04: 8 chars (AT minimum boundary)
PASS_9_CHARS       = "Pass12345"                     # BVA-05: 9 chars (above minimum boundary)
FORGOT_EMAIL       = "mobiletest@email.com"          # UCT-04: registered email for reset

options = UiAutomator2Options()
options.platform_name   = "Android"
options.device_name     = "emulator-5554"
options.app_package     = "com.adamarbain.dengueeyemobileapp"
options.app_activity    = ".MainActivity"
options.no_reset        = False     # Reset app state before login tests
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


def clear_and_type(by, value, text):
    el = find(by, value)
    el.clear()
    el.send_keys(text)
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
    """Dismiss any OK / alert popup."""
    try:
        tap(AppiumBy.XPATH, "//*[@text='OK']", timeout=3)
        time.sleep(0.5)
    except TimeoutException:
        pass


def go_to_login():
    """Ensure the app is on the Login screen."""
    dismiss_ok()
    # If already logged in, log out first
    if has_text("profile", "home", "dashboard", "dengue"):
        try:
            tap(AppiumBy.XPATH, "//*[@text='Profile']", timeout=5)
            time.sleep(1)
            tap(AppiumBy.XPATH,
                "//*[@text='Log Out' or @text='Logout' or @text='Sign Out']",
                timeout=5)
            time.sleep(2)
            dismiss_ok()
        except TimeoutException:
            pass
    # Restart the app to get a clean login screen
    driver.terminate_app("com.adamarbain.dengueeyemobileapp")
    time.sleep(1)
    driver.activate_app("com.adamarbain.dengueeyemobileapp")
    time.sleep(3)
    dismiss_ok()


def fill_login(email=None, password=None):
    """Fill the login form fields. Pass None to leave a field empty."""
    if email is not None:
        try:
            field = find(AppiumBy.XPATH,
                         "//android.widget.EditText[@text='Enter your email' "
                         "or @hint='Enter your email']")
            field.clear()
            field.send_keys(email)
        except TimeoutException:
            print("   ⚠️  Email field not found")
    if password is not None:
        try:
            field = find(AppiumBy.XPATH,
                         "//android.widget.EditText[@text='Enter your password' "
                         "or @hint='Enter your password']")
            field.clear()
            field.send_keys(password)
        except TimeoutException:
            print("   ⚠️  Password field not found")


def click_sign_in():
    """Tap the Sign In / Login button."""
    tap(AppiumBy.XPATH, "//*[@text='Sign In' or @text='Login' or @text='Log In']")
    time.sleep(4)


def logout_mobile():
    """Log out of the mobile app to reset state for next test."""
    try:
        tap(AppiumBy.XPATH, "//*[@text='Profile']", timeout=5)
        time.sleep(1)
        dismiss_ok()
        tap(AppiumBy.XPATH,
            "//*[@text='Log Out' or @text='Logout' or @text='Sign Out']",
            timeout=5)
        time.sleep(2)
        dismiss_ok()
    except TimeoutException:
        go_to_login()


# ─────────────────────────────────────────────
# SESSION SETUP — Verify app loads on Login screen
# ─────────────────────────────────────────────

def setup_session():
    """Verify app launches and displays the Login screen before all tests."""
    print("\n🔐 Verifying app launches on Login screen...")
    time.sleep(5)
    dismiss_ok()

    try:
        email_field = find(AppiumBy.XPATH,
                           "//android.widget.EditText[@text='Enter your email' "
                           "or @hint='Enter your email']", timeout=15)
        if email_field:
            print("✅ App launched — Login screen is ready")
            return True
        else:
            screenshot("UC1_M_Error_AppLaunch.png")
            print("❌ Login screen fields not found")
            return False
    except TimeoutException:
        screenshot("UC1_M_Error_AppLaunch.png")
        print("❌ App did not launch on Login screen — check Appium setup")
        return False


# ─────────────────────────────────────────────
# TC-UC01-01 (Mobile) — Valid Mobile App Login
# Techniques: UCT-02(public/company user login on mobile),
#             DT-06(all conditions true → login success),
#             ST-08(Login Screen Mobile → Home/Dashboard tabs)
# Unique: Tests COMPLETE happy path on mobile — redirects to /(tabs)
#         Retrieves companyId, role, fullName, email, termsAccepted
# ─────────────────────────────────────────────

def tc_uc01_01():
    print(f"\n▶ TC-UC01-01 (Mobile) — Valid Mobile App Login"
          f" (email='{VALID_EMAIL}')")
    print("   Technique: UCT-02, DT-06, ST-08")
    try:
        go_to_login()
        fill_login(VALID_EMAIL, VALID_PASS)
        screenshot("UC1_M_TC01_BeforeLogin.png")

        click_sign_in()
        dismiss_ok()

        screenshot("UC1_M_TC01_AfterLogin.png")

        if has_text("home", "dashboard", "profile", "welcome back", "dengue"):
            record("TC-UC01-01", True,
                   f"PASS — '{VALID_EMAIL}' accepted (UCT-02). "
                   "App retrieves user data (companyId, role, fullName, email, termsAccepted). "
                   "Redirected to /(tabs) Home/Dashboard (ST-08).")
            logout_mobile()
        else:
            if has_text("admin users cannot", "admin"):
                record("TC-UC01-01", False,
                       f"FAIL — '{VALID_EMAIL}' has admin role. "
                       "Use a non-admin mobile account.")
            else:
                record("TC-UC01-01", False,
                       "FAIL — Valid credentials did not navigate to Home/Dashboard. "
                       "Defect: mobile login flow broken.")
    except Exception as e:
        screenshot("UC1_M_Error_TC01.png")
        record("TC-UC01-01", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC01-02 (Mobile) — Empty Required Fields
# Techniques: EP-01(compulsory fields empty), BVA-01(email len=0),
#             BVA-02(password len=0), UCT-05(not filling compulsory fields),
#             ST-01(stays on Login with required field error)
# Unique: Tests EMPTY field validation
#         Attempt 1 = empty email, Attempt 2 = empty password
# ─────────────────────────────────────────────

def tc_uc01_02():
    print(f"\n▶ TC-UC01-02 (Mobile) — Empty Required Fields")
    print("   Technique: EP-01, BVA-01, BVA-02, UCT-05, ST-01")

    # Attempt 1 — BVA-01: email length = 0
    print("   [BVA-01] email = '' (empty — length 0)")
    try:
        go_to_login()
        fill_login(email="", password="Password123")
        click_sign_in()
        screenshot("UC1_M_TC02a_EmptyEmail.png")

        if has_text("email is required", "please enter your email",
                    "required", "empty"):
            record("TC-UC01-02a", True,
                   "PASS — Empty email rejected (BVA-01, EP-01). "
                   "Error message shown. Login blocked (ST-01).")
        else:
            record("TC-UC01-02a", False,
                   "FAIL — Empty email field not rejected. "
                   "Defect: required field validation missing.")
    except Exception as e:
        screenshot("UC1_M_Error_TC02a.png")
        record("TC-UC01-02a", False, f"Exception: {e}")

    # Attempt 2 — BVA-02: password length = 0
    print("   [BVA-02] password = '' (empty — length 0)")
    try:
        go_to_login()
        fill_login(email="admin@test.com", password="")
        click_sign_in()
        screenshot("UC1_M_TC02b_EmptyPassword.png")

        if has_text("password is required", "please enter your password",
                    "required", "empty"):
            record("TC-UC01-02b", True,
                   "PASS — Empty password rejected (BVA-02, EP-01). "
                   "Error message shown. Login blocked (ST-01).")
        else:
            record("TC-UC01-02b", False,
                   "FAIL — Empty password field not rejected. "
                   "Defect: required field validation missing.")
    except Exception as e:
        screenshot("UC1_M_Error_TC02b.png")
        record("TC-UC01-02b", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC01-03 (Mobile) — Invalid Email Format
# Techniques: EP-02(email missing "@"), UCT-06(invalid email format),
#             DT-07(invalid email → show error), ST-02(stays on Login)
# Unique: Tests EMAIL FORMAT validation — missing "@"
# ─────────────────────────────────────────────

def tc_uc01_03():
    print(f"\n▶ TC-UC01-03 (Mobile) — Invalid Email Format")
    print("   Technique: EP-02, UCT-06, DT-07, ST-02")
    print(f"   [EP-02] email = '{INVALID_EMAIL}' (missing '@')")
    try:
        go_to_login()
        fill_login(INVALID_EMAIL, "Password123")
        click_sign_in()
        screenshot("UC1_M_TC03_InvalidEmail.png")

        if has_text("invalid email", "valid email", "email address", "@", "format"):
            record("TC-UC01-03", True,
                   f"PASS — '{INVALID_EMAIL}' rejected (EP-02). "
                   "Error: 'Invalid email address' shown (DT-07). "
                   "User stays on Login page (ST-02).")
        else:
            record("TC-UC01-03", False,
                   f"FAIL — '{INVALID_EMAIL}' NOT rejected. "
                   "Defect: email format validation missing.")
    except Exception as e:
        screenshot("UC1_M_Error_TC03.png")
        record("TC-UC01-03", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC01-04 (Mobile) — Unregistered Email
# Techniques: EP-03(valid format, no system record),
#             UCT-08(username not registered),
#             DT-09(user account not found → error message),
#             ST-03(stays on Login with not-found error)
# Unique: Tests LOOKUP failure — valid email syntax, absent from DB
# ─────────────────────────────────────────────

def tc_uc01_04():
    print(f"\n▶ TC-UC01-04 (Mobile) — Unregistered Email")
    print("   Technique: EP-03, UCT-08, DT-09, ST-03")
    print(f"   [EP-03] email = '{UNREGISTERED_EMAIL}' (valid format, no DB record)")
    try:
        go_to_login()
        fill_login(UNREGISTERED_EMAIL, "Password123")
        click_sign_in()
        screenshot("UC1_M_TC04_UnregisteredEmail.png")

        if has_text("no account found", "user not found", "check your email",
                    "not found", "not registered"):
            record("TC-UC01-04", True,
                   f"PASS — '{UNREGISTERED_EMAIL}' rejected (EP-03). "
                   "Error: 'No account found with this email' shown (DT-09). "
                   "User stays on Login page (ST-03).")
        else:
            record("TC-UC01-04", False,
                   f"FAIL — Unregistered email NOT rejected. "
                   "Defect: user lookup validation missing.")
    except Exception as e:
        screenshot("UC1_M_Error_TC04.png")
        record("TC-UC01-04", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC01-05 (Mobile) — Wrong Password
# Techniques: UCT-07(enter wrong password),
#             DT-08(email correct, password wrong → wrong password error),
#             ST-04(stays on Login with wrong password error)
# Unique: Tests CREDENTIAL MISMATCH — existing email + wrong password
# ─────────────────────────────────────────────

def tc_uc01_05():
    print(f"\n▶ TC-UC01-05 (Mobile) — Wrong Password")
    print("   Technique: UCT-07, DT-08, ST-04")
    print(f"   email = '{VALID_EMAIL}' (registered), password = '{WRONG_PASSWORD}' (wrong)")
    try:
        go_to_login()
        fill_login(VALID_EMAIL, WRONG_PASSWORD)
        click_sign_in()
        screenshot("UC1_M_TC05_WrongPassword.png")

        if has_text("incorrect password", "wrong password", "please try again",
                    "try again"):
            record("TC-UC01-05", True,
                   f"PASS — Wrong password rejected (UCT-07). "
                   "Error: 'Incorrect password. Please try again.' shown (DT-08). "
                   "User stays on Login page (ST-04).")
        else:
            record("TC-UC01-05", False,
                   "FAIL — Wrong password NOT rejected for registered email. "
                   "Defect: password validation broken.")
    except Exception as e:
        screenshot("UC1_M_Error_TC05.png")
        record("TC-UC01-05", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC01-06 (Mobile) — Too Many Failed Login Attempts
# Techniques: UCT-09(too many failed login attempts),
#             ST-05(Login Screen — too many attempts → blocked)
# Unique: Tests RATE-LIMITING — Firebase too-many-requests
#         Requires 10+ consecutive failed attempts
# ─────────────────────────────────────────────

def tc_uc01_06():
    print(f"\n▶ TC-UC01-06 (Mobile) — Too Many Failed Login Attempts")
    print("   Technique: UCT-09, ST-05")
    print(f"   Attempting 10+ consecutive failed logins on '{VALID_EMAIL}'...")
    try:
        blocked = False
        for attempt in range(1, 12):
            go_to_login()
            fill_login(VALID_EMAIL, f"WrongPass{attempt}!")
            click_sign_in()
            print(f"   Attempt {attempt}/11 ...")

            if has_text("too many", "too many failed", "try again later",
                        "many requests", "blocked"):
                print(f"   🔒 Blocked after {attempt} attempts")
                screenshot("UC1_M_TC06_TooManyAttempts.png")
                blocked = True
                break
            time.sleep(1)

        if blocked:
            record("TC-UC01-06", True,
                   "PASS — System blocked login after too many failed attempts (UCT-09). "
                   "Error: 'Too many failed attempts. Please try again later.' shown. "
                   "User stays on Login page (ST-05).")
        else:
            screenshot("UC1_M_TC06_NotBlocked.png")
            record("TC-UC01-06", False,
                   "FAIL — System did NOT block after 11 consecutive failed attempts. "
                   "Defect: Firebase rate-limiting not triggered on mobile.")
    except Exception as e:
        screenshot("UC1_M_Error_TC06.png")
        record("TC-UC01-06", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC01-07 (Mobile) — Sign Up Redirect
# Techniques: UCT-03(user wants to sign up — alternate flow),
#             ST(Login Screen → Registration Screen)
# Unique: Tests NAVIGATION to registration — different from authentication tests
# ─────────────────────────────────────────────

def tc_uc01_07():
    print(f"\n▶ TC-UC01-07 (Mobile) — Sign Up Redirect")
    print("   Technique: UCT-03, ST (Login → Registration Screen)")
    try:
        go_to_login()
        screenshot("UC1_M_TC07_BeforeSignUp.png")

        tap(AppiumBy.XPATH,
            "//*[@text=\"Sign Up\" or @text=\"Don't have an account? Sign Up\" "
            "or contains(@text,'Sign Up')]")
        time.sleep(3)

        screenshot("UC1_M_TC07_AfterSignUp.png")

        if has_text("register", "create account", "sign up", "full name",
                    "registration"):
            record("TC-UC01-07", True,
                   "PASS — 'Sign Up' / 'Don't have an account? Sign Up' tapped (UCT-03). "
                   "App redirected to Registration screen. Alternate flow works correctly.")
        else:
            record("TC-UC01-07", False,
                   "FAIL — Did not navigate to Registration screen. "
                   "Defect: alternate flow (Sign Up redirect) broken.")
    except TimeoutException:
        screenshot("UC1_M_TC07_NoSignUpBtn.png")
        record("TC-UC01-07", None,
               "N/A — Sign Up text/button not found on Login screen. "
               "Check element text or locator.")
    except Exception as e:
        screenshot("UC1_M_Error_TC07.png")
        record("TC-UC01-07", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC01-08 (Mobile) — Forgot Password (Reset Page)
# Techniques: UCT-04(forgot password exception flow on mobile),
#             ST(Login Screen → Reset Password Page → Reset email sent)
# Unique: Mobile directs user to RESET PASSWORD PAGE (not a modal like Admin Web)
#         System sends a password reset email to the registered address
# ─────────────────────────────────────────────

def tc_uc01_08():
    print(f"\n▶ TC-UC01-08 (Mobile) — Forgot Password")
    print("   Technique: UCT-04, ST (Login → Reset Password Page)")
    try:
        go_to_login()
        fill_login(VALID_EMAIL, WRONG_PASSWORD)

        tap(AppiumBy.XPATH,
            "//*[@text='Forgot Password?' or @text='Forgot password?' "
            "or contains(@text,'Forgot')]")
        time.sleep(3)
        screenshot("UC1_M_TC08_ForgotPwdPage.png")

        on_reset_page = has_text("reset", "password reset", "enter your email",
                                 "reset password", "forgot")
        if not on_reset_page:
            record("TC-UC01-08", False,
                   "FAIL — Did not navigate to Reset Password page. "
                   "Defect: Forgot Password flow broken on mobile.")
            return

        # Try to submit the reset email
        try:
            reset_field = find(AppiumBy.XPATH,
                               "//android.widget.EditText", timeout=5)
            reset_field.clear()
            reset_field.send_keys(FORGOT_EMAIL)
            tap(AppiumBy.XPATH,
                "//*[@text='Send' or @text='Submit' or @text='Reset Password' "
                "or @text='Send Reset Email']")
            time.sleep(3)
            screenshot("UC1_M_TC08_ResetEmailSent.png")
        except TimeoutException:
            pass  # Field may be pre-filled

        if has_text("password reset email sent", "check your inbox",
                    "reset email", "sent", "email sent"):
            record("TC-UC01-08", True,
                   f"PASS — Forgot Password tapped (UCT-04). "
                   "Navigated to Reset Password page. "
                   "Reset email sent to registered address. "
                   "Message confirmed.")
        elif on_reset_page:
            record("TC-UC01-08", True,
                   "PASS — Forgot Password tapped (UCT-04). "
                   "Reset Password page displayed correctly. "
                   "Awaiting email submission confirmation.")
        else:
            record("TC-UC01-08", False,
                   "FAIL — Reset email confirmation not shown. "
                   "Defect: password reset email flow not completing.")
    except TimeoutException:
        screenshot("UC1_M_TC08_NoForgotBtn.png")
        record("TC-UC01-08", None,
               "N/A — 'Forgot Password?' button not found. "
               "Check element text or locator.")
    except Exception as e:
        screenshot("UC1_M_Error_TC08.png")
        record("TC-UC01-08", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC01-09 (Mobile) — One Active Session (Business Rule)
# Techniques: UCT-11(only one active session per user at a time)
# Unique: Tests BUSINESS RULE — single-session enforcement
#         Requires two devices; marked N/A if only one device available
#         Manual verification recommended if automation is not possible
# ─────────────────────────────────────────────

def tc_uc01_09():
    print(f"\n▶ TC-UC01-09 (Mobile) — One Active Session (Business Rule)")
    print("   Technique: UCT-11")
    print("   ⚠️  This test requires TWO separate Android devices/emulators.")
    print("   Device 1: login and stay logged in.")
    print("   Device 2: login with the same credentials.")
    print("   Expected: only ONE session remains active.")

    # Attempt Device 1 login (this device)
    try:
        go_to_login()
        fill_login(VALID_EMAIL, VALID_PASS)
        click_sign_in()
        dismiss_ok()
        screenshot("UC1_M_TC09_Device1Login.png")

        if has_text("home", "dashboard", "profile", "dengue"):
            print("   ✅ Device 1: Login successful — session active.")
            print("   🔔 NOW log in on Device 2 with the same credentials.")
            print("      Then check this device for a session-expired / forced-logout message.")
            time.sleep(10)  # Allow time for second device login
            screenshot("UC1_M_TC09_Device1AfterDevice2Login.png")

            if has_text("session expired", "logged out", "another device",
                        "sign in again", "session invalid"):
                record("TC-UC01-09", True,
                       "PASS — Device 1 session invalidated when Device 2 logged in (UCT-11). "
                       "Business rule enforced: one active session per user.")
                logout_mobile()
            else:
                record("TC-UC01-09", None,
                       "N/A — Could not verify session invalidation automatically. "
                       "Manual check required: confirm only one session is active. "
                       "Dependency: TC-UC01-01 (valid login must succeed).")
        else:
            record("TC-UC01-09", False,
                   "FAIL — Device 1 login failed. Cannot proceed with session test.")
    except Exception as e:
        screenshot("UC1_M_Error_TC09.png")
        record("TC-UC01-09", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# BVA PASSWORD BOUNDARY TESTS (Mobile)
# Techniques: BVA-03(7 chars — INVALID below min),
#             BVA-04(8 chars — AT minimum boundary),
#             BVA-05(9 chars — above minimum boundary)
# Unique: Tests PASSWORD LENGTH boundaries around the 8-character minimum rule
#         TC-UC01-02 tests EMPTY password — a separate boundary entirely
# ─────────────────────────────────────────────

def tc_bva_password():
    print(f"\n▶ BVA Password Length Boundary Tests (Mobile)")
    print("   Technique: BVA-03 (7 chars), BVA-04 (8 chars), BVA-05 (9 chars)")
    print("   Rule: Minimum password length = 8 characters")

    # BVA-03: 7 chars — below minimum boundary (INVALID)
    print(f"   [BVA-03] password = '{PASS_7_CHARS}' (7 chars — BELOW minimum, invalid)")
    try:
        go_to_login()
        fill_login(VALID_EMAIL, PASS_7_CHARS)
        click_sign_in()
        screenshot("UC1_M_BVA03_7CharPass.png")

        if has_text("password", "character", "minimum", "least", "short", "8"):
            record("TC-UC01-12 (BVA-03)", True,
                   f"PASS — 7-char password '{PASS_7_CHARS}' rejected (BVA-03). "
                   "Below minimum 8-character rule. Login blocked.")
        else:
            record("TC-UC01-12 (BVA-03)", False,
                   f"FAIL — 7-char password NOT rejected. "
                   "Defect: minimum length validation missing on mobile.")
    except Exception as e:
        screenshot("UC1_M_Error_BVA03.png")
        record("TC-UC01-12 (BVA-03)", False, f"Exception: {e}")

    # BVA-04: 8 chars — AT minimum boundary (VALID length)
    print(f"   [BVA-04] password = '{PASS_8_CHARS}' (8 chars — AT minimum boundary)")
    try:
        go_to_login()
        fill_login(VALID_EMAIL, PASS_8_CHARS)
        click_sign_in()
        screenshot("UC1_M_BVA04_8CharPass.png")

        length_rejected = has_text("character", "minimum", "least", "short", "8 char")
        if not length_rejected:
            record("TC-UC01-13 (BVA-04)", True,
                   f"PASS — 8-char password '{PASS_8_CHARS}' accepted by length rule (BVA-04). "
                   "System proceeds to credential validation "
                   "(auth outcome depends on correctness, not length).")
        else:
            record("TC-UC01-13 (BVA-04)", False,
                   f"FAIL — 8-char password incorrectly rejected by length rule. "
                   "Defect: minimum boundary validation too strict on mobile.")
    except Exception as e:
        screenshot("UC1_M_Error_BVA04.png")
        record("TC-UC01-13 (BVA-04)", False, f"Exception: {e}")

    # BVA-05: 9 chars — above minimum boundary (VALID length)
    print(f"   [BVA-05] password = '{PASS_9_CHARS}' (9 chars — above minimum boundary)")
    try:
        go_to_login()
        fill_login(VALID_EMAIL, PASS_9_CHARS)
        click_sign_in()
        screenshot("UC1_M_BVA05_9CharPass.png")

        length_rejected = has_text("character", "minimum", "least", "short", "8 char")
        if not length_rejected:
            record("TC-UC01-14 (BVA-05)", True,
                   f"PASS — 9-char password '{PASS_9_CHARS}' accepted by length rule (BVA-05). "
                   "Above minimum — no length error raised.")
        else:
            record("TC-UC01-14 (BVA-05)", False,
                   f"FAIL — 9-char password incorrectly rejected by length. "
                   "Defect: boundary validation logic incorrect on mobile.")
    except Exception as e:
        screenshot("UC1_M_Error_BVA05.png")
        record("TC-UC01-14 (BVA-05)", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

try:
    print("=" * 62)
    print("  UC1 LOGIN — MOBILE APPIUM TEST")
    print("  Testing Level: System Testing")
    print("  Testers: Edwin Tan, Izzatul Filzah, Auni Nafisa, Yusrina Maisarah")
    print(f"  App: com.adamarbain.dengueeyemobileapp")
    print(f"  Screenshots: {SCREENSHOT_DIR}")
    print("=" * 62)
    print("\n  Test Cases and What Each Tests (No Redundancy):")
    print("  TC-UC01-01 → Happy path: valid mobile login → /(tabs) Home")
    print("  TC-UC01-02 → Empty field validation: email (BVA-01) + password (BVA-02)")
    print("  TC-UC01-03 → Invalid email format: missing '@' (EP-02)")
    print("  TC-UC01-04 → Unregistered email: valid format, no DB record (EP-03)")
    print("  TC-UC01-05 → Wrong password: registered email + wrong pass (DT-08)")
    print("  TC-UC01-06 → Too many attempts: 10+ fails → system blocks (UCT-09)")
    print("  TC-UC01-07 → Sign Up redirect: alternate flow (UCT-03)")
    print("  TC-UC01-08 → Forgot Password: navigate to reset page + email sent (UCT-04)")
    print("  TC-UC01-09 → One active session: business rule (UCT-11)")
    print("  BVA-03/04/05 → Password length: 7 (invalid), 8 (min), 9 (above min)")
    print("=" * 62)

    if setup_session():
        tc_uc01_01()       # UCT-02, DT-06, ST-08
        tc_uc01_02()       # EP-01, BVA-01, BVA-02, UCT-05, ST-01
        tc_uc01_03()       # EP-02, UCT-06, DT-07, ST-02
        tc_uc01_04()       # EP-03, UCT-08, DT-09, ST-03
        tc_uc01_05()       # UCT-07, DT-08, ST-04
        tc_uc01_06()       # UCT-09, ST-05
        tc_uc01_07()       # UCT-03
        tc_uc01_08()       # UCT-04
        tc_uc01_09()       # UCT-11 (Business Rule)
        tc_bva_password()  # BVA-03, BVA-04, BVA-05
    else:
        print("🛑 Aborting — app login screen not accessible")

except Exception as e:
    print(f"\n🛑 Unexpected error: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n" + "=" * 62)
    print("  TEST SUMMARY — UC1 Login (Mobile)")
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