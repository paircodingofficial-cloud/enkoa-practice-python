"""네이버 뉴스 무한 스크롤로 다량 수집 & JSON 저장"""
from playwright.sync_api import sync_playwright
from datetime import datetime
import pandas as pd

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

try:
    # ========== 네이버 접속 및 키워드 검색 ==========
    page.goto("https://www.naver.com")
    search_box = page.locator("#query")
    search_box.fill("인공지능")
    search_box.press("Enter")

    # ========== 뉴스 탭 클릭 ==========
    news_button = page.locator("#lnb a", has_text="뉴스").first
    news_button.click()

    # ========== 기사 목록 로딩 대기 ==========
    # .all() 사용 전에 반드시 wait_for_selector로 로딩 확인
    page.wait_for_selector(".fds-news-item-list-tab")

    news_articles = []
    seen_urls = set()   # 이미 수집한 URL 저장 → 중복 기사 방지

    scroll_pause_time = 2   # 스크롤 후 로딩 대기 시간 (초)
    max_scrolls = 10        # 최대 스크롤 횟수 (늘리면 더 많은 기사 수집)
    scroll_count = 0

    print(f"\n{'='*80}")
    print(f"뉴스 수집 시작 (최대 {max_scrolls}회 스크롤)")
    print(f"{'='*80}\n")

    # ========== 스크롤 반복 → 새 기사 로딩 ==========
    while scroll_count < max_scrolls:
        # evaluate(js) — 페이지에서 JavaScript 코드를 실행하고 결과를 반환
        # 페이지 맨 아래로 이동 → 무한 스크롤 트리거
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(scroll_pause_time * 1000)
        scroll_count += 1
        print(f"스크롤 {scroll_count}/{max_scrolls} 완료")

    # ========== 스크롤 완료 후 전체 기사 수집 ==========
    # .fds-news-item-list-tab > div : 기사 카드 div만 선택 (span 구분선 제외)
    search_results = page.locator(".fds-news-item-list-tab > div").all()

    for article in search_results:
        article_info = {'press': None, 'title': None, 'content': None, 'url': None}

        # ========== 기사 URL — 중복 체크를 위해 가장 먼저 추출 ==========
        # a:has(.sds-comps-text-type-headline1) : 제목을 감싸는 <a> 태그 직접 선택
        # 네이버뉴스든 외부 언론사 링크든 항상 존재
        try:
            article_info['url'] = article.locator(
                "a:has(.sds-comps-text-type-headline1)"
            ).get_attribute("href", timeout=3000)
        except:
            pass

        # URL이 없거나 이미 수집한 기사는 건너뜀
        if not article_info['url'] or article_info['url'] in seen_urls:
            continue
        seen_urls.add(article_info['url'])

        # ========== 언론사 이름 ==========
        # 기사 레이아웃에 따라 텍스트 위치가 다를 수 있어 두 셀렉터를 순서대로 시도
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

        news_articles.append(article_info)
        print(f"[{len(news_articles)}] {article_info['title']}")

    print(f"\n{'='*80}")
    print(f"수집 완료! 총 {len(news_articles)}개의 뉴스 기사 수집")
    print(f"{'='*80}\n")

    # ========== 수집 데이터 저장 ==========
    df = pd.DataFrame(news_articles)
    print("[데이터 미리보기]")
    print(df.head())

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = f"naver_news_{timestamp}.json"
    df.to_json(json_filename, orient='records', force_ascii=False, indent=2)
    print(f"\nJSON 저장 완료: {json_filename}")

except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()
finally:
    page.wait_for_timeout(3000)
    browser.close()
    pw.stop()
