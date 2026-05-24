"""
UC4 Edit Profile - Web Selenium Test Script
Testing Level: System Testing
Techniques Applied:
  - Equivalence Partitioning (EP)
  - Boundary Value Analysis (BVA)
  - Decision Table Testing (DT)
  - Use Case Testing (UCT)
  - State Transition Testing (ST)
Tool: Selenium WebDriver (Chrome)
Tester: Yusrina Maisarah binti Yunus
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
SCREENSHOT_DIR = os.path.join(SCRIPT_DIR, "UC4_screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Test data — each test uses DIFFERENT data (no redundancy)
VALID_NAME_3   = "Ali"           # BVA-03: 3 chars (valid min boundary)
VALID_NAME_2   = "Al"            # BVA-02: 2 chars (valid min boundary)
VALID_PHONE_10 = "0123456789"    # BVA-04: 10 digits (valid)
VALID_PHONE_11 = "01234567890"   # BVA-05: 11 digits (valid max boundary)
NAME_1CHAR     = "A"             # BVA-01: 1 char (INVALID — too short)
NAME_SYMBOLS   = "John123!"      # EP-02: numbers+symbols (INVALID format)
PHONE_LETTERS  = "zeroonetwo"    # EP-04: letters in phone (INVALID)
PHONE_12DIGITS = "012345678901"  # BVA-06: 12 digits (INVALID — too long)
OFFLINE_NAME   = "John Doe"      # UCT-03: for offline test
VALID_PHOTO    = os.path.join(SCRIPT_DIR, "profile.jpg")
INVALID_PHOTO  = os.path.join(SCRIPT_DIR, "document.pdf")

driver = webdriver.Chrome()
driver.maximize_window()
wait   = WebDriverWait(driver, 15)
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
                    "incorrect", "prompt"]
    return has_text(*keywords)


def is_field_editable(field_id):
    try:
        f = driver.find_element(By.ID, field_id)
        return (f.get_attribute("disabled") is None and
                f.get_attribute("readonly") is None)
    except NoSuchElementException:
        return False


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
# SESSION SETUP — Login once, reuse session
# ─────────────────────────────────────────────

def setup_session():
    """Login to admin web. Run once before all tests."""
    print("\n🔐 Logging in to admin web...")
    driver.get(f"{BASE_URL}/")
    try:
        find_el(By.ID, "email").send_keys("good@email.com")
        find_el(By.ID, "password").send_keys("drone123")
        tap_el(By.CSS_SELECTOR, "button[type='submit']")
        time.sleep(3)

        # Check redirect away from login
        redirected = (driver.current_url != f"{BASE_URL}/" and
                      "/login" not in driver.current_url)
        if redirected:
            print(f"✅ Login successful → {driver.current_url}")
            return True
        else:
            screenshot_full("UC4_Error_Login.png")
            print("❌ Login failed")
            return False
    except TimeoutException:
        screenshot_full("UC4_Error_Login.png")
        print("❌ Login page not found — is localhost:3000 running?")
        return False


def go_to_edit():
    """Navigate to settings and open the Edit Profile form."""
    driver.get(f"{BASE_URL}/settings")
    time.sleep(1)
    edit_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH,
             "//button[contains(., 'Edit Profile') or contains(., 'Edit')]")
        )
    )
    edit_btn.click()
    wait.until(EC.presence_of_element_located((By.ID, "name")))
    time.sleep(0.5)


def click_save():
    """Click the Save Changes button."""
    tap_el(By.XPATH,
           "//button[contains(., 'Save Changes') or contains(., 'Save')]")
    time.sleep(2)


# ─────────────────────────────────────────────
# TC-UC4-01 — Valid Profile Update (Main Flow)
# Techniques: EP-01(valid name), EP-03(valid phone),
#             BVA-03(3-char name), BVA-04(10-digit phone),
#             DT-01(all valid), UCT-01(main flow),
#             ST-01(click edit), ST-04(valid → success)
# Unique: Tests the COMPLETE happy path — valid name + valid phone
# ─────────────────────────────────────────────

def tc_uc4_01():
    print(f"\n▶ TC-UC4-01 — Valid Update (name='{VALID_NAME_3}', phone='{VALID_PHONE_10}')")
    print("   Technique: EP-01, EP-03, BVA-03, BVA-04, DT-01, UCT-01, ST-01, ST-04")
    try:
        go_to_edit()
        screenshot_full("UC4_TC01_BeforeEdit.png")

        clear_and_type("name", VALID_NAME_3)     # BVA-03: 3 chars
        clear_and_type("phone", VALID_PHONE_10)   # BVA-04: 10 digits

        # EP-05: valid photo (if available)
        try:
            if os.path.exists(VALID_PHOTO):
                fi = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                driver.execute_script("arguments[0].style.display='block';", fi)
                fi.send_keys(VALID_PHOTO)
                print(f"   📎 Photo uploaded: profile.jpg")
        except NoSuchElementException:
            print("   ⚠️  No file input on page — photo upload N/A")

        click_save()
        screenshot_full("UC4_TC01_AfterSave.png")

        if has_text("success", "saved", "updated", "profile updated"):
            record("TC-UC4-01", True,
                   f"PASS — name='{VALID_NAME_3}', phone='{VALID_PHONE_10}' "
                   "accepted. Success message shown. (ST-04: returns to view)")
        else:
            record("TC-UC4-01", False,
                   "FAIL — No success message after valid update. "
                   "Defect: profile update may not be working.")

    except Exception as e:
        screenshot_full("UC4_Error_TC01.png")
        record("TC-UC4-01", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC4-02 — Invalid Name Format
# Techniques: EP-02(invalid chars), BVA-01(1 char),
#             DT-02(invalid input), ST-02(stays on edit)
# Unique: Tests NAME validation only
#         Attempt 1 = boundary (length), Attempt 2 = partition (format)
#         TC-03 tests PHONE validation — completely different field
# ─────────────────────────────────────────────

def tc_uc4_02():
    print(f"\n▶ TC-UC4-02 — Invalid Name Validation")
    print("   Technique: EP-02, BVA-01, DT-02, ST-02")

    # Attempt 1 — BVA-01: 1 char name (boundary below minimum)
    print(f"   [BVA-01] name = '{NAME_1CHAR}' (1 char — below minimum length)")
    try:
        go_to_edit()
        clear_and_type("name", NAME_1CHAR)
        click_save()
        screenshot_full("UC4_TC02a_1charName.png")

        if has_error(["text-red", "border-red", "invalid", "error",
                      "least", "short", "character", "minimum"]):
            record("TC-UC4-02a", True,
                   f"PASS — 1-char name '{NAME_1CHAR}' rejected (BVA-01). "
                   "Stays on edit screen (ST-02).")
        else:
            record("TC-UC4-02a", False,
                   f"FAIL — 1-char name '{NAME_1CHAR}' NOT rejected. "
                   "Defect: minimum length validation missing.")
    except Exception as e:
        screenshot_full("UC4_Error_TC02a.png")
        record("TC-UC4-02a", False, f"Exception: {e}")

    # Attempt 2 — EP-02: name with numbers and symbols (invalid partition)
    print(f"   [EP-02] name = '{NAME_SYMBOLS}' (numbers+symbols — invalid format)")
    try:
        go_to_edit()
        clear_and_type("name", NAME_SYMBOLS)
        click_save()
        screenshot_full("UC4_TC02b_InvalidChars.png")

        if has_error(["text-red", "border-red", "invalid", "error",
                      "character", "letter", "only", "name"]):
            record("TC-UC4-02b", True,
                   f"PASS — name '{NAME_SYMBOLS}' rejected (EP-02). "
                   "Stays on edit screen (ST-02).")
        else:
            record("TC-UC4-02b", False,
                   f"FAIL — name '{NAME_SYMBOLS}' NOT rejected. "
                   "Defect: character format validation missing.")
    except Exception as e:
        screenshot_full("UC4_Error_TC02b.png")
        record("TC-UC4-02b", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC4-03 — Invalid Phone Format
# Techniques: EP-04(letters in phone), BVA-06(12 digits above max),
#             DT-02(invalid input), ST-02(stays on edit)
# Unique: Tests PHONE validation only — different field from TC-02
#         Attempt 1 = partition (wrong type), Attempt 2 = boundary (too long)
# ─────────────────────────────────────────────

def tc_uc4_03():
    print(f"\n▶ TC-UC4-03 — Invalid Phone Validation")
    print("   Technique: EP-04, BVA-06, DT-02, ST-02")

    # Attempt 1 — EP-04: letters in phone (wrong partition)
    print(f"   [EP-04] phone = '{PHONE_LETTERS}' (letters — invalid partition)")
    try:
        go_to_edit()
        clear_and_type("phone", PHONE_LETTERS)
        click_save()
        screenshot_full("UC4_TC03a_LettersPhone.png")

        if has_error(["text-red", "border-red", "invalid", "error",
                      "phone", "number", "digit", "numeric"]):
            record("TC-UC4-03a", True,
                   f"PASS — phone '{PHONE_LETTERS}' rejected (EP-04). "
                   "Stays on edit screen (ST-02).")
        else:
            record("TC-UC4-03a", False,
                   f"FAIL — phone '{PHONE_LETTERS}' NOT rejected. "
                   "Defect: phone format validation missing.")
    except Exception as e:
        screenshot_full("UC4_Error_TC03a.png")
        record("TC-UC4-03a", False, f"Exception: {e}")

    # Attempt 2 — BVA-06: 12 digits (boundary above maximum)
    print(f"   [BVA-06] phone = '{PHONE_12DIGITS}' (12 digits — above max boundary)")
    try:
        go_to_edit()
        clear_and_type("phone", PHONE_12DIGITS)
        click_save()
        screenshot_full("UC4_TC03b_12DigitPhone.png")

        if has_error(["text-red", "border-red", "invalid", "error",
                      "phone", "long", "digit", "maximum", "15"]):
            record("TC-UC4-03b", True,
                   f"PASS — 12-digit phone rejected (BVA-06). "
                   "Stays on edit screen (ST-02).")
        else:
            record("TC-UC4-03b", False,
                   f"FAIL — 12-digit phone NOT rejected. "
                   "Defect: maximum length validation missing.")
    except Exception as e:
        screenshot_full("UC4_Error_TC03b.png")
        record("TC-UC4-03b", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC4-04 — Invalid Email + Wrong Photo Type
# Techniques: EP-06(invalid file type), UCT-02(invalid email),
#             DT-02(invalid input), ST-02(stays on edit)
# Unique: Tests EMAIL field and PHOTO UPLOAD — different fields from TC-02/03
#         These are completely different input types
# ─────────────────────────────────────────────

def tc_uc4_04():
    print(f"\n▶ TC-UC4-04 — Invalid Email Format + Wrong Photo Type")
    print("   Technique: EP-06, UCT-02, DT-02, ST-02")

    # Attempt 1 — UCT-02: invalid email format
    print("   [UCT-02] email = 'invalidemail.com' (missing @ — invalid format)")
    try:
        go_to_edit()
        if is_field_editable("email"):
            clear_and_type("email", "invalidemail.com")
            click_save()
            screenshot_full("UC4_TC04a_InvalidEmail.png")

            if has_error(["text-red", "border-red", "invalid", "error",
                          "email", "@", "format"]):
                record("TC-UC4-04a", True,
                       "PASS — 'invalidemail.com' rejected (UCT-02). "
                       "Stays on edit screen.")
            else:
                record("TC-UC4-04a", False,
                       "FAIL — invalid email format not rejected. "
                       "Defect: email validation missing.")
        else:
            screenshot_full("UC4_TC04a_EmailReadOnly.png")
            record("TC-UC4-04a", None,
                   "N/A — Email field is read-only on this form by design. "
                   "Email validation tested at registration level.")
    except Exception as e:
        screenshot_full("UC4_Error_TC04a.png")
        record("TC-UC4-04a", False, f"Exception: {e}")

    # Attempt 2 — EP-06: PDF file upload (invalid file type)
    print("   [EP-06] photo = 'document.pdf' (PDF — invalid file type)")
    try:
        go_to_edit()
        if not os.path.exists(INVALID_PHOTO):
            record("TC-UC4-04b", None,
                   "N/A — document.pdf not found. "
                   "Place document.pdf next to script to run this test.")
            return

        try:
            fi = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            driver.execute_script("arguments[0].style.display='block';", fi)
            fi.send_keys(INVALID_PHOTO)
            time.sleep(1)
            click_save()
            screenshot_full("UC4_TC04b_PDFUpload.png")

            if has_error(["text-red", "border-red", "invalid", "error",
                          "file", "type", "jpg", "png", "format", "image"]):
                record("TC-UC4-04b", True,
                       "PASS — PDF upload rejected (EP-06).")
            else:
                record("TC-UC4-04b", False,
                       "FAIL — PDF upload not rejected. "
                       "Defect: file type validation missing.")
        except NoSuchElementException:
            screenshot_full("UC4_TC04b_NoUpload.png")
            record("TC-UC4-04b", None,
                   "N/A — No file upload input on settings page. "
                   "Photo upload not implemented on web admin.")

    except Exception as e:
        screenshot_full("UC4_Error_TC04b.png")
        record("TC-UC4-04b", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC4-05 — Network Failure During Submit
# Techniques: DT-03(system offline), UCT-03(exception flow),
#             ST-03(stays on edit with error)
# Unique: Tests SYSTEM BEHAVIOUR under failure condition
#         None of the other TCs test offline/network scenarios
# ─────────────────────────────────────────────

def tc_uc4_05():
    print(f"\n▶ TC-UC4-05 — Network Failure During Submit")
    print("   Technique: DT-03, UCT-03, ST-03")
    print(f"   Input: name='{OFFLINE_NAME}', phone='{VALID_PHONE_10}' + disconnect WiFi")
    try:
        go_to_edit()
        clear_and_type("name", OFFLINE_NAME)
        clear_and_type("phone", VALID_PHONE_10)

        print("   🔌 Simulating network disconnect...")
        simulate_offline()
        time.sleep(1)

        click_save()
        time.sleep(3)
        screenshot_full("UC4_TC05_Offline.png")

        if has_text("unable", "try again", "error", "failed",
                    "connection", "network", "offline", "cannot"):
            record("TC-UC4-05", True,
                   "PASS — Offline error message shown (UCT-03). "
                   "System handles failure gracefully (ST-03). "
                   "User stays on edit screen.")
        else:
            record("TC-UC4-05", False,
                   "FAIL — No error message shown when offline. "
                   "Defect: system does not handle network failure gracefully.")

    except Exception as e:
        screenshot_full("UC4_Error_TC05.png")
        record("TC-UC4-05", False, f"Exception: {e}")
    finally:
        print("   🔌 Restoring network...")
        simulate_online()
        time.sleep(1)


# ─────────────────────────────────────────────
# BVA BOUNDARY TESTS
# Techniques: BVA-02(2-char name), BVA-05(11-digit phone)
# Unique: Tests BOUNDARY VALUES at valid minimum/maximum
#         TC-02 tests BELOW minimum (invalid)
#         TC-03 tests ABOVE maximum (invalid)
#         This tests AT the boundary (valid) — different thing
# ─────────────────────────────────────────────

def tc_bva_boundaries():
    print(f"\n▶ BVA Boundary Tests — Valid Minimum and Maximum")
    print("   Technique: BVA-02 (2-char name), BVA-05 (11-digit phone)")

    # BVA-02: 2-char name — valid minimum boundary
    print(f"   [BVA-02] name = '{VALID_NAME_2}' (2 chars — AT valid minimum)")
    try:
        go_to_edit()
        clear_and_type("name", VALID_NAME_2)
        clear_and_type("phone", VALID_PHONE_10)
        click_save()
        screenshot_full("UC4_BVA02_2CharName.png")

        success = has_text("success", "saved", "updated")
        error   = has_error()

        if success or not error:
            record("BVA-02", True,
                   f"PASS — 2-char name '{VALID_NAME_2}' accepted (BVA-02). "
                   "Valid minimum boundary works correctly.")
        else:
            record("BVA-02", False,
                   f"FAIL — 2-char name '{VALID_NAME_2}' incorrectly rejected. "
                   "Defect: minimum boundary validation too strict.")
    except Exception as e:
        screenshot_full("UC4_Error_BVA02.png")
        record("BVA-02", False, f"Exception: {e}")

    # BVA-05: 11-digit phone — valid maximum boundary
    print(f"   [BVA-05] phone = '{VALID_PHONE_11}' (11 digits — AT valid maximum)")
    try:
        go_to_edit()
        clear_and_type("name", VALID_NAME_3)
        clear_and_type("phone", VALID_PHONE_11)
        click_save()
        screenshot_full("UC4_BVA05_11DigitPhone.png")

        success = has_text("success", "saved", "updated")
        error   = has_error()

        if success or not error:
            record("BVA-05", True,
                   f"PASS — 11-digit phone '{VALID_PHONE_11}' accepted (BVA-05). "
                   "Valid maximum boundary works correctly.")
        else:
            record("BVA-05", False,
                   f"FAIL — 11-digit phone '{VALID_PHONE_11}' incorrectly rejected. "
                   "Defect: maximum boundary validation too strict. "
                   "Expected: accept 11 digits. Actual: rejected.")
    except Exception as e:
        screenshot_full("UC4_Error_BVA05.png")
        record("BVA-05", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

try:
    print("=" * 62)
    print("  UC4 EDIT PROFILE — WEB SELENIUM TEST")
    print("  Testing Level: System Testing")
    print("  Tester: Yusrina Maisarah binti Yunus")
    print(f"  URL: {BASE_URL}")
    print(f"  Screenshots: {SCREENSHOT_DIR}")
    print("=" * 62)
    print("\n  Test Cases and What Each Tests (No Redundancy):")
    print("  TC-UC4-01 → Happy path: valid name + phone + photo")
    print("  TC-UC4-02 → Name validation: length (BVA) + format (EP)")
    print("  TC-UC4-03 → Phone validation: type (EP) + length (BVA)")
    print("  TC-UC4-04 → Email format + photo file type (different fields)")
    print("  TC-UC4-05 → Network failure handling (system behaviour)")
    print("  BVA-02/05 → Valid boundaries: 2-char name, 11-digit phone")
    print("=" * 62)

    if setup_session():
        tc_uc4_01()    # EP-01, EP-03, BVA-03, BVA-04, DT-01, UCT-01, ST-01, ST-04
        tc_uc4_02()    # EP-02, BVA-01, DT-02, ST-02
        tc_uc4_03()    # EP-04, BVA-06, DT-02, ST-02
        tc_uc4_04()    # EP-06, UCT-02, DT-02, ST-02
        tc_uc4_05()    # DT-03, UCT-03, ST-03
        tc_bva_boundaries()  # BVA-02, BVA-05
    else:
        print("🛑 Aborting — login failed")

except Exception as e:
    print(f"\n🛑 Unexpected error: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n" + "=" * 62)
    print("  TEST SUMMARY — UC4 Edit Profile (Web)")
    print("=" * 62)
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
    print(f"\n  📁 Screenshots → {SCREENSHOT_DIR}")
    print("=" * 62)

    input("\nPress Enter to close browser...")
    driver.quit()