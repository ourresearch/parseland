from bs4 import BeautifulSoup

from exceptions import ParserNotFoundError
from publisher.parsers.generic import GenericPublisherParser
from publisher.parsers.parser import PublisherParser
from publisher.utils import normalize_doi
from util.s3 import make_s3

_s3 = make_s3()


class PublisherController:
    def __init__(self, html, doi):
        self.doi = normalize_doi(doi)
        self.parsers = PublisherParser.__subclasses__()
        self.soup = BeautifulSoup(html, "lxml")

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
