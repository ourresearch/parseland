import re

from publisher.parsers.parser import PublisherParser


class Biorxiv(PublisherParser):
    parser_name = "bioRxiv"

    def is_correct_parser(self):
        return self.domain_in_meta_og_url("biorxiv.org")

    def authors_found(self):
        return self.soup.find_all('meta', attrs={'name': ['citation_author']})

    def parse(self):
        authors = self.get_authors()
        return authors

    def get_authors(self):
        results = []

        authors_and_institutions = self.soup.find_all(
            'meta', attrs={'name': ['citation_author', 'citation_author_institution']}
        )

        author = None
        affiliations = []
        for element in authors_and_institutions:
            if element.attrs.get('name') == 'citation_author_institution':
                if affiliation := element.attrs.get('content', None):
                    affiliations.append(affiliation)

            if element.attrs.get('name') == 'citation_author':
                if author is not None:
                    results.append({'name': author, 'affiliations': affiliations})

                author = element.attrs.get('content', '')
                affiliations = []

        if author is not None:
            results.append({'name': author, 'affiliations': affiliations})

        return results

    test_cases = [
        {
            "doi": "10.1101/2021.10.05.463052",
            "result": [
                {
                    "name": "Tess E. Brewer",
                    "affiliations": [
                        "Institute of Evolutionary Biology and Environmental Studies, University of Zurich",
                        "Swiss Institute of Bioinformatics"
                    ],
                },
                {
                    "name": "Andreas Wagner",
                    "affiliations": [
                        "Institute of Evolutionary Biology and Environmental Studies, University of Zurich",
                        "Swiss Institute of Bioinformatics",
                        "Santa Fe Institute",
                        "Stellenbosch Institute for Advanced Study (STIAS), Wallenberg Research Centre at Stellenbosch University"
                    ],
                },
            ],
        },
    ]
