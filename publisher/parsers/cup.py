from publisher.elements import AuthorAffiliations
from publisher.parsers.parser import PublisherParser


class CUP(PublisherParser):
    parser_name = "cambridge university press"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url("cambridge.org")

    def authors_found(self):
        return self.soup.find("div", class_="author")

    def parse(self):
        results = []
        authors = self.soup.findAll("div", class_="author")
        for author in authors:
            name = author.find("dt").text
            name = name.strip().replace("*", "")

            affiliations = []
            affiliation_soup = author.find("div", class_="d-sm-flex")
            if affiliation_soup:
                for organization in affiliation_soup.stripped_strings:
                    affiliations.append(organization.strip())

            results.append(AuthorAffiliations(name=name, affiliations=affiliations))
        return results

    test_cases = [
        {
            "doi": "10.1017/S1355770X21000218",
            "result": [
                {
                    "name": "Julien Wolfersberger",
                    "affiliations": [
                        "Université Paris-Saclay, INRAE, AgroParisTech, Economie Publique, Thiverval-Grignon, France",
                        "Climate Economics Chair, Palais Brongniart, Paris, France",
                    ],
                },
                {
                    "name": "Gregory S. Amacher",
                    "affiliations": [
                        "Virginia Polytechnic Institute and State University, Blacksburg, VA, USA"
                    ],
                },
                {
                    "name": "Philippe Delacote",
                    "affiliations": [
                        "Climate Economics Chair, Palais Brongniart, Paris, France",
                        "BETA, Université Lorraine, INRAE, AgroParisTech, Nancy, France",
                    ],
                },
                {
                    "name": "Arnaud Dragicevic",
                    "affiliations": ["IRSTEA, Clermont-Ferrand, Aubiere, France"],
                },
            ],
        },
    ]
