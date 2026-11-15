"""Offline, zero-network regression tests for the ERN SEO synchronization."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import update_seo


class SeoSyncTest(unittest.TestCase):
    def test_live_and_offline_and_idempotence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / "index.html"
            status = root / "live.json"
            feed = root / "feed.xml"
            text_sitemap = root / "sitemap.txt"
            sitemaps = [root / "sitemap.xml", root / "sitemap-ern.xml"]
            old = "hg8IooPYXeY"
            new = "BmgRaSxWcpU"
            html = (
                '<meta property="og:image" content="https://i.ytimg.com/vi/' + old + '/maxresdefault.jpg">'
                '<meta name="twitter:image" content="https://i.ytimg.com/vi/' + old + '/maxresdefault.jpg">'
                '<script type="application/ld+json">' +
                json.dumps({"@context": "https://schema.org", "@type": "WebPage"}) +
                '</script><script type="application/ld+json">' +
                json.dumps({"@type": "Organization"}) + '</script>'
                "<script>const defaultId='" + old + "';</script>"
                '<iframe id="earth-video" src="https://www.youtube.com/embed/' + old + '"></iframe>'
                '<a id="youtube-link" href="https://www.youtube.com/watch?v=' + old + '"></a>'
                '<a id="visit-live-link" href="https://www.youtube.com/watch?v=' + old + '"></a>'
            )
            page.write_text(html, encoding="utf-8")
            sitemap = ('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                       '<url><loc>' + update_seo.PAGE_URL + '</loc><lastmod>2026-11-14</lastmod></url></urlset>')
            for path in sitemaps:
                path.write_text(sitemap, encoding="utf-8")
            status.write_text(json.dumps({"status": "live", "videoId": new,
                                          "uploadDate": "2026-11-14T00:42:07Z"}), encoding="utf-8")
            with (patch.object(update_seo, "SITE", page),
                  patch.object(update_seo, "STATUS", status),
                  patch.object(update_seo, "SITEMAPS", sitemaps),
                  patch.object(update_seo, "TEXT_SITEMAP", text_sitemap),
                  patch.object(update_seo, "FEED", feed)):
                self.assertEqual(update_seo.main(), 0)
                content = page.read_text(encoding="utf-8")
                self.assertNotIn(old, content)
                self.assertIn(new, content)
                self.assertIn(new, feed.read_text(encoding="utf-8"))
                self.assertEqual(text_sitemap.read_text(encoding="utf-8"), "".join(url + "\n" for url in update_seo.DISCOVERY_URLS))
                for sitemap_path in sitemaps:
                    sitemap_content = sitemap_path.read_text(encoding="utf-8")
                    for discovery_url in update_seo.DISCOVERY_URLS:
                        self.assertIn(discovery_url, sitemap_content)
                sitemap_snapshots = {p: p.read_bytes() for p in sitemaps}
                self.assertEqual(update_seo.main(), 0)
                self.assertEqual(content, page.read_text(encoding="utf-8"))
                for sitemap_path in sitemaps:
                    self.assertEqual(sitemap_path.read_bytes(), sitemap_snapshots[sitemap_path],
                                     f"Sitemap changed on an identical repeat sync: {sitemap_path.name}")
                status.write_text(json.dumps({"status": "offline", "checkedAt": "2026-11-15T00:00:00Z"}),
                                  encoding="utf-8")
                self.assertEqual(update_seo.main(), 0)
                self.assertNotIn("VideoObject", page.read_text(encoding="utf-8"))
                self.assertIn("between live broadcasts", feed.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
