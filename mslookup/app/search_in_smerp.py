import logging
import re
from datetime import datetime
from time import sleep
from typing import Dict, List, Tuple, Union
from urllib.parse import urlparse
from unidecode import unidecode

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import (
    presence_of_element_located, visibility_of_element_located)
from selenium.webdriver.support.wait import WebDriverWait

from mslookup.app.element_interactor import ElementInteractor
from mslookup.app.logger_config import configure_logging


class SearchInSmerp:
    def __init__(self):
        configure_logging()
        self.name = self.__class__.__name__
        self.element_interactor = None

    def configure_chrome_options(
        self, detach: bool = False
    ) -> webdriver.ChromeOptions:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('detach', detach)
        return chrome_options

    def perform_google_search(
        self,
        driver: webdriver,
        description: str,
        brand: Union[Dict, str],
    ) -> None:
        driver.get('https://www.google.com/')

        search_input = self.element_interactor.wait_for_element_to_be_available(
            By.CSS_SELECTOR,
            'div textarea'
        )
        search_input.send_keys(f'registro anvisa {description} {brand} smerp')

        submit_button = self.element_interactor.wait_for_element_to_be_available(
            By.XPATH,
            '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[4]/center/input[1]',
        )
        submit_button.click()

    def get_smerp_urls(self, driver) -> List[str]:
        center_col = self.element_interactor.wait_for_element_to_be_available(
            By.ID,
            'center_col'
        )
        height = driver.execute_script('return document.body.scrollHeight')
        driver.set_window_size(1280, height + 100)
        sleep(1)
        a_elements = center_col.find_elements(By.TAG_NAME, 'a')

        smerp_urls = []
        for element in a_elements:
            url = urlparse(element.get_attribute('href')).netloc
            if isinstance(url, str):
                if 'smerp' in url:
                    smerp_urls.append(element)
        return smerp_urls

    def find_matching_smerp_entry(
        self,
        driver: webdriver,
        brand: Union[Dict, str],
        smerp_urls: List[str],
    ) -> Tuple[bool, str]:
        
        matchesURL = False
        message = ''
        for url in smerp_urls:
            url.click()
            dataset = self.element_interactor.wait_for_element_to_be_available(
                By.CSS_SELECTOR,
                '.dataset'
            )

            ref_date_str = dataset.find_element(
                By.XPATH,
                "//div[contains(text(), 'Validade/Situação')]/following-sibling::div/span",
            ).text
            try:
                ref_date = datetime.strptime(ref_date_str, '%d/%m/%Y')
                if ref_date < datetime.now():
                    message = 'Registro vencido para o item:'
                    driver.back()
                    continue
            except Exception:
                logging.critical(f'Date appears as:{ref_date_str}. Incorrect format')

            smerp_brand = dataset.find_element(
                By.XPATH,
                "//div[contains(text(), 'Nome da Empresa/Detentor')]/following-sibling::div",
            ).text
            if unidecode(brand).lower() in unidecode(smerp_brand).lower():
                matchesURL = True
                break
            else:
                message = 'Marca não encontrada para o item:'
                driver.back()

        return matchesURL, message

    def extract_process_number(self) -> str:
        dataset = self.element_interactor.wait_for_element_to_be_available(
            By.CSS_SELECTOR,
            '.dataset'
        )
        process_number_extracted = dataset.find_element(
            By.XPATH,
            "//div[contains(text(), 'Processo')]/following-sibling::div",
        ).text
        pattern = r'\D'
        process_number_formatted = re.sub(
            pattern, '', process_number_extracted
        )
        return process_number_formatted

    def extract_register(self) -> str:
        dataset = self.element_interactor.wait_for_element_to_be_available(
            By.CSS_SELECTOR,
            '.dataset'
        )
        register = dataset.find_element(
            By.XPATH,
            "//div[contains(text(), 'Registro')]/following-sibling::div",
        ).text[:9]
        return register

    def extract_expiration_date(self) -> str:
        dataset = self.element_interactor.wait_for_element_to_be_available(
            By.CSS_SELECTOR,
            '.dataset'
        )
        expiration_date = dataset.find_element(
            By.XPATH,
            "//div[contains(text(), 'Validade/Situação')]/following-sibling::div/span",
        ).text
        return expiration_date
    
    def start_driver(self, chrome_options):
        logging.info(f"{self.name}: Starting browser")
        driver = None
        try:
            driver = webdriver.Chrome(chrome_options)
            self.element_interactor = ElementInteractor(driver)
        except WebDriverException as e:
            if "This version of ChromeDriver only supports Chrome version" in str(e):
                chromedriver_version_supports = re.search(
                    "ChromeDriver only supports Chrome version (\\d+)", str(e)
                ).group(1)
                client_browser_version = re.search(
                    "Current browser version is (\\d+\\.\\d+\\.\\d+\\.\\d+)", str(e)
                ).group(1)

                logging.critical(
                    f"Browser is in version {client_browser_version}. ChromeDriver only "
                    f"supports the version {chromedriver_version_supports}. Please update your browser."
                )
            else:
                logging.critical("Error when instantiating browser.")

        return driver

    def get_data_from_smerp(
        self, description: str, brand: Union[Dict, str]
    ) -> List[Dict[str, str]]:
        
        reg_candidates = []
        b = brand if isinstance(brand, str) else brand['Name']

        chrome_options = self.configure_chrome_options()
        driver = self.start_driver(chrome_options)

        try:
            self.perform_google_search(driver, description, b)
        except TimeoutException as e:
            logging.error(
                'Timeout while performing Google search: %s', e.msg
            )
            driver.quit()
            return reg_candidates
        except Exception as e:
            logging.error(
                'Unexpected error while performing Google search: %s', e.msg
            )
            driver.quit()
            return reg_candidates

        smerp_urls = self.get_smerp_urls(driver)

        try:
            matchesURL, m = self.find_matching_smerp_entry(
                driver, b, smerp_urls
            )
        except TimeoutException as e:
            logging.error(
                'Timeout while finding matching SMERP entry: %s', e.msg
            )
            driver.quit()
            return reg_candidates
        except Exception as e:
            logging.error(
                'Error while finding matching SMERP entry: %s', e.msg
            )
            driver.quit()
            return reg_candidates

        if not matchesURL:
            driver.quit()
            logging.warning('No matching URL found in SMERP.')
            return reg_candidates

        try:
            process_number = self.extract_process_number()
            register = self.extract_register()
            expiration_date = self.extract_expiration_date()
        except TimeoutException as e:
            logging.error(
                'Timeout while extracting data from SMERP: %s', e.msg
            )
            return reg_candidates
        except Exception as e:
            logging.error(
                'Error while extracting data from SMERP: %s', e.msg
            )
            return reg_candidates
        finally:
            driver.quit()

        reg_candidates.append(
            {
                'register': register,
                'process_number': process_number,
                'expiration_date': expiration_date,
            }
        )
        return reg_candidates
