from publisher.elements import AuthorAffiliations
from publisher.parsers.parser import PublisherParser


class AOM(PublisherParser):
    parser_name = "academy of management"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url("aom.org")

    def authors_found(self):
        return self.soup.find("div", class_="loa-wrapper")

    def parse(self):
        results = []
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

            results.append(AuthorAffiliations(name=name, affiliations=affiliations))
        return results

    test_cases = [
        {
            "doi": "10.5465/AMBPP.2021.16285abstract",
            "result": [
                {
                    "name": "Paula Maria Infantes Sanchez",
                    "affiliations": [
                        "ESADE Business School",
                    ],
                },
                {
                    "name": "Bartolome Pascual-Fuster",
                    "affiliations": ["U. de les Illes Balears"],
                },
            ],
        },
    ]
