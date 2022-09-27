from exceptions import UnusualTrafficError
from publisher.elements import AuthorAffiliations
from publisher.parsers.parser import PublisherParser


class ACS(PublisherParser):
    parser_name = "acs"

    def is_publisher_specific_parser(self):
        if "Request forbidden by administrative rules" in str(self.soup):
            raise UnusualTrafficError(f"Page blocked within parser {self.parser_name}")
        return self.domain_in_meta_og_url(".acs.org")

    def authors_found(self):
        return self.soup.find("ul", class_="loa")

    def parse(self):
        result_authors = []
        author_soup = self.soup.find("ul", class_="loa")
        authors = author_soup.findAll("li")
        for author in authors:
            # method 1
            name = author.find("div", class_="loa-info-name")
            if name:
                name = name.text.strip()
            else:
                name = author.text

            if author.find("strong") and author.find("strong").text == "*":
                is_corresponding = True
            else:
                is_corresponding = False

            affiliations = []
            affiliation_soup = author.find("div", class_="loa-info-affiliations")
            if affiliation_soup:
                for organization in affiliation_soup.findAll("div"):
                    affiliations.append(organization.text.strip())

            result_authors.append(
                AuthorAffiliations(
                    name=name,
                    affiliations=affiliations,
                    is_corresponding=is_corresponding,
                )
            )
        return {"authors": result_authors, "abstract": self.parse_abstract_meta_tags()}

    test_cases = [
        {
            "doi": "10.1021/acs.jpcb.1c05793",
            "result": {
                "authors": [
                    {
                        "name": "Piotr Wróbel",
                        "affiliations": [
                            "Faculty of Chemistry, Jagiellonian University, Gronostajowa 2, 30-387 Kraków, Poland",
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Piotr Kubisiak",
                        "affiliations": [
                            "Faculty of Chemistry, Jagiellonian University, Gronostajowa 2, 30-387 Kraków, Poland"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Andrzej Eilmes",
                        "affiliations": [
                            "Faculty of Chemistry, Jagiellonian University, Gronostajowa 2, 30-387 Kraków, Poland"
                        ],
                        "is_corresponding": True,
                    },
                ],
                "abstract": "Classical molecular dynamics simulations have been performed for a series of electrolytes based on sodium bis(fluorosulfonyl)imide or sodium bis(trifluoromethylsulfonyl)imide salts and monoglyme, tetraglyme, and poly(ethylene oxide) as solvents. Structural properties have been assessed through the analysis of coordination numbers and binding patterns. Residence times for Na–O interactions have been used to investigate the stability of solvation shells. Diffusion coefficients of ions and electrical conductivity of the electrolytes have been estimated from molecular dynamics trajectories. Contributions to the total conductivity have been analyzed in order to investigate the role of ion–ion correlations. It has been found that the anion–cation interactions are more probable in the systems with NaTFSI salts. Accordingly, the degree of correlations between ion motions is larger in NaTFSI-based electrolytes.",
            },
        }
    ]
