import os
import re
import json
import logging

from time import sleep
from logger_config import main_logger

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

from utils import Utils
from pdf_manager import PDFManager

class AnvisaDomain:
    def __init__(self) -> None:
        self.logger = logging.getLogger(f'main_logger.{self.__class__.__name__}')
        self.pdf_manager = PDFManager()
    
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
    
    def process_number_to_be_present(self, webdriver):
        process_number = webdriver.find_element(By.XPATH, "//th[contains(text(), 'Processo')]/following-sibling::td/a").text
        return isinstance(process_number, str) and process_number
    
    def registration_to_be_present(self, webdriver):
        reg_found = webdriver.find_element(By.XPATH, '//*[@id="containerTable"]/table/tbody/tr[2]/td[5]').text
        return isinstance(reg_found, str) and reg_found
        
    def get_process_number(self, driver, wait, register):
        register_url = rf'https://consultas.anvisa.gov.br/#/medicamentos/q/?numeroRegistro={register}'
        driver.get(register_url)
        
        locator = (By.XPATH, f"//td[contains(text(), '{register}')]/following-sibling::td")
        process_number = wait.until(presence_of_element_located(locator), "Elemento não encontrado").text
        
        pattern = r'\D'
        return re.sub(pattern, '', process_number)
        
    # def try_print_anvisa_register(self, driver, wait, anvisa_medicamento_url, a_concentration, register):
    #     driver.get(rf'{anvisa_medicamento_url}{register}')
        
    #     try:
    #         registration_is_present = wait.until(self.registration_to_be_present)
    #         reg_btn = driver.find_element(By.XPATH, '//*[@id="containerTable"]/table/tbody/tr[2]')
    #         reg_btn.click()
            
    #         page_is_loaded = wait.until(self.process_number_to_be_present)
    #         presentations = driver.find_elements(By.CSS_SELECTOR, '.col-xs-4.ng-binding')
    #         match = any(Utils.remove_accents_and_spaces(a_concentration) in
    #                     Utils.remove_accents_and_spaces(presentation.text)
    #                     for presentation in presentations)
            
    #         register_found = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/form/div[1]/div[2]/table/tbody/tr[3]/td[2]').text
    #         if register_found == register and match:
    #             driver.execute_script('window.print();')
    #             sleep(0.5)
    #             return True
    #         else:
    #             print(f'O número do processo constante na Anvisa está diferente')
    #             return False
    #     except TimeoutException as e:
    #         print(rf'Erro ao tentar a impressão de: {anvisa_medicamento_url}{register}/')
    #         return False
    
    def try_print_anvisa_register(self, driver, wait, anvisa_medicamento_url, a_concentration, register):
        url = rf'{anvisa_medicamento_url}{register}'
        driver.get(url)
        
        try:
            if not self.wait_for_registration_presence(wait, url):
                return False
            
            if not self.click_registration_button(driver, url):
                return False
            
            if not self.wait_for_page_load(wait):
                return False
            
            if not self.verify_concentration(driver, a_concentration):
                return False
            
            if not self.verify_registration(driver, register):
                return False
            
            self.print_page(driver)
            
            if not self.pdf_manager.pdf_was_printed():
                self.logger.warning('The printed pdf was not found in the download folder')
                return False
            
            self.logger.info(f'Registration: {register} printed successfully')
            return True
        except TimeoutException:
            self.logger.error(f'Error trying to print: {register}')
            return False
        
    def wait_for_registration_presence(self, wait, url):
        try:
            wait.until(self.registration_to_be_present)
            return True
        except TimeoutException:
            self.logger.error(f'Registration not found on the page: {url}')
            return False
        
    def click_registration_button(self, driver, url):
        try:
            reg_btn = driver.find_element(By.XPATH, '//*[@id="containerTable"]/table/tbody/tr[2]')
            reg_btn.click()
            return True
        except Exception as e:
            self.logger.error(f'Error when clicking the registration button on the page: {url}')
            return False
        
    def wait_for_page_load(self, wait):
        try:
            wait.until(self.process_number_to_be_present)
            return True
        except TimeoutException:
            self.logger.error('The page did not fully load')
            return False
        
    def verify_concentration(self, driver, a_concentration):
        try:
            presentations = driver.find_elements(By.CSS_SELECTOR, '.col-xs-4.ng-binding')
            match = any(Utils.remove_accents_and_spaces(a_concentration) in
                        Utils.remove_accents_and_spaces(presentation.text)
                        for presentation in presentations)
            
            if match:
                return True
            else:
                self.logger.warning('Concentration found does not match')
                return False
        except Exception as e:
            self.logger.error(f'Error verifying concentration: {e}')
            return False
        
    def verify_registration(self, driver, register):
        try:
            register_found = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/form/div[1]/div[2]/table/tbody/tr[3]/td[2]').text
            if register_found == register:
                return True
            else:
                self.logger.warning('The registration found on the Anvisa page does not match')
                return False
        except Exception as e:
            self.logger.error(f'Error verifying registration: {e}')
            return False
        
    def print_page(self, driver):
        driver.execute_script('window.print();')
        sleep(0.5)
        
    def get_register_as_pdf(self, register, a_concentration, process_number=None):
        anvisa_medicamentos_url = r'https://consultas.anvisa.gov.br/#/medicamentos/q/?numeroRegistro='
        
        chrome_options = self.configure_chrome_options(detach=True)
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, timeout=10)
        
        defined_process_number = (process_number if not process_number is None
                                  else self.get_process_number(driver, wait, register))
        
        success = self.try_print_anvisa_register(driver, wait, anvisa_medicamentos_url, a_concentration, register)
        if not success:
            self.logger.error(f'Failed to obtain the registration {register} as a PDF')
            driver.quit()
            return False
            
        driver.quit()
        return True