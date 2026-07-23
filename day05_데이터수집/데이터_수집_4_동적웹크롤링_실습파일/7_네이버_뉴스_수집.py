"""네이버 뉴스 검색 & 기사 정보 수집 (단일 페이지)"""
from playwright.sync_api import sync_playwright
from pprint import pprint

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

# ========== 네이버 접속 및 검색 ==========
page.goto("https://www.naver.com")

# 검색창에 키워드 입력 후 Enter
search_box = page.locator("#query")
search_box.fill("인공지능")
search_box.press("Enter")

# ========== 뉴스 탭 클릭 ==========
# locator(selector, has_text="텍스트") — 셀렉터 + 텍스트 조건으로 요소 필터링
# .first — 여러 매칭 중 첫 번째 요소만 선택
# .click() — 요소가 보이고 클릭 가능할 때까지 자동 대기 후 클릭 (timeout 지원)
news_button = page.locator("#lnb a", has_text="뉴스").first
news_button.click()

# ========== 기사 목록 로딩 대기 후 전체 가져오기 ==========
# 주의: .all()은 자동 대기(auto-wait)가 없으므로, 먼저 컨테이너가 나타날 때까지 기다려야 함
page.wait_for_selector(".fds-news-item-list-tab")
# .fds-news-item-list-tab > div : 기사 카드 div만 선택 (span 구분선 제외)
search_results = page.locator(".fds-news-item-list-tab > div").all()

news_articles = []

print(f"\n{'='*80}")
print(f"총 {len(search_results)}개의 뉴스 기사 발견")
print(f"{'='*80}\n")

for article in search_results:
    article_info = {'press': None, 'title': None, 'content': None, 'url': None}

    # ========== 언론사 이름 ==========
    # 기사 레이아웃에 따라 언론사 텍스트 위치가 다를 수 있어 두 셀렉터를 순서대로 시도
    for selector in [
        ".sds-comps-profile-info-title-text",  # 일반 레이아웃
        ".sds-comps-text-type-body2",           # 일부 기사 대체 위치
    ]:
        try:
            text = article.locator(selector).first.inner_text(timeout=1500).strip()
            if text:
                article_info['press'] = text
                break  # 찾았으면 더 이상 시도하지 않음
        except:
            continue   # 타임아웃 → 다음 셀렉터 시도

    # ========== 기사 제목 ==========
    try:
        article_info['title'] = article.locator(".sds-comps-text-type-headline1").inner_text(timeout=3000)
    except:
        pass

    # ========== 본문 요약 ==========
    try:
        article_info['content'] = article.locator(".sds-comps-text-type-body1").inner_text(timeout=3000)
    except:
        pass

    # ========== 기사 URL ==========
    # a:has(.sds-comps-text-type-headline1) : 제목 텍스트를 감싸는 <a> 태그를 바로 선택
    # 네이버뉴스(n.news.naver.com)든 외부 언론사 링크든 항상 존재
    try:
        article_info['url'] = article.locator(
            "a:has(.sds-comps-text-type-headline1)"
        ).get_attribute("href", timeout=3000)
    except:
        pass

    news_articles.append(article_info)
    pprint(article_info)
    print()

browser.close()
pw.stop()
