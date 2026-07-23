"""요소에서 데이터 추출하기 (Unsplash 카테고리 & 이미지 카드)"""
from playwright.sync_api import sync_playwright

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

page.goto("https://unsplash.com/ko")

# wait_for_selector(selector) — 해당 CSS 셀렉터의 요소가 DOM에 나타날 때까지 대기
# Unsplash는 JavaScript로 이미지를 동적 로딩하므로
# figure 요소가 나타날 때까지 대기해야 합니다 (안 하면 빈 페이지에서 데이터 추출 시도)
page.wait_for_selector("figure")

# ========== 1. 텍스트 읽기: .inner_text() ==========
# inner_text() — 요소 안의 화면에 보이는 텍스트를 문자열로 반환
# 셀렉터: ul li a (카테고리 탭 → Copy selector → ul > li:nth-child(3) > a → 일반화)
# .all() — 셀렉터에 매칭되는 모든 요소를 리스트로 반환 (반복문 사용 가능)
category_links = page.locator("ul li a").all()
print(f"카테고리 {len(category_links)}개 발견\n")

for link in category_links:
    name = link.inner_text()             # 화면에 보이는 텍스트 읽기
    href = link.get_attribute("href")    # get_attribute(name) — HTML 속성값 읽기
    print(f"  {name}: https://unsplash.com{href}")

# ========== 2. 요소 개수 확인: .count() ==========
# count() — 매칭되는 요소의 개수만 반환 (.all() 없이 빠르게 확인)
total = page.locator("ul li a").count()
print(f"\n카테고리 총 {total}개\n")

# ========== 3. 이미지 카드에서 속성값 읽기: .get_attribute() ==========
# 셀렉터: figure (이미지 카드 → Copy selector → figure:nth-child(1) → 일반화)
figures = page.locator("figure").all()
print(f"이미지 카드 {len(figures)}개 발견\n")

for i, fig in enumerate(figures[:5], 1):  # 처음 5개만 출력
    # figure 안의 img, a 태그
    # .first — 매칭되는 여러 요소 중 첫 번째만 선택
    img = fig.locator("img").first
    link = fig.locator("a").first

    alt_text = img.get_attribute("alt")   # alt 속성: 이미지 설명
    img_src = img.get_attribute("src")    # src 속성: 이미지 URL
    href = link.get_attribute("href")     # href 속성: 상세 페이지 링크

    print(f"[{i}] {alt_text}")
    print(f"    링크: https://unsplash.com{href}")
    print(f"    이미지: {img_src[:80]}...")
    print()

browser.close()
pw.stop()
