import re
import json
from time import sleep, time
from urllib.parse import urlparse
from utils import Utils

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import (visibility_of_element_located,
                                                            presence_of_element_located,
                                                            text_to_be_present_in_element)

class SearchAndPrint:
    
    def configure_chrome_options(self, detach=False):
        chrome_options = webdriver.ChromeOptions()
        settings = {
            "recentDestinations": [{
                    "id": "Save as PDF",
                    "origin": "local",
                    "account": ""
                }],
                "selectedDestinationId": "Save as PDF",
                "version": 2
            }
        prefs = {'printing.print_preview_sticky_settings.appState': json.dumps(settings)}
        chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_experimental_option("detach", detach)
        chrome_options.add_argument('--kiosk-printing')
        return chrome_options
    
    def perform_google_search(self, driver, wait, name, brand):
        driver.get("https://www.google.com/")
        
        search_input_locator = (By.CSS_SELECTOR, 'div textarea')
        search_input = wait.until(visibility_of_element_located(search_input_locator), 'Elemento não encontrado')
        search_input.send_keys(f"registro anvisa {name} {brand}")

        submit_button_locator = (By.XPATH, '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[4]/center/input[1]')
        submit_button = wait.until(visibility_of_element_located(submit_button_locator), 'Elemento não encontrado')
        submit_button.click()
        
    def get_smerp_urls(self, driver, wait):
        center_col_locator = (By.ID, "center_col")
        center_col = wait.until(presence_of_element_located(center_col_locator), "Elemento não encontrado")
        height = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(1280,height+100)
        sleep(1)
        a_elements = center_col.find_elements(By.TAG_NAME, "a")

        smerp_urls = []
        for element in a_elements:
            url = urlparse(element.get_attribute("href")).netloc
            if isinstance(url, str):
                if "smerp" in url:
                    smerp_urls.append(element)
        return smerp_urls
    
    def find_matching_smerp_entry(self, driver, wait, brand, smerp_urls):
        dataset_locator = (By.CSS_SELECTOR, '.dataset')
        matchesURL = False
        for url in smerp_urls:
            url.click()
            dataset = wait.until(presence_of_element_located(dataset_locator), 'Elemento não encontrado')
            smerp_brand = dataset.find_element(By.XPATH, "//div[contains(text(), 'Nome da Empresa/Detentor')]/following-sibling::div").text
            print(f'Marca: {brand}, Smerp: {smerp_brand}, Iguais: {brand.lower() in smerp_brand.lower()}')
            if brand.lower() in smerp_brand.lower():
                matchesURL = True
                break
            else:
                driver.back()
        return matchesURL
    
    def extract_process_number(self, wait):
        dataset_locator = (By.CSS_SELECTOR, '.dataset')
        dataset = wait.until(presence_of_element_located(dataset_locator), 'Elemento não encontrado')
        process_number_extracted = dataset.find_element(By.XPATH, "//div[contains(text(), 'Processo')]/following-sibling::div").text
        pattern = r'\D'
        process_number_formatted = re.sub(pattern, '', process_number_extracted)
        return process_number_extracted, process_number_formatted
    
    def try_print_anvisa_register(self, driver, wait, anvisa_medicamento_url, process_number_extracted, process_number_formatted):
        driver.get(rf'{anvisa_medicamento_url}{process_number_formatted}/')
        try:
            number_locator = (By.XPATH, "//th[contains(text(), 'Processo')]/following-sibling::td/a")
            numberIsPresent = wait.until(text_to_be_present_in_element(number_locator, process_number_extracted), 'Elemento não encontrado')
            if numberIsPresent:
                driver.execute_script('window.print();')
                sleep(0.5)
        except TimeoutException as e:
            print(rf'Erro ao tentar a impressão de: {anvisa_medicamento_url}{process_number_formatted}/')
            return False
    
    def get_register_as_pdf(self, item, name, brand):
        
        chrome_options = self.configure_chrome_options()

        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, timeout=10)
        Utils.resize_window(driver)
        
        anvisa_medicamento_url = r'https://consultas.anvisa.gov.br/#/medicamentos/'

        self.perform_google_search(driver, wait, name, brand)
        smerp_urls = self.get_smerp_urls(driver, wait)
        
        matchesURL = self.find_matching_smerp_entry(driver, wait, brand, smerp_urls)
        if not matchesURL:
            print(f'Item {item}: Não encontrado')
            return False
        
        process_number_extracted, process_number_formatted = self.extract_process_number(wait)
        
        self.try_print_anvisa_register(driver, wait, anvisa_medicamento_url, process_number_extracted, process_number_formatted)
            
        driver.quit()
        return True
