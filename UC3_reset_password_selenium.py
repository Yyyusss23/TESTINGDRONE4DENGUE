from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()

print("=========================================")
print("🤖 STARTING FULL AUTOMATED TEST FOR UC-3")
print("=========================================")

# ---------------------------------------------------------
# TEST 1: INVALID FORMAT (TCV-UC3-01C)
# ---------------------------------------------------------
print("\n[TEST 1] Testing Invalid Format (admin_test.com)...")
driver.get("http://localhost:3000/forgot-password")
time.sleep(2)

email_box = driver.find_element(By.ID, "email")
email_box.send_keys("admin_test.com")
driver.find_element(By.XPATH, "//button[@type='submit']").click()
time.sleep(2)
print("📸 TAKING SCREENSHOT OF INVALID FORMAT WARNING...")
driver.save_screenshot("BUG_Invalid_Format.png")

# ---------------------------------------------------------
# TEST 2: UNREGISTERED EMAIL (TCV-UC3-01B)
# ---------------------------------------------------------
print("\n[TEST 2] Testing Unregistered Email...")
email_box.clear()
email_box.send_keys("fakeuser@test.com")
driver.find_element(By.XPATH, "//button[@type='submit']").click()
time.sleep(2)
print("📸 TAKING SCREENSHOT OF FAKE EMAIL CRASH...")
driver.save_screenshot("BUG_Fake_Email.png")

# ---------------------------------------------------------
# TEST 3: VALID EMAIL (TCV-UC3-01A)
# ---------------------------------------------------------
print("\n[TEST 3] Testing Valid Email...")
driver.get("http://localhost:3000/forgot-password") # Refresh to clear crash
time.sleep(2)
email_box = driver.find_element(By.ID, "email")
email_box.send_keys("test@email.com")
driver.find_element(By.XPATH, "//button[@type='submit']").click()
time.sleep(3)

try:
    # ---------------------------------------------------------
    # TEST 4: VERIFICATION CODE & RESEND LINK (TCND-UC3-02 & 04)
    # ---------------------------------------------------------
    print("\n[TEST 4] Testing Verification Code Page...")
    
    # Test Resend Link
    print("- Clicking Resend Link")
    driver.find_element(By.XPATH, "//button[contains(text(), 'Resend')]").click()
    time.sleep(2)

    # Enter invalid code (000000)
    print("- Entering invalid code: 000000")
    code_box = driver.find_element(By.ID, "code") # Update ID if needed
    code_box.send_keys("000000")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(2)
    print("📸 TAKING SCREENSHOT OF INVALID CODE...")
    driver.save_screenshot("BUG_Invalid_Code.png")

    # ---------------------------------------------------------
    # TEST 5: PASSWORD MATCHING (TCND-UC3-03)
    # ---------------------------------------------------------
    print("\n[TEST 5] Testing Password Mismatch...")
    # Assuming we passed the code phase and are on the New Password screen
    new_pass = driver.find_element(By.ID, "new-password") # Update ID if needed
    confirm_pass = driver.find_element(By.ID, "confirm-password") # Update ID if needed
    
    new_pass.send_keys("SecurePass123!")
    confirm_pass.send_keys("SecurePass124!")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(2)
    print("📸 TAKING SCREENSHOT OF MISMATCH ERROR...")
    driver.save_screenshot("BUG_Password_Mismatch.png")

except Exception as e:
    print("\nSYSTEM CRASHED: Could not reach the next pages because of the React Error.")
    print("Marking remaining test cases as BLOCKED.")

print("\n🎉 All accessible tests complete!")
driver.quit()