import re

from publisher.elements import Author, Affiliation
from publisher.parsers.parser import PublisherParser


class AIPPublishing(PublisherParser):
    parser_name = "aip_publishing"

    def is_correct_parser(self):
        return self.domain_in_meta_og_url("aip.scitation.org")

    def authors_found(self):
        return self.soup.find("div", class_="publicationContentAuthors")

    def parse(self):
        authors = self.get_authors()
        affiliations = self.get_affiliations()
        return self.merge_authors_affiliations(authors, affiliations)

    def get_authors(self):
        authors = []

        if authors_div := self.soup.find("div", class_="publicationContentAuthors"):
            for author_span in authors_div.find_all('span', class_="contrib-author"):
                if author_a := author_span.find("a", href=re.compile(r"^/author/")):
                    if author_a.text and (author_name := author_a.text.strip()):
                        affiliation_ids = []

                        for affiliation_sup in author_span.find_all('sup'):
                            if sup_text := affiliation_sup.text and affiliation_sup.text.strip():
                                for sup_split_part in sup_text.split(','):
                                    if (affiliation_id := sup_split_part.strip()) and affiliation_id.isdigit():
                                        affiliation_ids.append(affiliation_id)

                        authors.append(Author(name=author_name, aff_ids=affiliation_ids))
        return authors

    def get_affiliations(self):
        affiliations = []

        if affiliations_div := self.soup.find("div", class_="affiliations-list"):
            for affiliation_li in affiliations_div.find_all("li", class_="author-affiliation"):
                if institution_a := affiliation_li.find("a", class_="institution"):
                    if institution_name := institution_a.text and institution_a.text.strip():
                        if id_sup := affiliation_li.find("sup"):
                            if (affiliation_id := id_sup.text and id_sup.text.strip()) and affiliation_id.isdigit():
                                affiliations.append(Affiliation(aff_id=affiliation_id, organization=institution_name))

        return affiliations

    test_cases = [
        {
            "doi": "10.1063/5.0002598",
            "result": [
                {
                    "name": "Muhamad Sahlan",
                    "affiliations": [
                        "Department of Chemical Engineering, Faculty of Engineering, Universitas Indonesia"
                    ]
                },
                {
                    "name": "Etin Rohmatin",
                    "affiliations": [
                        "Department of Health Polytechnic Republic of Indonesia\u2019s Health Ministry Tasikmalaya"
                    ]
                },
                {
                    "name": "Dita Amalia Wijanarko",
                    "affiliations": [
                        "Department of Chemical Engineering, Faculty of Engineering, Universitas Indonesia"
                    ]
                },
                {
                    "name": "Kenny Lischer",
                    "affiliations": [
                        "Department of Chemical Engineering, Faculty of Engineering, Universitas Indonesia"
                    ]
                },
                {
                    "name": "Anondho Wijanarko",
                    "affiliations": [
                        "Department of Chemical Engineering, Faculty of Engineering, Universitas Indonesia"
                    ]
                },
                {
                    "name": "Ananda Bagus Richky Digdaya Putra",
                    "affiliations": [
                        "Department of Chemical Engineering, Faculty of Engineering, Universitas Indonesia"
                    ]
                },
                {
                    "name": "Nunuk Widhyastuti",
                    "affiliations": [
                        "Research center for Biology, Indonesian Institute of science, Bogor"
                    ]
                }
            ],
        },
        {
            "doi": "10.1063/5.0051325",
            "result": [
                {
                    "name": "M. Cavaiola",
                    "affiliations": [
                        "Department of Civil, Chemical and Environmental Engineering (DICCA), University of Genova",
                        "INFN, Genova Section"
                    ]
                },
                {
                    "name": "A. Mazzino",
                    "affiliations": [
                        "Department of Civil, Chemical and Environmental Engineering (DICCA), University of Genova",
                        "INFN, Genova Section"
                    ]
                }
            ],
        },
        {
            "doi": "10.1063/5.0028171",
            "result": [
                {
                    "name": "E. N. Eremin",
                    "affiliations": [
                        "Department of Mechanical Engineering and Material Science, Machine-Building Institute, Omsk State Technical University"
                    ]
                },
                {
                    "name": "V. M. Yurov",
                    "affiliations": [
                        "Department of Ion-Plasma Technologies, Karaganda State University E.A. Buketova"
                    ]
                },
                {
                    "name": "V. S. Oleshko",
                    "affiliations": [
                        "Military Training Center, Moscow Aviation Institute (National Research University)"
                    ]
                },
                {
                    "name": "S. A. Guchenko",
                    "affiliations": [
                        "Department of Ion-Plasma Technologies, Karaganda State University E.A. Buketova"
                    ]
                }
            ]
        },
        {
            "doi": "10.1063/1.5129000",
            "result": [
                {
                    "name": "Tushar Tyagi",
                    "affiliations": [
                        "Department of Electrical Engineering, Indian Institute of Technology Gandhinagar"
                    ]
                },
                {
                    "name": "P. Sumathi",
                    "affiliations": [
                        "Department of Electrical Engineering, Indian Institute of Technology Roorkee"
                    ]
                }
            ]
        }
    ]
