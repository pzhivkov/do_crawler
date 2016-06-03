#!/usr/bin/env python3

import logging
from do_crawler.crawler import Crawler


def configure_logging():
    logger = logging.getLogger('do_crawler')
    logger.setLevel(logging.INFO)
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))
    logger.addHandler(console)


def main():
    configure_logging()

    c = Crawler('http://digitalocean.com')
    try:
        c.parallel_crawl()
    except (KeyboardInterrupt, SystemExit) as _:
        c.pool.close()
        print(c.links_to_visit)


if __name__ == '__main__':
    main()
