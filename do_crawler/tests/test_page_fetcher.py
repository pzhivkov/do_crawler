import unittest

from unittest.mock import MagicMock
from do_crawler.page_fetcher import PageFetcher


class PageFetcherTests(unittest.TestCase):

    def setUp(self):
        """ Set up a basic page fetcher fixture, mocking the HTTPResponse. """

        self.html_content = '<html>The content that we expect the PageFetcher to return.</html>'

        self.pf = PageFetcher('')
        self.pf._response = MagicMock()
        content_type_mock = MagicMock()
        content_type_mock.get_content_type = MagicMock(return_value='text/html')
        self.pf._response.info = MagicMock(return_value=content_type_mock)
        self.pf._response.read = MagicMock(return_value=self.html_content)

    def test_is_valid(self):
        """ Test if the response is valid. """

        self.failUnless(self.pf.is_valid())

    def test_is_html(self):
        """ Test is the response type is HTML. """

        self.failUnless(self.pf.is_html())

    def test_returns_content(self):
        """ Test if we have the correct content. """

        self.failUnlessEqual(self.pf.content, self.html_content)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
