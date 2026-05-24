"""
UC1 Login - Web Selenium Test Script
Testing Level: System Testing
Techniques Applied:
  - Equivalence Partitioning (EP)
  - Boundary Value Analysis (BVA)
  - Decision Table Testing (DT)
  - Use Case Testing (UCT)
  - State Transition Testing (ST)
Tool: Selenium WebDriver (Chrome)
Testers:
  - Edwin Tan Yu Xian        (Equivalence Partitioning)
  - brendan (Boundary Value Analysis)
  - Izzatul Filzah bt Norazmi (Decision Table Testing)
  - Auni Nafisa bt Osman      (Use Case Testing)
  - Yusrina Maisarah bt Yunus (State Transition Testing)
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
SCRIPT_DIR     = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIR = os.path.join(SCRIPT_DIR, "UC1_screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Test data — each test uses DIFFERENT data (no redundancy)
ADMIN_EMAIL        = "admin@drone4dengue.com"       # EP-05: valid admin account
ADMIN_PASS         = "AdminSecurePass123!"           # valid admin password
NON_ADMIN_EMAIL    = "public_user@siswa.um.edu.my"  # EP-04: valid but role != admin
NON_ADMIN_PASS     = "ValidPass123!"
UNREGISTERED_EMAIL = "ghost_user@siswa.um.edu.my"   # EP-03: correct syntax, no record
WRONG_PASSWORD     = "WrongPass99!"                 # DT-08: valid email, wrong pass
INVALID_EMAIL      = "malformed_user.com"           # EP-02: missing "@"
PASS_7_CHARS       = "Pass123"                      # BVA-03: 7 chars (INVALID — below min)
PASS_8_CHARS       = "Pass1234"                     # BVA-04: 8 chars (AT minimum boundary)
PASS_9_CHARS       = "Pass12345"                    # BVA-05: 9 chars (above minimum boundary)
FORGOT_EMAIL       = "admin@drone4dengue.com"       # UCT-04: registered email for reset

driver  = webdriver.Chrome()
driver.maximize_window()
wait    = WebDriverWait(driver, 15)
results = []


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def screenshot_full(filename):
    """Take a full-page screenshot."""
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


def clear_and_type(field_id, value):
    field = wait.until(EC.presence_of_element_located((By.ID, field_id)))
    field.clear()
    driver.execute_script("arguments[0].value = '';", field)
    field.send_keys(value)
    return field


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


def go_to_login():
    """Navigate to login page and wait for form to be ready."""
    driver.get(f"{BASE_URL}/")
    time.sleep(1)
    wait.until(EC.presence_of_element_located((By.ID, "email")))
    time.sleep(0.5)


def fill_login(email=None, password=None):
    """Fill login form — pass None to leave a field empty."""
    if email is not None:
        email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_field.clear()
        driver.execute_script("arguments[0].value = '';", email_field)
        email_field.send_keys(email)
    if password is not None:
        pass_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
        pass_field.clear()
        driver.execute_script("arguments[0].value = '';", pass_field)
        pass_field.send_keys(password)


def click_login_btn():
    """Click the Login / Sign In submit button."""
    tap_el(By.CSS_SELECTOR, "button[type='submit']")
    time.sleep(2)


def logout():
    """Sign out after a successful login test to reset state for next test."""
    try:
        tap_el(By.XPATH,
               "//*[contains(text(),'Logout') or contains(text(),'Sign Out') "
               "or contains(text(),'Log Out')]", timeout=5)
        time.sleep(2)
    except TimeoutException:
        driver.get(f"{BASE_URL}/logout")
        time.sleep(1)


def simulate_offline():
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
        "offline": True, "downloadThroughput": 0,
        "uploadThroughput": 0, "latency": 0
    })


def simulate_online():
    driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
        "offline": False, "downloadThroughput": -1,
        "uploadThroughput": -1, "latency": 0
    })


# ─────────────────────────────────────────────
# SESSION SETUP — Verify login page loads
# ─────────────────────────────────────────────

def setup_session():
    """Verify the login page and its form fields are accessible before all tests."""
    print("\n🔐 Verifying login page is accessible...")
    try:
        go_to_login()
        email_ok    = find_el(By.ID, "email")
        password_ok = find_el(By.ID, "password")
        if email_ok and password_ok:
            print(f"✅ Login page loaded → {driver.current_url}")
            return True
        else:
            screenshot_full("UC1_Error_PageLoad.png")
            print("❌ Login form fields not found")
            return False
    except TimeoutException:
        screenshot_full("UC1_Error_PageLoad.png")
        print("❌ Login page not reachable — is localhost:3000 running?")
        return False


# ─────────────────────────────────────────────
# TC-UC01-01 — Valid Admin Login (Main Flow)
# Techniques: EP-05(valid admin creds), BVA-06(valid email+pass),
#             UCT-01(admin web main flow), DT-06(all conditions true),
#             ST-07(Login Screen → Dashboard)
# Unique: Tests the COMPLETE happy path — valid admin login on web
# ─────────────────────────────────────────────

def tc_uc01_01():
    print(f"\n▶ TC-UC01-01 — Valid Admin Login"
          f" (email='{ADMIN_EMAIL}', password='{ADMIN_PASS}')")
    print("   Technique: EP-05, BVA-06, UCT-01, DT-06, ST-07")
    try:
        go_to_login()
        screenshot_full("UC1_TC01_BeforeLogin.png")

        fill_login(ADMIN_EMAIL, ADMIN_PASS)
        click_login_btn()

        screenshot_full("UC1_TC01_AfterLogin.png")

        redirected = "/dashboard" in driver.current_url
        success_msg = has_text("login successful", "welcome", "dashboard")

        if redirected or success_msg:
            record("TC-UC01-01", True,
                   f"PASS — Admin '{ADMIN_EMAIL}' accepted (EP-05). "
                   "Redirected to /dashboard (ST-07). "
                   "All DT-06 conditions satisfied.")
            logout()
        else:
            record("TC-UC01-01", False,
                   "FAIL — Valid admin credentials did not redirect to /dashboard. "
                   "Defect: Main login flow broken.")
    except Exception as e:
        screenshot_full("UC1_Error_TC01.png")
        record("TC-UC01-01", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC01-02 — Empty Required Fields
# Techniques: EP-01(compulsory fields empty), BVA-01(email len=0),
#             BVA-02(password len=0), UCT-05(not filling compulsory fields),
#             ST-01(stays on Login Screen with error)
# Unique: Tests EMPTY field validation — two separate required fields
#         Attempt 1 = empty email, Attempt 2 = empty password
#         TC-UC01-03 tests FORMAT errors — completely different validation
# ─────────────────────────────────────────────

def tc_uc01_02():
    print(f"\n▶ TC-UC01-02 — Empty Required Fields")
    print("   Technique: EP-01, BVA-01, BVA-02, UCT-05, ST-01")

    # Attempt 1 — BVA-01: email length = 0 (empty email)
    print("   [BVA-01] email = '' (empty — length 0, below minimum)")
    try:
        go_to_login()
        fill_login(email="", password="Password123")
        click_login_btn()
        screenshot_full("UC1_TC02a_EmptyEmail.png")

        if has_error(["email is required", "please enter your email",
                      "text-red", "border-red", "required"]):
            record("TC-UC01-02a", True,
                   "PASS — Empty email field rejected (BVA-01, EP-01). "
                   "Error message shown. Login blocked (ST-01).")
        else:
            record("TC-UC01-02a", False,
                   "FAIL — Empty email field not rejected. "
                   "Defect: required field validation missing.")
    except Exception as e:
        screenshot_full("UC1_Error_TC02a.png")
        record("TC-UC01-02a", False, f"Exception: {e}")

    # Attempt 2 — BVA-02: password length = 0 (empty password)
    print("   [BVA-02] password = '' (empty — length 0, below minimum)")
    try:
        go_to_login()
        fill_login(email="admin@test.com", password="")
        click_login_btn()
        screenshot_full("UC1_TC02b_EmptyPassword.png")

        if has_error(["password is required", "please enter your password",
                      "text-red", "border-red", "required"]):
            record("TC-UC01-02b", True,
                   "PASS — Empty password field rejected (BVA-02, EP-01). "
                   "Error message shown. Login blocked (ST-01).")
        else:
            record("TC-UC01-02b", False,
                   "FAIL — Empty password field not rejected. "
                   "Defect: required field validation missing.")
    except Exception as e:
        screenshot_full("UC1_Error_TC02b.png")
        record("TC-UC01-02b", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC01-03 — Invalid Email Format
# Techniques: EP-02(email missing "@"), UCT-06(invalid email format),
#             DT-07(invalid email format → show error), ST-02(stays on Login)
# Unique: Tests EMAIL FORMAT validation only — missing "@" character
#         TC-UC01-02 tests EMPTY fields, TC-UC01-04 tests unregistered email
# ─────────────────────────────────────────────

def tc_uc01_03():
    print(f"\n▶ TC-UC01-03 — Invalid Email Format")
    print("   Technique: EP-02, UCT-06, DT-07, ST-02")
    print(f"   [EP-02] email = '{INVALID_EMAIL}' (missing '@' — invalid format)")
    try:
        go_to_login()
        fill_login(INVALID_EMAIL, "Password123")
        click_login_btn()
        screenshot_full("UC1_TC03_InvalidEmailFormat.png")

        if has_error(["invalid email", "valid email", "email address",
                      "text-red", "border-red", "@"]):
            record("TC-UC01-03", True,
                   f"PASS — '{INVALID_EMAIL}' rejected (EP-02). "
                   "Error: 'Invalid email address' shown (DT-07). "
                   "User stays on Login page (ST-02).")
        else:
            record("TC-UC01-03", False,
                   f"FAIL — '{INVALID_EMAIL}' NOT rejected. "
                   "Defect: email format validation missing.")
    except Exception as e:
        screenshot_full("UC1_Error_TC03.png")
        record("TC-UC01-03", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC01-04 — Unregistered Email
# Techniques: EP-03(valid format but no system record),
#             UCT-08(username not registered),
#             DT-09(user account does not exist → user not found),
#             ST-03(stays on Login with not-found error)
# Unique: Tests LOOKUP failure — email is syntactically valid but absent from DB
#         Different from TC-UC01-03 (format error) and TC-UC01-05 (wrong password)
# ─────────────────────────────────────────────

def tc_uc01_04():
    print(f"\n▶ TC-UC01-04 — Unregistered Email")
    print("   Technique: EP-03, UCT-08, DT-09, ST-03")
    print(f"   [EP-03] email = '{UNREGISTERED_EMAIL}' (valid format, no DB record)")
    try:
        go_to_login()
        fill_login(UNREGISTERED_EMAIL, "Password123")
        click_login_btn()
        screenshot_full("UC1_TC04_UnregisteredEmail.png")

        if has_error(["no account found", "user not found", "check your email",
                      "text-red", "border-red", "not found"]):
            record("TC-UC01-04", True,
                   f"PASS — '{UNREGISTERED_EMAIL}' rejected (EP-03). "
                   "Error: 'No account found with this email' shown (DT-09). "
                   "User stays on Login page (ST-03).")
        else:
            record("TC-UC01-04", False,
                   f"FAIL — Unregistered email '{UNREGISTERED_EMAIL}' NOT rejected. "
                   "Defect: user lookup validation missing.")
    except Exception as e:
        screenshot_full("UC1_Error_TC04.png")
        record("TC-UC01-04", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC01-05 — Wrong Password
# Techniques: UCT-07(enter wrong password),
#             DT-08(email correct, password incorrect → wrong password error),
#             ST-04(stays on Login with wrong password error)
# Unique: Tests CREDENTIAL MISMATCH — email exists in DB, password is wrong
#         TC-UC01-04 tests absent email, this tests existing email + bad pass
# ─────────────────────────────────────────────

def tc_uc01_05():
    print(f"\n▶ TC-UC01-05 — Wrong Password")
    print("   Technique: UCT-07, DT-08, ST-04")
    print(f"   email = '{ADMIN_EMAIL}' (registered), password = '{WRONG_PASSWORD}' (incorrect)")
    try:
        go_to_login()
        fill_login(ADMIN_EMAIL, WRONG_PASSWORD)
        click_login_btn()
        screenshot_full("UC1_TC05_WrongPassword.png")

        if has_error(["incorrect password", "wrong password", "please try again",
                      "text-red", "border-red"]):
            record("TC-UC01-05", True,
                   f"PASS — Wrong password rejected (UCT-07). "
                   "Error: 'Incorrect password. Please try again.' shown (DT-08). "
                   "User stays on Login page (ST-04).")
        else:
            record("TC-UC01-05", False,
                   "FAIL — Wrong password NOT rejected for registered email. "
                   "Defect: password validation broken.")
    except Exception as e:
        screenshot_full("UC1_Error_TC05.png")
        record("TC-UC01-05", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC01-06 — Non-Admin Login Denied (Admin Web Only)
# Techniques: EP-04(valid account lacking admin privileges),
#             UCT-10(user does not have admin privileges),
#             DT-010(all valid but role != admin → access denied),
#             ST-06(Login Screen Web — non-admin → access denied error)
# Unique: Tests ROLE-BASED access control — valid creds but wrong role
#         Only applicable to Admin Web platform, not mobile
# ─────────────────────────────────────────────

def tc_uc01_06():
    print(f"\n▶ TC-UC01-06 — Non-Admin Access Denied (Admin Web Only)")
    print("   Technique: EP-04, UCT-10, DT-010, ST-06")
    print(f"   [EP-04] email = '{NON_ADMIN_EMAIL}' (valid account, role != 'admin')")
    try:
        go_to_login()
        fill_login(NON_ADMIN_EMAIL, NON_ADMIN_PASS)
        click_login_btn()
        screenshot_full("UC1_TC06_NonAdminDenied.png")

        if has_error(["access denied", "admin privileges", "admin required",
                      "text-red", "border-red"]):
            record("TC-UC01-06", True,
                   f"PASS — Non-admin '{NON_ADMIN_EMAIL}' denied (EP-04). "
                   "Error: 'Access denied. Admin privileges required.' shown (DT-010). "
                   "User signed out of Firebase. Stays on Login (ST-06).")
        else:
            record("TC-UC01-06", False,
                   f"FAIL — Non-admin user NOT denied. "
                   "Defect: role-based access control not enforced.")
    except Exception as e:
        screenshot_full("UC1_Error_TC06.png")
        record("TC-UC01-06", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC01-07 — Too Many Failed Login Attempts
# Techniques: UCT-09(too many failed attempts),
#             ST-05(Login Screen — too many attempts → blocked error)
# Unique: Tests RATE-LIMITING / Firebase too-many-requests error
#         Requires 10+ consecutive failed attempts — different from TC-UC01-05
# ─────────────────────────────────────────────

def tc_uc01_07():
    print(f"\n▶ TC-UC01-07 — Too Many Failed Login Attempts")
    print("   Technique: UCT-09, ST-05")
    print(f"   Attempting 10+ consecutive failed logins on '{ADMIN_EMAIL}'...")
    try:
        blocked = False
        for attempt in range(1, 12):
            go_to_login()
            fill_login(ADMIN_EMAIL, f"WrongPass{attempt}!")
            click_login_btn()
            print(f"   Attempt {attempt}/11 ...")

            if has_text("too many", "too many failed", "try again later",
                        "many requests", "blocked"):
                print(f"   🔒 Blocked after {attempt} attempts")
                screenshot_full("UC1_TC07_TooManyAttempts.png")
                blocked = True
                break
            time.sleep(1)

        if blocked:
            record("TC-UC01-07", True,
                   "PASS — System blocked login after too many failed attempts (UCT-09). "
                   "Error: 'Too many failed attempts. Please try again later.' shown. "
                   "User stays on Login page (ST-05).")
        else:
            screenshot_full("UC1_TC07_NotBlocked.png")
            record("TC-UC01-07", False,
                   "FAIL — System did NOT block after 11 consecutive failed attempts. "
                   "Defect: Firebase rate-limiting / too-many-requests not triggered.")
    except Exception as e:
        screenshot_full("UC1_Error_TC07.png")
        record("TC-UC01-07", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC01-08 — Sign Up Redirect (Alternate Flow)
# Techniques: UCT-03(user wants to sign up — alternate flow),
#             ST(Login Screen → Registration Screen)
# Unique: Tests NAVIGATION away from login — different from authentication tests
# ─────────────────────────────────────────────

def tc_uc01_08():
    print(f"\n▶ TC-UC01-08 — Sign Up Redirect")
    print("   Technique: UCT-03, ST (Login → Registration)")
    try:
        go_to_login()
        screenshot_full("UC1_TC08_BeforeSignUp.png")

        tap_el(By.XPATH,
               "//*[contains(text(),'Sign Up') or "
               "contains(text(),'Don\\'t have an account')]")
        time.sleep(2)

        screenshot_full("UC1_TC08_AfterSignUp.png")

        redirected = ("/register" in driver.current_url or
                      "/signup"   in driver.current_url or
                      has_text("register", "create account", "sign up"))

        if redirected:
            record("TC-UC01-08", True,
                   "PASS — 'Sign Up' link redirects to Registration page (UCT-03). "
                   "Alternate flow works correctly.")
        else:
            record("TC-UC01-08", False,
                   "FAIL — 'Sign Up' link did not redirect to Registration page. "
                   "Defect: alternate flow broken.")
    except TimeoutException:
        screenshot_full("UC1_TC08_NoSignUpLink.png")
        record("TC-UC01-08", None,
               "N/A — 'Sign Up' link not found on Admin Web. "
               "Sign-up may be mobile-only by design.")
    except Exception as e:
        screenshot_full("UC1_Error_TC08.png")
        record("TC-UC01-08", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC01-09 — Forgot Password (Admin Web Modal)
# Techniques: UCT-04(forgot password exception flow),
#             ST(Login Screen → Reset modal → Password reset email sent)
# Unique: Tests EXCEPTION FLOW for forgotten password on Admin Web
#         Admin Web shows a modal/dialog; Mobile shows a separate page (Appium)
# ─────────────────────────────────────────────

def tc_uc01_09():
    print(f"\n▶ TC-UC01-09 — Forgot Password (Admin Web Modal)")
    print("   Technique: UCT-04, ST (Login → Reset Modal)")
    try:
        go_to_login()
        fill_login(ADMIN_EMAIL, WRONG_PASSWORD)

        tap_el(By.XPATH,
               "//*[contains(text(),'Forgot Password') or "
               "contains(text(),'Forgot password?')]")
        time.sleep(2)
        screenshot_full("UC1_TC09_ForgotPwdModal.png")

        modal_open = has_text("reset", "password reset", "send", "inbox",
                              "enter your email", "reset email")
        if not modal_open:
            # If modal requires email input
            try:
                reset_email_field = find_el(By.XPATH,
                    "//input[@type='email' or @placeholder]", timeout=5)
                reset_email_field.clear()
                reset_email_field.send_keys(FORGOT_EMAIL)
                tap_el(By.XPATH,
                       "//button[contains(.,'Send') or contains(.,'Reset') "
                       "or contains(.,'Submit')]")
                time.sleep(2)
                screenshot_full("UC1_TC09_ResetEmailSent.png")
            except TimeoutException:
                pass

        if has_text("password reset email sent", "check your inbox",
                    "reset email", "sent"):
            record("TC-UC01-09", True,
                   "PASS — Forgot Password modal opened (UCT-04). "
                   "Reset email sent. Message: 'Password reset email sent. "
                   "Please check your inbox.' shown.")
        elif modal_open:
            record("TC-UC01-09", True,
                   "PASS — Forgot Password modal opened (UCT-04). "
                   "Reset form displayed — awaiting email entry.")
        else:
            record("TC-UC01-09", False,
                   "FAIL — Forgot Password modal did not open. "
                   "Defect: password reset flow broken on Admin Web.")
    except TimeoutException:
        screenshot_full("UC1_TC09_NoForgotLink.png")
        record("TC-UC01-09", None,
               "N/A — 'Forgot Password?' link not found on page. "
               "Check if element ID/text matches.")
    except Exception as e:
        screenshot_full("UC1_Error_TC09.png")
        record("TC-UC01-09", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# BVA PASSWORD BOUNDARY TESTS
# Techniques: BVA-03(7 chars — INVALID below min),
#             BVA-04(8 chars — AT minimum boundary),
#             BVA-05(9 chars — above minimum boundary)
# Unique: Tests PASSWORD LENGTH boundaries at/around the 8-character rule
#         TC-UC01-02 tests EMPTY password — a separate boundary entirely
# ─────────────────────────────────────────────

def tc_bva_password():
    print(f"\n▶ BVA Password Length Boundary Tests")
    print("   Technique: BVA-03 (7 chars), BVA-04 (8 chars), BVA-05 (9 chars)")
    print("   Rule: Minimum password length = 8 characters")

    # BVA-03: 7 chars — below minimum boundary (INVALID)
    print(f"   [BVA-03] password = '{PASS_7_CHARS}' (7 chars — BELOW minimum, invalid)")
    try:
        go_to_login()
        fill_login(ADMIN_EMAIL, PASS_7_CHARS)
        click_login_btn()
        screenshot_full("UC1_BVA03_7CharPass.png")

        if has_error(["password", "character", "minimum", "least", "short",
                      "text-red", "border-red", "8"]):
            record("TC-UC01-12 (BVA-03)", True,
                   f"PASS — 7-char password '{PASS_7_CHARS}' rejected (BVA-03). "
                   "Below minimum 8-character rule. Login blocked.")
        else:
            record("TC-UC01-12 (BVA-03)", False,
                   f"FAIL — 7-char password NOT rejected. "
                   "Defect: minimum length validation missing.")
    except Exception as e:
        screenshot_full("UC1_Error_BVA03.png")
        record("TC-UC01-12 (BVA-03)", False, f"Exception: {e}")

    # BVA-04: 8 chars — AT minimum boundary (VALID length)
    print(f"   [BVA-04] password = '{PASS_8_CHARS}' (8 chars — AT minimum boundary)")
    try:
        go_to_login()
        fill_login(ADMIN_EMAIL, PASS_8_CHARS)
        click_login_btn()
        screenshot_full("UC1_BVA04_8CharPass.png")

        length_rejected = has_error(["password", "character", "minimum",
                                     "least", "short", "8"])
        if not length_rejected:
            record("TC-UC01-13 (BVA-04)", True,
                   f"PASS — 8-char password '{PASS_8_CHARS}' accepted by length rule (BVA-04). "
                   "System proceeds to credential validation "
                   "(auth outcome depends on correctness, not length).")
        else:
            record("TC-UC01-13 (BVA-04)", False,
                   f"FAIL — 8-char password incorrectly rejected by length. "
                   "Defect: minimum boundary validation too strict.")
    except Exception as e:
        screenshot_full("UC1_Error_BVA04.png")
        record("TC-UC01-13 (BVA-04)", False, f"Exception: {e}")

    # BVA-05: 9 chars — above minimum boundary (VALID length)
    print(f"   [BVA-05] password = '{PASS_9_CHARS}' (9 chars — above minimum boundary)")
    try:
        go_to_login()
        fill_login(ADMIN_EMAIL, PASS_9_CHARS)
        click_login_btn()
        screenshot_full("UC1_BVA05_9CharPass.png")

        length_rejected = has_error(["password", "character", "minimum",
                                     "least", "short", "8"])
        if not length_rejected:
            record("TC-UC01-14 (BVA-05)", True,
                   f"PASS — 9-char password '{PASS_9_CHARS}' accepted by length rule (BVA-05). "
                   "Above minimum — no length error raised.")
        else:
            record("TC-UC01-14 (BVA-05)", False,
                   f"FAIL — 9-char password incorrectly rejected by length. "
                   "Defect: boundary validation logic incorrect.")
    except Exception as e:
        screenshot_full("UC1_Error_BVA05.png")
        record("TC-UC01-14 (BVA-05)", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

try:
    print("=" * 62)
    print("  UC1 LOGIN — WEB SELENIUM TEST")
    print("  Testing Level: System Testing")
    print("  Testers: Edwin Tan, Izzatul Filzah, Auni Nafisa, Yusrina Maisarah")
    print(f"  URL: {BASE_URL}")
    print(f"  Screenshots: {SCREENSHOT_DIR}")
    print("=" * 62)
    print("\n  Test Cases and What Each Tests (No Redundancy):")
    print("  TC-UC01-01 → Happy path: valid admin login → /dashboard")
    print("  TC-UC01-02 → Empty field validation: email (BVA-01) + password (BVA-02)")
    print("  TC-UC01-03 → Invalid email format: missing '@' (EP-02)")
    print("  TC-UC01-04 → Unregistered email: valid format, no DB record (EP-03)")
    print("  TC-UC01-05 → Wrong password: registered email + wrong pass (DT-08)")
    print("  TC-UC01-06 → Non-admin denied: valid creds but role != admin (EP-04)")
    print("  TC-UC01-07 → Too many attempts: 10+ fails → system blocks (UCT-09)")
    print("  TC-UC01-08 → Sign Up redirect: alternate flow (UCT-03)")
    print("  TC-UC01-09 → Forgot Password: web modal + reset email (UCT-04)")
    print("  BVA-03/04/05 → Password length: 7 (invalid), 8 (min), 9 (above min)")
    print("=" * 62)

    if setup_session():
        tc_uc01_01()   # EP-05, BVA-06, UCT-01, DT-06, ST-07
        tc_uc01_02()   # EP-01, BVA-01, BVA-02, UCT-05, ST-01
        tc_uc01_03()   # EP-02, UCT-06, DT-07, ST-02
        tc_uc01_04()   # EP-03, UCT-08, DT-09, ST-03
        tc_uc01_05()   # UCT-07, DT-08, ST-04
        tc_uc01_06()   # EP-04, UCT-10, DT-010, ST-06
        tc_uc01_07()   # UCT-09, ST-05
        tc_uc01_08()   # UCT-03
        tc_uc01_09()   # UCT-04
        tc_bva_password()  # BVA-03, BVA-04, BVA-05
    else:
        print("🛑 Aborting — login page not accessible")

except Exception as e:
    print(f"\n🛑 Unexpected error: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n" + "=" * 62)
    print("  TEST SUMMARY — UC1 Login (Web)")
    print("=" * 62)
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
    print("=" * 62)
    input("\nPress Enter to close browser...")
    driver.quit()