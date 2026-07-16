import pytest
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shutil

# Use EC2 public IP so Chrome container can reach the app
BASE_URL = os.environ.get("BASE_URL", "http://44.220.57.88:32500")

def test_frontend_sentiment():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    chromedriver = (
        shutil.which("chromedriver") or
        shutil.which("chromium-driver") or
        "/usr/bin/chromedriver"
    )
    service = Service(executable_path=chromedriver)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(BASE_URL)

        text_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "text-input"))
        )
        text_input.clear()
        text_input.send_keys(
            "The cinematography was breathtaking "
            "and the performances were outstanding"
        )

        submit_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submit-btn"))
        )
        submit_btn.click()

        WebDriverWait(driver, 15).until(
            lambda d: len(
                d.find_element(By.ID, "result-output").text.strip()
            ) > 0
        )

        result_text = driver.find_element(By.ID, "result-output").text
        assert len(result_text) > 0
        assert any(word in result_text for word in
                   ["POSITIVE", "NEGATIVE", "Confidence"])

    finally:
        driver.quit()
