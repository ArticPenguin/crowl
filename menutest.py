from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from time import sleep



def switch_left():
    driver.switch_to.parent_frame()
    iframe = driver.find_element(By.XPATH,'//*[@id="searchIframe"]')
    driver.switch_to.frame(iframe)
    
def switch_right():
    driver.switch_to.parent_frame()
    iframe = driver.find_element(By.XPATH,'//*[@id="entryIframe"]')
    driver.switch_to.frame(iframe)



driver = webdriver.Chrome()

URL = 'https://map.naver.com/p/search/통큰감자탕?c=13.49,0,0,0,dh'
driver.get(url=URL)


sleep(5)

switch_right()

Menuflag = False
for i in range(1,5):
    menu_container = driver.find_elements(By.XPATH,'//*[@id="_pcmap_list_scroll_container"]//li')
    if menu_container.text == '메뉴':
        menu_container.click()
        sleep(2)
        Menuflag = True
        break

menu_sections = driver.find_elements(By.XPATH, './/div[contains(@class="order_list_inner")]')
print(menu_sections)


driver.quit()