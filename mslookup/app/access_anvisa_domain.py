import json
import logging
import re
from time import sleep
from typing import Dict, List, Tuple, Union

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.expected_conditions import \
    presence_of_element_located
from selenium.webdriver.support.wait import WebDriverWait

from mslookup.app.logger_config import configure_logging
from mslookup.app.pdf_manager import PDFManager
from mslookup.app.utils import Utils


class AnvisaDomain:
    def __init__(self, pdf_manager: PDFManager) -> None:
        configure_logging()
        self.name = self.__class__.__name__
        logging.info(f'{self.name}: Instantiated.')
        
        self.pdf_manager = pdf_manager

    def configure_chrome_options(
        self, detach: bool = False
    ) -> webdriver.ChromeOptions:
        chrome_options = webdriver.ChromeOptions()
        settings = {
            'recentDestinations': [
                {'id': 'Save as PDF', 'origin': 'local', 'account': ''}
            ],
            'selectedDestinationId': 'Save as PDF',
            'version': 2,
        }
        prefs = {
            'printing.print_preview_sticky_settings.appState': json.dumps(
                settings
            )
        }
        chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_experimental_option('detach', detach)
        chrome_options.add_argument('--kiosk-printing')
        return chrome_options

    def process_number_to_be_present(self, webdriver: webdriver) -> bool:
        process_number = webdriver.find_element(
            By.XPATH,
            "//th[contains(text(), 'Processo')]/following-sibling::td/a",
        ).text
        return isinstance(process_number, str) and process_number

    def registration_to_be_present(self, webdriver: webdriver) -> bool:
        reg_found = webdriver.find_element(
            By.XPATH, '//*[@id="containerTable"]/table/tbody/tr[2]/td[5]'
        ).text
        return isinstance(reg_found, str) and reg_found

    def get_process_number(
        self, driver: webdriver, wait: WebDriverWait, register: str
    ) -> str:
        register_url = rf'https://consultas.anvisa.gov.br/#/medicamentos/q/?numeroRegistro={register}'
        driver.get(register_url)

        locator = (
            By.XPATH,
            f"//td[contains(text(), '{register}')]/following-sibling::td",
        )
        process_number = wait.until(
            presence_of_element_located(locator), 'Elemento não encontrado'
        ).text

        pattern = r'\D'
        return re.sub(pattern, '', process_number)

    def try_print_anvisa_register(
        self,
        driver: webdriver,
        wait: WebDriverWait,
        anvisa_medicamento_url: str,
        concentration: str,
        register: str,
        exp_date: str,
        reg_data: Dict[str, Dict[str, Union[str, List[str]]]],
    ) -> bool:
        
        presentation = None
        url = rf'{anvisa_medicamento_url}{register}'
        driver.get(url)

        try:
            if not self.wait_for_registration_presence(wait, url):
                return False, presentation

            if not self.click_registration_button(driver, url):
                return False, presentation

            if not self.wait_for_page_load(wait):
                return False, presentation

            concentration_matches, presentations = self.verify_concentration(
                driver, concentration
            )
            if not concentration_matches:
                return False, presentation

            if not self.verify_registration(driver, register):
                return False, presentation

            self.print_page(driver)

            if not self.pdf_manager.pdf_was_printed():
                logging.warning(
                    f'{self.name}: The printed pdf was not found in the download folder'
                )
                return False, presentation

            reg_data[str(register)] = {
                'expiration_date': exp_date,
                'presentations': presentations,
            }
            
            presentation = self.get_presentation(concentration, presentations)

            return True, presentation
        except TimeoutException:
            logging.error(f'{self.name}: Error trying to print: {register}')
            return False, presentation

    def wait_for_registration_presence(
        self, wait: WebDriverWait, url: str
    ) -> bool:
        try:
            wait.until(self.registration_to_be_present)
            return True
        except TimeoutException:
            logging.error(f'{self.name}: Registration not found on the page: {url}')
            return False

    def click_registration_button(self, driver: webdriver, url: str) -> bool:
        try:
            reg_btn = driver.find_element(
                By.XPATH, '//*[@id="containerTable"]/table/tbody/tr[2]'
            )
            reg_btn.click()
            return True
        except Exception:
            logging.error(
                f'{self.name}: Error when clicking the registration button on the page: {url}'
            )
            return False

    def wait_for_page_load(self, wait: WebDriverWait) -> bool:
        try:
            wait.until(self.process_number_to_be_present)
            return True
        except TimeoutException:
            logging.error(f'{self.name}: The page did not fully load')
            return False

    def verify_concentration(
        self, driver: webdriver, concentration: str
    ) -> Tuple[bool, List[str]]:
        presentations_texts = []
        ignore_keywords = ["cancelada", "caduca", "inativa"]
        try:
            presentations_elements = driver.find_elements(
                By.CSS_SELECTOR, '.col-xs-4.ng-binding'
            )
            
            filtered_presentations = [
                presentation for presentation in presentations_elements
                if not any(keyword in presentation.text.lower() for keyword in ignore_keywords)
            ]
            
            match = any(
                Utils.remove_accents_and_spaces(concentration)
                in Utils.remove_accents_and_spaces(presentation.text)
                for presentation in filtered_presentations
            )

            presentations_texts = [
                presentation.text
                for presentation in filtered_presentations
            ]

            if match:
                return True, presentations_texts
            else:
                logging.warning(f'{self.name}: Concentration found does not match')
                return False, presentations_texts
        except Exception as e:
            logging.error(f'{self.name}: Error verifying concentration: {e}')
            return False, presentations_texts

    def verify_registration(self, driver: webdriver, register: str) -> bool:
        try:
            register_found = driver.find_element(
                By.XPATH,
                '/html/body/div[3]/div[1]/form/div[1]/div[2]/table/tbody/tr[2]/td[1]',
            ).text
            if register_found == register:
                return True
            else:
                logging.warning(
                    f'{self.name}: The registration found on the Anvisa page does not match'
                )
                return False
        except Exception as e:
            logging.error(f'{self.name}: Error verifying registration: {e}')
            return False

    def print_page(self, driver: webdriver):
        driver.execute_script('window.print();')
        sleep(0.5)
        
    def get_presentation(self, concentration: str, presentations: List[str]) -> str:
        try:
            for presentation in presentations:
                if Utils.remove_accents_and_spaces(concentration) in Utils.remove_accents_and_spaces(presentation):
                    return presentation

            logging.warning(f'{self.name}: Concentration found does not match')
            return None
        except Exception as e:
            logging.critical(f'{self.name}: Error verifying concentration: {e}')
            return None

    def get_register_as_pdf(
        self,
        register: str,
        concentration: str,
        exp_date: str,
        reg_data: Dict[str, Dict[str, Union[str, List[str]]]],
    ) -> bool:
        logging.info(f'{self.name}: Starting execution.')

        anvisa_medicamentos_url = r'https://consultas.anvisa.gov.br/#/medicamentos/q/?numeroRegistro='

        chrome_options = self.configure_chrome_options(detach=True)
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, timeout=10)

        presentation = None
        success, presentation = self.try_print_anvisa_register(
            driver,
            wait,
            anvisa_medicamentos_url,
            concentration,
            register,
            exp_date,
            reg_data,
        )
        if not success:
            logging.error(
                f'{self.name}: Failed to obtain the registration {register} as a PDF'
            )
            driver.quit()
            logging.info(f'{self.name}: Execution completed.')
            return False, presentation

        driver.quit()
        logging.info(f'{self.name}: Execution completed.')
        return True, presentation
