import bs4

from bs4 import BeautifulSoup
from functools import lru_cache
from urllib.parse import urlparse
from urllib.parse import urljoin


def _url_has_http_scheme(url: str) -> bool:
    """Check if a given URL has the HTTP scheme."""
    return urlparse(url, 'http').scheme == 'http'


def _absolutize_link(domain: str, link: str) -> str:
    """Make an absolute link from a URL and a relative link."""
    return urljoin(domain, link)


def _make_unique_root_url(url: str) -> str:
    """Make sure we point correctly to the root if this is a root URL."""
    if not urlparse(url)[2]:
        return _absolutize_link(url, '/')
    return url


def _get_domain(url: str) -> str:
    """Extract the domain name from a URL."""
    return urlparse(url)[1]


class LinkClassifier(object):
    """
    This class parses an HTML content page and classifies the links within it
    into three types:
        - Static assets
        - External links
        - Internal links.

    """

    BASE_TAG = ('base', 'href')

    FORWARD_LINK_TAGS = [
        ('a', 'href'),
        ('iframe', 'src'),
        ('form', 'action'),
        ('blockquote', 'cite'),
        ('q', 'cite'),
        ('area', 'href'),
        ('link', 'href', {'alternate', 'author', 'help', 'license', 'next', 'prev', 'search'})
    ]

    STATIC_ASSET_TAGS = [
        ('source', 'src'),
        ('audio', 'src'),
        ('video', 'src'),
        ('video', 'poster'),
        ('img', 'src'),
        ('script', 'src'),
        ('link', 'href', {'icon', 'prefetch', 'stylesheet'})
    ]

    def __init__(self, url: str, html_content: str):
        """
        The LinkClassifier constructor takes a string with the HTML content.

        :param url: the URL corresponding to the document (used to resolve relative links)
        :type url: str
        :param html_content: the content of the HTML document
        :type html_content: str
        """

        try:
            self.bs_obj = BeautifulSoup(html_content, 'html.parser')
        except bs4.FeatureNotFound:
            raise ValueError('Bad html content.')

        self.base_url = self._get_base_url()
        if not self.base_url:
            self.base_url = url

        self.base_url = _make_unique_root_url(self.base_url)

    def _get_base_url(self) -> str:
        """
        Extract the base tag link from the document.
        :rtype: str
        """
        base_tag = self.bs_obj.find(self.BASE_TAG[0])
        if not base_tag:
            return None

        try:
            base_attr = base_tag[self.BASE_TAG[1]]
        except KeyError:
            return None
        else:
            return base_attr

    def _get_links_of_type(self, link_types: list) -> set:
        """
        Iterate over all possible static asset links and generate a list of absolute links.
        :param link_types: a set of tag/attribute pairs that specify the type of links to retrieve
        :type link_types: list
        :return: a list of all links in the document that follow the specified tag/attribute types
        :rtype: list
        """
        links = set()
        for link_type in link_types:
            for tag in self.bs_obj.find_all(link_type[0]):
                try:
                    link = tag[link_type[1]]
                    if not link or not _url_has_http_scheme(link):
                        continue

                    # If this is a <link> tag, check it has the correct 'rel' attribute.
                    if len(link_type) > 2 and tag['rel']:
                        if not set.intersection(set(tag['rel']), link_type[2]):
                            continue

                    # Add the link.
                    abs_link = _absolutize_link(self.base_url, link)
                    uniq_link = _make_unique_root_url(abs_link)
                    links.add(uniq_link)

                except KeyError:
                    continue

        # Make sure we don't consider the base URL that we started from.
        if self.base_url in links:
            links.remove(self.base_url)

        return links

    @property
    @lru_cache(maxsize=1)
    def static_assets(self) -> set:
        """
        All links to potential static assets in the document.
        :rtype: list
        """
        return self._get_links_of_type(self.STATIC_ASSET_TAGS)


    @property
    @lru_cache(maxsize=1)
    def _maybe_forward_links(self) -> set:
        """
        All forward links in the document.
        :rtype: list
        """
        return self._get_links_of_type(self.FORWARD_LINK_TAGS)

    @property
    @lru_cache(maxsize=1)
    def external_links(self) -> set:
        """
        All external forward links in the document.
        :return: list
        """
        return self._maybe_forward_links - self.same_domain_links

    @property
    @lru_cache(maxsize=1)
    def same_domain_links(self) -> set:
        """
        All forward links that are in the same domain.
        :return: list
        """
        return {link for link in self._maybe_forward_links if self._is_same_domain_link(link)}

    def _is_same_domain_link(self, url) -> bool:
        """Check whether a given link is in the same domain."""
        return _get_domain(url) == _get_domain(self.base_url)


def main():
    from do_crawler.crawler import read_page

    html_resp = read_page('http://cnn.com')
    if not html_resp:
        return

    url = html_resp.geturl()
    html = html_resp.read()
    link_classifier = LinkClassifier(url, html)
    print(link_classifier.static_assets)
    print(link_classifier.same_domain_links)


if __name__ == '__main__':
    main()
