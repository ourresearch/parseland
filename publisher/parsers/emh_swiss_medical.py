from bs4 import NavigableString, Tag

from publisher.parsers.parser import PublisherParser

from publisher.parsers.utils import strip_prefix, cleanup_raw_name


class EMHSwissMedical(PublisherParser):
    parser_name = "emh_swiss_medical"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('bullmed.ch')

    def authors_found(self):
        return bool(self.soup.select('.authors'))

    def parse_affs(self):
        affs = {}
        affs_tag = self.soup.select_one('.affiliation')
        current_num = None
        for child in affs_tag.children:
            if isinstance(child, NavigableString):
                affs[current_num] = child.text.strip()
            elif isinstance(child, Tag) and child.name == 'sup':
                current_num = child.text.strip()
        return affs

    def parse_authors(self):
        authors_tag = self.soup.select_one('.authors')
        authors = []
        affs = self.parse_affs()
        for child in authors_tag.children:
            if isinstance(child, NavigableString):
                if name := cleanup_raw_name(child.text):
                    author = {'name': name,
                              'affiliations': [],
                              'is_corresponding': None}
                    authors.append(author)
            elif isinstance(child, Tag) and child.name == 'sup':
                authors[-1]['affiliations'].append(affs[child.text.strip()])
        return authors

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract_meta_tags()}
