import hashlib

from urllib.parse import urlparse


# --- Site map helper funcs:


def compute_page_hash(content: bytes) -> str:
    """Generate a page content hash to detect duplicate pages."""
    utf8_content = str(content).encode('utf-8')
    sha = hashlib.sha224(utf8_content)
    return sha.hexdigest()


def _get_relative_url(url: str) -> str:
    """Return the relative part of a URL."""
    return urlparse(url)[2]


# --- Page:


class Page(object):
    """
    A page structure holding information about a given page's URL,
    hash code, static assets, and forward links.
    """

    def __init__(self, url: str, page_hash: str, static_assets: set, links: set):
        self.urls = [_get_relative_url(url)]
        self.page_hash = page_hash
        self.static_assets = static_assets
        self.links = links

        self._cleanup_links()

    def _cleanup_links(self):
        """Clean up forward links so they don't duplicate the base URL."""
        clean_links = set()
        for link in self.links:
            clean_links.add(_get_relative_url(link))
        self.links = clean_links


# --- SiteMap:


class SiteMap(object):
    """
    A sitemap object that stores the currently generated sitemap:

        - A dictionary of page urls to page structs.
        - A dictionary of hash codes to page structs.
    """

    def __init__(self):
        self.pages = {}
        self._hashes = {}

    def add_page(self, page: Page):
        """Add a new page to the sitemap."""

        url = next(iter(page.urls))
        assert len(page.urls) == 1, "Incorrectly formed page."

        # Skip pages that are already in there.
        if self.has_page(url):
            return

        # Check if we have the same hash and make the url point to the original entry.
        if page.page_hash in self._hashes:
            existing_page = self._hashes[page.page_hash]
            self.pages[url] = existing_page

            # Store the alternative URL in the page for future reference.
            existing_page.urls.append(url)
            return

        # This is a completely new page, add it.
        self.pages[url] = page
        self._hashes[page.page_hash] = self.pages[url]

    def has_page(self, url: str) -> bool:
        """Check if the sitemap already contains a page with a given URL."""
        return url in self.pages


# --- Main function:


def main():
    pass


if __name__ == '__main__':
    main()
