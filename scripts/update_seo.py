"""Synchronize ERN public SEO and distribution metadata with live.json."""
import email.utils
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "index.html"
STATUS = ROOT / "live.json"
SITEMAPS = [ROOT / "sitemap.xml", ROOT / "sitemap-ern.xml"]
TEXT_SITEMAP = ROOT / "sitemap.txt"
FEED = ROOT / "feed.xml"
PAGE_URL = "https://ern-inc.github.io/earth-right-now/"
SCRIPT_RE = re.compile(r'(<script type="application/ld\\+json">)(.*?)(</script>)', re.S)
VIDEO_ID_RE = re.compile(r"[A-Za-z0-9_-]{11}\\Z")


def valid_video_id(value):
    return isinstance(value, str) and bool(VIDEO_ID_RE.fullmatch(value))


def rss_date(value):
    if not value:
        return email.utils.format_datetime(datetime.now(timezone.utc))
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return email.utils.format_datetime(dt)
    except ValueError:
        return email.utils.format_datetime(datetime.now(timezone.utc))


def main():
    if not STATUS.exists():
        print("No live.json yet; leaving SEO metadata unchanged")
        return 0

    status = json.loads(STATUS.read_text(encoding="utf-8"))
    if status.get("status") not in ("live", "offline"):
        raise ValueError("Unknown live status; refusing to alter SEO")

    video_id = status.get("videoId")
    if status["status"] == "live" and not valid_video_id(video_id):
        raise ValueError("Invalid live video ID; refusing to alter SEO")

    html = SITE.read_text(encoding="utf-8")
    match = SCRIPT_RE.search(html)
    if not match:
        raise ValueError("Existing structured data script not found")

    page = json.loads(match.group(2))
    if page.get("@type") != "WebPage":
        raise ValueError("Unexpected structured data; refusing to overwrite")

    upload_date = status.get("uploadDate")
    checked_at = status.get("checkedAt")

    if status["status"] == "live":
        watch_url = f"https://www.youtube.com/watch?v={video_id}"
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        thumb_hq = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
        thumb_max = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"

        page["mainEntity"] = {
            "@type": "VideoObject",
            "name": "EARTH RIGHT NOW — Live Earth Screensaver",
            "description": "Live Earth visualization featuring sunrise, sunset and city news across 286 cities.",
            "thumbnailUrl": thumb_hq,
            "embedUrl": embed_url,
            "url": watch_url,
            "isLiveBroadcast": True,
        }
        if isinstance(upload_date, str) and upload_date:
            page["mainEntity"]["uploadDate"] = upload_date

        # Keep share previews and no-JS fallbacks synchronized with the live stream.
        html = re.sub(
            r'(<meta property="og:image" content=")https://i\\.ytimg\\.com/vi/[A-Za-z0-9_-]{11}/maxresdefault\\.jpg(">)',
            rf'\\1{thumb_max}\\2',
            html,
            count=1,
        )
        html = re.sub(
            r'(<meta name="twitter:image" content=")https://i\\.ytimg\\.com/vi/[A-Za-z0-9_-]{11}/maxresdefault\\.jpg(">)',
            rf'\\1{thumb_max}\\2',
            html,
            count=1,
        )
        html = re.sub(
            r"(const defaultId=')[A-Za-z0-9_-]{11}(';)",
            rf"\\1{video_id}\\2",
            html,
            count=1,
        )
        html = re.sub(
            r'(id="earth-video"[^>]*src="https://www\\.youtube\\.com/embed/)[A-Za-z0-9_-]{11}',
            rf'\\1{video_id}',
            html,
            count=1,
        )
        html = re.sub(
            r'(id="youtube-link" href="https://www\\.youtube\\.com/watch\\?v=)[A-Za-z0-9_-]{11}',
            rf'\\1{video_id}',
            html,
            count=1,
        )
        html = re.sub(
            r'(id="visit-live-link" href="https://www\\.youtube\\.com/watch\\?v=)[A-Za-z0-9_-]{11}',
            rf'\\1{video_id}',
            html,
            count=1,
        )
    else:
        page.pop("mainEntity", None)

    # Re-find after replacements so offsets are correct.
    match = SCRIPT_RE.search(html)
    serialized = json.dumps(page, ensure_ascii=False, separators=(",", ":"))
    updated_html = html[:match.start(2)] + serialized + html[match.end(2):]
    html_changed = updated_html != SITE.read_text(encoding="utf-8")
    if html_changed:
        SITE.write_text(updated_html, encoding="utf-8")

    # Keep all sitemap variants deterministic and synchronized.
    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", ns)
    today = datetime.now(timezone.utc).date().isoformat()
    for sitemap in SITEMAPS:
        tree = ET.parse(sitemap)
        url = next(
            (
                node
                for node in tree.getroot().findall(f"{{{ns}}}url")
                if node.findtext(f"{{{ns}}}loc") == PAGE_URL
            ),
            None,
        )
        if url is None:
            raise ValueError(f"Homepage not present in {sitemap.name}")
        lastmod = url.find(f"{{{ns}}}lastmod")
        if lastmod is None:
            lastmod = ET.SubElement(url, f"{{{ns}}}lastmod")
        if html_changed:
            lastmod.text = today
        tree.write(sitemap, encoding="utf-8", xml_declaration=True)

    TEXT_SITEMAP.write_text(PAGE_URL + "\\n", encoding="utf-8")

    if status["status"] == "live":
        watch_url = f"https://www.youtube.com/watch?v={video_id}"
        title = "EARTH RIGHT NOW — Live Earth 24/7"
        description = "Live Earth visualization with sunrise, sunset and city moments across 286 cities."
        item = f"""    <item>
      <title>{title}</title>
      <link>{watch_url}</link>
      <guid isPermaLink="true">{watch_url}</guid>
      <pubDate>{rss_date(upload_date or checked_at)}</pubDate>
      <description>{description}</description>
    </item>"""
    else:
        item = f"""    <item>
      <title>EARTH RIGHT NOW</title>
      <link>{PAGE_URL}</link>
      <guid isPermaLink="true">{PAGE_URL}</guid>
      <pubDate>{rss_date(checked_at)}</pubDate>
      <description>ERN is currently between live broadcasts. Visit the site for the next live Earth stream.</description>
    </item>"""

    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>EARTH RIGHT NOW</title>
    <link>{PAGE_URL}</link>
    <description>Live Earth visualization, sunrise, sunset and city moments.</description>
    <language>en</language>
{item}
  </channel>
</rss>
"""
    FEED.write_text(feed, encoding="utf-8")
    print("Synchronized ERN SEO, share previews, feed and sitemap endpoints")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
