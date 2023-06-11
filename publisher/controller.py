from gzip import decompress
from pathlib import Path

import requests
import filetype
from bs4 import BeautifulSoup

from exceptions import ParserNotFoundError, S3FileNotFoundError, \
    WrongFormatLandingPageError
from publisher.parsers.generic import GenericPublisherParser
from publisher.parsers.parser import PublisherParser


class PublisherController:
    def __init__(self, doi):
        self.doi = doi
        self.landing_page_endpoint = f"https://api.unpaywall.org/doi_page/{self.doi}"
        self.parsers = PublisherParser.__subclasses__()
        self.soup = self.get_soup()

    def get_html(self):
        r = requests.get(self.landing_page_endpoint)
        if r.status_code == 404:
            raise S3FileNotFoundError(f"Tried endpoint: {self.landing_page_endpoint}")
        html = decompress(r.content)

        ext = filetype.guess_extension(html)
        # ext will probably be None if content is actually html
        if ext and 'html' not in ext:
            raise WrongFormatLandingPageError(ext)

        return html

    def get_soup(self):
        soup = BeautifulSoup(self.get_html(), "lxml")
        return soup

    def find_parser(self):
        best_parser = None
        for cls in self.parsers:
            parser = cls(self.soup)
            if parser.is_publisher_specific_parser():
                best_parser = parser
                if parser.authors_found():
                    return parser

        generic_parser = GenericPublisherParser(self.soup)
        if generic_parser.authors_found():
            best_parser = generic_parser

        if best_parser:
            return best_parser
        raise ParserNotFoundError(f"Parser not found for {self.doi}")
