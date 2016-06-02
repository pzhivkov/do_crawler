from http.client import HTTPResponse
from urllib.error import URLError
from urllib.request import urlopen


def _get_page(url: str) -> HTTPResponse:
    """
    Follow a URL and return an HTTP response if the content is a valid HTML page.

    :param url: a valid URL to a page
    :return: a response object
    :rtype: HTTPResponse
    """
    try:
        html_content = urlopen(url)
    except URLError as e:
        # print(e.reason)
        return None
    except ValueError as e:
        # print("Bad URL: " + str(e))
        return None

    if not isinstance(html_content, HTTPResponse):
        return None

    return html_content


class PageFetcher(object):
    """
    A basic class that provides HTML resource download.
    """

    def __init__(self, url: str):
        self.url = url
        self._response = _get_page(self.url)
        if self._response:
            self.response_url = self._response.geturl()
        else:
            self.response_url = None

    def is_html(self) -> bool:
        """Return whether the content type is HTML."""
        return self._content_type() == 'text/html'

    def _content_type(self) -> str:
        """Return the content type from the headers of the requested URL."""
        if self.is_valid():
            return self._response.info().get_content_type()
        else:
            return None

    def is_valid(self) -> bool:
        """Return whether the fetch was successful and resulted in a valid response."""
        return bool(self._response)

    @property
    def content(self) -> bytes:
        """
        The page HTML content that can be parsed later.
        :return: the content; None, if
        """
        if self.is_valid() and self.is_html():
            return self._response.read()
        else:
            return None


def main():
    pf = PageFetcher('http://www.cnn.com/asia/')
    print(pf)

if __name__ == '__main__':
    main()
