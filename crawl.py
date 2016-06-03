#!/usr/bin/env python3

import argparse
import logging

from do_crawler.crawler import Crawler
from do_crawler.sitemap_viz import print_sitemap


__author__ = "Peter Zhivkov"
__version__ = '1.0'


def configure_logging(verbose: bool):
    """ Configure logging to console at level INFO. """

    logger = logging.getLogger('do_crawler')

    console = logging.StreamHandler()
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)

    logger.addHandler(console)
    if verbose:
        logger.setLevel(logging.INFO)


# --- Main function:


def main():
    """ Run the crawler and handle command-line options. """

    parser = argparse.ArgumentParser(
        prog='crawl',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='A crawler utility that builds a site map.\n\n'
        'Starts from a domain root and follows forward page links within the same domain,\n'
        'building a site map. Each record in the site map consisting of page urls for a given page, \''
        'lists of forward links, and static assets.\n\n'
        'Examples:\n'
        '\tcrawl http://www.cnn.com -o output.txt\n\n'
    )

    parser.add_argument('DOMAIN_ROOT')
    parser.add_argument(
        '--version',
        action='version',
        version='crawl ' + __version__
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Return self.verbose output.'
    )
    parser.add_argument(
        '-o', '--output-file',
        dest='output_file',
        help='Specify a file to which the sitemap will be written.\n'
    )

    args = parser.parse_args()
    domain_root = str(args.DOMAIN_ROOT)
    domain_root.strip()
    if not domain_root.startswith('http://'):
        domain_root = 'http://' + domain_root

    configure_logging(args.verbose)

    # Start a parallel crawl.
    c = Crawler(domain_root)
    try:
        c.parallel_crawl()
    except (KeyboardInterrupt, SystemExit) as _:
        c.links_to_visit = set()
        c.pool.close()
        c.pool.terminate()
        c.pool.join()

    # If we're done (or were interrupted), then output the result so far.
    if args.output_file:
        with open(args.output_file, 'w') as f:
            print_sitemap(c.sitemap, f)
    else:
        print_sitemap(c.sitemap)

    if args.verbose and c.links_to_visit:
        print(c.links_to_visit)


if __name__ == '__main__':
    main()
