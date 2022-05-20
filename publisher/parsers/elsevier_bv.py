from publisher.elements import AuthorAffiliations
from publisher.parsers.parser import PublisherParser


class ElsevierBV(PublisherParser):
    parser_name = "Elsevier BV"

    def is_publisher_specific_parser(self):
        return self.soup.find(
            "script", {"src": "https://cdn.cookielaw.org/scripttemplates/otSDKStub.js"}
        ) and not self.domain_in_canonical_link("papers.ssrn.com")

    def authors_found(self):
        return self.soup.findAll("li", class_="author")

    def parse(self):
        author_results = []
        author_soup = self.soup.findAll("li", class_="author")
        for author in author_soup:
            name_soup = author.find("a", class_="loa__item__name")
            if name_soup:
                name = name_soup.text
            else:
                continue
            affiliations = []
            # method 1
            info_groups = author.findAll("div", class_="article-header__info__group")
            for group in info_groups:
                header = group.find("span", class_="article-header__info__group__label")
                for sup in group.find_all("sup"):
                    sup.unwrap()  # remove sup tags
                    group.smooth()  # join navigable strings
                if header.text == "Affiliations":
                    affiliation_soup = group.find(
                        "div", class_="article-header__info__group__body"
                    )

                    if affiliation_soup:
                        for aff in affiliation_soup.stripped_strings:
                            affiliations.append(aff.strip())

            # method 2
            affiliation_soup = author.find(
                "div", class_="article-header__info__group__body"
            )
            if affiliation_soup and not info_groups:
                for aff in affiliation_soup.stripped_strings:
                    affiliations.append(aff.strip())
            author_results.append(
                AuthorAffiliations(name=name.strip(), affiliations=affiliations)
            )
        return {"authors": author_results, "abstract": self.parse_abstract_meta_tags()}

    test_cases = [
        {
            "doi": "10.1016/j.jvs.2021.03.049",
            "result": {
                "authors": [
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
                "abstract": "Publication bias has been shown to exist in research across medical and surgical specialties.\nBias can occur at any stage of the publication process and can be related to race,\nethnicity, age, religion, sex, gender, or sexual orientation. Although some improvements\nhave been made toward addressing this issue, bias still spans the publication process\nfrom authors and peer reviewers, to editorial board members and editors, with poor\ninclusion of women and underrepresented minorities throughout. The result of bias\nremaining unchecked is the publication of research that leaves out certain groups,\nis not applicable to all people, and can result in harm to some populations.",
            },
        },
    ]
