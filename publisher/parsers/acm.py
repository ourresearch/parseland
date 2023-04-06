from bs4 import BeautifulSoup

from publisher.parsers.parser import PublisherParser


class AssociationForComputingMachinery(PublisherParser):
    parser_name = "association_for_computing_machineinery"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('acm.org')

    def authors_found(self):
        return bool(self.soup.select('span[class*="author-info"]'))

    def parse_authors(self):
        author_tags = self.soup.select('span[class*="author-info"]')
        authors = []

        for author_tag in author_tags:
            if name_tag := author_tag.select_one('[class*="author-name"]'):
                name = name_tag.text.strip()
            else:
                continue
            aff_tags = author_tag.select('[class*="author_inst"]')
            affs = [tag.text for tag in aff_tags]
            authors.append({
                'name': name,
                'affiliations': affs,
                'is_corresponding': None,
            })

        return authors

    def parse_abstract(self):
        if abs_tag := self.soup.select_one('.abstractInFull p'):
            return abs_tag.text
        return None

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract()}
