# notion_publisher.py — 노션 페이지 생성
import os
import html
import re
from datetime import datetime, timezone, timedelta
from notion_client import Client

KST = timezone(timedelta(hours=9))


def _strip_html(text: str) -> str:
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", "", text)
    return " ".join(text.split())


def _truncate(text: str, limit: int = 110) -> str:
    text = _strip_html(text)
    return text[:limit] if len(text) > limit else text


def _fmt_published(entry) -> str:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).astimezone(KST)
        return dt.strftime("%Y-%m-%d %H:%M KST")
    return "발행시각 미상"


def _image_block(url: str) -> dict:
    return {
        "object": "block",
        "type": "image",
        "image": {"type": "external", "external": {"url": url}},
    }


def _paragraph_block(text: str, url: str | None = None, color: str = "default") -> dict:
    if url:
        rich = [
            {
                "type": "text",
                "text": {"content": text, "link": {"url": url}},
                "annotations": {"bold": True},
            }
        ]
    else:
        rich = [
            {
                "type": "text",
                "text": {"content": text},
                "annotations": {"color": color},
            }
        ]
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": rich},
    }


def _heading2_block(text: str) -> dict:
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        },
    }


def _divider_block() -> dict:
    return {"object": "block", "type": "divider", "divider": {}}


def _get_thumbnail(entry) -> str | None:
    # media:thumbnail (YouTube Atom)
    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        return entry.media_thumbnail[0].get("url")
    # enclosure (일부 RSS)
    if hasattr(entry, "enclosures") and entry.enclosures:
        for enc in entry.enclosures:
            mime = enc.get("type", "")
            if mime.startswith("image/"):
                return enc.get("href") or enc.get("url")
    # links with image type
    if hasattr(entry, "links"):
        for lnk in entry.links:
            if lnk.get("type", "").startswith("image/"):
                return lnk.get("href")
    return None


def _entry_blocks(entry, include_summary: bool = False) -> list[dict]:
    blocks = []
    thumb = _get_thumbnail(entry)
    if thumb:
        blocks.append(_image_block(thumb))
    title = _strip_html(getattr(entry, "title", "(제목 없음)"))
    link = getattr(entry, "link", None)
    blocks.append(_paragraph_block(title, url=link))
    if include_summary:
        summary = _truncate(getattr(entry, "summary", getattr(entry, "description", "")), 110)
        if summary:
            blocks.append(_paragraph_block(summary))
    source = getattr(entry, "_feed_name", "")
    pub = _fmt_published(entry)
    meta = f"{source}  ·  {pub}" if source else pub
    blocks.append(_paragraph_block(meta, color="gray"))
    return blocks


def _section_blocks(
    label: str,
    entries: list,
    include_summary: bool = False,
) -> list[dict]:
    blocks = [_heading2_block(label)]
    for entry in entries:
        blocks.extend(_entry_blocks(entry, include_summary=include_summary))
    blocks.append(_divider_block())
    return blocks


def publish_daily_briefing(
    market_news: list,
    market_label: str,
    naver_blogs: list,
    naver_label: str,
    youtube: list,
    youtube_label: str,
    date_str: str,
) -> str:
    api_key = os.environ.get("NOTION_API_KEY")
    parent_page_id = os.environ.get("NOTION_PARENT_PAGE_ID")
    if not api_key:
        raise RuntimeError("NOTION_API_KEY 환경변수가 설정되지 않았습니다.")
    if not parent_page_id:
        raise RuntimeError("NOTION_PARENT_PAGE_ID 환경변수가 설정되지 않았습니다.")

    notion = Client(auth=api_key)
    title = f"[가시제거연구소 데일리 브리핑] {date_str}"

    blocks: list[dict] = []
    blocks.extend(_section_blocks(market_label, market_news, include_summary=True))
    blocks.extend(_section_blocks(naver_label, naver_blogs, include_summary=False))
    blocks.extend(_section_blocks(youtube_label, youtube, include_summary=False))

    # Notion API는 블록을 100개씩 나눠서 전송해야 함
    CHUNK = 100
    response = notion.pages.create(
        parent={"page_id": parent_page_id},
        properties={
            "title": {
                "title": [{"type": "text", "text": {"content": title}}]
            }
        },
        children=blocks[:CHUNK],
    )
    page_id = response["id"]

    for i in range(CHUNK, len(blocks), CHUNK):
        notion.blocks.children.append(
            block_id=page_id,
            children=blocks[i : i + CHUNK],
        )

    page_url = response.get("url", f"https://notion.so/{page_id.replace('-', '')}")
    return page_url
