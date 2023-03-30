from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import is_h_tag


class AmericanSocietyOfHematology(PublisherParser):
    parser_name = "american_society_of_hematology"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('ashpublications.org')

    def authors_found(self):
        return bool(self.soup.select('.al-author-name'))

    def parse_authors(self):
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

    def parse_abstract(self):
        if abs_heading := self.soup.find(lambda tag: is_h_tag(tag) and tag.text.lower() == 'abstract'):
            if abs_tag := abs_heading.find_next_sibling('div'):
                return abs_tag.text

        return None

    def parse(self):
        return {'authors': self.parse_authors(), 'abstract': self.parse_abstract()}


