import re

from repository.parsers.parser import RepositoryParser


class HAL(RepositoryParser):
    parser_name = "HAL"

    def is_correct_parser(self):
        meta_dc_identifiers = self.soup.find_all('meta', {'name': 'DC.identifier'})

        for meta_dc_identifier in meta_dc_identifiers:
            if content := meta_dc_identifier.get('content'):
                if re.match(r'^hal-\d+$', content):
                    return True

        return False

    def authors_found(self):
        return self.soup.find("meta", {"name": "citation_author"})

    def parse(self):
        return self.parse_meta_tags()

    test_cases = [
        {
            'page-id': 'VZut289qtYx4h5WRMEKn',  # https://hal.archives-ouvertes.fr/hal-00889367
            'result': [
                {'name': 'F Enjalbert', 'affiliations': []},
                {'name': 'Mc Nicot', 'affiliations': []},
                {'name': 'C Bayourthe', 'affiliations': []},
                {'name': 'R Moncoulon', 'affiliations': []},
            ]
        },
        {
            'page-id': 'aCS85rinbe2ywzSM8tUs',  # https://hal.archives-ouvertes.fr/hal-00874572
            'result': [
                {
                    'name': 'Jérôme Garnier',
                    'affiliations': [
                        'Institut Charles Gerhardt Montpellier - Institut de Chimie Moléculaire et des Matériaux de Montpellier',
                    ],
                },
                {
                    'name': 'Jérôme Warnant',
                    'affiliations': [
                        'Institut Charles Gerhardt Montpellier - Institut de Chimie Moléculaire et des Matériaux de Montpellier',
                    ],
                },
                {
                    'name': 'Patrick Lacroix-Desmazes',
                    'affiliations': [
                        'Institut Charles Gerhardt Montpellier - Institut de Chimie Moléculaire et des Matériaux de Montpellier'
                    ],
                },
                {
                    'name': 'Pierre-Emmanuel Dufils',
                    'affiliations': [
                        'Solvay'
                    ],
                },
                {
                    'name': 'Jérôme Vinas',
                    'affiliations': [
                        'Solvay'
                    ],
                },
                {
                    'name': 'Alex van Herk',
                    'affiliations': [
                        'Eindhoven University of Technology [Eindhoven]',
                        'Institute of Chemical and Engineering Sciences',
                    ],
                },
            ]
        },
    ]
