from publisher.elements import AuthorAffiliations
from publisher.parsers.parser import PublisherParser


class CUP(PublisherParser):
    parser_name = "cambridge university press"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url("cambridge.org")

    def authors_found(self):
        return self.soup.find("div", class_="author")

    def parse(self):
        result_authors = []
        authors = self.soup.findAll("div", class_="author")
        for author in authors:
            name = author.find("dt").text
            if "*" in name:
                is_corresponding = True
            else:
                is_corresponding = False
            name = name.strip().replace("*", "")

            affiliations = []
            affiliation_soup = author.find("div", class_="d-sm-flex")
            if affiliation_soup:
                for organization in affiliation_soup.stripped_strings:
                    affiliations.append(organization.strip())

            result_authors.append(
                AuthorAffiliations(
                    name=name,
                    affiliations=affiliations,
                    is_corresponding_author=is_corresponding,
                )
            )
        return {"authors": result_authors, "abstract": self.parse_abstract_meta_tags()}

    test_cases = [
        {
            "doi": "10.1017/S1355770X21000218",
            "result": {
                "authors": [
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
                "abstract": "We develop a model of optimal land allocation in a developing economy that features three possible land uses: agriculture, primary and secondary forests. The distinction between those forest types reflects their different contributions in terms of public goods. In our model, reforestation is costly because it undermines land title security. Using the forest transition concept, we study long-term land-use change and explain important features of cumulative deforestation across countries. Our results shed light on the speed at which net deforestation ends, on the effect of tenure costs in this process, and on composition in steady state. We also present a policy analysis that emphasizes the critical role of institutional reforms addressing the costs of both deforestation and tenure in order to promote a transition. We find that focusing only on net forest losses can be misleading since late transitions may yield, upon given conditions, a higher level of environmental benefits.",
            },
        },
    ]
