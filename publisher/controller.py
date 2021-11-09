from gzip import decompress

import requests
from bs4 import BeautifulSoup

from exceptions import ParserNotFoundError, S3FileNotFoundError
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
        return html

    def get_soup(self):
        soup = BeautifulSoup(self.get_html(), "html.parser")
        return soup

    def find_parser(self):
        for cls in self.parsers:
            parser = cls(self.soup)
            if parser.is_publisher_specific_parser():
                return parser

        generic_parser = GenericPublisherParser(self.soup)
        if generic_parser.authors_found():
            return generic_parser

        raise ParserNotFoundError(f"Parser not found for {self.doi}")
