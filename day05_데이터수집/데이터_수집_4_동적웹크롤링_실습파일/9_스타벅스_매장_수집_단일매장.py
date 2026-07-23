"""스타벅스 매장 정보 수집 — 기초 버전 (함수 없이 단계별 실행)
- 매장찾기 페이지에서 getStoreDetail(매장ID) 호출 → 팝업에서 정보 추출
"""
from playwright.sync_api import sync_playwright
from pprint import pprint

# ============================================================
# 1. 브라우저 실행 및 페이지 접속
# ============================================================
pw = sync_playwright().start()
browser = pw.chromium.launch(channel="chrome", headless=False)
context = browser.new_context(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    viewport={"width": 1920, "height": 1080},
)
page = context.new_page()
page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined })
""")

page.goto("https://www.starbucks.co.kr/store/store_map.do")
# wait_for_load_state(state) — 페이지 로딩 상태가 될 때까지 대기
#   "networkidle": 네트워크 요청이 0.5초간 없을 때 (= 페이지 완전 로딩)
#   "load": HTML, CSS, 이미지 로딩 완료 시 / "domcontentloaded": HTML 파싱 완료 시
page.wait_for_load_state("networkidle")
print(f"접속 완료: {page.title()}")

# ============================================================
# 2. 매장 팝업 열기 — JavaScript 함수 호출
# ============================================================
# 스타벅스 사이트에 내장된 getStoreDetail() 함수를 호출하면 매장 팝업이 열립니다
# 매장 ID 예시: 3593 (대전탄방역점)
store_id = 3593
page.evaluate(f"getStoreDetail('{store_id}')")
print(f"매장 {store_id} 팝업 열기 완료")

# ============================================================
# 3. 팝업에서 매장 정보 추출
# ============================================================
# 팝업 요소 선택
popup = page.locator(".shopArea_pop01")

# 3-1. 매장명
name = popup.locator("header.titl h6").inner_text(timeout=3000).strip()
print(f"매장명: {name}")

# 3-2. 주소 — 도로명 주소만 추출 (지번 주소 제외)
raw_address = popup.locator(
    ".shopArea_infoWrap > dl.shopArea_info:first-child dd"
).inner_text(timeout=3000).strip()
address = raw_address.split("\n")[0].strip()
print(f"주소: {address}")

# 3-3. 전화번호 — "1522-3232 (평일, 09:00~18:00)" 에서 번호만 추출
try:
    raw_tel = popup.locator("dl.shopArea_info.dl_tel dd").inner_text(timeout=3000).strip()
    tel = raw_tel.split("(")[0].strip()
except:
    tel = "정보 없음"
print(f"전화번호: {tel}")

# 3-4. 주차정보 & 오시는 길: dt 텍스트로 필터링
parking = "정보 없음"
directions = "정보 없음"

dl_items = popup.locator(".shopArea_infoWrap dl.shopArea_info").all()
for dl in dl_items:
    dt_text = dl.locator("dt").first.inner_text().strip()
    if "주차" in dt_text:
        parking = dl.locator("dd").inner_text().strip()
    elif "오시는 길" in dt_text:
        directions = dl.locator("dd").inner_text().strip()

print(f"주차정보: {parking}")
print(f"오시는 길: {directions}")

# ============================================================
# 4. 결과 정리 및 출력
# ============================================================
result = {
    "id": store_id,
    "매장명": name,
    "주소": address,
    "전화번호": tel,
    "주차정보": parking,
    "오시는 길": directions,
}

print("\n" + "=" * 60)
print("수집 결과:")
print("=" * 60)
pprint(result)

# ============================================================
# 5. 팝업 닫기 및 브라우저 종료
# ============================================================
popup.locator("p.btn_pop_close a.isStoreViewClosePop").click()
page.wait_for_timeout(500)

browser.close()
pw.stop()
print("\n브라우저 종료")
