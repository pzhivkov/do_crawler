from do_crawler.sitemap import (
    Page,
    SiteMap
)
from pprint import pformat
from sys import stdout
from textwrap import indent


def print_page(page: Page, file):
    """ Output a page record. """

    print("Page: " + str(set(page.urls)), file=file)

    print(indent("Links: " + pformat(page.links), '    '), file=file)
    print(indent("Static Assets: " + pformat(page.static_assets), '    '), file=file)

    print(file=file)


def print_sitemap(sitemap: SiteMap, file=stdout):
    """Generate a console dump of a site map."""

    for page in sitemap.pages.values():
        print_page(page, file)


# --- Main function:


def main():
    pass


if __name__ == '__main__':
    main()
