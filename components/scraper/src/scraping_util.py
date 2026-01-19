from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

def retrieve_from_script(driver, url: str, script_name: str, global_tags: list = [], timeout: int = 20):
    driver.get(url)
    time.sleep(5)
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, script_name)))

    except TimeoutException:
        print(f"Timeout waiting for {script_name}") 

    element = driver.find_element(By.ID, script_name).get_attribute('textContent')
    json_element = decode_nested_json(element)


    for tag in global_tags:
        json_element = json_element[tag]

def decode_nested_json(obj):
    if isinstance(obj, str):
        try:
            return decode_nested_json(json.loads(obj))
        except json.JSONDecodeError:
            return obj

    if isinstance(obj, dict):
        return {k: decode_nested_json(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [decode_nested_json(v) for v in obj]

    return obj