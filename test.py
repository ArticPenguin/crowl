from selenium.webdriver.common.by import By
import re
import os
import requests
def download_image(image_url, save_path):
    r = requests.get(image_url, stream=True)
    if r.status_code == 200:
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        print(f"이미지 다운로드 완료: {save_path}")
    else:
        print(f"이미지 다운로드 실패: {r.status_code}")

def crawl_menu_with_xpath(driver, path):
    menus_data = []

    # 메뉴 섹션 찾기
    menu_items = driver.find_elements(By.XPATH, '//*[@class="item_info"]')

    print(menu_items)

    for item in menu_items:
        menu_section = "네이버주문"
        try:
            # 메뉴 이미지
            try:
                img_el = item.find_element(By.XPATH, './/img')
                menu_img_url = img_el.get_attribute("src")
            except:
                menu_img_url = ""

            # 메뉴 이름
            try:
                menu_name = item.find_element(By.XPATH, './/*[@class="tit"]').text.strip()
            except:
                menu_name = ""

            # 메뉴 설명
            try:
                menu_desc = item.find_element(By.XPATH, './/*[@class="detail_txt"]').text.strip()
            except:
                menu_desc = ""

            # 메뉴 가격
            try:
                menu_price = item.find_element(By.XPATH, './/*[@class="price"]').text.strip()
            except:
                menu_price = ""

            # 이미지 저장

            safe_name = re.sub(r'[\\/*?:"<>|]', "_", menu_name)
            image_path = os.path.join(path, f"{safe_name}.jpg")
            os.makedirs(path, exist_ok=True)
            download_image(menu_img_url, image_path)



            if menu_img_url:
                download_image(menu_img_url, image_path)

            menus_data.append({
                "menu_section": menu_section,
                "menu_name": menu_name,
                "menu_desc": menu_desc,
                "menu_price": menu_price,
                "menu_image_url": menu_img_url,
                "menu_image_local_path": image_path
            })
        except Exception as e:
            print(f"메뉴 정보 크롤링 중 오류: {e}")

    return menus_data