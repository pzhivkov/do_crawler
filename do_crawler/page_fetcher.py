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
        print(e.reason)
        return None
    except ValueError as e:
        print("Bad URL: " + str(e))
        return None

    if not isinstance(html_content, HTTPResponse):
        return None

    return html_content


class PageFetcher(object):

    def __init__(self, url: str):
        self._url = url
        self._response = _get_page(self._url)
        if not self._response:
            raise ValueError('Bad URL: ' + self._url)

        self._url = self._response.geturl()

        print(self._url)


def main():
    pf = PageFetcher('http://www.cnn.com/asia/')
    print(pf)

if __name__ == '__main__':
    main()
