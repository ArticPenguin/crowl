import json

# 원본 데이터 읽기
with open('data/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 광진구 음식점만 필터링
gwangjin_stores = [store for store in data if '서울' in store['address']]

# 새로운 파일로 저장
with open('data/data-서울.json', 'w', encoding='utf-8') as f:
    json.dump(gwangjin_stores, f, ensure_ascii=False, indent=4)

print(f"광진구 음식점 {len(gwangjin_stores)}개를 저장했습니다.")
