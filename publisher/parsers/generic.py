from publisher.parsers.parser import PublisherParser


class GenericPublisherParser(PublisherParser):
    parser_name = "generic_publisher_parser"

    def is_publisher_specific_parser(self):
        return False

    def authors_found(self):
        return self.soup.find("meta", {"name": "citation_author_institution"})

    def parse(self):
        return self.parse_meta_tags()

    test_cases = [
        {
            "doi": "10.1158/1538-7445.sabcs18-4608",
            "result": [
                {
                    "name": "Shanshan Deng",
                    "affiliations": [
                        "University of Tennessee Health Science Center, Memphis, TN."
                    ]
                },
                {
                    "name": "Hao Chen",
                    "affiliations": [
                        "University of Tennessee Health Science Center, Memphis, TN."
                    ]
                },
                {
                    "name": "Raisa Krutilina",
                    "affiliations": [
                        "University of Tennessee Health Science Center, Memphis, TN."
                    ]
                },
                {
                    "name": "Najah G. Albadari",
                    "affiliations": [
                        "University of Tennessee Health Science Center, Memphis, TN."
                    ]
                },
                {
                    "name": "Tiffany N. Seagroves",
                    "affiliations": [
                        "University of Tennessee Health Science Center, Memphis, TN."
                    ]
                },
                {
                    "name": "Duane D. Miller",
                    "affiliations": [
                        "University of Tennessee Health Science Center, Memphis, TN."
                    ]
                },
                {
                    "name": "Wei Li",
                    "affiliations": [
                        "University of Tennessee Health Science Center, Memphis, TN."
                    ]
                },
            ],
        },
    ]
