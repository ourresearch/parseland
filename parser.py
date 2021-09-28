from gzip import decompress

from bs4 import BeautifulSoup
import requests

from parsers.sciencedirect import ScienceDirect
from parsers.springer import Springer


class ParserController:
    def __init__(self, doi):
        self.landing_page_endpoint = f"https://api.unpaywall.org/doi_page/{doi}"
        self.parsers = [ScienceDirect, Springer]
        self.soup = self.get_soup()

    def get_html(self):
        r = requests.get(self.landing_page_endpoint)
        html = decompress(r.content)
        return html

    def get_soup(self):
        soup = BeautifulSoup(self.get_html(), "html.parser")
        return soup

    def find_parser(self):
        for cls in self.parsers:
            parser = cls(self.soup)
            if parser.is_correct_parser():
                return parser
