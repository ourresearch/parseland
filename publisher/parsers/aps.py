from publisher.parsers.parser import PublisherParser


class APS(PublisherParser):
    parser_name = "aps"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('journals.aps.org')

    def authors_found(self):
        return self.soup.find("meta", {"name": "citation_author"})

    def parse(self):
        return self.parse_meta_tags()

    test_cases = [
        {
            "doi": "10.1103/physreve.99.032306",
            "result": [
                {
                    "name": "Pedro H. T. Schimit",
                    "affiliations": [
                        "Informatics and Knowledge Management Graduate Program, Universidade Nove de Julho, Rua Vergueiro, 235/249, CEP 01504-000, São Paulo, São Paulo, Brazil"
                    ],
                },
                {
                    "name": "Karan Pattni",
                    "affiliations": [
                        "Department of Mathematical Sciences, University of Liverpool, Mathematical Sciences Building, Liverpool L69 7ZL, United Kingdom"
                    ],
                },
                {
                    "name": "Mark Broom",
                    "affiliations": [
                        "Department of Mathematics, City, University of London, Northampton Square, London EC1V 0HB, United Kingdom"
                    ],
                }
            ],
        },
        {
            "doi": "10.1103/physrevb.103.235137",
            "result": [
                {
                    "name": "Christoph Schönle",
                    "affiliations": [
                        "Institut für Theoretische Physik, Georg-August-Universität Göttingen, D-37077 Göttingen, Germany"
                    ]
                },
                {
                    "name": "David Jansen",
                    "affiliations": [
                        "Institut für Theoretische Physik, Georg-August-Universität Göttingen, D-37077 Göttingen, Germany"
                    ]
                },
                {
                    "name": "Fabian Heidrich-Meisner",
                    "affiliations": [
                        "Institut für Theoretische Physik, Georg-August-Universität Göttingen, D-37077 Göttingen, Germany"
                    ]
                },
                {
                    "name": "Lev Vidmar",
                    "affiliations": [
                        "Department of Theoretical Physics, J. Stefan Institute, SI-1000 Ljubljana, Slovenia",
                        "Department of Physics, Faculty of Mathematics and Physics, University of Ljubljana, SI-1000 Ljubljana, Slovenia"
                    ]
                }
            ]
        },
        {
            "doi": "10.1103/physrevd.103.029901",
            "result": [
                {
                    "name": "Josipa Majstorović",
                    "affiliations": []
                },
                {
                    "name": "Séverine Rosat",
                    "affiliations": []
                },
                {
                    "name": "Yves Rogister",
                    "affiliations": []
                }
            ]
        }
    ]
