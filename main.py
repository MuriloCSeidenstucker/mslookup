from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()

driver.get("https://www.google.com/")
driver.maximize_window()
driver.implicitly_wait(0.5)

text_box_xpath = r'//*[@id="APjFqb"]'
text_box = driver.find_element(by=By.XPATH, value=text_box_xpath)

submit_button_xpath = r'/html/body/div[1]/div[3]/form/div[1]/div[1]/div[4]/center/input[1]'
submit_button = driver.find_element(by=By.XPATH, value=submit_button_xpath)

text_box.send_keys("Selenium")
submit_button.click()

driver.quit()