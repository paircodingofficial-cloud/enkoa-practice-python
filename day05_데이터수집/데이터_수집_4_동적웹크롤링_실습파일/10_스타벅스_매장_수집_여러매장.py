"""스타벅스 매장 정보 수집 (Playwright)
- 매장찾기 페이지에서 getStoreDetail(매장ID) 호출 → 팝업에서 정보 추출
"""
from playwright.sync_api import sync_playwright
from pprint import pprint
import pandas as pd


# ============================================================
# 헬퍼 함수
# ============================================================

def get_browser_and_page():
    """봇 감지를 회피하는 브라우저 및 페이지 생성"""
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
    return pw, browser, page


def extract_store_info(page, store_id):
    """
    매장 ID로 팝업을 열어 정보를 추출하고 팝업을 닫는 함수

    Args:
        page: Playwright 페이지 객체
        store_id: 스타벅스 매장 ID (숫자)

    Returns:
        dict: 매장 정보 딕셔너리 (실패 시 None)
    """
    try:
        # ── 1) 팝업 열기: JavaScript 함수 호출 ──
        page.evaluate(f"getStoreDetail('{store_id}')")

        # ── 2) 팝업창 선택 ──
        popup = page.locator(".shopArea_pop01")

        # ── 3) 매장명 ──
        name = popup.locator("header.titl h6").inner_text(timeout=3000).strip()

        # ── 4) 주소 — 도로명 주소만 추출 (지번 주소 제외) ──
        raw_address = popup.locator(
            ".shopArea_infoWrap > dl.shopArea_info:first-child dd"
        ).inner_text(timeout=3000).strip()
        address = raw_address.split("\n")[0].strip()

        # ── 5) 전화번호 — "1522-3232 (평일, 09:00~18:00)" 에서 번호만 추출 ──
        try:
            raw_tel = popup.locator("dl.shopArea_info.dl_tel dd").inner_text(timeout=3000).strip()
            tel = raw_tel.split("(")[0].strip()
        except:
            tel = "정보 없음"

        # ── 6) 주차정보 & 오시는 길: dt 텍스트로 필터링 ──
        parking = "정보 없음"
        directions = "정보 없음"

        dl_items = popup.locator(".shopArea_infoWrap dl.shopArea_info").all()
        for dl in dl_items:
            dt_text = dl.locator("dt").first.inner_text().strip()
            if "주차" in dt_text:
                parking = dl.locator("dd").inner_text().strip()
            elif "오시는 길" in dt_text:
                directions = dl.locator("dd").inner_text().strip()

        # ── 8) 팝업 닫기 ──
        popup.locator("p.btn_pop_close a.isStoreViewClosePop").click()
        page.wait_for_timeout(500)

        return {
            "id": store_id,
            "매장명": name,
            "주소": address,
            "전화번호": tel,
            "주차정보": parking,
            "오시는 길": directions,
        }

    except Exception as e:
        print(f"  - 매장 {store_id} 추출 실패: {e}")
        try:
            page.locator("p.btn_pop_close a.isStoreViewClosePop").click(timeout=1000)
            page.wait_for_timeout(500)
        except:
            pass
        return None


# ============================================================
# 1. 단일 매장 테스트 (ID: 3593 — 대전탄방역점)
# ============================================================
print("=" * 60)
print("1. 단일 매장 테스트")
print("=" * 60)

pw, browser, page = get_browser_and_page()
page.goto("https://www.starbucks.co.kr/store/store_map.do")
# wait_for_load_state(state) — 페이지 로딩 상태가 될 때까지 대기
#   "networkidle": 네트워크 요청이 0.5초간 없을 때 (= 페이지 완전 로딩)
page.wait_for_load_state("networkidle")
print(f"접속 완료: {page.title()}")

result = extract_store_info(page, 3593)
if result:
    pprint(result)

browser.close()
pw.stop()
print("브라우저 종료\n")


# ============================================================
# 2. 여러 매장 반복 수집 (ID 1~9)
# ============================================================
print("=" * 60)
print("2. 여러 매장 반복 수집")
print("=" * 60)

pw, browser, page = get_browser_and_page()
page.goto("https://www.starbucks.co.kr/store/store_map.do")
page.wait_for_load_state("networkidle")
print(f"접속 완료: {page.title()}\n")

store_ids = list(range(1, 10))
store_list = []

for sid in store_ids:
    print(f"매장 {sid} 수집 중...")
    data = extract_store_info(page, sid)

    if data:
        store_list.append(data)
        print(f"  -> {data['매장명']}")
    else:
        print(f"  -> 건너뜀")

browser.close()
pw.stop()
print(f"\n수집 완료: {len(store_list)}개 / {len(store_ids)}개")
print("브라우저 종료\n")


# ============================================================
# 3. DataFrame 변환 & JSON 저장
# ============================================================
print("=" * 60)
print("3. DataFrame 변환 & JSON 저장")
print("=" * 60)

df = pd.DataFrame(store_list)
print(df)

filename = "starbucks_stores.json"
df.to_json(filename, orient="records", force_ascii=False, indent=2)
print(f"\n'{filename}' 저장 완료 ({len(df)}개 매장)")
