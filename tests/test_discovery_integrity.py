"""Zero-network checks for the ERN discovery inventory and internal links."""
from html.parser import HTMLParser
import unittest
from pathlib import Path
from urllib.parse import urlparse, unquote
from xml.etree import ElementTree as ET

from scripts.update_seo import DISCOVERY_URLS, PAGE_URL

ROOT = Path(__file__).resolve().parents[1]
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}


class DiscoveryIntegrityTest(unittest.TestCase):
    def test_discovery_urls_are_unique_and_local(self):
        self.assertEqual(len(DISCOVERY_URLS), len(set(DISCOVERY_URLS)))
        for url in DISCOVERY_URLS:
            self.assertTrue(url.startswith(PAGE_URL), url)
            relative = url.removeprefix(PAGE_URL)
            path = ROOT / relative
            if relative.endswith("/") or not relative:
                path = path / "index.html"
            self.assertTrue(path.is_file(), f"Missing discovery page: {path}")
            html = path.read_text(encoding="utf-8")
            self.assertIn('<link rel="canonical" href="' + url + '">', html)

    def test_sitemaps_include_every_discovery_page(self):
        for name in ("sitemap.xml", "sitemap-ern.xml"):
            root = ET.parse(ROOT / name).getroot()
            urls = [node.text for node in root.findall("s:url/s:loc", NS)]
            self.assertEqual(len(urls), len(set(urls)), name)
            self.assertTrue(set(DISCOVERY_URLS).issubset(urls), name)
        text_urls = (ROOT / "sitemap.txt").read_text(encoding="utf-8").splitlines()
        self.assertEqual(text_urls, DISCOVERY_URLS)


    def test_discovery_internal_links_resolve(self):
        """Verify internal navigation without network access or JS execution."""
        class LinkCollector(HTMLParser):
            def __init__(self):
                super().__init__()
                self.hrefs = []

            def handle_starttag(self, tag, attrs):
                if tag == "a":
                    self.hrefs.extend(value for key, value in attrs if key == "href" and value)

        for url in DISCOVERY_URLS:
            relative = url.removeprefix(PAGE_URL)
            page = ROOT / relative
            if not relative or relative.endswith("/"):
                page /= "index.html"
            collector = LinkCollector()
            collector.feed(page.read_text(encoding="utf-8"))
            for href in collector.hrefs:
                parsed = urlparse(href)
                if parsed.scheme or parsed.netloc or href.startswith("#"):
                    continue
                target = (page.parent / unquote(parsed.path)).resolve()
                if target.is_dir():
                    target /= "index.html"
                self.assertTrue(target.is_file(), f"Broken link in {page}: {href}")


    def test_language_hreflang_is_reciprocal(self):
        """Each translated landing page must point to the same canonical language set."""
        language_urls = {
            "en": PAGE_URL,
            "ja": PAGE_URL + "ja/",
            "es": PAGE_URL + "es/",
            "id": PAGE_URL + "id/",
            "x-default": PAGE_URL,
        }
        for lang in ("en", "ja", "es", "id"):
            page = ROOT / ("index.html" if lang == "en" else f"{lang}/index.html")
            html = page.read_text(encoding="utf-8")
            for code, target in language_urls.items():
                self.assertIn(f'<link rel="alternate" hreflang="{code}" href="{target}">', html,
                              f"Missing reciprocal {code} in {page}")

    def test_homepage_links_to_city_and_language_hubs(self):
        homepage = (ROOT / "index.html").read_text(encoding="utf-8")
        for link in ('href="./cities/"', 'href="./ja/"', 'href="./es/"', 'href="./id/"'):
            self.assertIn(link, homepage)


if __name__ == "__main__":
    unittest.main()
