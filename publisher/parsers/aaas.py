from publisher.elements import AuthorAffiliations
from publisher.parsers.parser import PublisherParser


# American Association for the Advancement of Science
class AAAS(PublisherParser):
    def authors_found(self):
        return bool(self.soup.select('div[property=author]'))

    parser_name = "aaas"

    def is_publisher_specific_parser(self):
        return self.domain_in_canonical_link('science.org')

    def parse_authors(self):
        author_tags = self.soup.select('div[property=author]:has(span)')
        authors = []
        for tag in author_tags:
            given_name = tag.select_one('span[property=givenName]').text
            family_name = tag.select_one('span[property=familyName]').text
            name = f'{given_name} {family_name}'
            is_corresponding = bool(tag.sup)
            affiliations_tags = tag.select('div[property=affiliation]')
            affiliations = [aff_tag.text for aff_tag in affiliations_tags]
            authors.append(
                AuthorAffiliations(name=name, is_corresponding=is_corresponding,
                                   affiliations=affiliations))
        return authors

    def parse_abstract(self):
        abstract_tag = self.soup.select_one('section#abstract div')
        return abstract_tag.text if abstract_tag else None

    def parse(self):
        return {"authors": self.parse_authors(),
                "abstract": self.parse_abstract()}
