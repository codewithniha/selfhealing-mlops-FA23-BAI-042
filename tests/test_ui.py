import pytest
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")

def test_frontend_sentiment():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(BASE_URL)

        # Find the input and type a sentence
        text_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "text-input"))
        )
        text_input.send_keys("The cinematography was breathtaking and the performances were outstanding")

        # Click the submit button
        submit_btn = driver.find_element(By.ID, "submit-btn")
        submit_btn.click()

        # Wait for result and assert it is non-empty and contains expected text
        result_output = WebDriverWait(driver, 15).until(
            EC.text_to_be_present_in_element((By.ID, "result-output"), "")
        )

        result_text = driver.find_element(By.ID, "result-output").text
        assert len(result_text) > 0
        assert any(word in result_text for word in ["POSITIVE", "NEGATIVE", "Confidence"])

    finally:
        driver.quit()
