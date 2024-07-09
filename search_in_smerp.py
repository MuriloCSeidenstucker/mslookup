import logging
import re

from typing import Dict, List, Tuple, Union
from logger_config import main_logger
from urllib.parse import urlparse
from unidecode import unidecode
from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import (visibility_of_element_located,
                                                            presence_of_element_located)

class SearchInSmerp:
    def __init__(self):
        self.logger = logging.getLogger(f'main_logger.{self.__class__.__name__}')
    
    def configure_chrome_options(self, detach: bool = False) -> webdriver.ChromeOptions:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("detach", detach)
        return chrome_options
    
    def perform_google_search(self, driver: webdriver, wait: WebDriverWait, description: str, brand: Union[Dict, str]) -> None:
        driver.get("https://www.google.com/")
        
        search_input_locator = (By.CSS_SELECTOR, 'div textarea')
        search_input = wait.until(visibility_of_element_located(search_input_locator), 'Elemento não encontrado')
        search_input.send_keys(f"registro anvisa {description} {brand} smerp")

        submit_button_locator = (By.XPATH, '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[4]/center/input[1]')
        submit_button = wait.until(visibility_of_element_located(submit_button_locator), 'Elemento não encontrado')
        submit_button.click()
        
    def get_smerp_urls(self, driver: webdriver, wait: WebDriverWait) -> List[str]:
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
    
    def find_matching_smerp_entry(self, driver: webdriver, wait: WebDriverWait, brand: Union[Dict, str], smerp_urls: List[str]) -> Tuple[bool, str]:
        dataset_locator = (By.CSS_SELECTOR, '.dataset')
        matchesURL = False
        message = ''
        for url in smerp_urls:
            url.click()
            dataset = wait.until(presence_of_element_located(dataset_locator), 'Elemento não encontrado')
            
            ref_date_str = dataset.find_element(By.XPATH, "//div[contains(text(), 'Validade/Situação')]/following-sibling::div/span").text
            try:
                ref_date = datetime.strptime(ref_date_str, '%d/%m/%Y')
                if ref_date < datetime.now():
                    message = 'Registro vencido para o item:'
                    driver.back()
                    continue
            except Exception as e:
                print(f'Data consta como:{ref_date_str}. Formato incorreto')
            
            smerp_brand = dataset.find_element(By.XPATH, "//div[contains(text(), 'Nome da Empresa/Detentor')]/following-sibling::div").text
            if unidecode(brand).lower() in unidecode(smerp_brand).lower():
                matchesURL = True
                break
            else:
                message = 'Marca não encontrada para o item:'
                driver.back()
                
        return matchesURL, message
    
    def extract_process_number(self, wait: WebDriverWait) -> str:
        dataset_locator = (By.CSS_SELECTOR, '.dataset')
        dataset = wait.until(presence_of_element_located(dataset_locator), 'Elemento não encontrado')
        process_number_extracted = dataset.find_element(By.XPATH, "//div[contains(text(), 'Processo')]/following-sibling::div").text
        pattern = r'\D'
        process_number_formatted = re.sub(pattern, '', process_number_extracted)
        return process_number_formatted
    
    def extract_register(self, wait: WebDriverWait) -> str:
        dataset_locator = (By.CSS_SELECTOR, '.dataset')
        dataset = wait.until(presence_of_element_located(dataset_locator), 'Elemento não encontrado')
        register = dataset.find_element(By.XPATH, "//div[contains(text(), 'Registro')]/following-sibling::div").text[:9]
        return register
    
    def extract_expiration_date(self, wait: WebDriverWait) -> str:
        dataset_locator = (By.CSS_SELECTOR, '.dataset')
        dataset = wait.until(presence_of_element_located(dataset_locator), 'Elemento não encontrado')
        expiration_date = dataset.find_element(By.XPATH, "//div[contains(text(), 'Validade/Situação')]/following-sibling::div/span").text
        return expiration_date
    
    def get_data_from_smerp(self, description: str, brand: Union[Dict, str]) -> List[Dict[str, str]]:
        reg_candidates = []
        b = brand if isinstance(brand, str) else brand['Name']
        
        chrome_options = self.configure_chrome_options()
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, timeout=10)

        try:
            self.perform_google_search(driver, wait, description, b)
        except TimeoutException as e:
            self.logger.error('Timeout while performing Google search: %s', e.msg)
            driver.quit()
            return reg_candidates
        except Exception as e:
            self.logger.error('Unexpected error while performing Google search: %s', e.msg)
            driver.quit()
            return reg_candidates
                
        smerp_urls = self.get_smerp_urls(driver, wait)
        
        try:
            matchesURL, m = self.find_matching_smerp_entry(driver, wait, b, smerp_urls)
        except TimeoutException as e:
            self.logger.error('Timeout while finding matching SMERP entry: %s', e.msg)
            driver.quit()
            return reg_candidates
        except Exception as e:
            self.logger.error('Error while finding matching SMERP entry: %s', e.msg)
            driver.quit()
            return reg_candidates
            
        if not matchesURL:
            driver.quit()
            self.logger.info('No matching URL found in SMERP.')
            return reg_candidates
        
        try:
            process_number = self.extract_process_number(wait)
            register = self.extract_register(wait)
            expiration_date = self.extract_expiration_date(wait)
        except TimeoutException as e:
            self.logger.error('Timeout while extracting data from SMERP: %s', e.msg)
            return reg_candidates
        except Exception as e:
            self.logger.error('Error while extracting data from SMERP: %s', e.msg)
            return reg_candidates
        finally:
            driver.quit()
        
        reg_candidates.append(
            {
                'register': register,
                'process_number': process_number,
                'expiration_date': expiration_date
            }
        )
        return reg_candidates
