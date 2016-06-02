import hashlib


# --- Site map helper funcs:


def compute_page_hash(content: str) -> str:
    """
    Generate a page content hash to detect duplicate pages.
    """
    utf8_content = str.encode('utf-8')
    sha = hashlib.sha224(utf8_content)
    return sha.hexdigest()


# --- SiteMap:


class SiteMap(object):
    """
    A sitemap object that stores the currently generated sitemap.
    """

    def __init__(self):
        self.pages = {}
        self._hashes = {}

    def add_page(self, url: str, page_hash: str, static_assets: set, links: set):
        self.pages[url] = (url, page_hash, static_assets, links)
        self._hashes[hash] = self.pages[url]

    def has_page(self):
        pass


# --- Main function:


def main():
    pass


if __name__ == '__main__':
    main()
