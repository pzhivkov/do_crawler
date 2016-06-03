import unittest

from do_crawler.crawler import Crawler
from unittest.mock import patch


class CrawlerTests(unittest.TestCase):

    def test_crawler_keeps_root(self):
        url = 'http://root'
        c = Crawler(url)
        self.failUnlessEqual(c.root, url)

    @patch('test_crawler.Crawler._get_page_content')
    def test_visit_link(self, mock_get_page_content):
        """
        Test that when we visit a link, it is added to the sitemap
        and its forward links and static assets are also added.
        """
        html = (
            "<html><body>"
            "<a href='next.link'>"
            "<img src='img-src.link'>"
            "<body></html>"
        ).encode('utf-8')

        mock_get_page_content.side_effect = [bytes(html)]

        c = Crawler('http://test.domain')
        root = '/'
        c._visit_link(root)

        # Check that the root page is in the sitemap.
        self.failUnless(c.sitemap.has_page(root))
        page = c.sitemap.pages[root]

        # Check the hash is also stored.
        hash_code = page.page_hash
        self.failUnless(hash_code in c.sitemap._hashes)

        # Check that the page has all the expected forward links.
        self.failUnless(len(page.links) == 1)
        self.failUnless('/next.link' in page.links)

        # Check that the page has all the expected static assets.
        self.failUnless(len(page.static_assets) == 1)
        self.failUnless('http://test.domain/img-src.link' in page.static_assets)

        # Check that the forward links are added for future inspection.
        self.failUnless(len(c.links_to_visit) == 1)
        self.failUnless('/next.link' in c.links_to_visit)

    @patch('test_crawler.Crawler._get_page_content')
    def test_visit_duplicate_link(self, mock_get_page_content):
        """Test that we don't visit a link twice."""
        html = (
            "<html><body>"
            "<a href='/'>"
            "<a href='#'>"
            "<a href='//'>"
            "<body></html>"
        ).encode('utf-8')

        mock_get_page_content.side_effect = [bytes(html)]

        c = Crawler('http://test.domain')
        root = '/'
        c._visit_link(root)

        # Check that the root page is in the sitemap.
        self.failUnless(c.sitemap.has_page(root))
        page = c.sitemap.pages[root]

        # Check that no forward links are added for the same page.
        self.failUnless(len(c.links_to_visit) == 0)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
