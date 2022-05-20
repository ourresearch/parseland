from gzip import decompress

import requests
from bs4 import BeautifulSoup

from exceptions import ParserNotFoundError, S3FileNotFoundError
from repository.parsers.parser import RepositoryParser


class RepositoryController:
    def __init__(self, page_id):
        self.page_id = page_id
        self.page_archive_endpoint = (
            f"https://api.unpaywall.org/repo_page/{self.page_id}"
        )
        self.parsers = RepositoryParser.__subclasses__()
        self.soup = self.get_soup()

    def get_html(self):
        r = requests.get(self.page_archive_endpoint)
        if r.status_code == 404:
            raise S3FileNotFoundError(f"Tried endpoint: {self.page_archive_endpoint}")
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
        raise ParserNotFoundError(f"Parser not found for {self.page_id}")
