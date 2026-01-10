import json
import copy
from pathlib import Path
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import time
import asyncio
from web_data_handling.tranform_data import *
from dotenv import load_dotenv
import os

class SiteJob:
    def __init__(self, config: dict):
        self.config = config
        self.extraction_fields = {k: None for k, v in config["fields"].items()}

    def scrape(self, driver, url):
        property_data = None
       
        # url =  self.config["base_url"]
        if self.config["from_script"] == "true":
            property_data = retrieve_from_script(driver=driver, url = url, script_name=self.config["script_name"], global_tags=self.config["global_tags"])

            for k,v in self.extraction_fields.items():
                try:
                    target_fields = self.config["fields"][k]['keys']
                    
                    nested_field = property_data[target_fields.pop(0)]

                    for key in target_fields:
                        
                        nested_field = nested_field[key]
                        if isinstance(nested_field, str):
                            try:
                                nested_field = json.loads(nested_field)
                                
                            except json.JSONDecodeError:
                                break
                except KeyError as e:
                    print(f"Error: {e}")
                    continue

                self.extraction_fields[k] = nested_field
                
        

    def transform(self, data):
        pass

    def load(self, data):
        pass

    def run(self):
        pass

def load_config(file_path):
    config_file = None 
    with open(file_path, "r") as file:
        config_file = json.load(file)

    if config_file["use_api"] == "true":
        config_file["api_key"] = os.getenv(config_file["api_key_name"])

    return config_file

async def extract_listing_pages(driver, links, config):
    all_listings = []
    
    for link in links:
        driver.get(link)
        
        try:
            _wait_for_element_presence(driver=driver, locator=(By.CSS_SELECTOR, config["listing_card_selector"]))
        except TimeoutException:
                print(f"Timeout waiting for listings on {link}")
                continue
            
            # Get all property listing links directly
            # This avoids the carousel clones issue
        link_elements = driver.find_elements(By.CSS_SELECTOR, 'a.address')
        
        # Remove duplicates (carousel creates clones)
        unique_urls = set()
        for link_element in link_elements:
            try:
                url = link_element.get_attribute('href')
                if url:
                    unique_urls.add(url)
            except Exception as e:
                print(f"Error: {e}")
                continue
        
        all_listings.extend(list(unique_urls))
    return all_listings


def _wait_for_element_presence(driver, locator: tuple[str, str], timeout = 10,):
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
    
def _wait_for_element_visibility(driver, locator: tuple[str, str], timeout = 10):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(locator)
    )

def _wait_for_element_clickable(driver, locator: tuple[str, str], timeout = 10):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(locator)
    )


async def main():
    options = Options()
    options.add_argument("--headless")

    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(options=options, service=service)

    

    config_files = ["./extraction_configs/domain.json"]

    configs = [load_config(path) for path in config_files ]

    #TODO: Dynamically handling configs for different site configs

    target_urls = [config["base_url"] + target + config["location_tags"] for config in configs for target in config["target_property_type"] ]

    target_links = [await extract_listing_pages(driver=driver, links=target_urls, config=config) for config in configs]

    


    
    for links in target_links:

        for link in links:
            print(link)
            job = SiteJob(config=load_config(config_files[0]))
            print(job)
            result = job.scrape(driver=driver, url=link)
            with open("./results.json", "a") as f:
                f.write("\n\n=======NEW RESULTS=======\n\n")
                json.dump(job.extraction_fields, fp=f, indent=4)


if __name__ == "__main__":
    asyncio.run(main())


    '''TODO:
     - Automate this part and spin up jenkins in homelab:
        * continue development with CICD setup
        * write tests jenkins can use (check data formatting and other deterministic stuff)

    - Transform scraped data:
        * Normalise fields
        * Then dedup results of entire scrape 

   

    TODO: LATER (this part should done when CICD is up and running)
    - Write webscraping -> extract -> clean logic for html/js scraped data:
        * Use selenium to load scripts on property listing pages
        * soup to grab tags by css or html
        * store in dataframe
        * normalise and load data from 
        * dedup rows then dedup entries

    '''
    




