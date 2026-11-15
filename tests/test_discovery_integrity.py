"""Zero-network checks for the ERN discovery inventory and internal links."""
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse
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

    def test_homepage_links_to_city_and_language_hubs(self):
        homepage = (ROOT / "index.html").read_text(encoding="utf-8")
        for link in ('href="./cities/"', 'href="./ja/"', 'href="./es/"', 'href="./id/"'):
            self.assertIn(link, homepage)


if __name__ == "__main__":
    unittest.main()
