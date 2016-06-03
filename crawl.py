#!/usr/bin/env python3

import logging
from do_crawler.crawler import Crawler
from do_crawler.sitemap_viz import print_sitemap


def configure_logging():
    """Configure logging to console at level INFO."""

    logger = logging.getLogger('do_crawler')

    console = logging.StreamHandler()
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)

    logger.addHandler(console)
    logger.setLevel(logging.INFO)


# --- Main function:


def main():
    configure_logging()

    # Start a parallel crawl.
    c = Crawler('http://digitalocean.com')
    try:
        c.parallel_crawl()
    except (KeyboardInterrupt, SystemExit) as _:
        c.pool.close()

    # If we're done (or were interrupted), then output the result so far.
    c.pool.join()
    print_sitemap(c.sitemap)
    if c.links_to_visit:
        print(c.links_to_visit)


if __name__ == '__main__':
    main()
