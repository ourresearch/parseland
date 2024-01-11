import re

from publisher.parsers.parser import PublisherParser
from bs4.element import NavigableString
import unidecode


class SciELO(PublisherParser):
    parser_name = "scielo"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('www.scielo.br')

    def authors_found(self):
        return bool(self.soup.select('div.contribGroup span.dropdown'))

    def parse_authors(self):
        authors_tags = self.soup.select('div.contribGroup span.dropdown')
        authors = []
        for tag in authors_tags:
            author = {
                'name': '',
                'is_corresponding': None,
                'affiliations': []
            }
            if name_tag := tag.select_one('a'):
                author['name'] = name_tag.text.strip()
            else:
                continue
            for aff_tag in tag.select_one('ul').children:
                if isinstance(aff_tag, NavigableString) and len(
                        aff_tag.text.strip()) > 5:
                    aff = unidecode.unidecode(aff_tag.text.strip('\n ,'))
                    aff = re.sub(r' +', ' ', aff.replace('\n', ' ')).replace(' , ', ', ').replace(',,', ',').strip(', \n')
                    author['affiliations'].append(aff)
            authors.append(author)
        return authors

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract_meta_tags()}
