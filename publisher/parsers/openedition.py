from bs4 import NavigableString

from publisher.parsers.parser import PublisherParser


class OpenEdition(PublisherParser):
    parser_name = "open_edition"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('openedition.org')

    def authors_found(self):
        return bool(self.soup.select('.section.authors'))

    def parse_authors(self):
        authors_section = self.soup.select_one('.section.authors')
        if not authors_section:
            return []
        aff_tags = authors_section.select('.description.directionltr')
        authors = []
        for aff_tag in aff_tags:
            if aff_tag.find('.affiliation'):
                aff_tag = aff_tag.find('.affiliation')
            affs = [child.strip() for child in aff_tag.children if isinstance(child, NavigableString)]
            author_name = aff_tag.find_previous_sibling('h3').text
            author = {'name': author_name, 'affiliations': affs, 'is_corresponding': None}
            authors.append(author)
        return authors

    def parse(self):
        return {'authors': self.parse_authors(), 'abstract': self.parse_abstract_meta_tags()}

