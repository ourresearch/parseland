from abc import ABC, abstractmethod


class Parser(ABC):
    def __init__(self, soup):
        self.soup = soup

    @abstractmethod
    def is_correct_parser(self):
        pass

    @abstractmethod
    def parse(self):
        pass
