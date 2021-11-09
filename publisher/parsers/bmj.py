from publisher.elements import Author, Affiliation
from publisher.parsers.parser import PublisherParser


class BMJ(PublisherParser):
    parser_name = "bmj"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url("bmj.com")

    def authors_found(self):
        return self.soup.find("ol", class_="contributor-list") or self.soup.find(
            "meta", {"name": "citation_author"}
        )

    def parse(self):
        authors = self.get_authors()
        if not authors:
            # try meta tags
            return self.parse_meta_tags()

        affiliations = self.get_affiliations()
        authors_affiliations = self.merge_authors_affiliations(authors, affiliations)
        return authors_affiliations

    def get_authors(self):
        authors = []
        author_soup = self.soup.find("ol", class_="contributor-list")
        if not author_soup:
            return None

        author_soup = author_soup.findAll("li")
        for author in author_soup:
            name_soup = author.find("span", class_="name")
            if not name_soup:
                continue
            name = name_soup.text.strip()
            aff_ids_raw = author.findAll("a", class_="xref-aff")
            aff_ids = []
            for aff_id_raw in aff_ids_raw:
                aff_id = aff_id_raw.text.strip()
                if aff_id:
                    aff_ids.append(aff_id)
            authors.append(Author(name=name, aff_ids=aff_ids))
        return authors

    def get_affiliations(self):
        aff_soup = self.soup.find("ol", class_="affiliation-list")

        results = []
        if aff_soup:
            affiliations = aff_soup.findAll("li", class_="aff")
            for aff_raw in affiliations:
                # affiliation id
                aff_id_raw = aff_raw.find("sup")
                if aff_id_raw:
                    aff_id = aff_id_raw.text
                    aff_id_raw.clear()
                else:
                    aff_id = None

                # affiliation
                aff = aff_raw.text.strip()
                results.append(Affiliation(organization=aff, aff_id=aff_id))
        return results

    test_cases = [
        {
            "doi": "10.1136/bcr-2020-239618",
            "result": [
                {
                    "name": "Brian Alexander Hummel",
                    "affiliations": [
                        "Division of Infectious Diseases, Immunology and Allergy, Department of Pediatrics, University of Ottawa Faculty of Medicine, Ottawa, Ontario, Canada",
                    ],
                },
                {
                    "name": "Julie Blackburn",
                    "affiliations": [
                        "Département de Microbiologie et Immunologie, University of Montreal Faculty of Medicine, Montreal, Quebec, Canada"
                    ],
                },
                {
                    "name": "Anne Pham-Huy",
                    "affiliations": [
                        "Division of Infectious Diseases, Immunology and Allergy, Department of Pediatrics, University of Ottawa Faculty of Medicine, Ottawa, Ontario, Canada",
                    ],
                },
                {
                    "name": "Katherine Muir",
                    "affiliations": [
                        "Division of Neurology, Department of Pediatrics, University of Ottawa Faculty of Medicine, Ottawa, Ontario, Canada"
                    ],
                },
            ],
        },
        {
            "doi": "10.1136/bmjopen-2020-043554",
            "result": [
                {
                    "name": "Kelly Teo",
                    "affiliations": [
                        "Department of Gerontology, Simon Fraser University, Vancouver, British Columbia, Canada",
                    ],
                },
                {
                    "name": "Ryan Churchill",
                    "affiliations": [
                        "Department of Gerontology, Simon Fraser University, Vancouver, British Columbia, Canada"
                    ],
                },
                {
                    "name": "Indira Riadi",
                    "affiliations": [
                        "Department of Gerontology, Simon Fraser University, Vancouver, British Columbia, Canada",
                    ],
                },
                {
                    "name": "Lucy Kervin",
                    "affiliations": [
                        "Department of Gerontology, Simon Fraser University, Vancouver, British Columbia, Canada"
                    ],
                },
                {
                    "name": "Theodore Cosco",
                    "affiliations": [
                        "Department of Gerontology, Simon Fraser University, Vancouver, British Columbia, Canada",
                        "Oxford Institute of Population Ageing, University of Oxford, Oxford, Oxfordshire, UK",
                    ],
                },
            ],
        },
        {
            "doi": "10.1136/bcr-2021-243370",
            "result": [
                {
                    "name": "John Leso",
                    "affiliations": [
                        "Internal Medicine, Albany Medical College, Albany, New York, USA",
                    ],
                },
                {
                    "name": "Majd Al-Ahmad",
                    "affiliations": [
                        "Internal Medicine, Albany Medical College, Albany, New York, USA"
                    ],
                },
                {
                    "name": "Drinnon O Hand",
                    "affiliations": [
                        "Internal Medicine, Albany Medical College, Albany, New York, USA",
                    ],
                },
            ],
        },
    ]
