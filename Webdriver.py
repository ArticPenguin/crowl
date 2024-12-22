from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os   
import requests
from pathlib import Path
import urllib.parse
import traceback  # 스택 트레이스를 출력하기 위한 모듈

class NaverMapCrawler:
    def __init__(self, crawl_restaurant_name=True, crawl_menu_name=True, crawl_menu_price=True, crawl_menu_image=True):
        self.crawl_restaurant_name = crawl_restaurant_name
        self.crawl_menu_name = crawl_menu_name
        self.crawl_menu_price = crawl_menu_price
        self.crawl_menu_image = crawl_menu_image
        
        self.setup_driver()
        
        # CSS 선택자 변수 정의
        self.restaurant_name_selector = "span.YwYLL"  # 음식점 이름 요소
        self.menu_name_selector = "div.erVoL > div > span"  # 메뉴 이름
        self.menu_price_selector = "div.MN48z > div.Yrsei > div > em"  # 메뉴 가격
        self.menu_image_selector = "div.ZHqBk > div > img"  # 메뉴 이미지

    def setup_driver(self):
        """Chrome WebDriver 설정"""
        options = webdriver.ChromeOptions()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36")
        # options.add_argument('--headless')  # 헤드리스 모드 필요시 주석 해제
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
    def get_restaurant_data(self, search_query: str, center: str, restaurant_id: str) -> dict:
        """
        네이버 지도의 음식점 정보를 크롤링하는 메인 함수
        
        Args:
            search_query: 검색어
            center: 지도의 중심점
            restaurant_id: 음식점 고유 ID
        
        Returns:
            음식점 정보를 담은 딕셔너리
        """
        try:
            # 검색어를 URL 인코딩
            encoded_query = urllib.parse.quote(search_query)
            url = f"https://map.naver.com/p/search/{encoded_query}?c={center}"
            try:
                # WebDriver 실행
                self.driver.get(url)
                print(f"URL 로드 성공: {url}")
            except Exception as e:
                print(f"URL 로드 실패: {str(e)}")

            
            # 페이지 로딩 대기
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.restaurant_name_selector))
                )
            except Exception as e:
                print(f"페이지 로딩 실패??: {str(e)}")
                traceback.print_exc()
            
            # 음식점 이름 추출
            try:
                restaurant_name = None
                if self.crawl_restaurant_name:
                    restaurant_name = self.driver.find_element(By.CSS_SELECTOR, self.restaurant_name_selector).text
            except Exception as e:
                print(f"음식점 이름 추출 실패: {str(e)}")
                traceback.print_exc()
            
            # 메뉴 정보 추출
            menus = self._extract_menu_info()
            
            # 데이터 저장
            data = {
                "restaurant_name": restaurant_name,
                "menus": menus
            }
            
            # 파일 저장
            self._save_data(data, restaurant_id)
            
            return data
            
        except Exception as e:
            print(f"크롤링 중 오류 발생: {str(e)}")
            return None
        
    def _extract_menu_info(self) -> list:
        """메뉴 정보 추출"""
        menus = []
        # 메뉴 섹션으로 스크롤
        self.driver.execute_script("window.scrollTo(0, 800)")
        time.sleep(2)
        
        # 메뉴 요소들 찾기
        menu_elements = self.driver.find_elements(By.CSS_SELECTOR, "li")  # 모든 메뉴 항목을 찾기 위해 li 태그 사용
        
        for menu in menu_elements:
            try:
                menu_data = {}
                if self.crawl_menu_name:
                    menu_data["menu_name"] = menu.find_element(By.CSS_SELECTOR, self.menu_name_selector).text
                if self.crawl_menu_price:
                    menu_data["price"] = menu.find_element(By.CSS_SELECTOR, self.menu_price_selector).text
                if self.crawl_menu_image:
                    menu_data["image_url"] = menu.find_element(By.CSS_SELECTOR, self.menu_image_selector).get_attribute("src")
                
                # 모든 항목이 크롤링되었을 경우에만 추가
                if menu_data:
                    menus.append(menu_data)
            except Exception as e:
                # 오류 발생 시 스택 트레이스를 출력
                print(f"메뉴 정보 추출 중 오류: {str(e)}")
                traceback.print_exc()  # 전체 스택 트레이스 출력
                continue
                
        return menus
    
    def _save_data(self, data: dict, restaurant_id: str):
        """데이터와 이미지 저장"""
        # 디렉토리 생성
        base_path = Path(f"data/{restaurant_id}")
        images_path = base_path / "images"
        base_path.mkdir(parents=True, exist_ok=True)
        images_path.mkdir(parents=True, exist_ok=True)
        
        # 이미지 다운로드
        for menu in data["menus"]:
            try:
                if "image_url" in menu:
                    image_filename = f"{menu['menu_name'].replace('/', '_')}.jpg"
                    image_path = images_path / image_filename
                    
                    # 이미지 다운로드
                    response = requests.get(menu["image_url"])
                    with open(image_path, "wb") as f:
                        f.write(response.content)
                    
                    # 상대 경로 저장
                    menu["image_local_path"] = f"images/{image_filename}"
                
            except Exception as e:
                print(f"이미지 다운로드 중 오류: {str(e)}")
                continue
        
        # JSON 저장
        with open(base_path / "data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def close(self):
        """WebDriver 종료"""
        self.driver.quit()

def main():
    """
    실행 방법:
    1. 가상환경 생성: python -m venv venv
    2. 가상환경 활성화: 
       - Windows: venv/Scripts/activate
       - Linux/Mac: source venv/bin/activate
    3. 패키지 설치: pip install selenium requests webdriver-manager
    4. 크롬 드라이버 설치 및 프로젝트 루트에 배치
    """
    
    # 크롤러 인스턴스 생성
    crawler = NaverMapCrawler(crawl_restaurant_name=True, crawl_menu_name=False, crawl_menu_price=False, crawl_menu_image=False)
    
    # 테스트 실행
    search_query = "탕화쿵후"
    center = "15.00,0,0,0dh"
    restaurant_id = "test_restaurant"
    
    try:
        data = crawler.get_restaurant_data(search_query, center, restaurant_id)
        if data:
            print("크롤링 완료!")
            print(f"저장된 데이터: data/{restaurant_id}/data.json")
    finally:
        crawler.close()

if __name__ == "__main__":
    main()