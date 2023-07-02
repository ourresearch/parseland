import re

from publisher.elements import AuthorAffiliations
from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import is_h_tag


class ElsevierBV(PublisherParser):
    parser_name = "Elsevier BV"

    def is_publisher_specific_parser(self):
        return self.soup.find(
            "script", {"src": "https://cdn.cookielaw.org/scripttemplates/otSDKStub.js"}
        ) and not self.domain_in_canonical_link("papers.ssrn.com")

    def authors_found(self):
        return bool(self.soup.findAll("li", class_="author"))

    def parse_abstract(self):

        if abs_header := self.soup.find(lambda tag: is_h_tag(tag) and tag.text.lower().strip() == 'abstract'):
            if abs_tag := abs_header.find_next_sibling('div', class_='section-paragraph'):
                return abs_tag.text

        abs_text = ''
        for i, tag in enumerate(self.soup.select('div[class*=article__sections] div.section-paragraph')):
            if tag.figure:
                tag.figure.decompose()
            if i != 0:
                abs_text += '\n'
            prev_sibling = tag.find_previous_sibling()
            if prev_sibling and is_h_tag(prev_sibling) and 'funding' in prev_sibling.text.lower():
                break
            abs_text += tag.text
            if prev_sibling and is_h_tag(prev_sibling) and 'conclusion' in prev_sibling.text.lower():
                break

        return abs_text

    def parse(self):
        author_results = []
        author_soup = self.soup.findAll("li", class_="author")
        for author in author_soup:
            name_soup = author.find("a", class_="loa__item__name")
            if name_soup:
                name = name_soup.text
            else:
                continue
            is_corresponding = False
            if correspondence := author.find(
                "span", class_="article-header__info__group__label"):
                if correspondence.text.lower().strip() == 'correspondence':
                    is_corresponding = True
            if author.select_one('.icon-gizmo-person'):
                is_corresponding = True
            elif author.select_one('.article-header__info__email'):
                is_corresponding = True

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
                AuthorAffiliations(
                    name=name.strip(),
                    affiliations=affiliations,
                    is_corresponding=is_corresponding,
                )
            )

        return {"authors": author_results,
                "abstract": self.parse_abstract() or self.parse_abstract_meta_tags(),}

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
                        "is_corresponding": False,
                    },
                    {
                        "name": "Gabriela Velazquez, MD",
                        "affiliations": [
                            "Department of Vascular and Endovascular Surgery, Wake Forest School of Medicine, Wake Forest, NC"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Julie Freischlag, MD",
                        "affiliations": [
                            "Department of Vascular and Endovascular Surgery, Wake Forest School of Medicine, Wake Forest, NC"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Melina R. Kibbe, MD",
                        "affiliations": [
                            "Department of Surgery, University of North Carolina at Chapel Hill, Chapel Hill, NC",
                            "Department of Biomedical Engineering, University of North Carolina at Chapel Hill, Chapel Hill, NC",
                        ],
                        "is_corresponding": True,
                    },
                ],
                "abstract": "<h2>Abstract</h2><p>Publication bias has been shown to exist in research across medical and surgical specialties. Bias can occur at any stage of the publication process and can be related to race, ethnicity, age, religion, sex, gender, or sexual orientation. Although some improvements have been made toward addressing this issue, bias still spans the publication process from authors and peer reviewers, to editorial board members and editors, with poor inclusion of women and underrepresented minorities throughout. The result of bias remaining unchecked is the publication of research that leaves out certain groups, is not applicable to all people, and can result in harm to some populations. We have highlighted the current landscape of publication bias and strived to demonstrate the importance of addressing it. We have also provided solutions for reducing bias at multiple stages throughout the publication process. Increasing diversity, equity, and inclusion throughout all aspects of the publication process, requiring diversity, equity, and inclusion statements in reports, and providing specific education and guidelines will ensure the identification and eradication of publication bias. By following these measures, we hope that publication bias will be eliminated, which will reduce further harm to certain populations and promote better, more effective research pertinent to all people.</p>",
            },
        },
    ]
