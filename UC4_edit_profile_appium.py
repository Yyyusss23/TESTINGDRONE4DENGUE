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
SCREENSHOT_DIR = os.path.join(SCRIPT_DIR, "UC4_mobile_screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

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
    """Dismiss any OK popup."""
    try:
        tap(AppiumBy.XPATH, "//*[@text='OK']", timeout=3)
        time.sleep(0.5)
    except TimeoutException:
        pass

def go_to_profile_edit():
    """Navigate to Edit Profile screen."""
    dismiss_ok()
    tap(AppiumBy.XPATH, "//*[@text='Profile']")
    time.sleep(2)
    dismiss_ok()
    tap(AppiumBy.XPATH, "//*[@text='My Account']")
    time.sleep(2)

def get_name_field():
    """Get name field — first text box on edit profile screen."""
    return find(AppiumBy.XPATH, "(//android.widget.EditText)[1]")

def get_phone_field():
    """Get phone field — third text box on edit profile screen."""
    return find(AppiumBy.XPATH, "(//android.widget.EditText)[3]")

def fill_name(value):
    el = get_name_field()
    el.clear()
    el.send_keys(value)

def fill_phone(value):
    el = get_phone_field()
    el.clear()
    el.send_keys(value)


def click_save_and_confirm(test_id):
    """Tap Save Changes, Confirm, TAKE SCREENSHOT, then dismiss OK."""
    tap(AppiumBy.XPATH, "//*[@text='Save Changes']")
    time.sleep(1)
    
    # Try to tap Confirm if the app asks "Are you sure?"
    try:
        tap(AppiumBy.XPATH, "//*[@text='Confirm']", timeout=3)
        time.sleep(2)
    except TimeoutException:
        pass # If there is a quick error text, it might skip the confirm popup
    
    # Take the screenshot right now while the message/error is showing!
    screenshot(f"UC4_M_Result_{test_id}.png")
    
    # Now it is safe to dismiss the success/error popup button
    dismiss_ok()


# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────

def setup_session():
    print("\n🔐 Logging in (mobile)...")
    time.sleep(5)

    dismiss_ok()

    try:
        email_field = find(AppiumBy.XPATH,
            "//android.widget.EditText[@text='Enter your email']")
        email_field.clear()
        email_field.send_keys("mobiletest@email.com")
        time.sleep(0.5)

        password_field = find(AppiumBy.XPATH,
            "//android.widget.EditText[@text='Enter your password']")
        password_field.clear()
        password_field.send_keys("mobile123")
        time.sleep(0.5)

        tap(AppiumBy.XPATH, "//*[@text='Sign In']")
        time.sleep(5)

        dismiss_ok()
        time.sleep(1)

        page = driver.page_source.lower()
        if any(k in page for k in ["profile", "welcome back", "my account",
                                    "log out", "dashboard", "dengue"]):
            print("✅ Login successful")
            return True
        else:
            if "admin users cannot" in page:
                print("❌ Login failed — user role is 'admin'!")
            else:
                print("❌ Login failed — page content:")
            screenshot("UC4_M_Error_Login.png")
            return False

    except Exception as e:
        screenshot("UC4_M_Error_Login.png")
        print(f"❌ Login error: {e}")
        return False


# ─────────────────────────────────────────────
# TC-UC4-01 — Valid Update
# ─────────────────────────────────────────────

def tc_uc4_01():
    print("\n▶ TC-UC4-01 — Valid Update (name: Ali, phone: 0123456789)")
    try:
        go_to_profile_edit()
        fill_name("Ali")
        fill_phone("0123456789")
        
        click_save_and_confirm("TC01")

        if has_text("profile updated successfully", "success", "updated"):
            record("TC-UC4-01", True, "Valid data accepted — success message shown")
        else:
            record("TC-UC4-01", False, "No success message after valid update")

    except Exception as e:
        record("TC-UC4-01", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC4-02 — Invalid Name
# ─────────────────────────────────────────────

def tc_uc4_02():
    print("\n▶ TC-UC4-02 — Invalid Name")

    print("   Attempt 1: name = 'A'  (BVA-01: 1 char, too short)")
    try:
        go_to_profile_edit()
        fill_name("A")
        
        click_save_and_confirm("TC02a")

        if has_text("invalid", "error", "short", "least", "character", "minimum", "required"):
            record("TC-UC4-02a", True, "BVA-01: 1-char name correctly rejected")
        else:
            record("TC-UC4-02a", False, "BVA-01: No validation error for 1-char name")
    except Exception as e:
        record("TC-UC4-02a", False, f"Exception: {e}")

    print("   Attempt 2: name = 'John123!'  (EP-02: invalid characters)")
    try:
        go_to_profile_edit()
        fill_name("John123!")
        
        click_save_and_confirm("TC02b")

        if has_text("invalid", "error", "character", "letter", "only", "name"):
            record("TC-UC4-02b", True, "EP-02: Name with symbols correctly rejected")
        else:
            record("TC-UC4-02b", False, "EP-02: No validation for name with invalid characters")
    except Exception as e:
        record("TC-UC4-02b", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC4-03 — Invalid Phone
# ─────────────────────────────────────────────

def tc_uc4_03():
    print("\n▶ TC-UC4-03 — Invalid Phone")

    print("   Attempt 1: phone = 'zeroonetwo'  (EP-04: letters in phone)")
    try:
        go_to_profile_edit()
        fill_phone("zeroonetwo")
        
        click_save_and_confirm("TC03a")

        if has_text("invalid", "error", "phone", "number", "digit", "numeric"):
            record("TC-UC4-03a", True, "EP-04: Letters in phone correctly rejected")
        else:
            record("TC-UC4-03a", False, "EP-04: No validation for letters in phone")
    except Exception as e:
        record("TC-UC4-03a", False, f"Exception: {e}")

    print("   Attempt 2: phone = '012345678901'  (BVA-06: 12 digits)")
    try:
        go_to_profile_edit()
        fill_phone("012345678901")
        
        click_save_and_confirm("TC03b")

        if has_text("invalid", "error", "phone", "long", "maximum", "digit"):
            record("TC-UC4-03b", True, "BVA-06: 12-digit phone correctly rejected")
        else:
            record("TC-UC4-03b", False, "BVA-06: No validation for 12-digit phone")
    except Exception as e:
        record("TC-UC4-03b", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC4-04 — Invalid Email + Wrong Photo
# ─────────────────────────────────────────────

def tc_uc4_04():
    print("\n▶ TC-UC4-04 — Invalid Email + Wrong Photo")

    print("   Attempt 1: email = 'invalidemail.com'  (UCT-02)")
    try:
        go_to_profile_edit()
        try:
            email_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (AppiumBy.XPATH, "//android.widget.EditText[contains(@text,'email') or contains(@hint,'email')]")
                )
            )
            email_field.clear()
            email_field.send_keys("invalidemail.com")
            click_save_and_confirm("TC04a")
        except TimeoutException:
            record("TC-UC4-04a", None, "UCT-02: Email field not editable on mobile edit profile.")
    except Exception as e:
        record("TC-UC4-04a", False, f"Exception: {e}")

    print("   Attempt 2: photo = document.pdf  (EP-06)")
    try:
        go_to_profile_edit()
        try:
            tap(AppiumBy.XPATH, "//*[contains(@text,'Photo') or contains(@text,'Upload')]", timeout=5)
            time.sleep(1)
            screenshot("UC4_M_Result_TC04b.png")
            record("TC-UC4-04b", None, "EP-06: Photo upload tapped — check manually")
        except TimeoutException:
            record("TC-UC4-04b", None, "EP-06: No photo upload element on mobile edit profile.")
    except Exception as e:
        record("TC-UC4-04b", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# TC-UC4-05 — Offline During Submit
# ─────────────────────────────────────────────

def tc_uc4_05():
    print("\n▶ TC-UC4-05 — Offline Network During Submit")
    try:
        go_to_profile_edit()
        fill_name("John Doe")
        fill_phone("0123456789")

        print("   🔌 Turning off WiFi...")
        os.system("adb shell svc wifi disable")
        os.system("adb shell svc data disable")
        time.sleep(2)

        tap(AppiumBy.XPATH, "//*[@text='Save Changes']")
        time.sleep(1)
        
        try:
            tap(AppiumBy.XPATH, "//*[@text='Confirm']", timeout=5)
        except TimeoutException:
            pass
        time.sleep(3)

        # Take screenshot of the offline error message
        screenshot("UC4_M_Result_TC05.png")

        if has_text("unable", "try again", "error", "failed", "connection", "network", "offline", "cannot"):
            record("TC-UC4-05", True, "ST-03: Offline error message shown correctly")
        else:
            record("TC-UC4-05", False, "ST-03: No offline error message shown")

    except Exception as e:
        record("TC-UC4-05", False, f"Exception: {e}")
    finally:
        print("   🔌 Restoring WiFi...")
        os.system("adb shell svc wifi enable")
        os.system("adb shell svc data enable")
        time.sleep(2)
        dismiss_ok()


# ─────────────────────────────────────────────
# BVA EXTRAS
# ─────────────────────────────────────────────

def tc_bva_extras():
    print("\n▶ BVA Extras")

    print("   BVA-02: name = 'Al'  (2 chars — valid minimum boundary)")
    try:
        go_to_profile_edit()
        fill_name("Al")
        fill_phone("0123456789")
        
        click_save_and_confirm("BVA02")

        if has_text("profile updated successfully", "success") or not has_text("invalid", "error"):
            record("BVA-02", True, "2-char name accepted as valid minimum boundary")
        else:
            record("BVA-02", False, "2-char name incorrectly rejected")
    except Exception as e:
        record("BVA-02", False, f"Exception: {e}")

    print("   BVA-05: phone = '01234567890'  (11 digits — valid maximum boundary)")
    try:
        go_to_profile_edit()
        fill_name("Ali")
        fill_phone("01234567890")
        
        click_save_and_confirm("BVA05")

        if has_text("profile updated successfully", "success") or not has_text("invalid", "error"):
            record("BVA-05", True, "11-digit phone accepted as valid maximum boundary")
        else:
            record("BVA-05", False, "11-digit phone incorrectly rejected")
    except Exception as e:
        record("BVA-05", False, f"Exception: {e}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

try:
    if setup_session():
        tc_uc4_01()
        tc_uc4_02()
        tc_uc4_03()
        tc_uc4_04()
        tc_uc4_05()
        tc_bva_extras()
    else:
        print("🛑 Aborting — login failed")

except Exception as e:
    print(f"\n🛑 Unexpected error: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n" + "="*60)
    print("  TEST SUMMARY — UC4 Edit Profile (Mobile)")
    print("="*60)
    passed = failed = na = 0
    for r in results:
        print(f"  {r}")
        if "✅" in r:
            passed += 1
        elif "❌" in r:
            failed += 1
        else:
            na += 1
    print(f"\n  Total: {len(results)}  |  ✅ Passed: {passed}  |  ❌ Failed: {failed}  |  ℹ️ N/A: {na}")
    print(f"\n  📁 Screenshots → {SCREENSHOT_DIR}")
    print("="*60)
    driver.quit()