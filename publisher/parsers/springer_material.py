import re

from exceptions import UnusualTrafficError
from publisher.elements import Author, Affiliation
from publisher.parsers.parser import PublisherParser


class SpringerMaterial(PublisherParser):
    parser_name = "springer material"

    def is_publisher_specific_parser(self):
        head = self.soup.head
        if head:
            title = head.title
            if title:
                title = title.text
                if "SpringerMaterials" in title:
                    return True

    def authors_found(self):
        return self.soup.find("dd", {"id": "authors"})

    def parse(self):
        authors = self.get_authors()
        affiliations = self.get_affiliations()
        authors_affiliations = self.merge_authors_affiliations(authors, affiliations)
        return authors_affiliations

    def get_authors(self):
        authors = []
        section = self.soup.find("dd", {"id": "authors"})
        if not section and "Unusual traffic from your account" in str(self.soup):
            raise UnusualTrafficError(
                f"Unable to parse due to page returning error: Unusual traffic from your account"
            )
        name_soup = section.findAll("li")
        for name in name_soup:
            authors.append(
                Author(
                    name=self.format_name(name),
                    aff_ids=[self.find_aff_id_in_name(name)],
                )
            )
        return authors

    def get_affiliations(self):
        aff_soup = self.soup.find("dd", class_="author-affiliation")

        results = []
        if aff_soup:
            affiliations = aff_soup.findAll("li")
            for aff_raw in affiliations:
                aff_raw = aff_raw.text
                aff_id = self.find_aff_id_in_aff(aff_raw)
                aff = aff_raw.replace(str(aff_id), "").strip()
                results.append(Affiliation(aff_id=aff_id, organization=aff))
        return results

    @staticmethod
    def format_name(name):
        name_raw = name.text
        if name.sup:
            sup = name.sup.text
            name = name_raw.replace(sup, "").strip()
        else:
            name = name_raw.strip()
        return name

    @staticmethod
    def find_aff_id_in_name(name):
        aff_id = None
        if name.sup:
            aff_id_raw = name.sup.text
            aff_id_text = aff_id_raw.replace("(", "").replace(")", "").strip()
            aff_id = int(aff_id_text)
        return aff_id

    @staticmethod
    def find_aff_id_in_aff(aff_raw):
        m = re.search(r"\d+\n", aff_raw)
        m = m.group().strip()
        aff_id = int(m)
        return aff_id

    test_cases = [
        {
            "doi": "10.1007/10201640_144",
            "result": [
                {
                    "name": "H. von Philipsborn",
                    "affiliations": [],
                    "is_corresponding_author": False,
                },
                {
                    "name": "L. Treitinger",
                    "affiliations": [],
                    "is_corresponding_author": False,
                },
            ],
        },
        {
            "doi": "10.1007/10730534_69",
            "result": [
                {
                    "name": "S.I. Sukhoruchkin",
                    "affiliations": [
                        "Petersburg Nuclear Physics Institute, 188350, Gatchina, Leningrad District, Russia"
                    ],
                    "is_corresponding_author": False,
                },
                {
                    "name": "Z.N. Soroko",
                    "affiliations": [
                        "Petersburg Nuclear Physics Institute, 188350, Gatchina, Leningrad District, Russia"
                    ],
                    "is_corresponding_author": False,
                },
            ],
        },
    ]
