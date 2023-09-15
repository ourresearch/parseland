from gzip import decompress

import filetype
from bs4 import BeautifulSoup

from exceptions import ParserNotFoundError, WrongFormatLandingPageError
from publisher.parsers.generic import GenericPublisherParser
from publisher.parsers.parser import PublisherParser
from publisher.utils import normalize_doi
from util.s3 import make_s3, get_obj, S3_LANDING_PAGE_BUCKET, doi_to_lp_key

_s3 = make_s3()


class PublisherController:
    def __init__(self, doi):
        self.doi = normalize_doi(doi)
        self.parsers = PublisherParser.__subclasses__()
        self.html = self.get_html()
        self.soup = self.get_soup()

    def get_html(self):
        obj = get_obj(S3_LANDING_PAGE_BUCKET, doi_to_lp_key(self.doi), s3=_s3)
        contents = decompress(obj['Body'].read())
        ext = filetype.guess_extension(contents)
        # ext will probably be None if content is actually html
        if ext and 'pdf' in ext:
            raise WrongFormatLandingPageError(ext)
        elif not ext:
            self.html = contents
            return self.html
        else:
            raise WrongFormatLandingPageError(ext)

    def get_soup(self):
        soup = BeautifulSoup(self.html, "lxml")
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
