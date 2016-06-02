import unittest

from do_crawler.link_classifier import LinkClassifier


class LinkClassifierTests(unittest.TestCase):

    def testHasBSObject(self):
        """Check that a valid classifier has a BS object."""
        classifier = LinkClassifier('', '<html></html>')
        self.failUnless(classifier.bs_obj)

    def testNoBaseURL(self):
        """Check that if the document contains no base URL, the given URL will be used."""
        # Create a classifier with no base url.
        given_url = 'http://given_url/'
        html = '<html></html>'
        classifier = LinkClassifier(given_url, html)
        self.failUnlessEqual(classifier.base_url, given_url)

    def testIncompleteBaseUrl(self):
        """Check that a badly formed document base tag won't replace the given URL."""
        # Create a classifier with an incomplete base url.
        given_url = 'http://given_url/'
        html = '<html><base></html>'
        classifier = LinkClassifier(given_url, html)
        self.failUnlessEqual(classifier.base_url, given_url)

    def testBaseUrlIsWellTerminated(self):
        """Test that the base URL explicitly specifies the root of the document."""
        given_url = 'http://given_url'
        html = '<html><</html>'
        classifier = LinkClassifier(given_url, html)
        self.failUnlessEqual(classifier.base_url, given_url + '/')

    def testHasBaseUrl(self):
        """Test that classifier correctly finds the base URL in the document instead of the given one."""
        # Create a classifier with a base url and compare it.
        base_url = 'http://base_url.com/index.html'
        html = "<html><head><base href='" + base_url + "'></head></html>"
        classifier = LinkClassifier('http://not_this_base_url', html)
        self.failUnlessEqual(classifier.base_url, base_url)

    def testURLHasHttpScheme(self):
        """Check that we can filter non-http scheme URLs."""
        from do_crawler.link_classifier import _url_has_http_scheme
        self.failIf(_url_has_http_scheme('data:img/jpeg;01234567890ABCDEF'))
        self.failUnless(_url_has_http_scheme('http://www.foo.com'))
        self.failUnless(_url_has_http_scheme('//index.html'))

    def testPotentialStaticAssets(self):
        """Test a sample HTML document containing all static assets types against an expected list."""
        url = 'http://www/'
        html = (
            "<html><body>"
            "<link href='link-href.css.link' rel='stylesheet'>"
            "<link href='link-href.icon.link' rel='icon'>"
            "<link href='link-href.pf.link' rel='prefetch'>"
            "<audio src='audio-src.link'/>"
            "<video src='video-src.link' poster='video-poster.link'/>"
            "<img src='img-src.link'>"
            "<source src='source-src.link'>"
            "<script src='script-src.link'/>"
            "<body></html>"
        )
        classifier = LinkClassifier(url, html)
        expected_static_assets = {
            'http://www/link-href.css.link',
            'http://www/link-href.icon.link',
            'http://www/link-href.pf.link',
            'http://www/source-src.link',
            'http://www/audio-src.link',
            'http://www/video-src.link',
            'http://www/video-poster.link',
            'http://www/img-src.link',
            'http://www/script-src.link'
        }
        self.failUnlessEqual(classifier.static_assets, expected_static_assets)

    def testPotentialForwardLinks(self):
        """Test a sample HTML document containing all forward link types against an expected list."""
        url = 'http://www/'
        html = (
            "<html><body>"
            "<a href='a-href.link'/>"
            "<iframe src='iframe-src.link'></iframe>"
            "<form action='form-action.link'></form>"
            "<blockquote cite='bloqkquote-cite.link'></blockquote>"
            "<q cite='q-cite.link'></q>"
            "<map name='map'><area href='area-href.link'/></map>"
            "<link href='link-href.alt.link' rel='alternate'>"
            "<link href='link-href.auth.link' rel='author'>"
            "<link href='link-href.help.link' rel='help'>"
            "<link href='link-href.lic.link' rel='license'>"
            "<link href='link-href.next.link' rel='next'>"
            "<link href='link-href.prev.link' rel='prev'>"
            "<link href='link-href.search.link' rel='search'>"
            "<body></html>"
        )
        classifier = LinkClassifier(url, html)
        expected_links = {
            'http://www/a-href.link',
            'http://www/iframe-src.link',
            'http://www/form-action.link',
            'http://www/bloqkquote-cite.link',
            'http://www/q-cite.link',
            'http://www/area-href.link',
            'http://www/link-href.alt.link',
            'http://www/link-href.auth.link',
            'http://www/link-href.help.link',
            'http://www/link-href.lic.link',
            'http://www/link-href.next.link',
            'http://www/link-href.prev.link',
            'http://www/link-href.search.link',
        }
        self.failUnlessEqual(classifier._maybe_forward_links, expected_links)

    def testForwardLinksDontIncludeBaseURL(self):
        """Test that the forward links in a sample HTML document won't include the URL of the document."""
        url = 'http://www.base_url.com'
        html = (
            "<html><body>"
            "<a href='http://www.base_url.com'/>"
            "<a href='//www.base_url.com'/>"
            "<a href='//'/>"
            "<a href='/'/>"
            "<a href=''/>"
            "<a href='#'/>"
            "<body></html>"
        )
        classifier = LinkClassifier(url, html)
        self.failIf(classifier._maybe_forward_links)

    def testIsSameDomainLink(self):
        """Make sure that the classifier can distinguish same domain links from external links."""
        url = 'http://www.base_url.com'
        classifier = LinkClassifier(url, '')
        self.failUnless(classifier._is_same_domain_link(url))
        self.failUnless(classifier._is_same_domain_link('http://www.base_url.com/some/weird/path/index.html'))
        self.failIf(classifier._is_same_domain_link('http://www.external.com'))
        self.failIf(classifier._is_same_domain_link('http://www.external.com/some/weird/path/index.html'))


def main():
    unittest.main()

if __name__ == '__main__':
    main()
