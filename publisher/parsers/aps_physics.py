from bs4 import NavigableString

from publisher.elements import Author, Affiliation, AuthorAffiliations
from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import name_in_text


class APSPhysics(PublisherParser):
    parser_name = "aps_physics"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('physics.aps.org')

    def authors_found(self):
        return bool(self.soup.select('.author div'))

    def parse_authors(self):
        author_tags = self.soup.select('.author div')
        authors = []
        for author_tag in author_tags:
            name = author_tag.find('a').text.strip()
            affs = [aff_tag.text.strip() for aff_tag in author_tag.select('ul li')]
            authors.append({
                'name': name,
                'affiliations': affs,
                'is_corresponding': None
            })
        return authors

    def parse(self):
        return {
            'authors': self.parse_authors(),
            'abstract': self.parse_abstract_meta_tags()
        }