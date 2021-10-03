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

    @property
    def test_cases(self):
        return []
