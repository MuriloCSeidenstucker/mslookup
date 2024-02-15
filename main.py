import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from urllib.parse import urlparse

chrome_options = webdriver.ChromeOptions()
settings = {
       "recentDestinations": [{
            "id": "Save as PDF",
            # "id": "\\\\farmacia\\HP LaserJet Professional M1212nf MFP_1/local/",
            "origin": "local",
            "account": "",
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2
    }
prefs = {'printing.print_preview_sticky_settings.appState': json.dumps(settings)}
chrome_options.add_experimental_option('prefs', prefs)
chrome_options.add_argument('--kiosk-printing')

def resize_window(driver):
    driver.maximize_window()
    screen_width = driver.execute_script("return window.screen.availWidth")
    screen_height = driver.execute_script("return window.screen.availHeight")
    new_position = (screen_width // 2, 0)
    new_size = (screen_width // 2, screen_height)
    driver.set_window_position(*new_position)
    driver.set_window_size(*new_size)

process_number = ''
anvisa_medicamento_url = r'https://consultas.anvisa.gov.br/#/medicamentos/'

driver = webdriver.Chrome(options=chrome_options)

driver.get("https://www.google.com/")
resize_window(driver)
driver.implicitly_wait(0.5)

name = input("Qual o nome do medicamento? -> ")
brand = input("Qual a marca do medicamento? -> ")
# name = "aciclovir"
# brand = "cimed"

text_box_xpath = r'//*[@id="APjFqb"]'
text_box = driver.find_element(by=By.XPATH, value=text_box_xpath)
text_box.send_keys(f"registro anvisa {name} {brand}")

submit_button_xpath = r'/html/body/div[1]/div[3]/form/div[1]/div[1]/div[4]/center/input[1]'
submit_button = driver.find_element(by=By.XPATH, value=submit_button_xpath)
submit_button.click()

driver.implicitly_wait(0.5)
center_col = driver.find_element(By.ID, "center_col")
a_elements = center_col.find_elements(By.TAG_NAME, "a")

for element in a_elements:
    url = urlparse(element.get_attribute("href")).netloc
    if isinstance(url, str):
        if "smerp" in url:
            element.click()
            break

driver.implicitly_wait(0.5)
dataset = driver.find_element(By.CLASS_NAME, "dataset")
text = dataset.find_element(By.XPATH, '/html/body/section/center/article/div[1]/div[6]/div[2]').text
reg2 = r'\D'
process_number = re.sub(reg2, '', text)

driver.get(rf'{anvisa_medicamento_url}{process_number}/')
sleep(3)
driver.execute_script('window.print();')

# input()
# driver.quit()

