from publisher.elements import AuthorAffiliations
from publisher.parsers.parser import PublisherParser


class AOM(PublisherParser):
    parser_name = "academy_of_management"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url("aom.org")

    def authors_found(self):
        return self.soup.find("div", class_="loa-wrapper")

    def parse(self):
        result_authors = []
        author_soup = self.soup.find("div", class_="loa-wrapper")
        authors = author_soup.findAll("div", class_="accordion-tabbed__tab-mobile")
        for author in authors:
            name = author.a.text.strip()

            affiliations = []
            affiliation_soup = author.find("div", class_="author-info")
            if affiliation_soup:
                bottom_info = author.find("div", class_="bottom-info")
                bottom_info.clear()
                affiliations.append(affiliation_soup.text.strip())

            result_authors.append(
                AuthorAffiliations(name=name, affiliations=affiliations)
            )

        return {"authors": result_authors, "abstract": self.parse_abstract_meta_tags()}
