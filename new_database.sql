-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS restaurant_db;
USE restaurant_db;

-- 음식점 테이블 생성
CREATE TABLE restaurants (
    id VARCHAR(20) PRIMARY KEY,     -- store_id를 PK로 사용
    name VARCHAR(100) NOT NULL,     -- store_name
    category VARCHAR(50),           -- category
    rating DECIMAL(3,2),           -- rating (별점)
    visited_review VARCHAR(100),    -- visited_review
    blog_review VARCHAR(100),       -- blog_review
    address TEXT,                   -- address
    latitude DECIMAL(10,7),        -- 위도
    longitude DECIMAL(10,7),       -- 경도
    phone_num VARCHAR(20),          -- phone_num
    business_hours TEXT             -- business_hours (JSON 형태로 저장)
);

-- 메뉴 테이블 생성
CREATE TABLE menus (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- 메뉴 고유 ID
    restaurant_id VARCHAR(20),          -- 음식점 ID (FK)
    section VARCHAR(50),                -- menu_section
    name VARCHAR(200) NOT NULL,         -- menu_name
    description TEXT,                   -- menu_desc
    price INT,                          -- menu_price (숫자만 저장)
    image_url TEXT,                     -- menu_image_url
    image_path TEXT,                    -- menu_image_local_path
    has_nutrition BOOLEAN DEFAULT FALSE, -- 영양정보 유무
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);

-- 영양정보 테이블 생성
CREATE TABLE nutrition_facts (
    menu_id INT PRIMARY KEY,           -- 메뉴 ID (FK)
    calories INT,                      -- 칼로리 (kcal)
    sugar DECIMAL(6,2),               -- 당류 (g)
    protein DECIMAL(6,2),             -- 단백질 (g)
    sodium DECIMAL(6,2),              -- 나트륨 (mg)
    saturated_fat DECIMAL(6,2),       -- 포화지방 (g)
    FOREIGN KEY (menu_id) REFERENCES menus(id)
);
