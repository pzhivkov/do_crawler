import unittest

from do_crawler.sitemap import (
    Page,
    SiteMap
)


class SiteMapTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_compute_page_hash(self):
        """Test page hash computation func."""
        from do_crawler.sitemap import compute_page_hash

        content = bytes("<html>html content goes here</html>".encode('utf-8'))
        page_hash = compute_page_hash(content)
        expected_hash = '2b63f5a34821056f8effcee7c4ce00a001188846cdc5c4a6df64612c'
        self.failUnlessEqual(page_hash, expected_hash)

    def test_get_relative_url(self):
        """Test the get_relative_url func."""
        from do_crawler.sitemap import _get_relative_url

        url = "http://www.cnn.com/asia/interesting_articles_1023/foo.html"
        rel = "/asia/interesting_articles_1023/foo.html"
        self.failUnlessEqual(rel, _get_relative_url(url))

    def test_page_construction(self):
        """Check that a page is properly constructed with all links correctly relativized."""
        url = "http://base.url/"
        page_hash = '1c593c303dc21157133543e88d5577a6b05719af1bba55fe8f10dc73'
        static_assets = {'http://asset1', 'http://asset2'}
        links = {'http://base.url/link1', 'http://base.url/link2'}
        p = Page(url, page_hash, static_assets, links)

        self.failUnless('/' in p.urls)
        self.failUnlessEqual(p.page_hash, page_hash)
        self.failUnlessEqual(p.static_assets, static_assets)
        self.failUnlessEqual(p.links, {'/link1', '/link2'})

    def test_sitemap_add_page(self):
        """Test that pages can be added to the SiteMap."""
        sm = SiteMap()
        p = Page('url', 'hash1', set(), set())

        sm.add_page(p)
        self.failUnless(sm.has_page('url'))
        self.failIf(sm.has_page('random_url'))

    def test_sitemap_add_duplicate_page(self):
        """Test that duplicate pages can't be added to the SiteMap."""
        sm = SiteMap()
        p1 = Page('url', 'hash1', set(), set())
        p2 = Page('url', 'hash2', set(), set())

        sm.add_page(p1)
        sm.add_page(p2)
        self.failUnless(sm.has_page('url'))
        self.failUnless(len(sm.pages) == 1)

    def test_sitemap_add_duplicate_hash_page(self):
        """Test that pages with the same url but with different hashes will be merged in the SiteMap."""
        sm = SiteMap()
        p1 = Page('url1', 'hash', set(), set())
        p2 = Page('url2', 'hash', set(), set())

        sm.add_page(p1)
        sm.add_page(p2)
        self.failUnless(sm.has_page('url1'))
        self.failUnless(sm.has_page('url2'))
        self.failUnlessEqual(sm.pages['url1'], sm.pages['url2'])
        self.failUnless(len(sm.pages) == 2)
        self.failUnlessEqual(sm.pages['url1'].urls, ['url1', 'url2'])


def main():
    unittest.main()

if __name__ == '__main__':
    main()
