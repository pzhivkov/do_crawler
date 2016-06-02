import bs4

from bs4 import BeautifulSoup
from http.client import HTTPResponse
from urllib.error import URLError
from urllib.request import urlopen


def read_page(url: str) -> HTTPResponse:
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

    assert isinstance(html_content, HTTPResponse)
    if html_content.info().get_content_type() != 'text/html':
        return None

    return html_content


def get_outgoing_links(page):
    links = []
    try:
        bs_obj = BeautifulSoup(page, 'html.parser')
    except bs4.FeatureNotFound:
        pass
    else:
        for tag in bs_obj.findAll('a', href=True):
            links.append(tag['href'])

    return links


def main():
    html_resp = read_page('http://cnn.com')
    if html_resp:
        html = html_resp.read()
        print(get_outgoing_links(html))


if __name__ == '__main__':
    main()
