from abc import ABC, abstractmethod
from gzip import decompress

from bs4 import BeautifulSoup
import requests


class Parser(ABC):
    def __init__(self, doi):
        self.landing_page_endpoint = f"https://api.unpaywall.org/doi_page/{doi}"
        self.parser_name = None
        self.soup = self.get_soup()

    def get_html(self):
        r = requests.get(self.landing_page_endpoint)
        html = decompress(r.content)
        return html

    def get_soup(self):
        soup = BeautifulSoup(self.get_html(), "html.parser")
        return soup

    @abstractmethod
    def authors_affiliations(self):
        """Core method that returns authors and associated affiliations."""
        pass
