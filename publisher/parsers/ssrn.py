from publisher.elements import AuthorAffiliations
from publisher.parsers.parser import PublisherParser


class SSRN(PublisherParser):
    parser_name = "ssrn"

    def is_correct_parser(self):
        return self.domain_in_canonical_link("papers.ssrn.com")

    def authors_found(self):
        return self.soup.find("div", class_="authors")

    def parse(self):
        results = []
        authors = self.soup.find("div", class_="authors")
        name_soup = authors.findAll("h2")
        affiliation_soup = authors.findAll("p")

        for name, affiliation in zip(name_soup, affiliation_soup):
            name = name.text.strip()
            affiliations = []
            affiliation = affiliation.text.strip()
            if affiliation != "affiliation not provided to SSRN":
                aff_split = affiliation.split(";")
                for aff in aff_split:
                    affiliations.append(aff.strip())
            results.append(AuthorAffiliations(name=name, affiliations=affiliations))

        return results

    test_cases = [
        {
            "doi": "10.2139/ssrn.1500730",
            "result": [
                {
                    "name": "Susann Rohwedder",
                    "affiliations": [
                        "RAND Corporation",
                    ],
                },
                {
                    "name": "Robert J. Willis",
                    "affiliations": [
                        "University of Michigan at Ann Arbor - Department of Economics",
                        "National Bureau of Economic Research (NBER)",
                    ],
                },
            ],
        },
        {
            "doi": "10.2139/ssrn.3782675",
            "result": [
                {
                    "name": "Madison Condon",
                    "affiliations": [
                        "Boston University - School of Law",
                        "New York University School of Law",
                    ],
                },
            ],
        },
    ]
