import re

from publisher.parsers.parser import PublisherParser
from publisher.elements import Author, Affiliation
from publisher.parsers.utils import name_in_text, split_name


class Lippincott(PublisherParser):
    parser_name = "lippincott"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url(
            "journals.lww.com") or bool(self.soup.find(id="ejp-article-authors")) or self.substr_in_citation_publisher('American Society of Anesthesiologists')

    def authors_found(self):
        return self.soup.find(id="ejp-article-authors") or self.soup.select('.al-author-name')

    def parse(self):
        if bool(self.soup.select('.al-author-name')):
            authors_affiliations = self.get_authors_2()
        else:
            authors = self.get_authors()
            affiliations = self.get_affiliations()
            authors_affiliations = self.merge_authors_affiliations(authors,
                                                                   affiliations)
        abstract = None
        if abs_wrap := self.soup.select_one(
                'section#abstractWrap'):
            if len(abs_wrap.text) > 100:
                abstract = abs_wrap.text.strip()
        elif abstract_tag := self.soup.select_one('section#ArticleBody'):
            abstract = abstract_tag.text.strip()
        abstract = re.sub('^abstract', '', abstract,
                          flags=re.IGNORECASE).strip() if abstract else None
        return {"authors": authors_affiliations, "abstract": abstract}

    def get_authors_2(self):
        author_names = [tag.text for tag in
                        self.soup.select('.al-author-name a.linked-name')]
        affiliation_tag = self.soup.select_one('.article-footnote')
        if email_tag := affiliation_tag.find('a'):
            email_tag.decompose()
        aff = affiliation_tag.text.strip()
        authors = []
        corr_author_email = (self.soup.select_one('.article-footnote a[href*=mailto]') or self.soup.select_one('.info-author-correspondence a[href*=mailto]')).get('href')
        for name in author_names:
            name_split = [item for item in split_name(name) if '.' not in item]
            authors.append(
                {'name': name, 'affiliations': [aff], 'is_corresponding': name_in_text(name_split[-1].lower(), corr_author_email.lower())})
        return authors

    def get_authors(self):
        authors = []
        author_section = self.soup.find(id="ejp-article-authors")
        if not author_section:
            return authors
        author_soup = author_section.findAll("sup")

        # authors with ids
        for author in author_soup:
            is_corresponding = None
            # set name
            name = self.clean_name(author.previous_element)
            if ";" in name:
                break

            if '∗' in author.text or '*' in author.text:
                is_corresponding = True

            # set aff_ids
            aff_ids = self.format_ids(author.text)

            if not aff_ids and name.lower().startswith("editor"):
                continue

            authors.append(Author(name=name, aff_ids=aff_ids if aff_ids else [],
                                  is_corresponding=is_corresponding))

        # authors without ids
        if not authors and author_section.p:
            author_names = author_section.find("p")

            parsed_author_names = author_names.text.split(";")
            for name in parsed_author_names:
                name = name.replace("∗", "").strip()
                authors.append(Author(name=name, aff_ids=[]))

        if not [author for author in authors if author.is_corresponding]:
            if corresponding_text_tag := self.soup.find(
                    lambda tag: tag.name == 'p' and 'correspondence' in tag.text.lower()):
                for author in authors:
                    if ',' in author.name:
                        last_name = author.name.split(',')[0]
                        if last_name in corresponding_text_tag.text:
                            author.is_corresponding = True
                    else:
                        if author.name in corresponding_text_tag.text:
                            author.is_corresponding = True
        return authors

    def get_affiliations(self):
        aff_soup = self.soup.find("div",
                                  class_="ejp-article-authors-info-holder")
        if not aff_soup:
            return []

        results = []
        # affiliations with ids
        affiliations = aff_soup.findAll("sup")
        for aff in affiliations:
            if aff.parent.get("id", "").startswith("cor"):
                continue

            aff_id = aff.text
            organization = aff.next_element.next_element
            results.append(
                Affiliation(aff_id=aff_id, organization=organization))

        # affiliation with no ids
        affiliations = aff_soup.findAll("p")
        for aff in affiliations:
            aff_id = None
            if aff_ids := re.findall(r'^(\d+)\.', aff.text):
                aff_id = aff_ids[0]
            organization = re.sub(r'^(\d+)\.', '', aff.text.strip()).strip()
            if 'financial disclosure' not in organization.lower():
                results.append(
                    Affiliation(aff_id=aff_id, organization=organization))

        return results

    @staticmethod
    def clean_name(name):
        if name.startswith(";"):
            name = name[1:]
        name = name.strip()
        return name

    @staticmethod
    def format_ids(ids):
        ids_split = ids.split(",")
        aff_ids = []
        for aff_id in ids_split:
            if aff_id:
                aff_ids.append(aff_id)
        return aff_ids

    test_cases = [
        {
            "doi": "10.1097/LBR.0000000000000778",
            "result": [
                {
                    "name": "Avasarala, Sameer K. MBBS",
                    "affiliations": [
                        "Division of Allergy, Pulmonary, and Critical Care Medicine"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Lentz, Robert J. MD",
                    "affiliations": [
                        "Division of Allergy, Pulmonary, and Critical Care Medicine",
                        "Department of Thoracic Surgery, Vanderbilt University Medical Center",
                        "Department of Veterans Affairs Medical Center, Nashville, TN",
                    ],
                    "is_corresponding": None,
                },
            ],
        },
        {
            "doi": "10.1097/MJT.0000000000001293",
            "result": [
                {
                    "name": "Zhang, Wei-Yun MS",
                    "affiliations": [
                        "Department of Pulmonary and Critical Care Medicine, First Affiliated Hospital of Soochow University Suzhou, China"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Wang, Jia-Jia MM",
                    "affiliations": [
                        "Department of Pulmonary and Critical Care Medicine, First Affiliated Hospital of Soochow University Suzhou, China"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Liu, Ying-Ying MS",
                    "affiliations": [
                        "Department of Pulmonary and Critical Care Medicine, First Affiliated Hospital of Soochow University Suzhou, China"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Zeng, Da-Xiong MD",
                    "affiliations": [
                        "Department of Pulmonary and Critical Care Medicine, First Affiliated Hospital of Soochow University Suzhou, China"
                    ],
                    "is_corresponding": None,
                },
            ],
        },
        {
            "doi": "10.2106/jbjs.19.01395",
            "result": [
                {
                    "name": "Castile, Ryan M. BS",
                    "affiliations": [
                        "Departments of Mechanical Engineering & Materials Science (R.M.C., M.J.J., and S.P.L.) and Orthopaedic Surgery (S.P.L. and R.H.B.), Washington University in St. Louis, St. Louis, Missouri"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Jenkins, Matthew J. BS",
                    "affiliations": [
                        "Departments of Mechanical Engineering & Materials Science (R.M.C., M.J.J., and S.P.L.) and Orthopaedic Surgery (S.P.L. and R.H.B.), Washington University in St. Louis, St. Louis, Missouri"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Lake, Spencer P. PhD",
                    "affiliations": [
                        "Departments of Mechanical Engineering & Materials Science (R.M.C., M.J.J., and S.P.L.) and Orthopaedic Surgery (S.P.L. and R.H.B.), Washington University in St. Louis, St. Louis, Missouri"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Brophy, Robert H. MD",
                    "affiliations": [
                        "Departments of Mechanical Engineering & Materials Science (R.M.C., M.J.J., and S.P.L.) and Orthopaedic Surgery (S.P.L. and R.H.B.), Washington University in St. Louis, St. Louis, Missouri"
                    ],
                    "is_corresponding": None,
                },
            ],
        },
    ]
