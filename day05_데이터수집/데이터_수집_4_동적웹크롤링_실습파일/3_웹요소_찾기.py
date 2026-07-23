"""웹 요소 찾기 & 검색어 입력"""
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

page.goto("https://www.naver.com")

# ========== 요소 찾기 ==========
# 네이버 검색창의 실제 HTML:
# <input id="query" name="query" class="search_input"
#        placeholder="검색어를 입력해 주세요." role="combobox">

# 1. ID로 찾기 (#은 ID를 뜻함)
# locator(selector) — CSS 셀렉터 또는 XPath로 웹 요소를 찾는 핵심 함수
#   요소를 바로 찾지 않고, 실제 조작(click, fill 등) 시점에 찾음 (지연 평가)
search_box = page.locator("#query")

# 2. NAME 속성으로 찾기
# search_box = page.locator("[name='query']")

# 3. CLASS로 찾기 (.은 class를 뜻함)
# search_box = page.locator(".search_input")

# 4. XPath로 찾기 (xpath= 접두사 필요)
# search_box = page.locator("xpath=//input[@name='query']")

# 5. placeholder 텍스트로 찾기 (Playwright 고유 기능)
# get_by_placeholder(text) — placeholder 속성값으로 input 요소를 찾음
# search_box = page.get_by_placeholder("검색어를 입력해 주세요.")

# ========== 검색어 입력 및 실행 ==========
# fill(text) — 기존 텍스트를 모두 지우고 새 텍스트를 입력
# press(key) — 키보드 키 입력 ("Enter", "Tab", "Escape" 등)
# ※ 모든 동작 메서드는 timeout 파라미터 지원 (기본 30초, 밀리초 단위)
#    예: .fill("텍스트", timeout=5000)  → 5초 안에 입력 가능해야 함
search_box.fill("Python Playwright")
search_box.press("Enter")

# 결과 확인을 위해 5초 대기 후 제목 출력
page.wait_for_timeout(5000)
print("검색 완료:", page.title())

browser.close()
pw.stop()
