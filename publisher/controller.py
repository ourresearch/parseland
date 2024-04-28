import traceback

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

    def best_parser_msg(self):
        both_conditions_parsers = []
        authors_found_parsers = []

        def has_affs(parsed):
            return any([author['affiliations'] if isinstance(parsed, dict) else author.affiliations for author in parsed['authors']])

        for cls in self.parsers:
            parser = cls(self.soup)
            if parser.authors_found():
                if parser.is_publisher_specific_parser():
                    both_conditions_parsers.append(parser)
                else:
                    authors_found_parsers.append(parser)

        for parser in both_conditions_parsers:
            try:
                parsed = parser.parse()
                if has_affs(parsed):
                    return parser, parsed
            except Exception as e:
                print(f'Exception with DOI: {self.doi}')
                traceback.print_exc()
                continue

        for parser in authors_found_parsers:
            try:
                parsed = parser.parse()
                if has_affs(parsed):
                    return parser, parsed
            except Exception as e:
                print(f'Exception with DOI: {self.doi}')
                traceback.print_exc()
                continue

        generic_parser = GenericPublisherParser(self.soup)
        if generic_parser.authors_found():
            return generic_parser, generic_parser.parse()

        raise ParserNotFoundError(f"Parser not found for {self.doi}")
