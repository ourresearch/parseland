import re
from bs4 import BeautifulSoup, NavigableString

from repository.parsers.parser import RepositoryParser


class HAL(RepositoryParser):
    parser_name = "HAL"

    def is_correct_parser(self):
        meta_dc_identifiers = self.soup.find_all("meta", {"name": "DC.identifier"})

        for meta_dc_identifier in meta_dc_identifiers:
            if content := meta_dc_identifier.get("content"):
                if re.match(r"^hal-\d+$", content):
                    return True

        return False

    def authors_found(self):
        return self.soup.find("meta", {"name": "citation_author"}) or bool(self.soup.select('div.authors a'))

    def parse_affs(self):
        affs = {}
        for tag in self.soup.select('div.structures span:not([class=icon-institution])'):
            _id = tag.text.strip()
            popup_tag = tag.next_sibling
            if isinstance(popup_tag, NavigableString):
                popup_tag = popup_tag.next_sibling
            popup_content = popup_tag.get('data-content')
            popup_soup = BeautifulSoup(popup_content, features="lxml", parser='lxml')
            org_tag = popup_soup.select_one('a')
            org = org_tag.text.strip()
            if org_tag.next_sibling.name == 'small':
                org += ' ' + org_tag.next_sibling.text.strip()
            affs[_id] = org
        return affs

    def parse_authors(self):
        authors = []
        affs = self.parse_affs()
        for tag in self.soup.select('div.authors a'):
            aff_ids_text = tag.next_sibling.text
            aff_ids = re.findall(r"\b\d+\b", aff_ids_text)
            author = {'name': tag.text.strip(),
                      'affiliations': [affs[aff_id] for aff_id in aff_ids],
                      'is_corresponding': None}
            authors.append(author)
        return authors

    def parse(self):
        return self.parse_authors()

    test_cases = [
        {
            "page-id": "VZut289qtYx4h5WRMEKn",  # https://hal.archives-ouvertes.fr/hal-00889367
            "result": [
                {
                    "name": "F Enjalbert",
                    "affiliations": [],
                    "is_corresponding": None,
                },
                {
                    "name": "Mc Nicot",
                    "affiliations": [],
                    "is_corresponding": None,
                },
                {
                    "name": "C Bayourthe",
                    "affiliations": [],
                    "is_corresponding": None,
                },
                {
                    "name": "R Moncoulon",
                    "affiliations": [],
                    "is_corresponding": None,
                },
            ],
        },
        {
            "page-id": "aCS85rinbe2ywzSM8tUs",  # https://hal.archives-ouvertes.fr/hal-00874572
            "result": [
                {
                    "name": "Jérôme Garnier",
                    "affiliations": [
                        "Institut Charles Gerhardt Montpellier - Institut de Chimie Moléculaire et des Matériaux de Montpellier",
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Jérôme Warnant",
                    "affiliations": [
                        "Institut Charles Gerhardt Montpellier - Institut de Chimie Moléculaire et des Matériaux de Montpellier",
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Patrick Lacroix-Desmazes",
                    "affiliations": [
                        "Institut Charles Gerhardt Montpellier - Institut de Chimie Moléculaire et des Matériaux de Montpellier"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Pierre-Emmanuel Dufils",
                    "affiliations": ["Solvay"],
                    "is_corresponding": None,
                },
                {
                    "name": "Jérôme Vinas",
                    "affiliations": ["Solvay"],
                    "is_corresponding": None,
                },
                {
                    "name": "Alex van Herk",
                    "affiliations": [
                        "Eindhoven University of Technology [Eindhoven]",
                        "Institute of Chemical and Engineering Sciences",
                    ],
                    "is_corresponding": None,
                },
            ],
        },
    ]
