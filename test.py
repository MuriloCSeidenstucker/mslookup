import json
import re
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import visibility_of_element_located, presence_of_element_located, text_to_be_present_in_element
from urllib.parse import urlparse

name = 'lacosamida 100 mg'
brand = 'torrent'

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
# chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument('--kiosk-printing')

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, timeout=10)

process_number = ''
anvisa_medicamento_url = r'https://consultas.anvisa.gov.br/#/medicamentos/'

driver.get("https://www.google.com/")

search_input_locator = (By.CSS_SELECTOR, 'div textarea')
search_input = wait.until(visibility_of_element_located(search_input_locator), 'Elemento não encontrado')
search_input.send_keys(f"registro anvisa {name} {brand}")

# submit_button_locator = (By.XPATH, '//input[@name="btnK"]')
submit_button_locator = (By.XPATH, '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[4]/center/input[1]')
submit_button = wait.until(visibility_of_element_located(submit_button_locator), 'Elemento não encontrado')
submit_button.click()

center_col_locator = (By.ID, "center_col")
center_col = wait.until(presence_of_element_located(center_col_locator), "Elemento não encontrado")
a_elements = center_col.find_elements(By.TAG_NAME, "a")

smerp_urls = []
for element in a_elements:
    url = urlparse(element.get_attribute("href")).netloc
    if isinstance(url, str):
        if "smerp" in url:
            smerp_urls.append(element)
            
dataset_locator = (By.CSS_SELECTOR, '.dataset')
dataset = None
for url in smerp_urls:
    url.click()
    dataset = wait.until(presence_of_element_located(dataset_locator), 'Elemento não encontrado')
    smerp_brand = dataset.find_element(By.XPATH, "//div[contains(text(), 'Nome da Empresa/Detentor')]/following-sibling::div").text
    print(f'Marca: {brand}, Smerp: {smerp_brand}, Iguais: {brand.lower() in smerp_brand.lower()}')
    if brand.lower() in smerp_brand.lower():
        break
    else:
        driver.back()