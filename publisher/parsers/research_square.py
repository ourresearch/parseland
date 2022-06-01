from publisher.elements import AuthorAffiliations
from publisher.parsers.parser import PublisherParser


class ResearchSquare(PublisherParser):
    parser_name = "research square"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url("researchsquare.com")

    def authors_found(self):
        return self.soup.findAll("div", class_="author")

    def parse(self):
        results = []
        author_section = self.soup.find("div", class_="authors-expanded")
        authors = author_section.findAll("div", class_="author")
        for author in authors:
            name = author.find("h5").text.strip()

            is_corresponding = (
                True if "corresponding author" in author.text.lower() else False
            )

            affiliations = []
            affiliations_soup = author.findAll("h6")
            for aff in affiliations_soup:
                if "corresponding" in aff.text.lower():
                    break
                affiliations.append(aff.text)

            results.append(
                AuthorAffiliations(
                    name=name,
                    affiliations=affiliations,
                    is_corresponding_author=is_corresponding,
                )
            )
        return results

    test_cases = [
        {
            "doi": "10.21203/rs.3.rs-725749/v1",
            "result": [
                {
                    "name": "Bo WenBo",
                    "affiliations": [
                        "College of Electrical and Mechanical Engineering"
                    ],
                    "is_corresponding_author": True,
                },
                {
                    "name": "Chao-Qing Dai",
                    "affiliations": [
                        "College of Optical,Mechanical and Electrical Engineering,Zhejiang A&F University"
                    ],
                    "is_corresponding_author": False,
                },
                {
                    "name": "Yue-Yue Wang",
                    "affiliations": [
                        "College of Optical,Mechanical and Engineering,Zhejiang A&F University,Lin'an 311300,China"
                    ],
                    "is_corresponding_author": False,
                },
                {
                    "name": "Peng-Fei Li",
                    "affiliations": [
                        "Department of Physics, Taiyuan Normal University"
                    ],
                    "is_corresponding_author": False,
                },
            ],
        },
    ]
