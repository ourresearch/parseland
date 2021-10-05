from exceptions import UnusualTrafficError
from parser import Parser


class Oxford(Parser):
    parser_name = "oxford university press"

    def is_correct_parser(self):
        if self.soup.find(
            "div", class_="explanation-message"
        ) and "help us confirm that you are not a robot and we will take you to your content" in str(
            self.soup
        ):
            raise UnusualTrafficError(
                f"content blocked within {self.parser_name} parser"
            )
        return self.domain_in_meta_og_url("academic.oup.com")

    def authors_found(self):
        return self.soup.find("div", class_="at-ArticleAuthors")

    def parse(self):
        results = []
        author_soup = self.soup.find("div", class_="at-ArticleAuthors")
        authors = author_soup.findAll("div", class_="info-card-author")
        for author in authors:
            name = author.find("div", class_="info-card-name").text.strip()

            affiliations = []
            affiliation_section = author.find("div", class_="info-card-affilitation")
            if affiliation_section:
                affiliations_soup = affiliation_section.findAll("div", class_="aff")
                for aff in affiliations_soup:
                    affiliations.append(aff.text)

            results.append({"name": name, "affiliations": affiliations})
        return results

    test_cases = [
        {
            "doi": "10.1093/bib/bbab286",
            "result": [
                {
                    "name": "Chun-Chun Wang",
                    "affiliations": [
                        "School of Information and Control Engineering, China University of Mining and Technology"
                    ],
                },
                {
                    "name": "Chen-Di Han",
                    "affiliations": [
                        "School of Information and Control Engineering, China University of Mining and Technology"
                    ],
                },
                {
                    "name": "Qi Zhao",
                    "affiliations": [
                        "School of Computer Science and Software Engineering, University of Science and Technology Liaoning"
                    ],
                },
                {
                    "name": "Xing Chen",
                    "affiliations": ["China University of Mining and Technology"],
                },
            ],
        },
        {
            "doi": "10.1093/jamia/ocab164",
            "result": [
                {
                    "name": "Chi Yuan",
                    "affiliations": [
                        "Department of Biomedical Informatics, Columbia University, New York, New York, USA"
                    ],
                },
                {
                    "name": "Patrick B Ryan",
                    "affiliations": [
                        "Department of Biomedical Informatics, Columbia University, New York, New York, USA",
                        "Observational Health Data Sciences and Informatics, New York, New York, USA",
                        "Epidemiology Analytics, Janssen Research and Development, Titusville, New Jersey, USA",
                    ],
                },
                {
                    "name": "Casey N Ta",
                    "affiliations": [
                        "Department of Biomedical Informatics, Columbia University, New York, New York, USA"
                    ],
                },
                {
                    "name": "Jae Hyun Kim",
                    "affiliations": [
                        "Department of Biomedical Informatics, Columbia University, New York, New York, USA"
                    ],
                },
                {
                    "name": "Ziran Li",
                    "affiliations": [
                        "Department of Biomedical Informatics, Columbia University, New York, New York, USA"
                    ],
                },
                {
                    "name": "Chunhua Weng",
                    "affiliations": [
                        "Department of Biomedical Informatics, Columbia University, New York, New York, USA"
                    ],
                },
            ],
        },
        {
            "doi": "10.1093/arclin/acab062.129",
            "result": [
                {
                    "name": "Julianne Wilson",
                    "affiliations": [],
                },
                {
                    "name": "Amanda R Rabinowitz",
                    "affiliations": [],
                },
                {
                    "name": "Tessa Hart",
                    "affiliations": [],
                },
            ],
        },
    ]
