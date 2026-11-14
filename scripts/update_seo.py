"""Synchronize public ERN video SEO metadata with verified live.json status.

No Search Console or Product Hunt credentials are required.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "index.html"
STATUS = ROOT / "live.json"
SITEMAP = ROOT / "sitemap.xml"
PAGE_URL = "https://ern-inc.github.io/earth-right-now/"
SCRIPT_RE = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)
VIDEO_ID_RE = re.compile(r"[A-Za-z0-9_-]{11}\Z")


def main():
    if not STATUS.exists():
        print("No live.json yet; leaving SEO metadata unchanged")
        return 0
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    if status.get("status") not in ("live", "offline"):
        raise ValueError("Unknown live status; refusing to alter SEO")
    video_id = status.get("videoId")
    if status["status"] == "live" and (not isinstance(video_id, str) or not VIDEO_ID_RE.fullmatch(video_id)):
        raise ValueError("Invalid live video ID; refusing to alter SEO")

    html = SITE.read_text(encoding="utf-8")
    match = SCRIPT_RE.search(html)
    if not match:
        raise ValueError("Existing structured data script not found")
    page = json.loads(match.group(2))
    if page.get("@type") != "WebPage":
        raise ValueError("Unexpected structured data; refusing to overwrite")

    upload_date = status.get("uploadDate")
    if status["status"] == "live":
        page["mainEntity"] = {
            "@type": "VideoObject",
            "name": "EARTH RIGHT NOW — Live Earth Screensaver",
            "description": "Live Earth visualization featuring sunrise, sunset and city news across 286 cities.",
            "thumbnailUrl": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
            "embedUrl": f"https://www.youtube.com/embed/{video_id}",
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "isLiveBroadcast": True,
        }
        if isinstance(upload_date, str) and upload_date:
            page["mainEntity"]["uploadDate"] = upload_date
    else:
        page.pop("mainEntity", None)

    serialized = json.dumps(page, ensure_ascii=False, separators=(",", ":"))
    updated = html[:match.start(2)] + serialized + html[match.end(2):]
    if updated == html:
        print("SEO metadata unchanged")
        return 0
    SITE.write_text(updated, encoding="utf-8")

    # lastmod reflects actual page content changes, not every detector poll.
    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", ns)
    tree = ET.parse(SITEMAP)
    url = next((node for node in tree.getroot().findall(f"{{{ns}}}url")
                if node.findtext(f"{{{ns}}}loc") == PAGE_URL), None)
    if url is None:
        raise ValueError("Homepage not present in sitemap")
    lastmod = url.find(f"{{{ns}}}lastmod")
    if lastmod is None:
        lastmod = ET.SubElement(url, f"{{{ns}}}lastmod")
    lastmod.text = datetime.now(timezone.utc).date().isoformat()
    tree.write(SITEMAP, encoding="utf-8", xml_declaration=True)
    print("Updated structured data and sitemap lastmod")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
