# feeds.py — RSS 피드 목록
# 검증 기준: WebFetch HTTP 200 + 유효 XML 확인 (2026-05-15)
#
# [Naver 블로그 RSS 안내]
# rss.blog.naver.com 및 blog.naver.com 도메인은 Naver가 외부 봇 접근을 차단합니다.
# Claude Code 환경에서 자동 검증이 불가능하므로 아래 URL은 수동 확인이 필요합니다.
# Naver 블로그 RSS 형식: https://rss.blog.naver.com/{blogId}.xml
# 작동하지 않는 항목은 feedparser가 자동으로 무시합니다.

# ── 시장 뉴스 ──────────────────────────────────────────────
# 수산가공·1인가구·워킹맘 간편식 관련 식품 전문 매체
# 모두 HTTP 200 + RSS 2.0 XML 검증 완료
MARKET_NEWS_FEEDS = [
    {
        "name": "식품저널 foodnews",
        "url": "http://www.foodnews.co.kr/rss/allArticle.xml",
        "domain": "foodnews.co.kr",
    },
    {
        "name": "식품외식경제",
        "url": "https://www.foodbank.co.kr/rss/allArticle.xml",
        "domain": "foodbank.co.kr",
    },
    {
        "name": "식품음료신문",
        "url": "https://www.thinkfood.co.kr/rss/allArticle.xml",
        "domain": "thinkfood.co.kr",
    },
]

# ── 경쟁사 네이버 블로그 ────────────────────────────────────
# rss.blog.naver.com 도메인은 Naver의 봇 차단 정책으로 자동 검증 불가.
# 아래 URL은 Naver 표준 RSS 형식 기반으로 작성된 것으로,
# 실제 블로그 ID를 확인한 후 URL을 수정해 주세요.
# 확인 방법: 해당 블로그 접속 → 우상단 RSS 아이콘 클릭 → URL 복사
#
# 현재 주요 경쟁사(비비고·동원F&B·오뚜기·청정원)는 Instagram/YouTube/자사 사이트를
# 주 채널로 운영하며 Naver 블로그는 운영하지 않거나 비공개 운영 중입니다.
# 아래 URL을 직접 확인하고 실제 운영 중인 경쟁사 블로그로 교체해 주세요.
NAVER_BLOG_FEEDS = [
    {
        "name": "비비고 공식 블로그 (확인 필요)",
        "url": "https://rss.blog.naver.com/cjcheiljedang.xml",
        "domain": "rss.blog.naver.com",
        "group": "CJ제일제당",
        "verified": False,
    },
    {
        "name": "동원F&B 공식 블로그 (확인 필요)",
        "url": "https://rss.blog.naver.com/dongwonfnb.xml",
        "domain": "rss.blog.naver.com",
        "group": "동원F&B",
        "verified": False,
    },
    {
        "name": "오뚜기 공식 블로그 (확인 필요)",
        "url": "https://rss.blog.naver.com/ottogirecipe.xml",
        "domain": "rss.blog.naver.com",
        "group": "오뚜기",
        "verified": False,
    },
    {
        "name": "청정원 공식 블로그 (확인 필요)",
        "url": "https://rss.blog.naver.com/chungjungone.xml",
        "domain": "rss.blog.naver.com",
        "group": "청정원",
        "verified": False,
    },
]

# ── 경쟁사 유튜브 ───────────────────────────────────────────
# YouTube Atom feed: https://www.youtube.com/feeds/videos.xml?channel_id={ID}
# 모두 HTTP 200 + Atom XML 검증 완료
YOUTUBE_FEEDS = [
    {
        "name": "비비고 (bibigo)",
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCGmLtNZFTL6PiKsz3Vpdgbw",
        "domain": "youtube.com",
        "channel": "비비고",
    },
    {
        "name": "동원F&B(Dongwon)",
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCs_L1_g_MeTHhuRhJEkF_xA",
        "domain": "youtube.com",
        "channel": "동원F&B",
    },
    {
        "name": "청정원",
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCni5yuiUB59rF5h3eGrhqJg",
        "domain": "youtube.com",
        "channel": "청정원",
    },
]
