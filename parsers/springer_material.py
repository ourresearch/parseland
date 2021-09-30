import re

from exceptions import AuthorNotFoundError


class SpringerMaterial:
    def __init__(self, soup):
        self.soup = soup
        self.parser_name = "springer material"

    def is_correct_parser(self):
        title = self.soup.head.title.text
        if "SpringerMaterials" in title:
            return True

    def parse(self):
        authors = self.get_authors()
        affiliations = self.get_affiliations()
        authors_affiliations = self.get_authors_affiliations(authors, affiliations)
        return authors_affiliations

    def get_authors(self):
        authors = []
        section = self.soup.find("dd", {"id": "authors"})
        if not section:
            raise AuthorNotFoundError(f"no authors found with springer materials parser,")
        name_soup = section.findAll("li")
        for name in name_soup:
            authors.append(
                {
                    "name": self.format_name(name),
                    "aff_id": self.find_aff_id_in_name(name),
                }
            )
        return authors

    def get_affiliations(self):
        aff_soup = self.soup.find("dd", class_="author-affiliation")

        result = None
        if aff_soup:
            aff_raw = aff_soup.li.text
            aff_id = self.find_aff_id_in_aff(aff_raw)
            aff = aff_raw.replace(str(aff_id), "").strip()
            result = {"aff_id": aff_id, "affiliation": aff}
        return result

    def get_authors_affiliations(self, authors, affiliations):
        results = []
        for author in authors:
            matching_affiliation = None
            if affiliations and author["aff_id"] == affiliations["aff_id"]:
                matching_affiliation = affiliations["affiliation"]

            results.append(
                {
                    "name": author["name"],
                    "affiliations": [matching_affiliation]
                    if matching_affiliation
                    else [],
                }
            )
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
        "doi": "10.1007/10783448_2306",
        "result": [
            {
                "name": "H. Duddeck",
                "affiliations": [
                    "Institut für Organische Chemie, Universität Hannover, 30167, Hannover, Germany"
                ],
            },
        ],
    },
    {
        "doi": "10.1007/10201640_144",
        "result": [
            {
                "name": "H. von Philipsborn",
                "affiliations": [],
            },
            {
                "name": "L. Treitinger",
                "affiliations": [],
            },
        ],
    },
]
