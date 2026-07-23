"""봇 감지를 회피하는 브라우저 설정"""
from playwright.sync_api import sync_playwright

pw = sync_playwright().start()

# Chrome 브라우저 실행
browser = pw.chromium.launch(channel="chrome", headless=False)

# ========== 자동화 감지 회피 ==========
# new_context() — 독립된 브라우저 환경 생성 (쿠키, 캐시가 분리됨)
#   user_agent: 웹사이트에 보내는 브라우저 정보 문자열 (일반 Chrome처럼 위장)
#   viewport:   브라우저 창 크기 설정 (width × height, 픽셀 단위)
context = browser.new_context(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    viewport={"width": 1920, "height": 1080},
)

page = context.new_page()

# ========== JavaScript를 통한 추가 위장 ==========
# add_init_script(script) — 페이지가 로드되기 전에 JavaScript를 자동 실행
# navigator.webdriver 속성을 제거하여 자동화 도구 감지 회피
# (웹사이트가 navigator.webdriver를 확인해도 undefined → 일반 사용자처럼 보임)
page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    })
""")

# ========== 테스트 ==========
page.goto("https://www.naver.com")
print("드라이버 준비 완료!")

page.wait_for_timeout(2000)
browser.close()
pw.stop()
