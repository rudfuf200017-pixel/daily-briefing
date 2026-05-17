# main.py — 가시제거연구소 데일리 브리핑 메인 실행
# 실행: python main.py
# AI API 호출 없음. feedparser + notion-client만 사용.

import sys
import time
from datetime import datetime, timezone, timedelta

# Windows 콘솔 UTF-8 출력
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import feedparser_compat as feedparser
from dotenv import load_dotenv

from feeds import MARKET_NEWS_FEEDS, NAVER_BLOG_FEEDS, YOUTUBE_FEEDS
from notion_publisher import publish_daily_briefing

load_dotenv()

KST = timezone(timedelta(hours=9))


def _now_kst() -> datetime:
    return datetime.now(tz=KST)


def _parse_published(entry) -> datetime | None:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        except Exception:
            pass
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        try:
            return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
        except Exception:
            pass
    return None


def _fetch_feed(feed_meta: dict) -> list:
    url = feed_meta["url"]
    name = feed_meta["name"]
    try:
        parsed = feedparser.parse(url)
        if parsed.bozo and not parsed.entries:
            print(f"  [SKIP] {name} — 파싱 오류 또는 빈 피드")
            return []
        entries = parsed.entries
        for e in entries:
            e._feed_name = name
        print(f"  [OK]   {name} — {len(entries)}건 수신")
        return entries
    except Exception as exc:
        print(f"  [FAIL] {name} — {exc}")
        return []


def _collect_section(feeds: list, tag: str) -> list:
    """모든 피드에서 엔트리를 수집하고 _feed_name 태그를 붙여 반환."""
    all_entries = []
    for feed_meta in feeds:
        entries = _fetch_feed(feed_meta)
        all_entries.extend(entries)
    return all_entries


def _filter_24h(entries: list, now_kst: datetime) -> list:
    cutoff = now_kst - timedelta(hours=24)
    result = []
    for e in entries:
        pub = _parse_published(e)
        if pub and pub >= cutoff:
            result.append((pub, e))
    result.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in result]


def _fallback_recent_n(entries: list, n: int) -> list:
    """기간 제한 없이 발행시각 있는 항목만 내림차순 최근 n건."""
    dated = []
    for e in entries:
        pub = _parse_published(e)
        if pub:
            dated.append((pub, e))
    dated.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in dated[:n]]


def _fallback_per_source(feeds: list, all_entries: list, max_total: int) -> list:
    """소스(feed name)별 최신 1건씩, 합산 최대 max_total건."""
    source_latest: dict[str, tuple] = {}
    for e in all_entries:
        pub = _parse_published(e)
        if pub is None:
            continue
        name = getattr(e, "_feed_name", "unknown")
        if name not in source_latest or pub > source_latest[name][0]:
            source_latest[name] = (pub, e)
    result = sorted(source_latest.values(), key=lambda x: x[0], reverse=True)
    return [e for _, e in result[:max_total]]


def process_market_news(now_kst: datetime) -> tuple[list, str]:
    print("\n[시장 뉴스] 수집 중...")
    all_entries = _collect_section(MARKET_NEWS_FEEDS, "market")
    recent = _filter_24h(all_entries, now_kst)[:3]
    if recent:
        label = f"1. 시장 핵심 뉴스 🆕 24시간 내 신규 {len(recent)}건"
        print(f"  → 1순위 성공: {len(recent)}건")
        return recent, label
    # 폴백
    fallback = _fallback_recent_n(all_entries, 3)
    label = f"1. 시장 핵심 뉴스 📚 24h 신규 없음 — 최근 {len(fallback)}건 참고"
    print(f"  → 폴백 발동: 최근 {len(fallback)}건")
    return fallback, label


def process_naver_blogs(now_kst: datetime) -> tuple[list, str]:
    print("\n[네이버 블로그] 수집 중...")
    all_entries = _collect_section(NAVER_BLOG_FEEDS, "blog")
    recent = _filter_24h(all_entries, now_kst)[:5]
    if recent:
        label = f"2. 경쟁사 블로그 동향 🆕 24시간 내 신규 {len(recent)}건"
        print(f"  → 1순위 성공: {len(recent)}건")
        return recent, label
    # 폴백: 소스별 최신 1건씩
    fallback = _fallback_per_source(NAVER_BLOG_FEEDS, all_entries, 5)
    label = f"2. 경쟁사 블로그 동향 📚 24h 신규 없음 — 소스별 최신 {len(fallback)}건 참고"
    print(f"  → 폴백 발동: 소스별 최신 {len(fallback)}건")
    return fallback, label


def process_youtube(now_kst: datetime) -> tuple[list, str]:
    print("\n[유튜브] 수집 중...")
    all_entries = _collect_section(YOUTUBE_FEEDS, "youtube")
    recent = _filter_24h(all_entries, now_kst)[:5]
    if recent:
        label = f"3. 경쟁사 유튜브 동향 🆕 24시간 내 신규 {len(recent)}건"
        print(f"  → 1순위 성공: {len(recent)}건")
        return recent, label
    # 폴백: 소스별 최신 1건씩
    fallback = _fallback_per_source(YOUTUBE_FEEDS, all_entries, 5)
    label = f"3. 경쟁사 유튜브 동향 📚 24h 신규 없음 — 소스별 최신 {len(fallback)}건 참고"
    print(f"  → 폴백 발동: 소스별 최신 {len(fallback)}건")
    return fallback, label


def main():
    now = _now_kst()
    date_str = now.strftime("%Y-%m-%d")
    print(f"=== 가시제거연구소 데일리 브리핑 시작 ({now.strftime('%Y-%m-%d %H:%M KST')}) ===")

    market_entries, market_label = process_market_news(now)
    blog_entries, blog_label = process_naver_blogs(now)
    yt_entries, yt_label = process_youtube(now)

    print("\n[노션 페이지 생성 중...]")
    try:
        page_url = publish_daily_briefing(
            market_news=market_entries,
            market_label=market_label,
            naver_blogs=blog_entries,
            naver_label=blog_label,
            youtube=yt_entries,
            youtube_label=yt_label,
            date_str=date_str,
        )
        print(f"\n✅ 노션 페이지 생성 완료: {page_url}")
    except Exception as exc:
        print(f"\n❌ 노션 페이지 생성 실패: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
