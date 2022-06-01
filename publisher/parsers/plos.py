from publisher.elements import AuthorAffiliations
from publisher.parsers.parser import PublisherParser


class PLOS(PublisherParser):
    parser_name = "plos"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url("plos.org")

    def authors_found(self):
        return self.soup.find("div", class_="title-authors")

    def parse(self):
        results = []
        author_soup = self.soup.find("div", class_="title-authors")
        authors = author_soup.findAll("li")
        for author in authors:
            name = author.find("a", class_="author-name")
            if not name:
                continue
            name = name.text.replace(",", "").strip()

            is_corresponding = True if author.find("span", class_="email") else False

            affiliations = []
            affiliation_soup = author.findAll("p")
            if affiliation_soup:
                for aff_raw in affiliation_soup:
                    if aff_raw.span and aff_raw.span.text.lower().startswith(
                        "affiliation"
                    ):
                        aff_raw.span.clear()
                        for aff in aff_raw.text.split("\n"):
                            if aff and aff.strip().endswith(","):
                                affiliations.append(aff.strip()[:-1])
                            elif aff.strip():
                                affiliations.append(aff.strip())

            results.append(
                AuthorAffiliations(
                    name=name,
                    affiliations=affiliations,
                    is_corresponding=is_corresponding,
                )
            )
        return results

    test_cases = [
        {
            "doi": "10.1371/journal.pone.0245719",
            "result": [
                {
                    "name": "Niclas Kuper",
                    "affiliations": ["Bielefeld University, Bielefeld, Germany"],
                    "is_corresponding": True,
                },
                {
                    "name": "Nick Modersitzki",
                    "affiliations": ["Bielefeld University, Bielefeld, Germany"],
                    "is_corresponding": False,
                },
                {
                    "name": "Le Vy Phan",
                    "affiliations": ["Bielefeld University, Bielefeld, Germany"],
                    "is_corresponding": False,
                },
                {
                    "name": "John Rauthmann",
                    "affiliations": ["Bielefeld University, Bielefeld, Germany"],
                    "is_corresponding": False,
                },
            ],
        },
        {
            "doi": "10.1371/journal.pcbi.1009157",
            "result": [
                {
                    "name": "Marianyela Sabina Petrizzelli",
                    "affiliations": [
                        "Université Paris-Saclay, INRAE, CNRS, AgroParisTech, GQE–Le Moulon, Gif-sur-Yvette, France",
                        "Institut Curie, PSL Research University, Paris, France",
                        "INSERM, U900, Paris, France",
                        "CBIO-Centre for Computational Biology, MINES ParisTech, PSL Research University, Paris, France",
                    ],
                    "is_corresponding": True,
                },
                {
                    "name": "Dominique de Vienne",
                    "affiliations": [
                        "Université Paris-Saclay, INRAE, CNRS, AgroParisTech, GQE–Le Moulon, Gif-sur-Yvette, France"
                    ],
                    "is_corresponding": False,
                },
                {
                    "name": "Thibault Nidelet",
                    "affiliations": [
                        "SPO, INRAE, Montpellier SupAgro, Université de Montpellier, Montpellier, France"
                    ],
                    "is_corresponding": False,
                },
                {
                    "name": "Camille Noûs",
                    "affiliations": ["Laboratoire Cogitamus, France"],
                    "is_corresponding": False,
                },
                {
                    "name": "Christine Dillmann",
                    "affiliations": [
                        "Université Paris-Saclay, INRAE, CNRS, AgroParisTech, GQE–Le Moulon, Gif-sur-Yvette, France"
                    ],
                    "is_corresponding": False,
                },
            ],
        },
    ]
