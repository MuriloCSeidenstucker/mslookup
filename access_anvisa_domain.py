import json
import re
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

from utils import Utils

class AnvisaDomain:
    """
    A classe AnvisaDomain automatiza a extração e a impressão de registros de medicamentos
    do site da Anvisa (Agência Nacional de Vigilância Sanitária) usando o Selenium WebDriver 
    com o navegador Chrome.

    Objetivo:
    -----------
    O principal objetivo desta classe é acessar o site da Anvisa, navegar até as páginas de 
    registros de medicamentos específicos e salvar essas páginas como arquivos PDF.

    Funcionalidades:
    ----------------
    - Configura o navegador Chrome para automação, incluindo preferências de impressão.
    - Verifica a presença de números de processo nas páginas da Anvisa.
    - Obtém o número do processo correspondente a um número de registro de medicamento.
    - Tenta imprimir a página de registro do medicamento como PDF se o número do processo 
      corresponder.
    - Controla o fluxo principal para obter o registro de um medicamento como PDF, 
      gerenciando o navegador e tratando possíveis falhas na impressão.
    """
    def configure_chrome_options(self, detach=False):
        """
        Configura as opções do navegador Chrome para automação.

        Args:
            detach (bool, opcional): Se True, o navegador será configurado para permanecer aberto após a execução do script. 
            Por padrão, é False.

        Returns:
            selenium.webdriver.ChromeOptions: As opções configuradas do navegador Chrome.

        Funcionalidades:
        ----------------
        - Configura as preferências do navegador para salvar impressões como PDF.
        - Ativa a impressão em modo quiosque.
        - Permite a opção de manter o navegador aberto após a execução do script.
        """
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
        """
        Verifica se um número de processo está presente na página carregada.

        Args:
            webdriver (selenium.webdriver.Chrome): O objeto WebDriver do Selenium, representando o navegador em que a página está carregada.

        Returns:
            bool: True se um número de processo estiver presente e for uma string; False caso contrário.

        Raises:
            NoSuchElementException: Se o elemento com o XPath especificado não for encontrado na página.
        """
        process_number = webdriver.find_element(By.XPATH, "//th[contains(text(), 'Processo')]/following-sibling::td/a").text
        return isinstance(process_number, str) and process_number
        
    def get_process_number(self, driver, wait, register):
        """
        Obtém o número do processo correspondente a um número de registro de medicamento na página da Anvisa.

        Args:
            driver (selenium.webdriver.Chrome): O objeto WebDriver do Selenium, representando o navegador.
            wait (selenium.webdriver.support.ui.WebDriverWait): O objeto WebDriverWait usado para esperar até
                que o elemento desejado esteja presente na página.
            register (str): O número de registro do medicamento para o qual o número do processo será obtido.

        Returns:
            str: O número do processo correspondente ao número de registro do medicamento.

        Raises:
            TimeoutException: Se o elemento com o XPath especificado não estiver presente na página após o tempo limite.
            
        Funcionalidades:
        ----------------
        - Acessa a URL da consulta de medicamentos da Anvisa com base no número de registro fornecido.
        - Utiliza um localizador XPath para encontrar o número do processo na página.
        - Remove caracteres não numéricos do número do processo.
        """
        register_url = rf'https://consultas.anvisa.gov.br/#/medicamentos/q/?numeroRegistro={register}'
        driver.get(register_url)
        
        locator = (By.XPATH, f"//td[contains(text(), '{register}')]/following-sibling::td")
        process_number = wait.until(presence_of_element_located(locator), "Elemento não encontrado").text
        
        pattern = r'\D'
        return re.sub(pattern, '', process_number)
    
    def try_print_anvisa_register(self, driver, wait, anvisa_medicamento_url, process_number_formatted, a_concentration):
        """
        Tenta imprimir o registro de um medicamento da Anvisa como PDF.

        Args:
            driver (selenium.webdriver.Chrome): O objeto WebDriver do Selenium, representando o navegador.
            wait (selenium.webdriver.support.ui.WebDriverWait): O objeto WebDriverWait usado para esperar
                até que o elemento desejado esteja presente na página.
            anvisa_medicamento_url (str): A URL base para acessar as páginas de registro de medicamentos da Anvisa.
            process_number_formatted (str): O número de processo formatado do medicamento para o qual a impressão será tentada.

        Returns:
            bool: True se a impressão for bem-sucedida e o número do processo corresponder; False caso contrário.

        Raises:
            TimeoutException: Se o elemento esperado não estiver presente na página após o tempo limite.
            
        Funcionalidades:
        ----------------
        - Acessa a página específica de um medicamento na Anvisa com base no número de processo formatado fornecido.
        - Verifica se o número do processo presente na página corresponde ao número fornecido.
        - Executa a impressão da página se o número do processo correspondente for encontrado.
        - Manipula exceções caso ocorra um timeout durante o processo de impressão.

        Notas:
        ------
        Este método tenta acessar a página específica de um medicamento na Anvisa usando o número de processo 
        formatado fornecido. Verifica se o número do processo presente na página corresponde ao número fornecido 
        e, se sim, executa a impressão da página. Caso contrário, imprime uma mensagem de erro.
        """
        driver.get(rf'{anvisa_medicamento_url}{process_number_formatted}/')
        try:
            number_is_present = wait.until(self.process_number_to_be_present)
            
            presentations = driver.find_elements(By.CSS_SELECTOR, '.col-xs-4.ng-binding')
            match = any(Utils.remove_accents_and_spaces(a_concentration) in
                        Utils.remove_accents_and_spaces(presentation.text)
                        for presentation in presentations)
            
            anvisa_process_number = driver.find_element(By.XPATH, "//th[contains(text(), 'Processo')]/following-sibling::td/a").text if number_is_present else ''
            pattern = r'\D'
            anvisa_process_number_formatted = re.sub(pattern, '', anvisa_process_number)
            if process_number_formatted == anvisa_process_number_formatted and match:
                driver.execute_script('window.print();')
                sleep(0.5)
                return True
            else:
                print(f'O número do processo constante na Anvisa está diferente')
                return False
        except TimeoutException as e:
            print(rf'Erro ao tentar a impressão de: {anvisa_medicamento_url}{process_number_formatted}/')
            return False
        
    def get_register_as_pdf(self, register, a_concentration, process_number=None):
        """
        Obtém o registro de um medicamento da Anvisa como um arquivo PDF.

        Args:
            register (str): O número de registro do medicamento cujo registro será obtido.
            process_number (str, opcional): O número de processo do medicamento. Se fornecido, será usado diretamente para a obtenção
                do registro. Caso contrário, o número de processo será obtido automaticamente com base no número de registro.

        Returns:
            bool: True se o registro for obtido com sucesso como PDF; False caso contrário.

        Funcionalidades:
        ----------------
        - Configura as opções do navegador Chrome para a impressão em modo quiosque e salvação como PDF.
        - Inicializa o WebDriver do Selenium e uma espera explícita.
        - Obtém o número de processo do medicamento, se não fornecido explicitamente.
        - Tenta imprimir o registro do medicamento como PDF.
        - Encerra o navegador após a obtenção do registro.
        """
        anvisa_medicamentos_url = r'https://consultas.anvisa.gov.br/#/medicamentos/'
        
        chrome_options = self.configure_chrome_options(detach=True)
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, timeout=10)
        
        defined_process_number = (process_number if not process_number is None
                                  else self.get_process_number(driver, wait, register))
        
        success = self.try_print_anvisa_register(driver, wait, anvisa_medicamentos_url, defined_process_number, a_concentration)
        if not success:
            print(f'Não foi possível obter o registro: {register}')
            driver.quit()
            return False
            
        driver.quit()
        return True