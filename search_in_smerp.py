import re
import json

from urllib.parse import urlparse
from unidecode import unidecode
from datetime import datetime
from utils import Utils
from time import sleep, time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import (visibility_of_element_located,
                                                            presence_of_element_located)

class SearchInSmerp:
    """
    Classe para buscar registros da Anvisa de medicamentos no Google e no site smerp.

    Esta classe é utilizada quando a API não consegue obter os registros diretamente das planilhas Excel disponibilizadas pela Anvisa.
    Ela automatiza a busca no Google e no site smerp, extraindo informações relevantes sobre os registros de medicamentos.

    Fluxo de Operação:
    ------------------
    1. Configura e inicializa o WebDriver do Chrome.
    2. Realiza uma busca no Google com os termos "registro anvisa {medicamento} {marca}".
    3. Obtém URLs relevantes do site smerp dos resultados de busca do Google.
    4. Verifica cada URL para encontrar uma entrada correspondente no site smerp.
    5. Extrai o número de registro, o número do processo e a data de expiração da entrada encontrada.
    6. Retorna os dados extraídos ou valores padrão (-1, -1, -1) se a busca não for bem-sucedida.

    Exemplos:
    ---------
    >>> search = SearchInSmerp()
    >>> register, process_number, expiration_date = search.get_data_from_smerp('Item123', 'ProductDescription', 'BrandName')
    >>> print(register, process_number, expiration_date)
    """
    
    def configure_chrome_options(self, detach=False):
        """
        Configura e retorna as opções do Chrome para o WebDriver.

        Este método define opções específicas para o WebDriver do Chrome, permitindo a customização do comportamento do navegador,
        como mantê-lo aberto após a execução do script.

        Args:
            detach (bool): Se True, o navegador Chrome permanecerá aberto após a execução do script. 
            O valor padrão é False, fazendo com que o navegador feche automaticamente ao final da execução.

        Returns:
            chrome_options (webdriver.ChromeOptions): As opções configuradas para o WebDriver do Chrome.
        """
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("detach", detach)
        return chrome_options
    
    def perform_google_search(self, driver, wait, description, brand):
        """
        Realiza uma busca no Google com termos específicos relacionados ao registro Anvisa de um medicamento.

        Este método navega até a página do Google, insere os termos de busca formados pela descrição do medicamento e sua marca,
        e executa a busca.

        Args:
            driver (webdriver.Chrome): A instância do WebDriver do Chrome utilizada para controlar o navegador.
            wait (WebDriverWait): A instância do WebDriverWait para aguardar a presença e/ou visibilidade dos elementos.
            description (str): A descrição do medicamento a ser pesquisado.
            brand (str): A marca ou laboratório do medicamento.

        Raises:
            TimeoutException: Se o elemento de entrada de busca ou o botão de submissão não forem encontrados dentro do tempo limite especificado.
        """
        driver.get("https://www.google.com/")
        
        search_input_locator = (By.CSS_SELECTOR, 'div textarea')
        search_input = wait.until(visibility_of_element_located(search_input_locator), 'Elemento não encontrado')
        search_input.send_keys(f"registro anvisa {description} {brand} smerp")

        submit_button_locator = (By.XPATH, '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[4]/center/input[1]')
        submit_button = wait.until(visibility_of_element_located(submit_button_locator), 'Elemento não encontrado')
        submit_button.click()
        
    def get_smerp_urls(self, driver, wait):
        """
        Extrai URLs do site smerp a partir dos resultados da busca no Google.

        Este método navega pelos resultados da busca no Google, identifica e coleta URLs que contêm "smerp" no domínio,
        retornando uma lista de elementos de âncora (anchor elements) correspondentes.

        Args:
            driver (webdriver.Chrome): A instância do WebDriver do Chrome utilizada para controlar o navegador.
            wait (WebDriverWait): A instância do WebDriverWait para aguardar a presença dos elementos.

        Returns:
            list: Uma lista de elementos de âncora (anchor elements) que contêm URLs do site smerp.

        Raises:
            TimeoutException: Se o elemento central contendo os resultados da busca não for encontrado dentro do tempo limite especificado.
        """
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
        """
        Encontra uma entrada correspondente no site smerp que coincida com a marca especificada.

        Este método navega pelas URLs fornecidas, verifica a validade do registro e compara a marca do medicamento com a marca especificada.
        Se encontrar uma entrada correspondente, retorna um indicador de sucesso. Caso contrário, continua a busca nas demais URLs.

        Args:
            driver (webdriver.Chrome): A instância do WebDriver do Chrome utilizada para controlar o navegador.
            wait (WebDriverWait): A instância do WebDriverWait para aguardar a presença dos elementos.
            brand (str): A marca ou laboratório do medicamento a ser pesquisado.
            smerp_urls (list): Uma lista de elementos de âncora (anchor elements) que contêm URLs do site smerp.

        Returns:
            tuple: Um booleano indicando se encontrou uma correspondência (matchesURL) e uma mensagem (message) explicativa.
                - matchesURL (bool): True se encontrou uma correspondência; False caso contrário.
                - message (str): Uma mensagem indicando o resultado da busca, como "Registro vencido para o item:" ou
                "Marca não encontrada para o item:".

        Raises:
            TimeoutException: Se o elemento de dados do registro não for encontrado dentro do tempo limite especificado.
        """
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
            except ValueError as e:
                print(f'Data consta como:{ref_date_str}. Formato incorreto')
            
            smerp_brand = dataset.find_element(By.XPATH, "//div[contains(text(), 'Nome da Empresa/Detentor')]/following-sibling::div").text
            if unidecode(brand).lower() in unidecode(smerp_brand).lower():
                matchesURL = True
                break
            else:
                message = 'Marca não encontrada para o item:'
                driver.back()
                
        return matchesURL, message
    
    def extract_process_number(self, wait):
        """
        Extrai e formata o número do processo a partir da página de detalhes do registro no site smerp.

        Este método localiza o elemento que contém o número do processo na página, extrai o texto, remove caracteres não numéricos,
        e retorna o número do processo formatado.

        Args:
            wait (WebDriverWait): A instância do WebDriverWait para aguardar a presença dos elementos.

        Returns:
            str: O número do processo formatado, contendo apenas dígitos.

        Raises:
            TimeoutException: Se o elemento contendo o número do processo não for encontrado dentro do tempo limite especificado.
        """
        dataset_locator = (By.CSS_SELECTOR, '.dataset')
        dataset = wait.until(presence_of_element_located(dataset_locator), 'Elemento não encontrado')
        process_number_extracted = dataset.find_element(By.XPATH, "//div[contains(text(), 'Processo')]/following-sibling::div").text
        pattern = r'\D'
        process_number_formatted = re.sub(pattern, '', process_number_extracted)
        return process_number_formatted
    
    def extract_register(self, wait):
        """
        Extrai o número de registro do medicamento a partir da página de detalhes do registro no site smerp.

        Este método localiza o elemento que contém o número de registro na página, extrai os primeiros 9 caracteres do texto,
        e retorna o número de registro.

        Args:
            wait (WebDriverWait): A instância do WebDriverWait para aguardar a presença dos elementos.

        Returns:
            str: O número de registro extraído.

        Raises:
            TimeoutException: Se o elemento contendo o número de registro não for encontrado dentro do tempo limite especificado.
        """
        dataset_locator = (By.CSS_SELECTOR, '.dataset')
        dataset = wait.until(presence_of_element_located(dataset_locator), 'Elemento não encontrado')
        register = dataset.find_element(By.XPATH, "//div[contains(text(), 'Registro')]/following-sibling::div").text[:9]
        return register
    
    def extract_expiration_date(self, wait):
        """
        Extrai a data de validade/situação a partir da página de detalhes do registro no site smerp.

        Este método localiza o elemento que contém a data de validade/situação na página e extrai o texto correspondente.

        Args:
            wait (WebDriverWait): A instância do WebDriverWait para aguardar a presença dos elementos.

        Returns:
            str: A data de validade/situação extraída.

        Raises:
            TimeoutException: Se o elemento contendo a data de validade/situação não for encontrado dentro do tempo limite especificado.
        """
        dataset_locator = (By.CSS_SELECTOR, '.dataset')
        dataset = wait.until(presence_of_element_located(dataset_locator), 'Elemento não encontrado')
        expiration_date = dataset.find_element(By.XPATH, "//div[contains(text(), 'Validade/Situação')]/following-sibling::div/span").text
        return expiration_date
    
    def get_data_from_smerp(self, item, description, brand):
        """
        Realiza uma busca automatizada no site "smerp" e extrai informações específicas de uma entrada correspondente.

        Args:
        - item (str): Número do item que está sendo pesquisado.
        - description (str): Descrição do item a ser pesquisado.
        - brand (str ou dict): Nome da marca como uma string ou um dicionário contendo a chave 'Name' com o nome da marca.

        Returns:
        - tuple: Uma tupla contendo o registro (register), o número do processo (process_number) e a data de expiração (expiration_date).
                Retorna (-1, -1, -1) se não for possível encontrar uma entrada correspondente no site "smerp".

        O método segue as seguintes etapas:
        1. Verifica e ajusta o parâmetro `brand`.
        2. Configura e inicializa o WebDriver do Chrome com as opções especificadas.
        3. Realiza uma busca no Google utilizando os parâmetros `name` e `brand`.
        4. Obtém URLs relevantes do site "smerp".
        5. Encontra uma entrada correspondente no site "smerp" utilizando os URLs obtidos.
        6. Extrai o número do processo, o registro e a data de expiração da página correspondente.
        7. Fecha o navegador e retorna os dados extraídos.

        Exceptions:
        - Imprime uma mensagem de erro se ocorrer um TimeoutException durante a busca no Google.
        - Retorna (-1, -1, -1) se não encontrar uma entrada correspondente no site "smerp" ou 
        se ocorrer um TimeoutException durante a busca no Google.

        Examples:
        >>> register, process_number, expiration_date = get_data_from_smerp('Item123', 'ProductName', 'BrandName')
        >>> print(register, process_number, expiration_date)
        """
        
        b = brand if isinstance(brand, str) else brand['Name']
        
        chrome_options = self.configure_chrome_options()

        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, timeout=10)

        try:
            self.perform_google_search(driver, wait, description, b)
        except TimeoutException as e:
            print('Erro ao tentar realizar a busca no Google')
            driver.quit()
            return -1, -1, -1
                
        smerp_urls = self.get_smerp_urls(driver, wait)
        
        matchesURL, m = self.find_matching_smerp_entry(driver, wait, b, smerp_urls)
        if not matchesURL:
            print(f'{m} {item}')
            driver.quit()
            return -1, -1, -1
        
        process_number = self.extract_process_number(wait)
        register = self.extract_register(wait)
        expiration_date = self.extract_expiration_date(wait)
            
        driver.quit()
        return register, process_number, expiration_date
