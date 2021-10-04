from abc import ABC, abstractmethod


class Parser(ABC):
    def __init__(self, soup):
        self.soup = soup

    @property
    @abstractmethod
    def parser_name(self):
        raise NotImplementedError

    @abstractmethod
    def is_correct_parser(self):
        pass

    @abstractmethod
    def authors_found(self):
        pass

    @staticmethod
    def no_authors_ouput():
        return []

    @abstractmethod
    def parse(self):
        pass

    def domain_in_canonical_link(self, domain):
        canonical_link = self.soup.find("link", {"rel": "canonical"})
        if canonical_link and domain in canonical_link.get("href"):
            return True

    def domain_in_meta_og_url(self, domain):
        meta_og_url = self.soup.find("meta", property="og:url")
        if meta_og_url and domain in meta_og_url.get("content"):
            return True

    @property
    def test_cases(self):
        return []
