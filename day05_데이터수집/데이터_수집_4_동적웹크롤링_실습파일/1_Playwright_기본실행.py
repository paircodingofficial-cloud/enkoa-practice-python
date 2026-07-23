from playwright.sync_api import sync_playwright    # Playwright 동기 API
from pprint import pprint                         
from datetime import datetime                    
import pandas as pd           


# sync_playwright().start() — Playwright 엔진을 시작하고 브라우저를 제어할 수 있는 객체 반환
pw = sync_playwright().start()

# ========== 브라우저 실행 ==========
# channel="chrome" : 설치된 Chrome 브라우저를 사용
# headless=False    : 브라우저 창을 화면에 보이게 실행 (True면 백그라운드에서 실행)
browser = pw.chromium.launch(channel="chrome", headless=False)

# 새 탭(페이지) 열기 — 웹페이지 하나를 조작하기 위한 단위
page = browser.new_page()

# ========== 웹페이지 접속 ==========
# goto()로 원하는 URL에 접속 (주소창에 URL 입력 후 Enter 치는 것과 동일)
page.goto("https://www.google.com")

# wait_for_timeout(ms) — 지정한 밀리초(1000ms = 1초)만큼 대기
page.wait_for_timeout(3000)

# title() — 현재 페이지의 <title> 태그 내용을 문자열로 반환
print("페이지 제목:", page.title())

# ========== 정리 ==========
# 반드시 사용 후 browser와 pw를 종료해야 리소스가 해제됩니다
browser.close()  # 브라우저 닫기
pw.stop()        # Playwright 엔진 종료