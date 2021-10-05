from publisher.parser import PublisherParser


class ElsevierBV(PublisherParser):
    parser_name = "Elsevier BV"

    def is_correct_parser(self):
        return self.soup.find(
            "script", {"src": "https://cdn.cookielaw.org/scripttemplates/otSDKStub.js"}
        )

    def authors_found(self):
        return self.soup.findAll("li", class_="author")

    def parse(self):
        results = []
        author_soup = self.soup.findAll("li", class_="author")
        for author in author_soup:
            name = author.find("a", class_="loa__item__name").text
            affiliations = []
            affiliation_soup = author.find(
                "div", class_="article-header__info__group__body"
            )
            for aff in affiliation_soup.stripped_strings:
                affiliations.append(aff.strip())
            results.append({"name": name.strip(), "affiliations": affiliations})
        return results

    test_cases = [
        {
            "doi": "10.1016/j.jvs.2021.03.049",
            "result": [
                {
                    "name": "Jessica Rouan, MD",
                    "affiliations": [
                        "Department of Surgery, University of North Carolina at Chapel Hill, Chapel Hill, NC"
                    ],
                },
                {
                    "name": "Gabriela Velazquez, MD",
                    "affiliations": [
                        "Department of Vascular and Endovascular Surgery, Wake Forest School of Medicine, Wake Forest, NC"
                    ],
                },
                {
                    "name": "Julie Freischlag, MD",
                    "affiliations": [
                        "Department of Vascular and Endovascular Surgery, Wake Forest School of Medicine, Wake Forest, NC"
                    ],
                },
                {
                    "name": "Melina R. Kibbe, MD",
                    "affiliations": [
                        "Department of Surgery, University of North Carolina at Chapel Hill, Chapel Hill, NC",
                        "Department of Biomedical Engineering, University of North Carolina at Chapel Hill, Chapel Hill, NC",
                    ],
                },
            ],
        },
    ]
