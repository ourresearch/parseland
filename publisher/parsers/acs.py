from publisher.elements import AuthorAffiliations
from publisher.parsers.parser import PublisherParser


class ACS(PublisherParser):
    parser_name = "acs"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url(".acs.org")

    def authors_found(self):
        return self.soup.find("ul", class_="loa")

    def parse(self):
        results = []
        author_soup = self.soup.find("ul", class_="loa")
        authors = author_soup.findAll("li")
        for author in authors:
            name = author.find("div", class_="loa-info-name").text.strip()

            affiliations = []
            affiliation_soup = author.find("div", class_="loa-info-affiliations")
            if affiliation_soup:
                for organization in affiliation_soup.findAll("div"):
                    affiliations.append(organization.text.strip())

            results.append(AuthorAffiliations(name=name, affiliations=affiliations))
        return results

    test_cases = [
        {
            "doi": "10.1021/acs.jpcb.1c05793",
            "result": [
                {
                    "name": "Piotr Wróbel",
                    "affiliations": [
                        "Faculty of Chemistry, Jagiellonian University, Gronostajowa 2, 30-387 Kraków, Poland",
                    ],
                },
                {
                    "name": "Piotr Kubisiak",
                    "affiliations": [
                        "Faculty of Chemistry, Jagiellonian University, Gronostajowa 2, 30-387 Kraków, Poland"
                    ],
                },
                {
                    "name": "Andrzej Eilmes",
                    "affiliations": [
                        "Faculty of Chemistry, Jagiellonian University, Gronostajowa 2, 30-387 Kraków, Poland"
                    ],
                },
            ],
        },
    ]
