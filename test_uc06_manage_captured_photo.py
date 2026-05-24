import os
import time

import pytest
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


BASE_URL = "http://localhost:3000"
API_URL = "http://localhost:4000"
SCREENSHOT_DIR = "screenshots"
ASSET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_assets"))
TEST_IMAGE = os.path.join(ASSET_DIR, "uc06_capture_site_a.jpg")
TEST_TEXT = os.path.join(ASSET_DIR, "uc06_notes.txt")
TEST_VIDEO = os.path.join(ASSET_DIR, "uc06_drone_scan.mp4")
TEST_OVERSIZED_VIDEO = os.path.join(ASSET_DIR, "uc06_oversized_drone_scan.mp4")
TEST_IMAGE_NAME = os.path.basename(TEST_IMAGE)
TEST_TEXT_NAME = os.path.basename(TEST_TEXT)
TEST_VIDEO_NAME = os.path.basename(TEST_VIDEO)
TEST_OVERSIZED_VIDEO_NAME = os.path.basename(TEST_OVERSIZED_VIDEO)

ASSET_SOURCES = {
    TEST_IMAGE_NAME: "https://commons.wikimedia.org/wiki/Special:Redirect/file/Mosquito_biting.jpg",
    TEST_TEXT_NAME: "https://www.example.com/",
    TEST_VIDEO_NAME: "https://mp4.to/static/samples/mp4/sample-640x480.mp4",
    TEST_OVERSIZED_VIDEO_NAME: "https://cdn.sampleyogi.com/video/mp4/xl/mp4-99mb-sample.mp4",
}

TEST_DRONES = {
    "gallery": {
        "name": "UC06 Gallery Drone",
        "model": "DJI Mini 3",
        "serial": "UC06-GALLERY-001",
        "status": "Operational",
    },
    "empty": {
        "name": "UC06 Empty Drone",
        "model": "DJI Mini 3",
        "serial": "UC06-EMPTY-001",
        "status": "Operational",
    },
}


def ensure_test_assets():
    required_assets = [TEST_IMAGE, TEST_TEXT, TEST_VIDEO, TEST_OVERSIZED_VIDEO]
    missing_assets = [path for path in required_assets if not os.path.exists(path)]
    if missing_assets:
        missing_names = ", ".join(os.path.basename(path) for path in missing_assets)
        pytest.fail(f"Missing UC06 online test asset(s): {missing_names}. Expected under {ASSET_DIR}")


def save_evidence(driver, filename):
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    driver.save_screenshot(os.path.join(SCREENSHOT_DIR, filename))


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
        pass
    return alert_text


def api_script(method, path, body=None):
    return """
        const done = arguments[arguments.length - 1];
        const token = window.localStorage.getItem('token');
        fetch(arguments[0], {
            method: arguments[1],
            headers: {
                Authorization: `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: arguments[2] ? JSON.stringify(arguments[2]) : undefined,
        })
            .then(async (response) => {
                const data = await response.json().catch(() => ({}));
                done({ ok: response.ok, status: response.status, data });
            })
            .catch((error) => done({ ok: false, status: 0, error: error.message }));
    """, f"{API_URL}{path}", method, body


def create_drone_via_api(driver, drone_data):
    script, url, method, body = api_script("POST", "/drones/register", drone_data)
    result = driver.execute_async_script(script, url, method, body)
    if result.get("status") == 409:
        return find_drone_by_serial(driver, drone_data["serial"])
    if not result.get("ok"):
        pytest.fail(f"Failed to create test drone {drone_data['name']}: {result}")
    return result["data"]["drone"]


def find_drone_by_serial(driver, serial):
    script = """
        const done = arguments[arguments.length - 1];
        const token = window.localStorage.getItem('token');
        fetch(`${arguments[0]}/drones?limit=1000`, {
            headers: { Authorization: `Bearer ${token}` },
        })
            .then((response) => response.json())
            .then((data) => done((data.drones || []).find((drone) => drone.serial === arguments[1]) || null))
            .catch((error) => done({ error: error.message }));
    """
    result = driver.execute_async_script(script, API_URL, serial)
    if not result or result.get("error"):
        pytest.fail(f"Failed to find test drone with serial {serial}: {result}")
    return result


def cleanup_uc06_data(driver):
    result = driver.execute_async_script(
        """
        const done = arguments[arguments.length - 1];
        const token = window.localStorage.getItem('token');
        const testSerials = new Set(arguments[0]);

        fetch(`${arguments[1]}/drones?limit=1000`, {
            headers: { Authorization: `Bearer ${token}` },
        })
            .then((response) => response.json())
            .then(async (data) => {
                const targets = (data.drones || []).filter((drone) => testSerials.has(drone.serial));
                await Promise.all(targets.map(async (drone) => {
                    const imagesResponse = await fetch(`${arguments[1]}/drones/${drone.id}/images?limit=1000`, {
                        headers: { Authorization: `Bearer ${token}` },
                    });
                    const imagesData = await imagesResponse.json().catch(() => ({ images: [] }));
                    await Promise.all((imagesData.images || []).map((image) =>
                        fetch(`${arguments[1]}/drones/images/${image.id}`, {
                            method: 'DELETE',
                            headers: { Authorization: `Bearer ${token}` },
                        })
                    ));
                    return fetch(`${arguments[1]}/drones/${drone.id}`, {
                        method: 'DELETE',
                        headers: { Authorization: `Bearer ${token}` },
                    });
                }));
                done({ ok: true, deleted: targets.length });
            })
            .catch((error) => done({ ok: false, error: error.message }));
        """,
        [drone["serial"] for drone in TEST_DRONES.values()],
        API_URL,
    )
    if not result.get("ok"):
        pytest.fail(f"UC06 cleanup failed: {result}")


def login_and_open_drone_management(driver):
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys("admin1@drone4dengue.com")
    driver.find_element(By.ID, "password").send_keys("adminpass1")
    driver.find_element(By.XPATH, "//button[contains(text(), 'LOGIN')]").click()
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Dashboard')]")))
    driver.find_element(By.XPATH, "//a[@href='/drone-management']").click()
    wait.until(EC.url_contains("/drone-management"))
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Drone Management')]")))


def refresh_and_wait_for_drones(driver):
    driver.refresh()
    WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(., 'Drone Management')]")))
    WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, "//td[contains(., 'UC06 Gallery Drone')]")))


def select_drone_for_gallery(driver, drone_name):
    wait = WebDriverWait(driver, 15)
    row = wait.until(EC.visibility_of_element_located((By.XPATH, f"//tr[.//td[contains(., '{drone_name}')]]")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
    driver.execute_script("arguments[0].click();", row)
    select_element = wait.until(EC.presence_of_element_located((By.XPATH, "//h3[contains(., 'Drone Images')]/ancestor::div[contains(@class, 'bg-white')]//select")))
    wait.until(lambda _: drone_name in Select(select_element).first_selected_option.text)
    wait_for_gallery_idle(driver)


def wait_for_gallery_idle(driver):
    WebDriverWait(driver, 15).until_not(
        EC.presence_of_element_located((By.XPATH, "//p[normalize-space()='Loading images...']"))
    )


def open_add_images_modal(driver, drone_name):
    wait = WebDriverWait(driver, 15)
    row = wait.until(EC.visibility_of_element_located((By.XPATH, f"//tr[.//td[contains(., '{drone_name}')]]")))
    button = row.find_element(By.XPATH, ".//button[contains(., 'Add Images')]")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
    driver.execute_script("arguments[0].click();", button)
    return wait.until(
        EC.visibility_of_element_located((By.XPATH, f"//h2[contains(., 'Add Drone Images') and contains(., '{drone_name}')]/ancestor::div[contains(@class, 'bg-white')]"))
    )


def close_add_images_modal(driver):
    close_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//h2[contains(., 'Add Drone Images')]/following-sibling::button"))
    )
    driver.execute_script("arguments[0].click();", close_button)
    WebDriverWait(driver, 10).until_not(EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Add Drone Images')]")))


def upload_image_through_ui(driver, drone_name):
    wait = WebDriverWait(driver, 20)
    modal = open_add_images_modal(driver, drone_name)
    file_input = modal.find_element(By.ID, "media-upload")
    file_input.send_keys(TEST_IMAGE)
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h4[contains(., 'Image Upload')]")))
    save_evidence(driver, "TC-UC06-004_image_file_accepted.png")
    modal.find_element(By.XPATH, ".//button[contains(., 'Upload Image')]").click()
    alert = wait.until(EC.alert_is_present())
    alert_text = capture_alert_evidence_and_accept(driver, alert, "TC-UC06-004_upload_success_alert.png")
    assert "Image uploaded successfully" in alert_text
    close_add_images_modal(driver)
    select_drone_for_gallery(driver, drone_name)
    image_card = wait.until(EC.visibility_of_element_located((By.XPATH, f"//div[contains(., '{TEST_IMAGE_NAME}') and contains(., 'Direct upload')]")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", image_card)
    save_evidence(driver, "TC-UC06-004_uploaded_image_visible.png")


def get_first_test_image_card(driver):
    return WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.XPATH, f"//div[contains(., '{TEST_IMAGE_NAME}') and contains(., 'Direct upload')]/ancestor::div[contains(@class, 'group')][1]"))
    )


def click_image_card_button(driver, card, button_index):
    buttons = card.find_elements(By.XPATH, ".//button")
    if len(buttons) <= button_index:
        pytest.fail(f"Expected image card button index {button_index}, found {len(buttons)} buttons")
    driver.execute_script("arguments[0].click();", buttons[button_index])


@pytest.fixture(scope="module")
def driver():
    ensure_test_assets()
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    prefs = {
        "download.default_directory": os.path.abspath(SCREENSHOT_DIR),
        "download.prompt_for_download": False,
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(3)
    driver.set_script_timeout(60)
    login_and_open_drone_management(driver)
    cleanup_uc06_data(driver)
    create_drone_via_api(driver, TEST_DRONES["gallery"])
    create_drone_via_api(driver, TEST_DRONES["empty"])
    refresh_and_wait_for_drones(driver)
    yield driver
    cleanup_uc06_data(driver)
    driver.quit()


def test_tc_uc06_001_access_drone_images_section(driver):
    wait = WebDriverWait(driver, 15)
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h3[contains(., 'Drone Images')]")))
    wait.until(EC.presence_of_element_located((By.XPATH, "//h3[contains(., 'Drone Images')]/ancestor::div[contains(@class, 'bg-white')]//select")))
    save_evidence(driver, "TC-UC06-001_drone_images_section_visible.png")


def test_tc_uc06_003_empty_gallery_message(driver):
    select_drone_for_gallery(driver, TEST_DRONES["empty"]["name"])
    WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'No Images Available') or contains(text(), 'No images available for this drone')]")))
    save_evidence(driver, "TC-UC06-003_empty_gallery_message_visible.png")


def test_tc_uc06_004_upload_valid_image(driver):
    upload_image_through_ui(driver, TEST_DRONES["gallery"]["name"])


def test_tc_uc06_002_gallery_displays_uploaded_image(driver):
    select_drone_for_gallery(driver, TEST_DRONES["gallery"]["name"])
    get_first_test_image_card(driver)
    save_evidence(driver, "TC-UC06-002_gallery_image_card_visible.png")


def test_tc_uc06_005_reject_invalid_non_media_file(driver):
    modal = open_add_images_modal(driver, TEST_DRONES["gallery"]["name"])
    file_input = modal.find_element(By.ID, "media-upload")
    file_input.send_keys(TEST_TEXT)
    alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
    alert_text = capture_alert_evidence_and_accept(driver, alert, "TC-UC06-005_invalid_file_alert.png")
    assert "Please upload an image or video file" in alert_text
    save_evidence(driver, "TC-UC06-005_invalid_file_rejected_state.png")
    close_add_images_modal(driver)


def test_tc_uc06_006_process_valid_video(driver):
    modal = open_add_images_modal(driver, TEST_DRONES["gallery"]["name"])
    modal.find_element(By.ID, "media-upload").send_keys(TEST_VIDEO)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//h4[contains(., 'Video Processing')]")))
    save_evidence(driver, "TC-UC06-006_video_processing_panel_visible.png")
    modal.find_element(By.XPATH, ".//button[contains(., 'Process Video')]").click()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Extracting frames from video')]")))
    save_evidence(driver, "TC-UC06-006_video_extracting_frames_visible.png")
    alert = WebDriverWait(driver, 180).until(EC.alert_is_present())
    alert_text = capture_alert_evidence_and_accept(driver, alert, "TC-UC06-006_video_success_alert.png")
    assert "Successfully processed" in alert_text
    close_add_images_modal(driver)


def test_tc_uc06_007_reject_oversized_or_overduration_video(driver):
    modal = open_add_images_modal(driver, TEST_DRONES["gallery"]["name"])
    modal.find_element(By.ID, "media-upload").send_keys(TEST_OVERSIZED_VIDEO)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(), '{TEST_OVERSIZED_VIDEO_NAME}')]"))
    )
    save_evidence(driver, "TC-UC06-007_oversized_video_accepted_defect.png")
    close_add_images_modal(driver)
    pytest.xfail("Known defect: current UI accepts a >50MB video file instead of rejecting it before processing.")


def test_tc_uc06_008_preview_captured_image(driver):
    select_drone_for_gallery(driver, TEST_DRONES["gallery"]["name"])
    card = get_first_test_image_card(driver)
    click_image_card_button(driver, card, 0)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//img[@alt='Drone capture']")))
    save_evidence(driver, "TC-UC06-008_image_preview_modal_visible.png")
    close_button = driver.find_element(By.XPATH, "//img[@alt='Drone capture']/ancestor::div[contains(@class, 'relative')]//button[1]")
    driver.execute_script("arguments[0].click();", close_button)


def test_tc_uc06_009_download_captured_image(driver):
    select_drone_for_gallery(driver, TEST_DRONES["gallery"]["name"])
    card = get_first_test_image_card(driver)
    click_image_card_button(driver, card, 1)
    time.sleep(2)
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()
        save_evidence(driver, "TC-UC06-009_download_error_alert_defect.png")
        pytest.xfail(f"Known defect: download action shows error alert: {alert_text}")
    except NoAlertPresentException:
        save_evidence(driver, "TC-UC06-009_download_action_completed_no_error.png")


def test_tc_uc06_010_cancel_image_deletion(driver):
    select_drone_for_gallery(driver, TEST_DRONES["gallery"]["name"])
    card = get_first_test_image_card(driver)
    click_image_card_button(driver, card, 2)
    dialog = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//h2[contains(., 'Delete Image')]/ancestor::div[contains(@class, 'bg-white')]")))
    save_evidence(driver, "TC-UC06-010_delete_confirmation_visible.png")
    dialog.find_element(By.XPATH, ".//button[contains(., 'Cancel')]").click()
    WebDriverWait(driver, 10).until_not(EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Delete Image')]")))
    get_first_test_image_card(driver)
    save_evidence(driver, "TC-UC06-010_image_remains_after_cancel.png")


def test_tc_uc06_011_confirm_image_deletion(driver):
    select_drone_for_gallery(driver, TEST_DRONES["gallery"]["name"])
    card = get_first_test_image_card(driver)
    click_image_card_button(driver, card, 2)
    dialog = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//h2[contains(., 'Delete Image')]/ancestor::div[contains(@class, 'bg-white')]")))
    save_evidence(driver, "TC-UC06-011_delete_confirmation_visible.png")
    dialog.find_element(By.XPATH, ".//button[contains(., 'Delete')]").click()
    success_dialog = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Image deleted successfully')]/ancestor::div[contains(@class, 'bg-white')]")))
    save_evidence(driver, "TC-UC06-011_delete_success_visible.png")
    success_dialog.find_element(By.XPATH, ".//button[contains(., 'Great') or contains(., 'OK')]").click()
    WebDriverWait(driver, 15).until_not(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{TEST_IMAGE_NAME}')]")))
    save_evidence(driver, "TC-UC06-011_image_removed_from_gallery.png")


def test_tc_uc06_012_image_transaction_failure_stable(driver):
    select_drone_for_gallery(driver, TEST_DRONES["gallery"]["name"])
    result = driver.execute_async_script(
        """
        const done = arguments[arguments.length - 1];
        const token = window.localStorage.getItem('token');
        fetch(`${arguments[0]}/drones/images/not-a-real-image-id/download`, {
            headers: { Authorization: `Bearer ${token}` },
        })
            .then(async (response) => done({ ok: response.ok, status: response.status }))
            .catch((error) => done({ ok: false, status: 0, error: error.message }));
        """,
        API_URL,
    )
    assert result["ok"] is False
    assert result["status"] in [0, 404, 500]
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//h3[contains(., 'Drone Images')]")))
    save_evidence(driver, "TC-UC06-012_failed_transaction_page_stable.png")
