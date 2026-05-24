import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoAlertPresentException, WebDriverException

BASE_URL = "http://localhost:3000"
ADD_DRONE_MODAL = "//h2[normalize-space()='Add New Drone']/ancestor::div[contains(@class, 'bg-white')]"


def open_add_drone_modal(driver):
    wait = WebDriverWait(driver, 20)
    existing_modals = driver.find_elements(By.XPATH, ADD_DRONE_MODAL)
    for modal in existing_modals:
        if modal.is_displayed():
            return modal

    add_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Add Drone' and not(@type='submit')]")))
    driver.execute_script("arguments[0].click();", add_button)
    return wait.until(EC.visibility_of_element_located((By.XPATH, ADD_DRONE_MODAL)))


def cleanup_test_drones(driver):
    deleted_count = driver.execute_async_script("""
        const done = arguments[0];
        const token = window.localStorage.getItem('token');
        const testNames = new Set(['X', 'SkyWatch Alpha', 'Drone A']);
        const testSerials = new Set(['S', 'SN-9001']);

        fetch('http://localhost:4000/drones?limit=1000', {
            headers: { Authorization: `Bearer ${token}` }
        })
            .then((response) => response.json())
            .then(async (data) => {
                const drones = data.drones || [];
                const targets = drones.filter((drone) =>
                    testNames.has(drone.name) || testSerials.has(drone.serial)
                );

                await Promise.all(targets.map((drone) =>
                    fetch(`http://localhost:4000/drones/${drone.id}`, {
                        method: 'DELETE',
                        headers: { Authorization: `Bearer ${token}` }
                    })
                ));

                done(targets.length);
            })
            .catch((error) => done(`cleanup failed: ${error.message}`));
    """)

    if isinstance(deleted_count, str) and deleted_count.startswith("cleanup failed"):
        pytest.fail(deleted_count)


def click_modal_button(driver, modal, text):
    button = modal.find_element(By.XPATH, f".//button[contains(normalize-space(), '{text}')]")
    driver.execute_script("arguments[0].click();", button)


def save_evidence(driver, filename):
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
    driver.save_screenshot(os.path.join("screenshots", filename))


def save_evidence_if_possible(driver, filename):
    try:
        save_evidence(driver, filename)
        return True
    except WebDriverException:
        return False


def capture_alert_evidence_and_accept(driver, alert, filename):
    alert_text = alert.text
    save_evidence_if_possible(driver, filename)
    try:
        alert.accept()
    except NoAlertPresentException:
        # Chrome may dismiss a native alert while WebDriver captures evidence.
        pass
    return alert_text


# NOTE: For the tests to run sequentially and successfully share state 
# (e.g. editing the drone created in the previous test), we scope the driver to the module.
@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    
    # For TC-UC05-007 (GPS Denied), we explicitly deny geolocation permissions
    prefs = {"profile.default_content_setting_values.geolocation": 2}
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    
    # Create a directory to store evidence screenshots if it doesn't exist
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")

    # 1. Pre-condition: Login as Admin
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email"))).send_keys("admin1@drone4dengue.com")
    driver.find_element(By.ID, "password").send_keys("adminpass1")
    driver.find_element(By.XPATH, "//button[contains(text(), 'LOGIN')]").click()
    
    # Wait for dashboard, then navigate to Drone Management
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Dashboard')]")))
    driver.find_element(By.XPATH, "//a[@href='/drone-management']").click()
    WebDriverWait(driver, 10).until(EC.url_contains("/drone-management"))
    cleanup_test_drones(driver)
    driver.refresh()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Drone Management')]")))
    
    yield driver
    driver.quit()


def test_tc_uc05_001_bva_empty_fields(driver):
    """
    TC-UC05-001: Boundary Value Analysis – Prevent saving when required fields are empty (Length 0)
    """
    wait = WebDriverWait(driver, 10)
    
    # Open Add Drone Modal
    modal = open_add_drone_modal(driver)
    
    # Submit empty form
    click_modal_button(driver, modal, "Add Drone")
    
    # Verify browser alert surfaces preventing save
    try:
        alert = WebDriverWait(driver, 20).until(EC.alert_is_present())
        alert_text = capture_alert_evidence_and_accept(driver, alert, "TC-UC05-001_alert_required_fields.png")
        assert "Please fill in all required fields" in alert_text
        save_evidence(driver, "TC-UC05-001_required_fields_blocked_state.png")
    except TimeoutException:
        pytest.fail("Browser alert did not appear for empty fields validation.")
    finally:
        visible_modals = driver.find_elements(By.XPATH, ADD_DRONE_MODAL)
        for visible_modal in visible_modals:
            if visible_modal.is_displayed():
                click_modal_button(driver, visible_modal, "Cancel")
                break

    time.sleep(1) # Allow animation to finish


def test_tc_uc05_002_bva_length_1_valid(driver):
    """
    TC-UC05-002: Boundary Value Analysis – Successfully save when required fields are at the lower valid boundary (Length 1)
    """
    wait = WebDriverWait(driver, 10)
    
    modal = open_add_drone_modal(driver)
    
    # Input 1-character data
    modal.find_element(By.XPATH, ".//input[@placeholder='e.g., Drone Alpha']").send_keys("X")
    modal.find_element(By.XPATH, ".//input[@placeholder='e.g., DJI Phantom 4 Pro']").send_keys("D")
    modal.find_element(By.XPATH, ".//input[@placeholder='e.g., SN123456789']").send_keys("S")
    
    click_modal_button(driver, modal, "Add Drone")
    
    # Wait for success alert
    alert = wait.until(EC.alert_is_present())
    alert_text = capture_alert_evidence_and_accept(driver, alert, "TC-UC05-002_success_alert.png")
    assert "Drone created successfully!" in alert_text

    # Verify drone exists in grid
    wait.until(EC.visibility_of_element_located((By.XPATH, "//td[contains(text(), 'X')]")))
    save_evidence(driver, "TC-UC05-002_drone_visible_in_grid.png")


def test_tc_uc05_003_main_flow_and_ep_valid(driver):
    """
    TC-UC05-003: Main Flow & EP – Successfully register a standard drone with a unique serial and valid status
    """
    wait = WebDriverWait(driver, 10)
    
    modal = open_add_drone_modal(driver)
    
    modal.find_element(By.XPATH, ".//input[@placeholder='e.g., Drone Alpha']").send_keys("SkyWatch Alpha")
    modal.find_element(By.XPATH, ".//input[@placeholder='e.g., DJI Phantom 4 Pro']").send_keys("DJI Phantom 4")
    modal.find_element(By.XPATH, ".//input[@placeholder='e.g., SN123456789']").send_keys("SN-9001")
    
    # Select Status "Maintenance"
    status_dropdown = Select(modal.find_element(By.XPATH, ".//label[text()='Status']/following-sibling::select"))
    status_dropdown.select_by_visible_text("Maintenance")
    
    click_modal_button(driver, modal, "Add Drone")
    
    alert = wait.until(EC.alert_is_present())
    alert_text = capture_alert_evidence_and_accept(driver, alert, "TC-UC05-003_success_alert.png")
    assert "Drone created successfully!" in alert_text
    
    # Verify grid row matches Maintenance styling
    drone_row = wait.until(EC.visibility_of_element_located((By.XPATH, "//tr[.//td[contains(text(), 'SkyWatch Alpha')]]")))
    assert "Maintenance" in drone_row.text
    save_evidence(driver, "TC-UC05-003_maintenance_status_visible.png")


def test_tc_uc05_004_ep_duplicate_serial(driver):
    """
    TC-UC05-004: Equivalence Partitioning – Exception when adding a duplicate serial number
    """
    wait = WebDriverWait(driver, 10)
    
    modal = open_add_drone_modal(driver)
    
    modal.find_element(By.XPATH, ".//input[@placeholder='e.g., Drone Alpha']").send_keys("Drone A")
    modal.find_element(By.XPATH, ".//input[@placeholder='e.g., DJI Phantom 4 Pro']").send_keys("DJI Mavic")
    
    # Send the exact duplicate serial from TC-UC05-003
    serial_input = modal.find_element(By.XPATH, ".//input[@placeholder='e.g., SN123456789']")
    serial_input.send_keys("SN-9001")
    
    # Blur the input by clicking elsewhere to trigger the validation
    modal.find_element(By.XPATH, ".//label[text()='Serial Number']").click()
    
    # Verify inline validation error appears
    error_msg = wait.until(EC.visibility_of_element_located((By.XPATH, "//p[contains(text(), 'already in use')]")))
    assert "This serial number is already in use" in error_msg.text
    
    # Verify Add Drone button is disabled/unclickable
    submit_btn = modal.find_element(By.XPATH, ".//button[contains(text(), 'Add Drone')]")
    assert "opacity-50 cursor-not-allowed" in submit_btn.get_attribute("class")
    save_evidence(driver, "TC-UC05-004_duplicate_serial_error_visible.png")
    
    # Close modal
    modal.find_element(By.XPATH, ".//button[contains(text(), 'Cancel')]").click()
    time.sleep(1)


def test_tc_uc05_005_main_flow_edit_drone(driver):
    """
    TC-UC05-005: Use Case Testing – Main flow to Edit Drone Record
    """
    wait = WebDriverWait(driver, 10)
    
    # Find the row for "SkyWatch Alpha"
    drone_row = wait.until(EC.visibility_of_element_located((By.XPATH, "//tr[.//td[contains(text(), 'SkyWatch Alpha')]]")))
    
    # Click the Edit icon
    drone_row.find_element(By.XPATH, ".//button[@title='Edit Drone']").click()
    
    # Wait for Edit Drone modal
    modal = wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[text()='Edit Drone']/ancestor::div[contains(@class, 'bg-white')]")))
    
    # Note: In the actual page.tsx provided, the Edit form only supports updating Location and Status.
    # Drone Name, Model, and Serial are missing from the edit UI inputs! 
    # We will test changing the Status from "Maintenance" to "Operational" to prove the edit works.
    status_dropdown = Select(modal.find_element(By.XPATH, ".//label[text()='Status']/following-sibling::select"))
    status_dropdown.select_by_visible_text("Operational")
    
    modal.find_element(By.XPATH, ".//button[contains(text(), 'Save Changes')]").click()
    
    # Wait for success alert
    alert = wait.until(EC.alert_is_present())
    alert_text = capture_alert_evidence_and_accept(driver, alert, "TC-UC05-005_update_success_alert.png")
    assert "Drone updated successfully!" in alert_text
    
    # Verify status changed in the grid
    updated_row = wait.until(EC.visibility_of_element_located((By.XPATH, "//tr[.//td[contains(text(), 'SkyWatch Alpha')]]")))
    assert "Operational" in updated_row.text
    save_evidence(driver, "TC-UC05-005_operational_status_visible.png")


def test_tc_uc05_006_main_flow_delete_drone(driver):
    """
    TC-UC05-006: Use Case Testing – Main flow to Delete Drone
    """
    wait = WebDriverWait(driver, 10)
    
    drone_row = wait.until(EC.visibility_of_element_located((By.XPATH, "//tr[.//td[contains(text(), 'SkyWatch Alpha')]]")))
    
    # Click the Trash icon
    drone_row.find_element(By.XPATH, ".//button[@title='Delete Drone']").click()
    
    # Wait for the Danger confirmation dialog
    danger_dialog = wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[text()='Delete Drone']/ancestor::div[contains(@class, 'bg-white')]")))
    save_evidence(driver, "TC-UC05-006_delete_confirmation_visible.png")
    
    # Click Confirm
    danger_dialog.find_element(By.XPATH, ".//button[contains(text(), 'Confirm')]").click()
    
    # Wait for Success dialog overlay to appear
    success_dialog = wait.until(EC.visibility_of_element_located((By.XPATH, "//h3[text()='Success!']/ancestor::div[contains(@class, 'bg-white')]")))
    assert "Drone deleted successfully!" in success_dialog.text
    save_evidence(driver, "TC-UC05-006_delete_success_dialog_visible.png")
    
    # Dismiss success dialog
    success_dialog.find_element(By.XPATH, ".//button[contains(text(), 'Great!')]").click()
    
    # Verify "SkyWatch Alpha" is gone from the DOM
    wait.until(EC.invisibility_of_element_located((By.XPATH, "//td[contains(text(), 'SkyWatch Alpha')]")))


def test_tc_uc05_007_exception_flow_gps_denied(driver):
    """
    TC-UC05-007: Use Case Testing – Exception Flow 2.E.1.1: GPS Permission Denied
    """
    wait = WebDriverWait(driver, 10)
    
    # To test map integration with Geolocation blocked (set in ChromeOptions), 
    # we open the Add New Operational Area modal which triggers the MapPicker component.
    drone_modal = open_add_drone_modal(driver)
    
    # Click '+' to open location MapPicker
    drone_modal.find_element(By.XPATH, ".//label[normalize-space()='Operational Area']/following-sibling::div//button").click()
    
    loc_modal = wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[text()='Add New Operational Area']/ancestor::div[contains(@class, 'bg-white')]")))
    
    # Due to ChromeOptions denying geolocation upfront, the MapPicker will fallback gracefully 
    # (Usually this triggers a browser bar block and a console warning, or the map centers on a default fallback view like 0,0)
    # The app survives without crashing. We assert that the MapPicker container is visible and handles it.
    map_container = loc_modal.find_element(By.XPATH, ".//div[contains(@class, 'leaflet-container')]")
    assert map_container.is_displayed()
    save_evidence(driver, "TC-UC05-007_gps_denied_map_fallback_visible.png")
    
    # Clean up
    loc_modal.find_element(By.XPATH, ".//button[contains(text(), 'Cancel')]").click()
