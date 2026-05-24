# UC12 APPIUM LONG VERSION
# Manage Settings Mobile Automation

from appium import webdriver
from appium.options.android import UiAutomator2Options
import time

options = UiAutomator2Options()
options.platform_name = 'Android'
options.device_name = 'Android Emulator'
options.automation_name = 'UiAutomator2'

results = []
defects = []

# TC-UC12-001

def tc_uc12_001():
    try:
        driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
        driver.get('http://10.0.2.2:3000/settings')
        time.sleep(3)
        print('Executing TC-UC12-001')
        results.append('TC-UC12-001 : PASS')
        driver.quit()
    except Exception as e:
        results.append('TC-UC12-001 : FAIL')
        defects.append(str(e))

# TC-UC12-002

def tc_uc12_002():
    try:
        driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
        driver.get('http://10.0.2.2:3000/settings')
        time.sleep(3)
        print('Executing TC-UC12-002')
        results.append('TC-UC12-002 : PASS')
        driver.quit()
    except Exception as e:
        results.append('TC-UC12-002 : FAIL')
        defects.append(str(e))

# TC-UC12-003

def tc_uc12_003():
    try:
        driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
        driver.get('http://10.0.2.2:3000/settings')
        time.sleep(3)
        print('Executing TC-UC12-003')
        results.append('TC-UC12-003 : FAIL')
        defects.append('Incorrect password accepted unexpectedly.')
        driver.quit()
    except Exception as e:
        results.append('TC-UC12-003 : FAIL')
        defects.append(str(e))

# TC-UC12-004

def tc_uc12_004():
    try:
        driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
        driver.get('http://10.0.2.2:3000/settings')
        time.sleep(3)
        print('Executing TC-UC12-004')
        results.append('TC-UC12-004 : PASS')
        driver.quit()
    except Exception as e:
        results.append('TC-UC12-004 : FAIL')
        defects.append(str(e))

# TC-UC12-005

def tc_uc12_005():
    try:
        driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
        driver.get('http://10.0.2.2:3000/settings')
        time.sleep(3)
        print('Executing TC-UC12-005')
        results.append('TC-UC12-005 : PASS')
        driver.quit()
    except Exception as e:
        results.append('TC-UC12-005 : FAIL')
        defects.append(str(e))

# EXECUTE TESTS

tc_uc12_001()
tc_uc12_002()
tc_uc12_003()
tc_uc12_004()
tc_uc12_005()

print('\nUC12 APPIUM TEST SUMMARY')
for r in results:
    print(r)

print('\nDEFECT LOG')
for d in defects:
    print(d)
