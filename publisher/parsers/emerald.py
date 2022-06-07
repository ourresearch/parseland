from publisher.elements import AuthorAffiliations
from publisher.parsers.parser import PublisherParser


class Emerald(PublisherParser):
    parser_name = "emerald"

    def is_publisher_specific_parser(self):
        return self.domain_in_canonical_link("emerald.com")

    def authors_found(self):
        return self.soup.find("span", class_="m:contributor-display")

    def parse(self):
        results = []
        author_soup = self.soup.find("span", class_="m:contributor-display")
        authors = author_soup.findAll("div", {"contrib-type": "author"})
        for author in authors:
            name = author.a.text.strip()

            affiliations = []
            affiliation_soup = author.find(
                "span", class_="intent_contributor_affiliate"
            )
            if affiliation_soup:
                for organization in affiliation_soup.text.split(", and"):
                    organization = (
                        organization.strip().replace(", and", "").replace("\n", "")
                    )
                    if organization.startswith("("):
                        organization = organization[1:]
                    if organization.endswith(")"):
                        organization = organization[:-1]
                    affiliations.append(organization)

            results.append(AuthorAffiliations(name=name, affiliations=affiliations))
        return results

    test_cases = [
        {
            "doi": "10.1108/SEF-09-2020-0364",
            "result": [
                {
                    "name": "Zakaria Lacheheb",
                    "affiliations": [
                        "School of Business and Economics, Universiti Putra Malaysia, Serdang, Malaysia",
                        "Kulliyyah of Economics and Management Sciences, International Islamic University Malaysia, Gombak, Malaysia",
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Normaz Wana Ismail",
                    "affiliations": [
                        "School of Business and Economics, Universiti Putra Malaysia, Serdang, Malaysia"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "N.A.M. Naseem",
                    "affiliations": [
                        "School of Business and Economics, Universiti Putra Malaysia, Serdang, Malaysia"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Ly Slesman",
                    "affiliations": [
                        "Centre for Advanced Research (CARe), Universiti Brunei Darussalam, Bandar Seri Begawan, Brunei Darussalam"
                    ],
                    "is_corresponding": None,
                },
            ],
        },
    ]
