from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import urlparse

process_number = -1
anvisa_medicamento_url = r'https://consultas.anvisa.gov.br/#/medicamentos/'

driver = webdriver.Chrome()

driver.get("https://www.google.com/")
driver.maximize_window()
driver.implicitly_wait(0.5)

# name = input("Qual o nome do medicamento? -> ")
# brand = input("Qual a marca do medicamento? -> ")
name = "aciclovir"
brand = "cimed"

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
a_elements_smerp = dataset.find_elements(By.TAG_NAME, "a")
for element in a_elements_smerp:
    if "consultar diretamente na anvisa" in element.text:
        element.click()
        break

frame = driver.switch_to.frame('aswift_12')
driver.switch_to.frame('ad_iframe')
driver.find_element(By.ID, "dismiss-button").click()
driver.current_url

# input()
# driver.quit()