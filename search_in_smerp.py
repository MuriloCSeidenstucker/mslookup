from datetime import datetime
import re
import json
from time import sleep, time
from urllib.parse import urlparse
from unidecode import unidecode
from utils import Utils

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import (visibility_of_element_located,
                                                            presence_of_element_located)

class SearchInSmerp:
    
    def configure_chrome_options(self, detach=False):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("detach", detach)
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
        message = ''
        for url in smerp_urls:
            url.click()
            dataset = wait.until(presence_of_element_located(dataset_locator), 'Elemento não encontrado')
            
            ref_date_str = dataset.find_element(By.XPATH, "//div[contains(text(), 'Validade/Situação')]/following-sibling::div/span").text
            ref_date = datetime.strptime(ref_date_str, '%d/%m/%Y')
            if ref_date < datetime.now():
                message = 'Registro vencido para o item:'
                driver.back()
                continue
            
            smerp_brand = dataset.find_element(By.XPATH, "//div[contains(text(), 'Nome da Empresa/Detentor')]/following-sibling::div").text
            if unidecode(brand).lower() in unidecode(smerp_brand).lower():
                matchesURL = True
                break
            else:
                message = 'Marca não encontrada para o item:'
                driver.back()
                
        return matchesURL, message
    
    def extract_process_number(self, wait):
        dataset_locator = (By.CSS_SELECTOR, '.dataset')
        dataset = wait.until(presence_of_element_located(dataset_locator), 'Elemento não encontrado')
        process_number_extracted = dataset.find_element(By.XPATH, "//div[contains(text(), 'Processo')]/following-sibling::div").text
        pattern = r'\D'
        process_number_formatted = re.sub(pattern, '', process_number_extracted)
        return process_number_formatted
    
    def extract_register(self, wait):
        dataset_locator = (By.CSS_SELECTOR, '.dataset')
        dataset = wait.until(presence_of_element_located(dataset_locator), 'Elemento não encontrado')
        register = dataset.find_element(By.XPATH, "//div[contains(text(), 'Registro')]/following-sibling::div").text[:9]
        return register
    
    def get_data_from_smerp(self, item, name, brand):
        
        b = brand if isinstance(brand, str) else brand['Name']
        
        chrome_options = self.configure_chrome_options()

        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, timeout=10)
        # Utils.resize_window(driver)

        try:
            self.perform_google_search(driver, wait, name, b)
        except TimeoutException as e:
            print('Erro ao tentar realizar a busca no Google')
                
        smerp_urls = self.get_smerp_urls(driver, wait)
        
        matchesURL, m = self.find_matching_smerp_entry(driver, wait, b, smerp_urls)
        if not matchesURL:
            print(f'{m} {item}')
            return -1, -1
        
        process_number = self.extract_process_number(wait)
        register = self.extract_register(wait)
            
        driver.quit()
        return register, process_number
