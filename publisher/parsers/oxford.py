import json
import re

from exceptions import UnusualTrafficError
from publisher.elements import AuthorAffiliations
from publisher.parsers.parser import PublisherParser


class Oxford(PublisherParser):
    parser_name = "oxford university press"

    def is_publisher_specific_parser(self):
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
        if author_soup := self.soup.find("div", class_="at-ArticleAuthors"):
            authors = author_soup.findAll("div", class_="info-card-author")

            for author in authors:
                name = author.find("div", class_="info-card-name").text.strip()

                is_corresponding = (
                    True
                    if author.find("div", class_="info-author-correspondence")
                    else False
                )

                affiliations = []
                affiliation_section = author.find("div",
                                                  class_="info-card-affilitation")
                if affiliation_section:
                    affiliations_soup = affiliation_section.findAll("div",
                                                                    class_="aff")
                    for aff in affiliations_soup:
                        aff_cleaned = re.sub('^\d+', '', aff.text)
                        affiliations.append(aff_cleaned)

                results.append(
                    AuthorAffiliations(
                        name=name,
                        affiliations=affiliations,
                        is_corresponding=is_corresponding,
                    )
                )
        abstract = '\n'.join([tag.text for tag in self.soup.select('section.abstract p')])
        return {"authors": results,
                "abstract": abstract,}


    test_cases = [
        {
            "doi": "10.1093/bib/bbab286",
            "result": [
                {
                    "name": "Chun-Chun Wang",
                    "affiliations": [
                        "School of Information and Control Engineering, China University of Mining and Technology"
                    ],
                    "is_corresponding": False,
                },
                {
                    "name": "Chen-Di Han",
                    "affiliations": [
                        "School of Information and Control Engineering, China University of Mining and Technology"
                    ],
                    "is_corresponding": False,
                },
                {
                    "name": "Qi Zhao",
                    "affiliations": [
                        "School of Computer Science and Software Engineering, University of Science and Technology Liaoning"
                    ],
                    "is_corresponding": True,
                },
                {
                    "name": "Xing Chen",
                    "affiliations": [
                        "China University of Mining and Technology"],
                    "is_corresponding": True,
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
                    "is_corresponding": False,
                },
                {
                    "name": "Patrick B Ryan",
                    "affiliations": [
                        "Department of Biomedical Informatics, Columbia University, New York, New York, USA",
                        "Observational Health Data Sciences and Informatics, New York, New York, USA",
                        "Epidemiology Analytics, Janssen Research and Development, Titusville, New Jersey, USA",
                    ],
                    "is_corresponding": False,
                },
                {
                    "name": "Casey N Ta",
                    "affiliations": [
                        "Department of Biomedical Informatics, Columbia University, New York, New York, USA"
                    ],
                    "is_corresponding": False,
                },
                {
                    "name": "Jae Hyun Kim",
                    "affiliations": [
                        "Department of Biomedical Informatics, Columbia University, New York, New York, USA"
                    ],
                    "is_corresponding": False,
                },
                {
                    "name": "Ziran Li",
                    "affiliations": [
                        "Department of Biomedical Informatics, Columbia University, New York, New York, USA"
                    ],
                    "is_corresponding": False,
                },
                {
                    "name": "Chunhua Weng",
                    "affiliations": [
                        "Department of Biomedical Informatics, Columbia University, New York, New York, USA"
                    ],
                    "is_corresponding": True,
                },
            ],
        },
        {
            "doi": "10.1093/arclin/acab062.129",
            "result": [
                {
                    "name": "Julianne Wilson",
                    "affiliations": [],
                    "is_corresponding": None,
                },
                {
                    "name": "Amanda R Rabinowitz",
                    "affiliations": [],
                    "is_corresponding": None,
                },
                {
                    "name": "Tessa Hart",
                    "affiliations": [],
                    "is_corresponding": None,
                },
            ],
        },
    ]
