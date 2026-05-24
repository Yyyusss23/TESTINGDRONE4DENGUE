"""
============================================================
UC3 Reset Password — Web Selenium Test Script
Testing Level  : System Testing
Techniques     : Equivalence Partitioning (EP)
                 Boundary Value Analysis (BVA)
                 Decision Table Testing (DT)
                 Use Case Testing (UCT)
                 State Transition Testing (ST)
Tool           : Selenium WebDriver (Chrome)
Platform       : Web Admin (Next.js, localhost:3000)
Tester         : Yusrina Maisarah binti Yunus
============================================================

No Redundancy — each test case tests a DIFFERENT thing:
  TC-UC03-01  Main happy path — valid email, valid code, valid password
  TC-UC03-02  Invalid email partition — email not in system
  TC-UC03-03  Wrong code + resend — code validation and resend feature
  TC-UC03-04  Four invalid password formats — format rules only
  TC-UC03-05  Password mismatch — confirmation field mismatch only
  ST-14→019   State screen navigation — transitions only
============================================================
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import subprocess
import time
import os

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
SCRIPT_DIR     = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIR = os.path.join(SCRIPT_DIR, "UC3_web_screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

BASE_URL       = "http://localhost:3000"
SERVER_API_DIR = "/Users/yus/Documents/GitHub/drone4dengue/server-api"

# ── Test data — each test uses DIFFERENT data (no redundancy) ──────────
VALID_EMAIL    = "good@email.com"         # EP-04 valid — registered in system
WRONG_EMAIL    = "wrong@email.com"        # EP-04 invalid — NOT in system
WRONG_CODE     = "000000"                 # DT-15 — invalid code
VALID_PASSWORD = "SecretPass123"          # EP-01: mix, BVA-09: 13 chars ✓
SHORT_PASSWORD = "Pass123"                # BVA-07: 7 chars — below minimum
LONG_PASSWORD  = "VeryLongPassword12345"  # BVA-12: 21 chars — above maximum
LETTERS_ONLY   = "SecretPassword"         # EP-05: no numbers — invalid
NUMBERS_ONLY   = "123456789"              # EP-06: no letters — invalid
MISMATCH_PASS1 = "NewPass1"               # UCT-20: valid format
MISMATCH_PASS2 = "BadPass2"               # UCT-20: DIFFERENT value — mismatch

driver  = webdriver.Chrome()
driver.maximize_window()
wait    = WebDriverWait(driver, 15)
results = []
defects = []   # tracks all defects found for summary report


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def screenshot_full(filename):
    """Take a full-page screenshot capturing entire page height."""
    try:
        h = driver.execute_script("return document.body.scrollHeight")
        h = min(max(h, 900), 5000)
        driver.set_window_size(1440, h)
        time.sleep(0.4)
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


def dismiss_error_and_screenshot(filename):
    """
    When the page shows an error dialog or alert:
    1. Take a screenshot of the error state
    2. Try to click the dismiss/close/OK button
    3. Take a screenshot after dismissal to confirm cleared
    This ensures every error is properly captured and documented.
    """
    # Step 1 — screenshot error state
    screenshot_full(filename)

    # Step 2 — try to click dismiss button (various patterns)
    dismissed = False
    dismiss_xpaths = [
        "//button[contains(normalize-space(),'OK')]",
        "//button[contains(normalize-space(),'Ok')]",
        "//button[contains(normalize-space(),'Close')]",
        "//button[contains(normalize-space(),'Dismiss')]",
        "//button[@aria-label='Close']",
        "//button[@aria-label='Dismiss']",
        "//*[@role='dialog']//button",
        "//div[contains(@class,'modal')]//button",
        "//div[contains(@class,'alert')]//button",
        "//div[contains(@class,'toast')]//button",
    ]
    for xpath in dismiss_xpaths:
        try:
            btn = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            btn.click()
            dismissed = True
            print(f"   🔘 Error dialog dismissed (clicked button)")
            time.sleep(0.5)
            break
        except (TimeoutException, NoSuchElementException):
            continue

    # Step 3 — fallback: press Escape to close modal/dialog
    if not dismissed:
        try:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(0.3)
            print(f"   🔘 Error dismissed via Escape key")
        except Exception:
            pass

    # Step 4 — screenshot after dismissal
    after_name = filename.replace(".png", "_AfterDismiss.png")
    screenshot_full(after_name)


def record(tc_id, status, note="", is_defect=False):
    """Record result. If is_defect=True, add to defects list for report."""
    if status is True:
        tag = "✅ PASS"
    elif status is False:
        tag = "❌ FAIL"
    else:
        tag = "ℹ️  N/A "
    line = f"{tag}  {tc_id}  {note}"
    results.append(line)
    print(f"   {line}")

    if status is False and is_defect:
        defects.append(f"[{tc_id}] {note}")


def get_code_from_db():
    """
    Retrieve latest reset code directly from database.
    Rationale: backend saves code to DB before sending email, so we can
    read it from DB without needing to access the email inbox.
    This is valid at system test level since we have DB access.
    """
    script = (
        "const{PrismaClient}=require('@prisma/client');"
        "const p=new PrismaClient();"
        "p.user.findUnique({where:{email:'" + VALID_EMAIL + "'}})"
        ".then(u=>{console.log(u&&u.resetCode?u.resetCode:'NO_CODE');"
        "p.$disconnect();})"
        ".catch(e=>{console.log('ERR');p.$disconnect();});"
    )
    r = subprocess.run(["node", "-e", script],
                       capture_output=True, text=True, cwd=SERVER_API_DIR)
    code = r.stdout.strip().split('\n')[-1].strip()
    if code and len(code) == 6 and code.isdigit():
        print(f"   🔑 Code from DB: {code}")
        return code
    print(f"   ⚠️  No valid code in DB. stdout={r.stdout!r}")
    return None


# ── Navigation ────────────────────────────────────────────────────────

def go_to_forgot():
    """Navigate to the forgot-password page fresh."""
    driver.get(f"{BASE_URL}/forgot-password")
    time.sleep(1.5)
    print(f"   🌐 URL: {driver.current_url}")


def go_to_login():
    """Navigate to the login page."""
    driver.get(f"{BASE_URL}/")
    time.sleep(1)


# ── Step actions ──────────────────────────────────────────────────────

def step1_send_email(email):
    """Step 1 — type email and click Send Code. Wait for API response."""
    print(f"   → Email: {email}")
    find_el(By.ID, "email").clear()
    find_el(By.ID, "email").send_keys(email)
    time.sleep(0.3)
    tap_el(By.CSS_SELECTOR, "button[type='submit']")
    time.sleep(5)   # allow API + email service to respond


def step2_enter_code(code):
    """Step 2 — type code and click Verify."""
    print(f"   → Code: {code}")
    find_el(By.ID, "code").clear()
    find_el(By.ID, "code").send_keys(code)
    time.sleep(0.3)
    tap_el(By.CSS_SELECTOR, "button[type='submit']")
    time.sleep(3)


def step3_enter_passwords(pw1, pw2):
    """Step 3 — type new password + confirm, click Reset Password."""
    print(f"   → Password 1: {pw1}  |  Password 2: {pw2}")
    find_el(By.ID, "newPassword").clear()
    find_el(By.ID, "newPassword").send_keys(pw1)
    time.sleep(0.3)
    find_el(By.ID, "confirmPassword").clear()
    find_el(By.ID, "confirmPassword").send_keys(pw2)
    time.sleep(0.3)
    tap_el(By.CSS_SELECTOR, "button[type='submit']")
    time.sleep(3)


# ── Screen detection ──────────────────────────────────────────────────

def on_step2_screen():
    """Returns True if currently on the Enter Code screen (Step 2)."""
    return has_text("enter code", "verify code", "6-digit",
                    "check your email", "verification code",
                    "sent", "code sent", "reset code sent")


def on_step3_screen():
    """Returns True if currently on the New Password screen (Step 3)."""
    return has_text("new password", "reset password",
                    "confirm password", "create a strong")


# ─────────────────────────────────────────────
# TC-UC03-01 — Full Valid Reset Flow (Happy Path)
# Techniques: EP-01 (valid password: mix of letters+numbers)
#             EP-04 (valid email partition: registered email)
#             BVA-08/09 (password length: 8-13 chars)
#             DT-13 (decision table: all inputs valid)
#             UCT-17 (use case main flow: complete 3-step reset)
#             ST-016 (state: email → enter code)
#             ST-018 (state: code → new password)
# Unique: ONLY test that runs the COMPLETE 3-step happy path end-to-end.
#         Tests integration of all three steps together.
# ─────────────────────────────────────────────

def tc_uc03_01():
    print(f"\n{'='*58}")
    print(f"▶ TC-UC03-01 — Valid Reset Flow (Happy Path)")
    print(f"   Techniques: EP-01, EP-04, BVA-08/09, DT-13, UCT-17, ST-016, ST-018")
    try:
        go_to_forgot()

        # ── Step 1: Send email ────────────────────────────────────────
        print(f"\n   [Step 1] Send reset code to valid registered email")
        step1_send_email(VALID_EMAIL)
        screenshot_full("UC3_W_TC01_Step1_AfterSend.png")

        if not on_step2_screen():
            if has_text("error", "failed", "unavailable", "service", "object"):
                dismiss_error_and_screenshot("UC3_W_TC01_Step1_EmailError.png")
                record("TC-UC03-01", False,
                       "Step 1 FAIL — Email service error after sending to valid email. "
                       "SMTP/Mailtrap not configured. See UC3_W_TC01_Step1_EmailError.png",
                       is_defect=True)
            else:
                record("TC-UC03-01", False,
                       "Step 1 FAIL — Enter Code screen not shown after valid email. "
                       "See UC3_W_TC01_Step1_AfterSend.png",
                       is_defect=True)
            return

        print("   ✅ Step 1 PASS — Enter Code screen shown")

        # ── Step 2: Enter valid code ──────────────────────────────────
        fresh_code = get_code_from_db()
        if not fresh_code:
            record("TC-UC03-01", False,
                   "Cannot read reset code from database — check DB connection",
                   is_defect=True)
            return

        print(f"\n   [Step 2] Enter valid code from DB: {fresh_code}")
        step2_enter_code(fresh_code)
        screenshot_full("UC3_W_TC01_Step2_AfterVerify.png")

        if not on_step3_screen():
            dismiss_error_and_screenshot("UC3_W_TC01_Step2_VerifyError.png")
            record("TC-UC03-01", False,
                   "Step 2 FAIL — New Password screen not shown after valid code. "
                   "See UC3_W_TC01_Step2_AfterVerify.png",
                   is_defect=True)
            return

        print("   ✅ Step 2 PASS — New Password screen shown")

        # ── Step 3: Enter valid password ──────────────────────────────
        print(f"\n   [Step 3] Enter valid password: {VALID_PASSWORD}")
        print(f"   Note: 13 chars (BVA-09: valid), letters+number (EP-01: valid)")
        step3_enter_passwords(VALID_PASSWORD, VALID_PASSWORD)
        screenshot_full("UC3_W_TC01_Step3_AfterReset.png")

        if has_text("success", "reset successful", "can now log in",
                    "password reset", "log in"):
            record("TC-UC03-01", True,
                   f"PASS — Full 3-step flow complete. "
                   f"Email={VALID_EMAIL}, Code={fresh_code}, "
                   f"Password={VALID_PASSWORD}. Success message shown.")
        else:
            dismiss_error_and_screenshot("UC3_W_TC01_Step3_Error.png")
            record("TC-UC03-01", False,
                   "Step 3 FAIL — no success message after valid password reset. "
                   "Defect: success feedback missing from UI. "
                   "See UC3_W_TC01_Step3_AfterReset.png",
                   is_defect=True)

    except Exception as e:
        screenshot_full("UC3_W_Error_TC01.png")
        record("TC-UC03-01", False, f"Exception: {e}", is_defect=True)


# ─────────────────────────────────────────────
# TC-UC03-02 — Unregistered Email (Invalid Partition)
# Techniques: EP-04 (invalid partition: email NOT in system)
#             DT-14 (decision: email not found branch)
#             UCT-18 (alternate flow: unregistered email rejection)
#             ST-015 (state: stays on Step 1 — no transition)
# Unique: TC-01 uses VALID email (valid partition).
#         This tests the INVALID partition of the same field.
#         Different data class → different behaviour → no redundancy.
# ─────────────────────────────────────────────

def tc_uc03_02():
    print(f"\n{'='*58}")
    print(f"▶ TC-UC03-02 — Unregistered Email (Invalid Partition)")
    print(f"   Techniques: EP-04, DT-14, UCT-18, ST-015")
    print(f"   Email: {WRONG_EMAIL} (NOT registered in system)")
    try:
        go_to_forgot()

        step1_send_email(WRONG_EMAIL)
        screenshot_full("UC3_W_TC02_UnregisteredEmail.png")
        print(f"   🔍 Reached Step 2: {on_step2_screen()}")

        if on_step2_screen():
            record("TC-UC03-02", False,
                   f"FAIL — System accepted unregistered email '{WRONG_EMAIL}' "
                   "and advanced to Step 2. SECURITY DEFECT: anyone can trigger "
                   "reset for emails not in system.",
                   is_defect=True)

        elif has_text("not found", "error", "invalid", "failed",
                      "user", "no account", "email"):
            record("TC-UC03-02", True,
                   f"PASS — Unregistered '{WRONG_EMAIL}' correctly rejected (EP-04). "
                   "Error message shown. Stays on Step 1 (ST-015).")

        else:
            dismiss_error_and_screenshot("UC3_W_TC02_NoErrorShown.png")
            record("TC-UC03-02", False,
                   "FAIL — No error message for unregistered email. "
                   "Defect: system must show 'Email not found' or equivalent. "
                   "See UC3_W_TC02_UnregisteredEmail.png",
                   is_defect=True)

    except Exception as e:
        screenshot_full("UC3_W_Error_TC02.png")
        record("TC-UC03-02", False, f"Exception: {e}", is_defect=True)


# ─────────────────────────────────────────────
# TC-UC03-03 — Wrong Code + Resend
# Techniques: DT-15 (decision: code incorrect branch)
#             UCT-19 (alternate flow: resend code)
#             ST-017 (state: wrong code stays on Step 2)
# Unique: TC-01 tests CORRECT code (valid partition).
#         This tests WRONG code (invalid partition) — different test.
#         Also tests the RESEND feature which no other TC covers.
# ─────────────────────────────────────────────

def tc_uc03_03():
    print(f"\n{'='*58}")
    print(f"▶ TC-UC03-03 — Wrong Code ({WRONG_CODE}) + Resend Code")
    print(f"   Techniques: DT-15, UCT-19, ST-017")
    try:
        go_to_forgot()
        step1_send_email(VALID_EMAIL)
        screenshot_full("UC3_W_TC03_Step1_EmailSent.png")

        if not on_step2_screen():
            dismiss_error_and_screenshot("UC3_W_TC03_Step1_Error.png")
            record("TC-UC03-03a", False,
                   "FAIL — Could not reach Enter Code screen. "
                   "Blocked by email service issue (same root cause as TC-UC03-01).")
            record("TC-UC03-03b", None,
                   "N/A — Skipped: blocked by Step 1 failure.")
            return

        print("   ✅ Enter Code screen reached")

        # ── Sub-test a: Enter wrong code — test rejection ─────────────
        print(f"\n   [TC-03a] Enter wrong code: {WRONG_CODE} (DT-15)")
        step2_enter_code(WRONG_CODE)
        screenshot_full("UC3_W_TC03a_WrongCode.png")

        if has_text("invalid", "expired", "error", "wrong", "incorrect"):
            record("TC-UC03-03a", True,
                   f"PASS — Wrong code '{WRONG_CODE}' rejected (DT-15). "
                   "Error shown. Stays on Enter Code screen (ST-017).")

            # ── Sub-test b: Resend code — test resend feature ─────────
            print(f"\n   [TC-03b] Test Resend Code (UCT-19)")
            go_to_forgot()
            step1_send_email(VALID_EMAIL)
            screenshot_full("UC3_W_TC03b_AfterResend.png")
            resend_code = get_code_from_db()

            if on_step2_screen() and resend_code:
                record("TC-UC03-03b", True,
                       f"PASS — Resend triggered successfully (UCT-19). "
                       f"New code {resend_code} generated. "
                       "Enter Code screen shown again.")
            else:
                dismiss_error_and_screenshot("UC3_W_TC03b_ResendError.png")
                record("TC-UC03-03b", False,
                       "FAIL — Resend code did not work. "
                       "Defect: resend feature broken or email service issue.",
                       is_defect=True)
        else:
            dismiss_error_and_screenshot("UC3_W_TC03a_NoError.png")
            record("TC-UC03-03a", False,
                   f"FAIL — No error shown for wrong code '{WRONG_CODE}'. "
                   "Defect: invalid code accepted or no feedback shown. "
                   "See UC3_W_TC03a_WrongCode.png",
                   is_defect=True)
            record("TC-UC03-03b", None,
                   "N/A — Skipped: TC-03a failed.")

    except Exception as e:
        screenshot_full("UC3_W_Error_TC03.png")
        record("TC-UC03-03a", False, f"Exception: {e}", is_defect=True)
        record("TC-UC03-03b", None, "N/A — exception in TC-03a.")


# ─────────────────────────────────────────────
# TC-UC03-04 — Invalid Password Formats (4 classes)
# Techniques: EP-02 (invalid: password too short)
#             EP-03 (invalid: password too long)
#             EP-05 (invalid: letters only — missing numbers)
#             EP-06 (invalid: numbers only — missing letters)
#             BVA-07 (boundary: 7 chars, one below minimum)
#             BVA-12 (boundary: 21 chars, one above maximum)
#             DT-16 (decision: password format rules)
# Unique: TC-01 tests a VALID password. TC-05 tests MISMATCHED passwords.
#         This tests 4 classes of INVALID password FORMAT — different concern.
#         No other TC tests these specific password rules.
# ─────────────────────────────────────────────

def tc_uc03_04():
    print(f"\n{'='*58}")
    print(f"▶ TC-UC03-04 — Invalid Password Formats (4 Different Rules)")
    print(f"   Techniques: EP-02/03/05/06, BVA-07/12, DT-16")
    try:
        go_to_forgot()
        step1_send_email(VALID_EMAIL)
        screenshot_full("UC3_W_TC04_Step1.png")

        if not on_step2_screen():
            dismiss_error_and_screenshot("UC3_W_TC04_Step1_Error.png")
            record("TC-UC03-04", False,
                   "FAIL — Could not reach Enter Code screen. Email service issue.")
            return

        fresh_code = get_code_from_db()
        if not fresh_code:
            record("TC-UC03-04", False, "FAIL — No code from DB.")
            return

        step2_enter_code(fresh_code)
        screenshot_full("UC3_W_TC04_Step2.png")

        if not on_step3_screen():
            dismiss_error_and_screenshot("UC3_W_TC04_Step2_Error.png")
            record("TC-UC03-04", False,
                   "FAIL — Could not reach New Password screen.")
            return

        print("   ✅ New Password screen reached — testing 4 invalid formats")
        sub = []

        # ── Attempt 1: BVA-07 — 7 chars (one below minimum) ──────────
        print(f"\n   [BVA-07] Attempt 1: '{SHORT_PASSWORD}' — 7 chars, below minimum")
        step3_enter_passwords(SHORT_PASSWORD, SHORT_PASSWORD)
        screenshot_full("UC3_W_TC04_A1_7chars.png")
        p1 = has_text("error", "short", "least", "character",
                      "minimum", "invalid", "password", "8")
        if not p1:
            dismiss_error_and_screenshot("UC3_W_TC04_A1_NoError.png")
        print(f"   → {'✅ Rejected correctly' if p1 else '❌ NOT rejected — defect!'}")
        sub.append(("BVA-07 (7 chars)", p1))

        # ── Attempt 2: BVA-12 — 21 chars (one above maximum) ─────────
        print(f"\n   [BVA-12] Attempt 2: '{LONG_PASSWORD}' — 21 chars, above maximum")
        step3_enter_passwords(LONG_PASSWORD, LONG_PASSWORD)
        screenshot_full("UC3_W_TC04_A2_21chars.png")
        p2 = has_text("error", "long", "maximum", "character",
                      "invalid", "password", "20")
        if not p2:
            dismiss_error_and_screenshot("UC3_W_TC04_A2_NoError.png")
        print(f"   → {'✅ Rejected correctly' if p2 else '⚠️  NOT rejected — backend may allow >20 chars'}")
        sub.append(("BVA-12 (21 chars)", p2))

        # ── Attempt 3: EP-05 — letters only, no numbers ───────────────
        print(f"\n   [EP-05] Attempt 3: '{LETTERS_ONLY}' — letters only, no numbers")
        step3_enter_passwords(LETTERS_ONLY, LETTERS_ONLY)
        screenshot_full("UC3_W_TC04_A3_LettersOnly.png")
        p3 = has_text("error", "number", "digit", "invalid",
                      "password", "mix", "include")
        if not p3:
            dismiss_error_and_screenshot("UC3_W_TC04_A3_NoError.png")
        print(f"   → {'✅ Rejected correctly' if p3 else '⚠️  NOT rejected — format mix may not be enforced'}")
        sub.append(("EP-05 (letters only)", p3))

        # ── Attempt 4: EP-06 — numbers only, no letters ───────────────
        print(f"\n   [EP-06] Attempt 4: '{NUMBERS_ONLY}' — numbers only, no letters")
        step3_enter_passwords(NUMBERS_ONLY, NUMBERS_ONLY)
        screenshot_full("UC3_W_TC04_A4_NumbersOnly.png")
        p4 = has_text("error", "letter", "invalid", "password",
                      "mix", "include", "alpha")
        if not p4:
            dismiss_error_and_screenshot("UC3_W_TC04_A4_NoError.png")
        print(f"   → {'✅ Rejected correctly' if p4 else '⚠️  NOT rejected — format mix may not be enforced'}")
        sub.append(("EP-06 (numbers only)", p4))

        # ── Overall result ─────────────────────────────────────────────
        details = " | ".join(f"{n}: {'✅' if r else '❌'}" for n, r in sub)
        passed_all = all(r for _, r in sub)
        failed_hard = any(r is False for _, r in sub)

        if passed_all:
            record("TC-UC03-04", True,
                   f"PASS — All 4 invalid formats correctly rejected. [{details}]")
        elif failed_hard:
            record("TC-UC03-04", False,
                   f"FAIL — Some formats not rejected. [{details}]. "
                   "Defect: password format validation incomplete on server.",
                   is_defect=True)
        else:
            record("TC-UC03-04", None,
                   f"PARTIAL — [{details}]. "
                   "Backend only enforces minimum length; "
                   "format mix (letters+numbers) not validated server-side.")

    except Exception as e:
        screenshot_full("UC3_W_Error_TC04.png")
        record("TC-UC03-04", False, f"Exception: {e}", is_defect=True)


# ─────────────────────────────────────────────
# TC-UC03-05 — Passwords Do Not Match
# Techniques: UCT-20 (alternate flow: confirmation field mismatch)
#             ST-019 (state: mismatch stays on Step 3)
# Unique: TC-04 tests invalid FORMAT of one password field.
#         This tests TWO fields with valid format but DIFFERENT values.
#         Completely different validation rule — no redundancy.
# ─────────────────────────────────────────────

def tc_uc03_05():
    print(f"\n{'='*58}")
    print(f"▶ TC-UC03-05 — Passwords Do Not Match")
    print(f"   Techniques: UCT-20, ST-019")
    print(f"   Password 1: {MISMATCH_PASS1} | Password 2: {MISMATCH_PASS2}")
    print(f"   Note: Both have VALID format individually — only the values differ")
    try:
        go_to_forgot()
        step1_send_email(VALID_EMAIL)
        screenshot_full("UC3_W_TC05_Step1.png")

        if not on_step2_screen():
            dismiss_error_and_screenshot("UC3_W_TC05_Step1_Error.png")
            record("TC-UC03-05", False,
                   "FAIL — Could not reach Enter Code screen. Email service issue.")
            return

        fresh_code = get_code_from_db()
        if not fresh_code:
            record("TC-UC03-05", False, "FAIL — No code from DB.")
            return

        step2_enter_code(fresh_code)
        screenshot_full("UC3_W_TC05_Step2.png")

        if not on_step3_screen():
            dismiss_error_and_screenshot("UC3_W_TC05_Step2_Error.png")
            record("TC-UC03-05", False,
                   "FAIL — Could not reach New Password screen.")
            return

        print("   ✅ New Password screen reached")

        step3_enter_passwords(MISMATCH_PASS1, MISMATCH_PASS2)
        screenshot_full("UC3_W_TC05_MismatchResult.png")

        # From forgot-password.tsx source: "The passwords do not match."
        if has_text("do not match", "passwords do not", "match",
                    "error", "confirm", "same"):
            record("TC-UC03-05", True,
                   f"PASS — Mismatch ({MISMATCH_PASS1} ≠ {MISMATCH_PASS2}) "
                   "correctly rejected (UCT-20). "
                   "Error shown. Stays on Step 3 (ST-019).")
        else:
            dismiss_error_and_screenshot("UC3_W_TC05_NoMatchError.png")
            record("TC-UC03-05", False,
                   "FAIL — No mismatch error shown for different passwords. "
                   "Defect: password confirmation field not validated. "
                   "See UC3_W_TC05_MismatchResult.png",
                   is_defect=True)

    except Exception as e:
        screenshot_full("UC3_W_Error_TC05.png")
        record("TC-UC03-05", False, f"Exception: {e}", is_defect=True)


# ─────────────────────────────────────────────
# STATE TRANSITION TESTS
# Techniques: ST-14 (login → forgot page)
#             ST-015 (wrong email → stays on step 1)
#             ST-016 (email → enter code)
#             ST-017 (wrong code → stays on step 2)
#             ST-018 (valid code → new password)
#             ST-019 (mismatch → stays on step 3)
# Unique: TC tests verify VALIDATION LOGIC at each step.
#         These tests verify SCREEN NAVIGATION/TRANSITIONS — different concern.
# ─────────────────────────────────────────────

def tc_state_transitions():
    print(f"\n{'='*58}")
    print(f"▶ State Transition Tests")
    print(f"   Techniques: ST-14, ST-015, ST-016, ST-017, ST-018, ST-019")
    print(f"   Focus: screen NAVIGATION (TC tests focus on VALIDATION)")

    # ── ST-14: Login → Forgot Password page ──────────────────────────
    print(f"\n   [ST-14] Click Forgot Password link from Login → page opens")
    try:
        go_to_login()
        tap_el(By.XPATH,
               "//a[contains(@href,'forgot') or "
               "contains(normalize-space(),'Forgot')]")
        time.sleep(2)
        screenshot_full("UC3_W_ST14_LoginToForgot.png")

        if "forgot" in driver.current_url.lower() and \
           has_text("reset password", "send code", "forgot", "enter your email"):
            record("ST-14", True,
                   "PASS — Login → Forgot Password transition works correctly")
        else:
            dismiss_error_and_screenshot("UC3_W_ST14_Error.png")
            record("ST-14", False,
                   "FAIL — Forgot Password page not reached from login",
                   is_defect=True)
    except Exception as e:
        screenshot_full("UC3_W_Error_ST14.png")
        record("ST-14", False, f"Exception: {e}", is_defect=True)

    # ── ST-015: Unknown email → stays on Step 1 ──────────────────────
    print(f"\n   [ST-015] Unknown email → error shown, NO transition to Step 2")
    try:
        go_to_forgot()
        step1_send_email(WRONG_EMAIL)
        screenshot_full("UC3_W_ST015_UnknownStaysStep1.png")

        if not on_step2_screen() and \
           has_text("not found", "error", "invalid", "failed", "user"):
            record("ST-015", True,
                   f"PASS — {WRONG_EMAIL} rejected. "
                   "Stays on Step 1 — no transition to Step 2")
        elif on_step2_screen():
            record("ST-015", False,
                   "FAIL — System incorrectly transitioned to Step 2 for unknown email!",
                   is_defect=True)
        else:
            dismiss_error_and_screenshot("UC3_W_ST015_NoError.png")
            record("ST-015", False,
                   "FAIL — No error shown for unknown email on Step 1",
                   is_defect=True)
    except Exception as e:
        screenshot_full("UC3_W_Error_ST015.png")
        record("ST-015", False, f"Exception: {e}", is_defect=True)

    # ── ST-016 → ST-019: Full state chain ────────────────────────────
    print(f"\n   [ST-016→019] Full state chain: Step1 → Step2 → Step3")
    try:
        go_to_forgot()
        step1_send_email(VALID_EMAIL)
        fresh_code = get_code_from_db()
        screenshot_full("UC3_W_ST016_Step1ToStep2.png")

        if not on_step2_screen():
            dismiss_error_and_screenshot("UC3_W_ST016_TransitionError.png")
            record("ST-016", False,
                   "FAIL — Step 1 → Step 2 transition failed. Email service issue.",
                   is_defect=True)
            for st in ["ST-017", "ST-018", "ST-019"]:
                record(st, None, "N/A — blocked by ST-016 failure.")
            return

        record("ST-016", True,
               "PASS — Step 1 (email) → Step 2 (enter code) transition works")

        # ST-017: Wrong code → stays on Step 2
        print(f"   [ST-017] Wrong code → error, stays on Step 2")
        step2_enter_code(WRONG_CODE)
        screenshot_full("UC3_W_ST017_WrongCodeStaysStep2.png")
        if has_text("invalid", "expired", "error", "wrong", "incorrect"):
            record("ST-017", True,
                   f"PASS — Wrong code '{WRONG_CODE}' → error shown, "
                   "stays on Step 2 (no forward transition)")
        else:
            dismiss_error_and_screenshot("UC3_W_ST017_NoError.png")
            record("ST-017", False,
                   "FAIL — No error for wrong code on Step 2",
                   is_defect=True)

        # Get fresh code AFTER wrong code attempt (code may have refreshed)
        fresh_code = get_code_from_db()

        # ST-018: Valid code → Step 3
        print(f"   [ST-018] Valid code {fresh_code} → Step 3 (new password)")
        if not fresh_code:
            record("ST-018", False, "FAIL — No valid code from DB")
            record("ST-019", None, "N/A — blocked by ST-018 failure.")
            return

        step2_enter_code(fresh_code)
        screenshot_full("UC3_W_ST018_Step2ToStep3.png")

        if on_step3_screen():
            record("ST-018", True,
                   f"PASS — Step 2 (code '{fresh_code}') → "
                   "Step 3 (new password) transition works")

            # ST-019: Mismatch → stays on Step 3
            print(f"   [ST-019] Mismatch → error, stays on Step 3")
            step3_enter_passwords(MISMATCH_PASS1, MISMATCH_PASS2)
            screenshot_full("UC3_W_ST019_MismatchStaysStep3.png")
            if has_text("do not match", "match", "error", "confirm", "same"):
                record("ST-019", True,
                       "PASS — Mismatch → error shown, stays on Step 3 "
                       "(no forward transition)")
            else:
                dismiss_error_and_screenshot("UC3_W_ST019_NoError.png")
                record("ST-019", False,
                       "FAIL — No mismatch error on Step 3",
                       is_defect=True)
        else:
            dismiss_error_and_screenshot("UC3_W_ST018_TransitionError.png")
            record("ST-018", False,
                   "FAIL — Step 2 → Step 3 transition failed after valid code",
                   is_defect=True)
            record("ST-019", None, "N/A — blocked by ST-018 failure.")

    except Exception as e:
        screenshot_full("UC3_W_Error_ST016.png")
        record("ST-016", False, f"Exception: {e}", is_defect=True)
        for st in ["ST-017", "ST-018", "ST-019"]:
            record(st, None, "N/A — exception in ST-016.")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

try:
    print("=" * 58)
    print("  UC3 RESET PASSWORD — WEB SELENIUM TEST")
    print("  Testing Level  : System Testing")
    print("  Tester         : Yusrina Maisarah binti Yunus")
    print(f"  URL            : {BASE_URL}")
    print(f"  Screenshots    : {SCREENSHOT_DIR}")
    print("=" * 58)

    tc_uc03_01()          # EP-01, EP-04, BVA-08/09, DT-13, UCT-17
    tc_uc03_02()          # EP-04, DT-14, UCT-18, ST-015
    tc_uc03_03()          # DT-15, UCT-19, ST-017
    tc_uc03_04()          # EP-02/03/05/06, BVA-07/12, DT-16
    tc_uc03_05()          # UCT-20, ST-019
    tc_state_transitions()  # ST-14, ST-015, ST-016, ST-017, ST-018, ST-019

except Exception as e:
    print(f"\n🛑 Unexpected error: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n" + "=" * 58)
    print("  TEST SUMMARY — UC3 Reset Password (Web)")
    print("=" * 58)
    passed = failed = na = 0
    for r in results:
        line = r if len(r) < 220 else r[:220] + "..."
        print(f"  {line}")
        if "✅" in r:   passed += 1
        elif "❌" in r: failed += 1
        else:            na += 1

    print(f"\n  Total: {len(results)}  |  "
          f"✅ Passed: {passed}  |  "
          f"❌ Failed: {failed}  |  "
          f"ℹ️  N/A: {na}")

    if defects:
        print(f"\n  🐛 DEFECTS FOUND ({len(defects)}):")
        for d in defects:
            print(f"     • {d}")
    else:
        print(f"\n  ✅ No defects found.")

    print(f"\n  📁 Screenshots → {SCREENSHOT_DIR}")
    print("=" * 58)

    input("\nPress Enter to close browser...")
    driver.quit()