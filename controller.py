from gzip import decompress

from bs4 import BeautifulSoup
import requests

from exceptions import ParserNotFoundError, S3FileNotFoundError
from parser import Parser
from parsers import *  # allows us to use __subclasses__()


class ParserController:
    def __init__(self, doi):
        self.doi = doi
        self.landing_page_endpoint = f"https://api.unpaywall.org/doi_page/{self.doi}"
        self.parsers = Parser.__subclasses__()
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
        for cls in Parser.__subclasses__():
            parser = cls(self.soup)
            if parser.is_correct_parser():
                return parser
        raise ParserNotFoundError(f"Parser not found for {self.doi}")
