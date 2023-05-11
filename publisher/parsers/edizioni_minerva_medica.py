import re

from bs4 import NavigableString, Tag

from publisher.parsers.parser import PublisherParser


class EMM(PublisherParser):
    parser_name = "edizioni_minerva_medica"

    def is_publisher_specific_parser(self):
        return self.domain_in_canonical_link('minervamedica.it')

    def authors_found(self):
        return bool(self.soup.select('h4 + p'))

    def parse_affs(self):
        affs = {}
        affs_tag = self.soup.select_one('h4 + p + p i')
        if not affs_tag.find('sup'):
            return affs_tag.text.strip()
        current_num = None
        for elem in affs_tag.children:
            if elem.name == 'sup':
                current_num = elem.text.strip()
            else:
                split = re.split('(\d)', elem.text.strip())
                if len(split) > 1:
                    for item in split:
                        if item.isdigit():
                            current_num = item
                        else:
                            affs[current_num] = item
                else:
                    affs[current_num] = elem.text.strip()
        return affs

    def parse_authors(self):
        authors_tag = self.soup.select_one('h4 + p')
        affs = self.parse_affs()
        authors = []
        for elem in authors_tag.children:
            if isinstance(elem, NavigableString):
                split = elem.text.split(', ')
                for author in split:
                    author = author.strip()
                    if len(author) < 3:
                        continue
                    authors.append({'name': author,
                                    'affiliations': [affs] if isinstance(affs, str) else [],
                                    'is_corresponding': None})
            elif isinstance(elem, Tag):
                if elem.find('a') and 'corresponding' in \
                    elem.find('a').attrs['alt'].lower():
                    authors[-1]['is_corresponding'] = True
                elif elem.name == 'sup' and isinstance(affs, dict):
                    for num in elem.text.strip().split(', '):
                        authors[-1]['affiliations'].append(affs[num])
        return authors

    def parse_abstract(self):
        if abs_tag := self.soup.select_one('.artlist2 + br + p'):
            return abs_tag.text
        return None

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract()}
