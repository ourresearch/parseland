from bs4 import NavigableString

from publisher.elements import Author, Affiliation
from publisher.parsers.parser import PublisherParser


class Thieme(PublisherParser):
    parser_name = "thieme"

    def is_publisher_specific_parser(self):
        if desc_tag := self.soup.select_one('meta[name=description]'):
            return desc_tag['content'].startswith('Thieme')
        return False

    def authors_found(self):
        return bool(self.soup.select_one('.authors'))

    def parse_affiliations(self):
        aff_tags = self.soup.select('.authorsAffiliationsList li')
        affs = []
        for tag in aff_tags:
            sup_tag = tag.find('sup')
            aff_id = sup_tag.text.strip()
            org = sup_tag.next_sibling.text.strip()
            affs.append(Affiliation(organization=org, aff_id=aff_id))
        return affs

    def parse_authors(self):
        authors_tag = self.soup.select_one('.authors')
        authors = []
        if not authors_tag:
            return authors
        for tag in authors_tag:
            if isinstance(tag, NavigableString):
                name = tag.text.strip(' ,\n\r')
                if not name:
                    continue
                aff_ids = []
                aff_tag = tag
                while aff_tag.next_sibling and aff_tag.next_sibling.name == 'a':
                    aff_tag = aff_tag.next_sibling
                    aff_ids.append(aff_tag.text.strip())
                authors.append(Author(name, aff_ids))
        return authors

    def parse(self):
        affs = self.parse_affiliations()
        authors = self.parse_authors()
        authors = self.merge_authors_affiliations(authors, affs)
        abstract = self.parse_abstract_meta_tags()
        return {
            'authors': authors,
            'abstract': abstract
        }
