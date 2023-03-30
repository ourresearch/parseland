import re

from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import strip_prefix


class IGIGlobal(PublisherParser):
    parser_name = "igi_global"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('igi-global.com')

    def authors_found(self):
        return bool(self.soup.select('span[id*=lblAffiliates]'))

    def parse_authors(self):
        authors_tag = self.soup.select_one('span[id*=lblAffiliates]')
        authors_split = re.split(r',(?![^()]*\))| and (?![^()]*\))', authors_tag.text)
        authors = []
        for author_txt in authors_split:
            if len(author_txt) < 3:
                continue
            if '(' in author_txt:
                split = author_txt.split('(')
                name = split[0].strip(' (')
                aff = split[1].strip(' )')
                author = {'name': name, 'affiliations': [aff],
                          'is_corresponding': None}
            else:
                name = author_txt
                author = {'name': name, 'affiliations': [],
                          'is_corresponding': None}
            authors.append(author)
        return authors

    def parse_abstract(self):
        if abs_tag := self.soup.select_one('span[id*=lblAbstract]'):
            return strip_prefix('abstract', abs_tag.text, flags=re.IGNORECASE)
        return None

    def parse(self):
        return {'authors': self.parse_authors(), 'abstract': self.parse_abstract()}
