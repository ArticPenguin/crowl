from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from test import crawl_menu_with_xpath
from selenium.common.exceptions import NoSuchElementException

from time import sleep
import random
import re
import requests
import sys
import json
import os

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'

def download_image(image_url, save_path):
    r = requests.get(image_url, stream=True)
    if r.status_code == 200:
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        print(f"이미지 다운로드 완료: {save_path}")
    else:
        print(f"이미지 다운로드 실패: {r.status_code}")

def is_element_present(driver, xpath):
    """
    특정 XPath를 기준으로 요소가 DOM에 존재하는지 확인합니다.
    
    Args:
        driver: WebDriver 인스턴스
        xpath: 확인하려는 요소의 XPath
    
    Returns:
        bool: 요소가 존재하면 True, 존재하지 않으면 False
    """
    try:
        driver.find_element(By.XPATH, xpath)
        return True
    except NoSuchElementException:
        return False


options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
options.add_argument('window-size=1380,900')
driver = webdriver.Chrome(options=options)

driver.implicitly_wait(time_to_wait=3)

loop = True

URL = 'https://map.naver.com/p/search/통큰감자탕?c=13.49,0,0,0,dh'
driver.get(url=URL)

def switch_left():
    driver.switch_to.parent_frame()
    iframe = driver.find_element(By.XPATH,'//*[@id="searchIframe"]')
    driver.switch_to.frame(iframe)
    
def switch_right():
    driver.switch_to.parent_frame()
    iframe = driver.find_element(By.XPATH,'//*[@id="entryIframe"]')
    driver.switch_to.frame(iframe)

# 결과를 담을 리스트
results = []

while(loop):
    switch_left()
    next_page = driver.find_element(By.XPATH,'//*[@id="_pcmap_list_scroll_container"]').get_attribute('aria-disabled')

    if(next_page == 'true'):
        print(Colors.RED + '------------ 더 이상 페이지가 없습니다. ------------' + Colors.RESET)
        break
    

     ############## 맨 밑까지 스크롤 ##############
    scrollable_element = driver.find_element(By.CLASS_NAME, "Ryr1F")
 
    last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_element)
 
    while True:
        sleep(2)

        # 요소 내에서 아래로 600px 스크롤
        driver.execute_script("arguments[0].scrollTop += 700;", scrollable_element)

        # 페이지 로드를 기다림
        sleep(2)  # 동적 콘텐츠 로드 시간에 따라 조절

        driver.execute_script("arguments[0].scrollTop += 400;", scrollable_element)
 
        # 새 높이 계산
        new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_element)
 
        # 스크롤이 더 이상 늘어나지 않으면 루프 종료
        if new_height == last_height:
            break
 
        last_height = new_height

    sleep(1)

    page_no = driver.find_element(By.XPATH,'//a[contains(@class, "mBN2s qxokY")]').text
    elemets = driver.find_elements(By.XPATH,'//*[@id="_pcmap_list_scroll_container"]//li')

    print('현재 ' + '\033[95m' + str(page_no) + '\033[0m' + ' 페이지 / '+ '총 ' + '\033[95m' + str(len(elemets)) + '\033[0m' + '개의 가게를 찾았습니다.\n')

    for index, e in enumerate(elemets, start=1):
        final_element = e.find_element(By.CLASS_NAME,'YwYLL')
        print(str(index) + ". " + final_element.text)

    print(Colors.RED + "-"*50 + Colors.RESET)
    switch_left()
    sleep(2)

    for index, e in enumerate(elemets, start=1):
        store_name = '' 
        category = '' 
        new_open = '' 
        rating = 0.0 
        visited_review = '' 
        blog_review = ''
        store_id = '' 
        address = '' 
        business_hours = [] 
        phone_num = ''
        menus_data = []

        switch_left()
        e.find_element(By.CLASS_NAME,'YwYLL').click()
        sleep(2)


        switch_right()

        title = driver.find_element(By.XPATH,'//div[@class="zD5Nm undefined"]')
        store_name = title.find_element(By.XPATH,'//*[@id="_title"]/div/span[1]').text
        category = title.find_element(By.XPATH,'//*[@id="_title"]/div/span[2]').text

        review = title.find_elements(By.XPATH,'.//div[2]/span')
        _index = 1

        # 리뷰 정보 파싱
        if len(review) > 2:
            rating_xpath = f'.//div[2]/span[{_index}]'
            rating_element = title.find_element(By.XPATH, rating_xpath)
            rating = rating_element.text.replace("\n", " ")
            _index += 1

        try:
            visited_review = title.find_element(By.XPATH,f'.//div[2]/span[{_index}]/a').text
            _index += 1
            blog_review = title.find_element(By.XPATH,f'.//div[2]/span[{_index}]/a').text
        except:
            print(Colors.RED + '------------ 리뷰 부분 오류 ------------' + Colors.RESET)

        store_id = driver.find_element(By.XPATH,'//div[@class="flicking-camera"]/a').get_attribute('href').split('/')[4]
        address = driver.find_element(By.XPATH,'//span[@class="LDgIH"]').text

        try:
            driver.find_element(By.XPATH,'//div[@class="y6tNq"]//span').click()
            sleep(2)
            parent_element = driver.find_element(By.XPATH,'//a[@class="gKP9i RMgN0"]')
            child_elements = parent_element.find_elements(By.XPATH, './*[@class="w9QyJ" or @class="w9QyJ undefined"]')

            for child in child_elements:
                span_elements = child.find_elements(By.XPATH, './/span[@class="A_cdD"]')
                for span in span_elements:
                    business_hours.append(span.text)

            phone_num = driver.find_element(By.XPATH,'//span[@class="xlx7Q"]').text

        except:
            print(Colors.RED + '------------ 영업시간 / 전화번호 부분 오류 ------------' + Colors.RESET)

        # ---------------------
        # 메뉴 정보 추출 부분
        # ---------------------
        # ./data/images/{store_id} 디렉토리 생성
        image_dir = f'./data/images/{index}-{store_name}-{store_id}'
        os.makedirs(image_dir, exist_ok=True)

        # try:

        # scrollable_element2 = driver.find_element(By.XPATH, '//*[@id="sub_panel"]')
        # scrollable_element2 = scrollable_element2.find_element(By.CLASS_NAME, 'place_on_pcmap')
        # last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_element2)

        # while True:
        #     driver.execute_script("arguments[0].scrollTop += 600;", scrollable_element2)
        #     sleep(1.5)
        #     new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_element2)
        #     if new_height == last_height:
        #         break
        #     last_height = new_height

        # 메뉴 컨테이너 탐색
        Menuflag = False
        for i in range(1,5):
            menu_container = driver.find_element(By.XPATH, f'//div[3]/div/div/div/div[4]/div/div/div/div/a[{i}]/span')
            if menu_container.text == '메뉴':
                menu_container.click()
                sleep(2)
                Menuflag = True
                break

        if Menuflag :
        
            if is_element_present(driver, '//div[1]/div[2]/div/div[1]/div/div[1]/div[1]'):
                print("네이버주문임")
                sleep(2)
                # try:
                menus_data.append(crawl_menu_with_xpath(driver, image_dir))
                # except:
                #     print(Colors.RED + '------------ 네이버 주문 메뉴 부분 오류 ------------' + Colors.RESET)

            else:
                print("네이버주문 아니고, 기본 메뉴정보임")
                try:    # 기본 메뉴
                    menu_items = driver.find_elements(By.XPATH, '//*[@class="E2jtL yxVGX"]')
                    print(menu_items)

                    for item in menu_items:
                        menu_section = "일반주문"

                        # 메뉴 이미지
                        try:
                            img_el = item.find_element(By.XPATH, './/img')
                            menu_img_url = img_el.get_attribute("src")
                        except:
                            menu_img_url = ""

                        # 메뉴 이름
                        try:
                            menu_name = item.find_element(By.XPATH, './/*[@class="lPzHi"]').text.strip()
                        except:
                            menu_name = ""

                        # 메뉴 설명
                        try:
                            menu_desc = item.find_element(By.XPATH, './/*[@class="TRxGt"]').text.strip()
                        except:
                            menu_desc = ""

                        # 메뉴 가격
                        try:
                            menu_price = item.find_element(By.XPATH, './/*[@class="GXS1X"]').text.strip()
                        except:
                            menu_price = ""

                        # 이미지 다운로드
                        safe_name = re.sub(r'[\\/*?:"<>|]', "_", menu_name)
                        image_path = os.path.join(image_dir, f"{safe_name}.jpg")
                        download_image(menu_img_url, image_path)

                        menus_data.append({
                            "menu_section": menu_section,
                            "menu_name": menu_name,
                            "menu_desc": menu_desc,
                            "menu_price": menu_price,
                            "menu_image_url": menu_img_url,
                            "menu_image_local_path": image_path
                        })

                        print("메뉴 추출 완료")
                        print(menus_data)
                except:
                    print(Colors.RED + '------------ 기본 메뉴 부분 오류 ------------' + Colors.RESET)
            
                # # "order_list_area" 요소 찾기
                # menu_sections = driver.find_elements(By.CSS_SELECTOR, ".order_list_wrap")
                # print(menu_sections)

                # for section in menu_sections:
                #     try:
                #         # 섹션 제목 (예: '사장님 추천 메뉴', '메인메뉴')
                #         menu_section = section.find_element(By.CSS_SELECTOR, ".order_list_tit .title").text

                #         # 섹션 내 메뉴 아이템들
                #         menu_items = section.find_elements(By.CSS_SELECTOR, ".order_list_item")

                #         for item in menu_items:
                #             try:
                #                 # 메뉴 이름
                #                 menu_name = item.find_element(By.CSS_SELECTOR, ".tit").text.strip()

                #                 # 메뉴 설명 (없을 수도 있음)
                #                 try:
                #                     menu_desc = item.find_element(By.CSS_SELECTOR, ".detail_txt").text.strip()
                #                 except:
                #                     menu_desc = ""

                #                 # 메뉴 가격
                #                 menu_price = item.find_element(By.CSS_SELECTOR, ".price").text.strip()

                #                 # 메뉴 이미지 URL
                #                 try:
                #                     img_el = item.find_element(By.CSS_SELECTOR, ".info_img img")
                #                     menu_img_url = img_el.get_attribute("src")
                #                 except:
                #                     menu_img_url = ""

                #                 # 이미지 다운로드
                #                 if menu_img_url:
                #                     safe_name = re.sub(r'[\\/*?\":<>|]', "_", menu_name)
                #                     image_path = os.path.join(image_dir, f"{safe_name}.jpg")
                #                     download_image(menu_img_url, image_path)
                #                 else:
                #                     image_path = ""

                #                 # 메뉴 데이터 추가
                #                 menus_data.append({
                #                     "menu_section": menu_section,
                #                     "menu_name": menu_name,
                #                     "menu_desc": menu_desc,
                #                     "menu_price": menu_price,
                #                     "menu_image_url": menu_img_url,
                #                     "menu_image_local_path": image_path
                #                 })
                #             except Exception as e:
                #                 print(f"메뉴 정보 크롤링 실패: {e}")

                #     except Exception as e:
                #         print(f"섹션 정보 크롤링 실패: {e}")
                                    
        else :
            print(Colors.RED + '------------ 등록된 메뉴가 없습니다. ------------' + Colors.RESET)


        # 추출한 가게 정보 딕셔너리
        store_data = {
            "store_name": store_name,
            "category": category,
            "new_open": new_open,
            "rating": rating,
            "visited_review": visited_review,
            "blog_review": blog_review,
            "store_id": store_id,
            "address": address,
            "business_hours": business_hours,
            "phone_num": phone_num,
            "menus": menus_data
        }

        # 결과 리스트에 추가
        results.append(store_data)

        print(Colors.BLUE + f'{index}. ' + str(store_name) + Colors.RESET + ' · ' + str(category) + Colors.RED + str(new_open) + Colors.RESET)
        print('평점 ' + Colors.RED + str(rating) + Colors.RESET + ' / ' + visited_review + ' · ' + blog_review)
        print(f'가게 고유 번호 -> {store_id}')
        print('가게 주소 ' + Colors.GREEN + str(address) + Colors.RESET)
        print(Colors.CYAN + '가게 영업 시간' + Colors.RESET)
        for i in business_hours:
            print(i)
        print('가게 번호 ' + Colors.GREEN + phone_num + Colors.RESET)
        print(Colors.MAGENTA + "-"*50 + Colors.RESET)
        print(menus_data)

    switch_left()

    if(next_page == 'false'):
        driver.find_element(By.XPATH,'//*[@id="app-root"]/div/div[3]/div[2]/a[7]').click()
    else:
        loop = False

# 모든 페이지 수집 완료 후 JSON 저장
os.makedirs('./data', exist_ok=True)
with open('./data/data.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

driver.quit()

