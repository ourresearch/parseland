import re

from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import is_h_tag


class ASMInternational(PublisherParser):
    parser_name = "asm_international"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('astm.org') or self.domain_in_meta_og_url('asme.org')

    def authors_found(self):
        return bool(self.soup.find(lambda tag: is_h_tag(tag) and 'Author Information' in tag.text) or self.soup.select('.al-author-name'))

    def parse_authors(self):
        author_heading = self.soup.find(lambda tag: is_h_tag(tag) and 'Author Information' in tag.text)
        authors = []
        for author_tag in author_heading.find_next_siblings('div'):
            author = {'name': None, 'affiliations': [], 'is_corresponding': None}
            for i, child in enumerate(author_tag.children):
                if len(child.text.strip()) < 3:
                    continue
                if author['name'] is None:
                    author['name'] = child.text
                else:
                    author['affiliations'].append(child.text.strip())
            authors.append(author)
        return authors

    def parse_abstract(self):
        if abs_heading := self.soup.find(lambda tag: is_h_tag(tag) and 'Abstract' in tag.text):
            abs_tag = abs_heading.find_next_sibling('div')
            return abs_tag.find('p').text
        return None

    def get_asme_corresponding_author(self):
        for author_tag in self.soup.select('.al-author-name'):
            if 'Corresponding author' in author_tag.text:
                return author_tag.find('a').text.strip()
        return None

    def parse(self):
        if self.domain_in_meta_og_url('asme.org'):
            authors = self.parse_author_meta_tags()
            if corr_author := self.get_asme_corresponding_author():
                split = [part.strip() for part in re.split(r'\W', corr_author)]
                for author in authors:
                    if all([part.lower() in author['name'].lower() for part in split]):
                        author['is_corresponding'] = True
            return {'authors': authors, 'abstract': self.parse_abstract_meta_tags()}
        return {'authors': self.parse_authors(), 'abstract': self.parse_abstract()}
