from repository.parsers.parser import RepositoryParser


class OSTI(RepositoryParser):
    parser_name = "OSTI"

    def is_correct_parser(self):
        return self.domain_in_canonical_link(
            "osti.gov/pages/biblio/"
        ) or "osti.gov" in self.soup.find("body").get("data-baseurl", "")

    def authors_found(self):
        return True

    def parse(self):
        authors = self.parse_meta_tags()
        for author in authors:
            if len(author["affiliations"]) == 1:
                author["affiliations"] = [
                    aff.strip() for aff in author["affiliations"][0].split(";")
                ]

        genre = None

        if dts := self.soup.find_all("dt"):
            for dt in dts:
                if dt.text and "Resource Type:" in dt.text:
                    if resource_type := dt.find_next_sibling("dd"):
                        genre = resource_type.text

        published_date = None
        if date_tag := self.soup.find("time", {"itemprop": "datePublished"}):
            published_date = date_tag.get("datetime")

        return {"authors": authors, "genre": genre, "published_date": published_date}

    test_cases = [
        {
            "page-id": "C8epNZ7hR2dA5jJkXSo8",  # https://www.osti.gov/biblio/1818766
            "result": {
                "authors": [
                    {
                        "name": "Park, Changwon",
                        "affiliations": [
                            "Oak Ridge National Lab. (ORNL), Oak Ridge, TN (United States). Center for Nanophase Materials Sciences (CNMS)",
                            "Univ. of Tennessee, Knoxville, TN (United States)",
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Kim, Sung Wng",
                        "affiliations": [
                            "Sungkyunkwan Univ., Cheoncheon (South Korea)",
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Yoon, Mina",
                        "affiliations": [
                            "Oak Ridge National Lab. (ORNL), Oak Ridge, TN (United States). Center for Nanophase Materials Sciences (CNMS)",
                            "Univ. of Tennessee, Knoxville, TN (United States)",
                        ],
                        "is_corresponding": False,
                    },
                ],
                "genre": "Journal Article: Accepted Manuscript",
                "published_date": "Mon Jan 08 00:00:00 EST 2018",
            },
        },
    ]
