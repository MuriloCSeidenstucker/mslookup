import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import (visibility_of_element_located,
                                                            element_to_be_clickable)

def text_to_be_present(webdriver: webdriver) -> bool:
    text = webdriver.find_element(By.XPATH, producer_xpath).text
    return isinstance(text, str) and text

df = pd.read_excel(r"C:\Users\dell\Downloads\Produtos Ativos - DM-LM.xlsx")

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, timeout=2)

driver.maximize_window()
driver.get("https://admin.meucatalogo.com.br/")

login = 'grupomachadonunes@gmail.com'
password = 'Nova0805@'

email_xpath = '//*[@id="root"]/main/div/div[2]/form/div[1]/div/input'
pass_xpath = '//*[@id="root"]/main/div/div[2]/form/div[2]/div/input'
enterBtn_xpath = '//*[@id="root"]/main/div/div[2]/form/button'

sku_xpath = '//*[@id="root"]/main/div/div/div[1]/form/div/div[1]/div/input'
producer_xpath = '//*[@id="root"]/main/div/div/div[2]/div[2]/div[5]'
imgProd_xpath = '//*[@id="root"]/main/div/div/div[2]/div[2]/div[1]/img'
editBtn_xpath = '//*[@id="root"]/main/div/div/div[2]/div[2]/div[7]/div/button[1]'
searchBtn_xpath = '//*[@id="root"]/main/div/div/div[1]/form/div/button[2]'

deleteBtn_xpath = '//*[@id="root"]/main/div/div/div[2]/div[2]/div[7]/div/button[3]'

cancelBtn_xpath = '//*[@id="modalContent"]/div/button[1]'
confirmBtn_xpath = '//*[@id="modalContent"]/div/button[2]'

driver.find_element(By.XPATH, email_xpath).send_keys(login)
driver.find_element(By.XPATH, pass_xpath).send_keys(password)
driver.find_element(By.XPATH, enterBtn_xpath).click()

report_data = []

try:
    for index, row in df.iterrows():
        print(f'Item: {index+1} de {len(df)}')
        
        try:
            producer = ''
            imgIsPresent = False
            
            sku_input_locator = (By.XPATH, sku_xpath)
            sku_input = wait.until(visibility_of_element_located(sku_input_locator), 'Elemento não encontrado')
            sku_input.send_keys(Keys.CONTROL, 'a', Keys.DELETE)
            sku_input.send_keys(str(row['SKU']))
            
            searchBtn_locator = (By.XPATH, searchBtn_xpath)
            searchBtn = wait.until(element_to_be_clickable(searchBtn_locator), 'Elemento indisponível')
            searchBtn.click()
            
            producerIsPresent = wait.until(text_to_be_present)
            
            if producerIsPresent:
                producer = driver.find_element(By.XPATH, producer_xpath).text
                imgElement = driver.find_element(By.XPATH, imgProd_xpath)
                altImg = imgElement.get_attribute('alt')
                if altImg == 'Imagem do produto':
                    imgIsPresent = True
            else:
                producer = 'Fabricante não encontrado'
            
            report_data.append({
                'SKU': str(row['SKU']),
                'COD.BARRAS': str(row['COD.BARRAS']),
                'DESCRIÇÃO': str(row['DESCRIÇÃO']),
                'FABRICANTE': producer,
                'POSSUI IMAGEM?': 'SIM' if imgIsPresent else 'NÃO'
            })
        except:
            report_data.append({
                'SKU': str(row['SKU']),
                'COD.BARRAS': str(row['COD.BARRAS']),
                'DESCRIÇÃO': str(row['DESCRIÇÃO']),
                'FABRICANTE': 'Não consta no catálogo',
                'POSSUI IMAGEM?': 'SIM' if imgIsPresent else 'NÃO'
            })
            continue
except:
    report_df = pd.DataFrame(report_data)
    report_df.to_excel(r'catalogo\relatorio_catalogo.xlsx', index=False)
    driver.quit()        

report_df = pd.DataFrame(report_data)
report_df.to_excel(r'catalogo\relatorio_catalogo.xlsx', index=False)

driver.quit()
