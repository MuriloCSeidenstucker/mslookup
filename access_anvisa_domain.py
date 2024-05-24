import json
import re
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

class AnvisaDomain:        
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
        
    def get_process_number(self, driver, wait, register):
        register_url = rf'https://consultas.anvisa.gov.br/#/medicamentos/q/?numeroRegistro={register}'
        driver.get(register_url)
        
        locator = (By.XPATH, f"//td[contains(text(), '{register}')]/following-sibling::td")
        process_number = wait.until(presence_of_element_located(locator), "Elemento não encontrado").text
        
        pattern = r'\D'
        return re.sub(pattern, '', process_number)
    
    def try_print_anvisa_register(self, driver, wait, anvisa_medicamento_url, process_number_formatted):
        driver.get(rf'{anvisa_medicamento_url}{process_number_formatted}/')
        try:
            number_is_present = wait.until(self.process_number_to_be_present)
            anvisa_process_number = driver.find_element(By.XPATH, "//th[contains(text(), 'Processo')]/following-sibling::td/a").text if number_is_present else ''
            pattern = r'\D'
            anvisa_process_number_formatted = re.sub(pattern, '', anvisa_process_number)
            if process_number_formatted == anvisa_process_number_formatted:
                driver.execute_script('window.print();')
                sleep(0.5)
                return True
            else:
                print(f'O número do processo constante na Anvisa está diferente')
                return False
        except TimeoutException as e:
            print(rf'Erro ao tentar a impressão de: {anvisa_medicamento_url}{process_number_formatted}/')
            return False
        
    def get_register_as_pdf(self, register, process_number=None):
        anvisa_medicamentos_url = r'https://consultas.anvisa.gov.br/#/medicamentos/'
        
        chrome_options = self.configure_chrome_options(detach=True)
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, timeout=10)
        
        defined_process_number = (process_number if not process_number is None
                                  else self.get_process_number(driver, wait, register))
        
        success = self.try_print_anvisa_register(driver, wait, anvisa_medicamentos_url, defined_process_number)
        if not success:
            print(f'Não foi possível obter o registro: {register}')
            driver.quit()
            return False
            
        driver.quit()
        return True