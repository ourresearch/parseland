import re

from publisher.parsers.parser import PublisherParser


class Frontiers(PublisherParser):
    parser_name = "frontiers"

    def is_correct_parser(self):
        return self.domain_in_meta_og_url("frontiersin.org")

    def authors_found(self):
        return self.soup.find("div", class_="authors")

    def parse(self):
        authors = self.get_authors()
        affiliations = self.get_affiliations()
        authors_affiliations = self.get_authors_affiliations(authors, affiliations)
        return authors_affiliations

    def get_authors(self):
        authors = []
        author_soup = self.soup.find("div", class_="authors")
        author_soup = author_soup.findAll("img", class_="pr5")
        for author in author_soup:
            # set name
            name_soup = author.next_sibling
            name = name_soup.text

            # set aff_ids
            aff_id_soup = name_soup.next_element
            if aff_id_soup.name == "sup":
                aff_ids = aff_id_soup.text
            else:
                aff_ids = None

            authors.append(
                {"name": name, "aff_ids": self.format_ids(aff_ids) if aff_ids else []}
            )
        return authors

    def get_affiliations(self):
        aff_soup = self.soup.find("ul", class_="notes")

        results = []
        if aff_soup:
            affiliations = aff_soup.findAll("li")
            for aff_raw in affiliations:
                aff_id_raw = aff_raw.find("sup")
                if aff_id_raw:
                    aff_id = aff_id_raw.text
                else:
                    aff_id = None
                aff = aff_raw.text
                if aff_id:
                    aff = aff.replace(aff_id, "").strip()
                if aff_id != "*" and aff_id != "†":
                    aff_id = int(aff_id) if aff_id else None
                    results.append({"aff_id": aff_id, "affiliation": aff})
        return results

    def get_authors_affiliations(self, authors, affiliations):
        results = []
        for author in authors:
            author_affiliations = []

            # scenario 1 affiliations with ids
            for aff_id in author["aff_ids"]:
                for affiliation in affiliations:
                    if aff_id == affiliation["aff_id"]:
                        author_affiliations.append(affiliation["affiliation"])

            # scenario 2 affiliations with no ids (applied to all authors)
            for affiliation in affiliations:
                if len(author["aff_ids"]) == 0 and affiliation["aff_id"] is None:
                    author_affiliations.append(affiliation["affiliation"])

            results.append(
                {"name": author["name"], "affiliations": author_affiliations}
            )
        return results

    @staticmethod
    def format_ids(ids):
        ids_cleaned = re.sub(
            "[^0-9^,]", "", ids
        )  # remove anything that is not a number or comma
        ids_split = ids_cleaned.split(",")
        aff_ids = []
        for aff_id in ids_split:
            if aff_id:
                aff_ids.append(int(aff_id))
        return aff_ids

    test_cases = [
        {
            "doi": "10.3389/fevo.2021.635552",
            "result": [
                {
                    "name": "Kohei Oguchi",
                    "affiliations": [
                        "Misaki Marine Biological Station, School of Science, The University of Tokyo, Miura, Japan",
                        "National Institute of Advanced Industrial Science and Technology, Tsukuba, Japan",
                    ],
                },
                {
                    "name": "Kiyoto Maekawa",
                    "affiliations": [
                        "Faculty of Science, Academic Assembly, University of Toyama, Gofuku, Japan",
                    ],
                },
                {
                    "name": "Toru Miura",
                    "affiliations": [
                        "Misaki Marine Biological Station, School of Science, The University of Tokyo, Miura, Japan"
                    ],
                },
            ],
        },
        {
            "doi": "10.3389/fgene.2021.642759",
            "result": [
                {
                    "name": "Seungjun Ahn",
                    "affiliations": [
                        "Department of Biostatistics, University of Florida, Gainesville, FL, United States"
                    ],
                },
                {
                    "name": "Tyler Grimes",
                    "affiliations": [
                        "Department of Biostatistics, University of Florida, Gainesville, FL, United States",
                    ],
                },
                {
                    "name": "Somnath Datta",
                    "affiliations": [
                        "Department of Biostatistics, University of Florida, Gainesville, FL, United States"
                    ],
                },
            ],
        },
        {
            "doi": "10.3389/fcvm.2021.697240",
            "result": [
                {
                    "name": "Sergey Kozhukhov",
                    "affiliations": [
                        "SI “National Scientific Center “The M.D.Strazhesko Institute of Cardiology,”” Kyiv, Ukraine"
                    ],
                },
                {
                    "name": "Nataliia Dovganych",
                    "affiliations": [
                        "SI “National Scientific Center “The M.D.Strazhesko Institute of Cardiology,”” Kyiv, Ukraine",
                    ],
                },
            ],
        },
    ]
