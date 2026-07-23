"""Unsplash 무한 스크롤 이미지 수집"""
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

# Unsplash는 JavaScript로 이미지를 동적 로딩하므로
# figure 요소가 나타날 때까지 대기해야 합니다 (안 하면 빈 페이지에서 데이터 추출 시도)
page.wait_for_selector("figure")

images = []
seen_srcs = set()   # 이미 수집한 이미지 URL 저장 (중복 방지)

max_scrolls = 5     # 최대 스크롤 횟수 (늘리면 더 많은 이미지 수집)
scroll_count = 0

print(f"이미지 수집 시작 (최대 {max_scrolls}회 스크롤)\n")

while scroll_count < max_scrolls:
    # ========== 현재 로딩된 이미지 수집 ==========
    figures = page.locator("figure").all()

    for fig in figures:
        img = fig.locator("img").first
        link = fig.locator("a").first

        src = img.get_attribute("src")
        if not src or src in seen_srcs:
            continue   # 이미 수집했거나 src 없으면 건너뜀

        seen_srcs.add(src)
        images.append({
            'alt': img.get_attribute("alt"),           # 이미지 설명
            'src': src,                                 # 이미지 URL
            'link': "https://unsplash.com" + (link.get_attribute("href") or ""),  # 상세 링크
        })

    print(f"스크롤 {scroll_count + 1}/{max_scrolls} — 현재 {len(images)}개 수집")

    # ========== 페이지 맨 아래로 스크롤 → 새 이미지 로딩 ==========
    prev_count = page.locator("figure").count()
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    # wait_for_function(js, timeout) — JS 표현식이 true가 될 때까지 대기
    # 새 figure가 추가될 때까지 최대 5초 대기
    try:
        page.wait_for_function(
            f"document.querySelectorAll('figure').length > {prev_count}",
            timeout=5000,
        )
    except:
        print("새 이미지 로딩 없음 — 종료")
        break

    scroll_count += 1

print(f"\n수집 완료! 총 {len(images)}개 이미지")
for i, img in enumerate(images[:5], 1):
    print(f"\n[{i}] {img['alt']}")
    print(f"    링크: {img['link']}")
    print(f"    이미지: {img['src'][:80]}...")

browser.close()
pw.stop()
