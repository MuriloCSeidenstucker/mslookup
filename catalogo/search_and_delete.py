import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import (visibility_of_element_located,
                                                            element_to_be_clickable)

def text_to_be_present(webdriver: webdriver) -> bool:
    text = webdriver.find_element(By.XPATH, '//*[@id="root"]/main/div/div/div[2]/div[2]/p').text
    return True

df = pd.read_excel(r"C:\Users\dell\Downloads\CÓDIGOS PARA EXCLUIR DO MEU CATALOGO.xlsx")
if 'Deletado' not in df.columns:
    df['Deletado'] = False

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
searchBtn_xpath = '//*[@id="root"]/main/div/div/div[1]/form/div/button[2]'

deleteBtn_xpath = '//*[@id="root"]/main/div/div/div[2]/div[2]/div[7]/div/button[3]'
imgProd_xpath = '//*[@id="root"]/main/div/div/div[2]/div[2]/div[1]/img'

cancelBtn_xpath = '//*[@id="modalContent"]/div/button[1]'
confirmBtn_xpath = '//*[@id="modalContent"]/div/button[2]'

driver.find_element(By.XPATH, email_xpath).send_keys(login)
driver.find_element(By.XPATH, pass_xpath).send_keys(password)
driver.find_element(By.XPATH, enterBtn_xpath).click()

for index, row in df.iterrows():
    print(f'Item: {index+1} de {len(df)}')
    
    if df.at[index, 'Deletado']:
        continue
    
    try:
        sku_input_locator = (By.XPATH, sku_xpath)
        sku_input = wait.until(visibility_of_element_located(sku_input_locator), 'Elemento não encontrado')
        sku_input.send_keys(Keys.CONTROL, 'a', Keys.DELETE)
        sku_input.send_keys(str(row['SKU']))
        
        searchBtn_locator = (By.XPATH, searchBtn_xpath)
        searchBtn = wait.until(element_to_be_clickable(searchBtn_locator), 'Elemento indisponível')
        searchBtn.click()
        
        deletedItem = True
        try:
            deletedItem = wait.until(text_to_be_present)
        except:
            deletedItem = False

        if not deletedItem:
            deleteBtn_locator = (By.XPATH, deleteBtn_xpath)
            deleteBtn = wait.until(element_to_be_clickable(deleteBtn_locator), 'Elemento indisponível')
            deleteBtn.click()

            confirmBtn_locator = (By.XPATH, confirmBtn_xpath)
            confirmBtn = wait.until(element_to_be_clickable(confirmBtn_locator), 'Elemento indisponível')
            confirmBtn.click()
            df.at[index, 'Deletado'] = True
        else:
            df.at[index, 'Deletado'] = True
            continue
    except Exception as e:
        print(f'Erro: {e}')
        break
    
df.to_excel(r"C:\Users\dell\Downloads\CÓDIGOS PARA EXCLUIR DO MEU CATALOGO.xlsx", index=False)
driver.quit()
