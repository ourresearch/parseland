from repository.parsers.parser import RepositoryParser


class HAL(RepositoryParser):
    parser_name = "HAL"

    def is_correct_parser(self):
        return self.domain_in_meta_og_url("hal.archives-ouvertes.fr")

    def authors_found(self):
        return self.soup.find("meta", {"name": "citation_author"})

    def parse(self):
        return self.parse_meta_tags()

    test_cases = [
        {
            'page-id': 'uvg3rMMYJVL9XfvGTHC9',  # https://hal.archives-ouvertes.fr/hal-00889367
            'result': [
                {'name': 'F Enjalbert', 'affiliations': []},
                {'name': 'Mc Nicot', 'affiliations': []},
                {'name': 'C Bayourthe', 'affiliations': []},
                {'name': 'R Moncoulon', 'affiliations': []},
            ]
        },
        {
            'page-id': 'gmg9hYqeTLKSFifo9CvG',  # https://hal.archives-ouvertes.fr/hal-00874572
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
