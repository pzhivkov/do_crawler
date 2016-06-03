from do_crawler import (
    link_classifier,
    page_fetcher,
    sitemap
)
from multiprocessing.dummy import Pool as ThreadPool


# --- Crawler:


class Crawler(object):
    """The main crawler class."""
    MAX_NUM_THREADS = 8

    def __init__(self, domain: str):
        self.pool = ThreadPool(self.MAX_NUM_THREADS)

        self.root = domain
        self.links_to_visit = set()
        self.failed_links = set()

        self.sitemap = sitemap.SiteMap()

    def _visit_link(self, url: str):
        """Visit a link and add it to the sitemap."""

        url = link_classifier.absolutize_link(self.root, url)
        print('Visiting ' + url)

        # Make sure this link hasn't already been visited.
        if self.sitemap.has_page(url):
            return

        page_content = self._get_page_content(url)
        if page_content:
            self._add_page_record(url, page_content)

    def _add_page_record(self, url: str, page_content: bytes):
        """Build a page and add it to the current sitemap."""

        page_hash = sitemap.compute_page_hash(page_content)
        cl = link_classifier.LinkClassifier(url, page_content)
        page = sitemap.Page(url, page_hash, cl.static_assets, cl.same_domain_links)

        self.sitemap.add_page(page)
        self.links_to_visit |= page.links - self.sitemap.pages.keys()

    def _get_page_content(self, url: str) -> bytes:
        """Get the page content for a given URL."""

        pf = page_fetcher.PageFetcher(url)

        # Store invalid/failed links for future inspection.
        if not pf.is_valid() or not pf.content:
            self.failed_links.add(url)
            return None

        return pf.content

    def crawl(self):
        """Start the crawling process."""

        self.links_to_visit.add('/')

        while self.links_to_visit:
            link = self.links_to_visit.pop()
            self._visit_link(link)

    def parallel_crawl(self):
        """Start a parallel crawl (multi-threaded version)."""

        self.links_to_visit.add('/')
        while self.links_to_visit:
            # Move the existing links_to_visit set to a temp var, and empty it,
            # so that it can be processed in parallel without interference.
            links = self.links_to_visit
            self.links_to_visit = set()
            self.pool.map(self._visit_link, links)


# --- Main function:


def main():
    c = Crawler('http://digitalocean.com')
    try:
        c.parallel_crawl()
    except (KeyboardInterrupt, SystemExit) as e:
        c.pool.close()
        print(c.links_to_visit)


if __name__ == '__main__':
    main()
