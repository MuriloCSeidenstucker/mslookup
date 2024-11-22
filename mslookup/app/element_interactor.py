from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException



from mslookup.app.logger_config import get_logger

class ElementInteractor:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.timeout = timeout
        self.logger = get_logger(self.__class__.__name__)

    def wait_for_element_to_be_available(self, by, locator):
        try:
            # Espera até que o elemento esteja presente no DOM
            element_present = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((by, locator))
            )

            # Espera até que o elemento esteja visível na página
            element_visible = WebDriverWait(self.driver, self.timeout).until(
                EC.visibility_of_element_located((by, locator))
            )

            # Espera até que o elemento esteja clicável (ativo)
            element_clickable = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((by, locator))
            )

            return element_clickable  # Retorna o elemento se todas as condições forem atendidas

        except TimeoutException:
            self.logger.warning(f"Elemento com {locator} não está disponível para interação.")
            return None
        
    def wait_for_elements_to_be_available(self, by, locator):
        try:
            # Espera até que a lista de elementos esteja presente no DOM
            elements_present = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_all_elements_located((by, locator))
            )
            return elements_present  # Retorna os elementos se forem encontrados

        except TimeoutException:
            print(f"Elementos com {locator} não estão disponíveis.")
            return []

    def click_element(self, by, locator):
        element = self.wait_for_element_to_be_available(by, locator)
        if element:
            element.click()
        else:
            self.logger.warning("Não foi possível clicar no elemento.")

    def send_keys_to_element(self, by, locator, text):
        element = self.wait_for_element_to_be_available(by, locator)
        if element:
            element.send_keys(text)
        else:
            self.logger.warning("Não foi possível enviar texto para o elemento.")
