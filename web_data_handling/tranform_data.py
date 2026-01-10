from selenium import webdriver
from .scraping_util import *
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

    return json_element

def fetch_html_with_js(driver, url, wait_for_selectors: list = None, timeout: int = 20, scroll: bool = False, button: list = None):

    driver.get(url)

    time.sleep(5)


    if wait_for_selectors:
        
        for elem in wait_for_selectors:
            try:
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, elem))
                )
                
            except TimeoutException:
                print(f"Timeout waiting for {elem}")

    if button:
        for b in button:
            click_all_load_more(driver, b)

    if scroll:
        scroll_to_bottom(driver)
            
    
    

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(0.5)

    html_string = driver.page_source
    soup = BeautifulSoup(html_string, "lxml")
    return soup


def normalise_target( target):

    
    if isinstance(target, str):
        return target

    if "attr" in target:
        if "value" in target:
            return f"[{target['attr']}='{target['value']}']"
        else:
            return f"[{target['attr']}]"

    if "class" in target:
        return f".{target['class']}"

    raise ValueError(f"Unsupported target format: {target}")

def extract_fields( dom, selector_map: dict):

    extracted_data = {}

    for selector, field in selector_map.items():
        data = dom.select(selector)
        for d in data:
            print(d.parent)
            if field not in extracted_data:
                extracted_data[field] = []
            extracted_data[field].append(d.text) 

    return extracted_data






'''
"h2.residential-card__address-heading a"

"span.property-price"

"li.styles__Li-sc-xhfhyt-0.iMbEAF"

'''