import re

from bs4 import NavigableString

from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import is_h_tag


class Karger(PublisherParser):
    parser_name = "karger"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('karger.com')

    def authors_found(self):
        return bool(self.soup.select_one('span.autoren')) or bool(self.soup.select('.al-author-name'))

    def parse_authors_2(self):
        author_tags = self.soup.select('.al-author-name')
        authors = []
        for author_tag in author_tags:
            name = author_tag.find('a').text
            author = {'name': name, 'affiliations': [], 'is_corresponding': bool(author_tag.select_one('.info-card-footnote'))}
            aff_tags = author_tag.select('.info-card-affilitation .aff')
            for aff_tag in aff_tags:
                label = aff_tag.find('span')
                label.decompose()
                author['affiliations'].append(aff_tag.text)
            authors.append(author)
        return authors

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
            elif child.name == 'span':
                authors.append(current_author)
                current_author = None
            elif current_author is None and len(child.text.strip()) >= 2:
                current_author = {'name': child.text.strip(), 'affiliations': [], 'is_corresponding': None}
        if len(affiliations) == 1:
            for author in authors:
                author['affiliations'] = affiliations.values()
        return authors

    def parse_abstract(self):
        if abs_heading := self.soup.find(lambda tag: is_h_tag(tag) and 'abstract' in tag.text.lower()):
            return abs_heading.find_next_sibling('p').text

    def parse(self):
        authors = self.parse_authors_2() if bool(self.soup.select('.al-author-name')) else self.parse_authors()
        return {'authors': authors, 'abstract': self.parse_abstract()}
