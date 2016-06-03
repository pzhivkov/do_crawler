import unittest

from do_crawler.link_classifier import LinkClassifier


class LinkClassifierTests(unittest.TestCase):

    def test_has_bsobject(self):
        """Check that a valid classifier has a BS object."""
        classifier = LinkClassifier('', bytes('<html></html>', 'utf-8'))
        self.failUnless(classifier._bs_obj)

    def test_no_base_url(self):
        """Check that if the document contains no base URL, the given URL will be used."""
        # Create a classifier with no base url.
        given_url = 'http://given_url/'
        html = '<html></html>'
        classifier = LinkClassifier(given_url, bytes(html, 'utf-8'))
        self.failUnlessEqual(classifier.base_url, given_url)

    def test_incomplete_base_url(self):
        """Check that a badly formed document base tag won't replace the given URL."""
        # Create a classifier with an incomplete base url.
        given_url = 'http://given_url/'
        html = '<html><base></html>'
        classifier = LinkClassifier(given_url, bytes(html, 'utf-8'))
        self.failUnlessEqual(classifier.base_url, given_url)

    def test_base_url_is_well_terminated(self):
        """Test that the base URL explicitly specifies the root of the document."""
        given_url = 'http://given_url'
        html = '<html><</html>'
        classifier = LinkClassifier(given_url, bytes(html, 'utf-8'))
        self.failUnlessEqual(classifier.base_url, given_url + '/')

    def test_has_base_url(self):
        """Test that classifier correctly finds the base URL in the document instead of the given one."""
        # Create a classifier with a base url and compare it.
        base_url = 'http://base_url.com/index.html'
        html = "<html><head><base href='" + base_url + "'></head></html>"
        classifier = LinkClassifier('http://not_this_base_url', bytes(html, 'utf-8'))
        self.failUnlessEqual(classifier.base_url, base_url)

    def test_url_has_http_scheme(self):
        """Check that we can filter non-http scheme URLs."""
        from do_crawler.link_classifier import _url_has_http_scheme
        self.failIf(_url_has_http_scheme('data:img/jpeg;01234567890ABCDEF'))
        self.failUnless(_url_has_http_scheme('http://www.foo.com'))
        self.failUnless(_url_has_http_scheme('//index.html'))

    def test_static_asset_types(self):
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
        classifier = LinkClassifier(url, bytes(html, 'utf-8'))
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

    def test_forward_link_types(self):
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
        classifier = LinkClassifier(url, bytes(html, 'utf-8'))
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
        self.failUnlessEqual(classifier._forward_links, expected_links)

    def test_forward_links_dont_include_base_url(self):
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
        classifier = LinkClassifier(url, bytes(html, 'utf-8'))
        self.failIf(classifier._forward_links)

    def test_is_same_domain_link(self):
        """Make sure that the classifier can distinguish same domain links from external links."""
        url = 'http://www.base_url.com'
        classifier = LinkClassifier(url, bytes('', 'utf-8'))
        self.failUnless(classifier._is_same_domain_link(url))
        self.failUnless(classifier._is_same_domain_link('http://www.base_url.com/some/weird/path/index.html'))
        self.failIf(classifier._is_same_domain_link('http://www.external.com'))
        self.failIf(classifier._is_same_domain_link('http://www.external.com/some/weird/path/index.html'))

    def test_distinguish_external_from_same_domain_links(self):
        """Make sure that the classifier can distinguish external from same-domain links."""
        url = 'http://www.this.com/'
        html = (
            "<html><body>"
            "<a href='same1.link'/>"
            "<a href='http://www.this.com/same2.link'/>"
            "<a href='../same3.link'/>"
            "<a href='http://www.that.com/other1.link'/>"
            "<a href='//www.there.com/other2.link'/>"
            "<body></html>"
        )
        classifier = LinkClassifier(url, bytes(html, 'utf-8'))
        expected_same_domain_links = {
            'http://www.this.com/same1.link',
            'http://www.this.com/same2.link',
            'http://www.this.com/same3.link'
        }
        expected_external_links = {
            'http://www.that.com/other1.link',
            'http://www.there.com/other2.link'
        }
        self.failUnlessEqual(classifier.same_domain_links, expected_same_domain_links)
        self.failUnlessEqual(classifier.external_links, expected_external_links)

    def test_handle_misquoted_links(self):
        """Handle links that have extra quotation marks."""
        url = 'http://www.this.com/'
        html = (
            "<html><body>"
            "<a href=\"\\'same1.link\\'\"/>"
            "<a href='\\\"same2.link\\\"'/>"
            "<body></html>"
        )
        expected_links = {
            'http://www.this.com/same1.link',
            'http://www.this.com/same2.link',
        }
        classifier = LinkClassifier(url, bytes(html, 'utf-8'))
        self.failUnlessEqual(classifier._forward_links, expected_links)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
