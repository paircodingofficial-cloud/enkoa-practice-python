"""스크롤 처리 및 JavaScript 실행 (클릭, 스크롤, 페이지 정보)"""
from playwright.sync_api import sync_playwright
import time

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

page.goto("https://play.google.com/store/apps?hl=ko")

# ========== 1. Playwright 네이티브 스크롤 ==========
# page.mouse.wheel(x, y) — 마우스 휠 스크롤 (Playwright 고유 기능)
# x: 가로 스크롤, y: 세로 스크롤 (양수 = 아래로)

# 1-1. 마우스 휠로 500px 아래로 스크롤
page.mouse.wheel(0, 500)
print("마우스 휠 스크롤 500px 완료")
page.wait_for_timeout(1000)

# 1-2. 부드러운 스크롤 — 조금씩 내려가며 자연스러운 스크롤 효과
#    사람처럼 천천히 스크롤하면 봇 감지 회피에도 도움이 됩니다
for _ in range(5):
    page.mouse.wheel(0, 200)
    time.sleep(0.3)
print("부드러운 스크롤 완료")
page.wait_for_timeout(1000)

# ========== 2. JavaScript 스크롤 ==========
# page.evaluate()로 JavaScript를 실행하여 스크롤할 수도 있습니다
# 특정 좌표로 정확히 이동하거나, 페이지 맨 아래/위로 이동할 때 유용

# 2-1. 페이지 맨 아래로 한 번에 스크롤
#    document.body.scrollHeight = 페이지 전체 높이
page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
print("페이지 맨 아래로 스크롤 완료")
page.wait_for_timeout(1000)

# 2-2. 특정 위치로 스크롤
page.evaluate("window.scrollTo(0, 1000)")  # 1000px 아래로 스크롤
print("JavaScript 스크롤 완료")
page.wait_for_timeout(1000)

# 2-3. 페이지 맨 위로 돌아가기
page.evaluate("window.scrollTo(0, 0)")
print("페이지 맨 위로 스크롤 완료")
page.wait_for_timeout(1000)

# ========== 3-1. 일반 Playwright 클릭 ==========
# Playwright의 click()은 실제 사용자처럼 요소가 보이고, 클릭 가능할 때까지 기다린 후 클릭합니다
# 대부분의 경우 이 방법을 먼저 사용합니다
try:
    element = page.locator("xpath=//*[@id='yDmH0d']/c-wiz[2]/div/div/c-wiz/div/div/div/div[1]/div[3]/a")

    # click(): 요소가 보이고(visible), 활성화(enabled)될 때까지 자동 대기 후 클릭
    element.click()
    print("일반 클릭 성공")
except Exception as e:
    print(f"일반 클릭 실패: {e}")

page.wait_for_timeout(2000)

# ========== 3-2. JavaScript로 요소 클릭 ==========
# 일반 click()이 안 되는 경우 (요소가 다른 요소에 가려져 있을 때 등)
# JavaScript의 el.click()을 사용하면 강제 클릭이 가능합니다
try:
    element = page.locator("xpath=//*[@id='yDmH0d']/c-wiz[2]/div/div/c-wiz/div/div/div/div[1]/div[3]/a")

    # evaluate(): 해당 요소에 JavaScript 코드를 직접 실행
    # "el => el.click()" — 화살표 함수로 요소(el)의 click() 호출
    element.evaluate("el => el.click()")
    print("JavaScript 클릭 성공")
except Exception as e:
    print(f"JavaScript 클릭 실패: {e}")

page.wait_for_timeout(2000)

# ========== 4. JavaScript로 페이지 정보 가져오기 ==========
# evaluate()의 반환값을 Python 변수로 받을 수 있습니다
page_height = page.evaluate("document.body.scrollHeight")
print(f"페이지 전체 높이: {page_height}px")
page.wait_for_timeout(1000)

browser.close()
pw.stop()
