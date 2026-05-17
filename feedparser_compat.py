# feedparser_compat.py — feedparser 인터페이스를 표준 라이브러리로 구현
# RSS 2.0 및 Atom 1.0 피드를 파싱하며 feedparser와 동일한 속성을 제공한다.

import time
import email.utils
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

import requests

_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "media": "http://search.yahoo.com/mrss/",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "dc": "http://purl.org/dc/elements/1.1/",
}

_ATOM_NS = "http://www.w3.org/2005/Atom"


class _Entry:
    def __init__(self):
        self.title = ""
        self.link = ""
        self.summary = ""
        self.description = ""
        self.published_parsed = None   # time.struct_time (UTC)
        self.updated_parsed = None     # time.struct_time (UTC)
        self.media_thumbnail = []      # [{"url": "..."}]
        self.enclosures = []           # [{"type": "...", "href": "...", "url": "..."}]
        self.links = []                # [{"type": "...", "href": "..."}]
        self._feed_name = ""


class _FeedResult:
    def __init__(self):
        self.entries = []
        self.bozo = False


def _parse_date(s: str):
    """RFC 2822 또는 ISO 8601 날짜 문자열을 time.struct_time(UTC)으로 변환."""
    if not s:
        return None
    s = s.strip()
    # RFC 2822 (RSS pubDate: "Mon, 01 Jan 2024 00:00:00 +0900")
    try:
        dt = email.utils.parsedate_to_datetime(s)
        return dt.utctimetuple()
    except Exception:
        pass
    # ISO 8601: Python 3.7+ fromisoformat handles "2024-01-01T00:00:00+09:00"
    try:
        # Replace trailing Z with +00:00 for fromisoformat
        iso = s.replace("Z", "+00:00")
        dt = datetime.fromisoformat(iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.utctimetuple()
    except Exception:
        pass
    # Plain date "2024-01-01"
    try:
        dt = datetime.strptime(s[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return dt.utctimetuple()
    except Exception:
        pass
    return None


def _text(el, tag, ns=None):
    child = el.find(tag) if ns is None else el.find(f"{{{ns}}}{tag}")
    return (child.text or "").strip() if child is not None else ""


def _parse_rss(root) -> list:
    entries = []
    channel = root.find("channel")
    if channel is None:
        return entries
    for item in channel.findall("item"):
        e = _Entry()
        e.title = _text(item, "title")
        e.link = _text(item, "link")
        e.summary = _text(item, "description")
        e.description = e.summary

        pub = _text(item, "pubDate") or _text(item, "date", _NS.get("dc", ""))
        e.published_parsed = _parse_date(pub)

        # dc:date fallback
        dc_date = item.find(f"{{{_NS['dc']}}}date")
        if dc_date is not None and not e.published_parsed:
            e.published_parsed = _parse_date((dc_date.text or "").strip())

        # media:thumbnail
        for mt in item.findall(f"{{{_NS['media']}}}thumbnail"):
            url = mt.get("url", "")
            if url:
                e.media_thumbnail.append({"url": url})

        # enclosure
        for enc in item.findall("enclosure"):
            e.enclosures.append({
                "type": enc.get("type", ""),
                "href": enc.get("url", ""),
                "url": enc.get("url", ""),
            })

        entries.append(e)
    return entries


def _parse_atom(root) -> list:
    entries = []
    ns = _ATOM_NS
    for item in root.findall(f"{{{ns}}}entry"):
        e = _Entry()
        e.title = _text(item, "title", ns)

        # link: prefer rel=alternate or no rel, type=text/html
        for lnk in item.findall(f"{{{ns}}}link"):
            rel = lnk.get("rel", "alternate")
            href = lnk.get("href", "")
            ltype = lnk.get("type", "")
            e.links.append({"type": ltype, "href": href, "rel": rel})
            if rel in ("alternate", "") and not e.link:
                e.link = href

        e.summary = _text(item, "summary", ns) or _text(item, "content", ns)
        e.description = e.summary

        pub = _text(item, "published", ns) or _text(item, "updated", ns)
        e.published_parsed = _parse_date(pub)
        upd = _text(item, "updated", ns)
        e.updated_parsed = _parse_date(upd)

        # media:thumbnail (YouTube)
        for mt in item.findall(f"{{{_NS['media']}}}thumbnail"):
            url = mt.get("url", "")
            if url:
                e.media_thumbnail.append({"url": url})
        # media:group > media:thumbnail
        mg = item.find(f"{{{_NS['media']}}}group")
        if mg is not None:
            for mt in mg.findall(f"{{{_NS['media']}}}thumbnail"):
                url = mt.get("url", "")
                if url:
                    e.media_thumbnail.append({"url": url})

        entries.append(e)
    return entries


def parse(url: str) -> _FeedResult:
    result = _FeedResult()
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        content = resp.content
    except Exception as exc:
        result.bozo = True
        return result

    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        result.bozo = True
        return result

    tag = root.tag.lower()
    # strip namespace
    local = tag.split("}")[-1] if "}" in tag else tag

    if local in ("rss", "rdf"):
        result.entries = _parse_rss(root)
    elif local == "feed":
        result.entries = _parse_atom(root)
    else:
        result.bozo = True

    return result
