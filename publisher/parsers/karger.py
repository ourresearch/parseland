import re

from bs4 import NavigableString

from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import is_h_tag


class Karger(PublisherParser):
    parser_name = "karger"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('karger.com')

    def authors_found(self):
        return bool(self.soup.select_one('span.autoren'))

    def parse_affiliations(self):
        affs = {}
        if affs_tag := self.soup.select_one('div#cAffi'):
            current_sup = None
            for child in affs_tag.children:
                if child.name == 'br':
                    continue
                elif child.name == 'sup':
                    current_sup = child.text.strip()
                else:
                    affs[current_sup] = child.text.strip()
        return affs

    def parse_authors(self):
        authors_tag = self.soup.select_one('span.autoren')
        affiliations = self.parse_affiliations()
        current_author = None
        authors = []
        for child in authors_tag.children:
            if isinstance(child, NavigableString):
                if len(child.text.strip()) >= 2:
                    current_author = {'name': child.text.strip(), 'affiliations': [],
                                      'is_corresponding': None}
                else:
                    continue
            elif child.name == 'sup':
                affs = child.text.split(',')
                for aff in affs:
                    if affiliations and aff in affiliations:
                        current_author['affiliations'].append(affiliations.get(aff))
                authors.append(current_author)
                current_author = None
            elif current_author is None and len(child.text.strip()) >= 2:
                current_author = {'name': child.text.strip(), 'affiliations': [], 'is_corresponding': None}
        return authors

    def parse_abstract(self):
        if abs_heading := self.soup.find(lambda tag: is_h_tag(tag) and 'abstract' in tag.text.lower()):
            return abs_heading.find_next_sibling('p').text

    def parse(self):
        return {'authors': self.parse_authors(), 'abstract': self.parse_abstract()}
