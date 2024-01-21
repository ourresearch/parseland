import re
from typing import List

from nameparser import HumanName

from publisher.parsers.parser import PublisherParser
from publisher.elements import Author, Affiliation, AuthorAffiliations
from publisher.parsers.utils import name_in_text, split_name, strip_prefix


class Lippincott(PublisherParser):
    parser_name = "lippincott"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url(
            "journals.lww.com") or bool(self.soup.find(
            id="ejp-article-authors")) or self.substr_in_citation_publisher(
            'American Society of Anesthesiologists')

    def authors_found(self):
        return self.soup.find(id="ejp-article-authors") or self.soup.select(
            '.al-author-name')

    @staticmethod
    def assign_affs_from_name(author_affiliations: List[AuthorAffiliations], affiliations):
        for aff in affiliations:
            matched_name = None
            for author in author_affiliations:
                name_parsed = HumanName(author.name)
                if name_parsed.first in aff.organization and name_parsed.last in aff.organization:
                    author.affiliations.append(aff.organization)
                    matched_name = name_parsed
            if matched_name:
                for author in author_affiliations:
                    name_parsed = HumanName(author.name)
                    if name_parsed.first in aff.organization and name_parsed.last in aff.organization:
                        continue
                    for i, _aff in enumerate(author.affiliations):
                        if aff.organization == _aff:
                            author.affiliations.pop(i)
                            break
        return author_affiliations

    def parse(self):
        if bool(self.soup.select('.al-author-name')):
            authors_affiliations = self.get_authors_2()
        else:
            authors = self.get_authors()
            affiliations = self.get_affiliations()
            authors_affiliations = self.merge_authors_affiliations(authors,
                                                                   affiliations)
            authors_affiliations = self.assign_affs_from_name(authors_affiliations, affiliations)

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

    @classmethod
    def affs_last_name_map(cls, aff_tags):
        d = {}
        fallback_affs = []
        for aff_tag in aff_tags:
            if email_tag := aff_tag.find('a'):
                email_tag.decompose()
            aff_txt = aff_tag.text.strip()
            fallback_affs.append(aff_txt)
            if last_name := re.findall(r'^(\(.*?\))', aff_txt):
                only_aff = aff_txt.replace(last_name[0], '')
                last_name = last_name[0]
                for name in last_name.split(','):
                    name = name.strip('()')
                    if name not in d:
                        d[name] = []
                    d[name].append(only_aff)
        return d, fallback_affs

    def get_authors_2(self):
        author_names = [tag.text for tag in
                        self.soup.select('.al-author-name a.linked-name')]
        affiliation_tags = self.soup.select('.article-footnote')
        affs_map, affs = self.affs_last_name_map(affiliation_tags)
        authors = []
        corr_author_email = ''
        if corr_author_email_tag := self.soup.select_one(
            '.article-footnote a[href*=mailto]') or self.soup.select_one(
            '.info-author-correspondence a[href*=mailto]'):
            corr_author_email = corr_author_email_tag.get('href')
        for name in author_names:
            name_parsed = HumanName(name)
            name_split = [item for item in split_name(name) if '.' not in item]
            authors.append(
                {'name': name, 'affiliations': affs_map.get(name_parsed.last, []) if affs_map else affs,
                 'is_corresponding': name_in_text(name_split[-1].lower(),
                                                  corr_author_email.lower())})
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
            aff_ids = self.parse_aff_ids(author.text, first=False)

            if not aff_ids and name.lower().startswith("editor"):
                continue
            authors.append(Author(name=name, aff_ids=aff_ids,
                                  is_corresponding=is_corresponding))

        def author_already_exists(name):
            for author in authors:
                if author.name.lower() == name.lower():
                    return True
            return False

        # authors without ids
        if author_section.p:
            author_names = author_section.find("p")
            for sup in author_names.find_all('sup'):
                sup.decompose()

            parsed_author_names = author_names.text.split(";")
            for name in parsed_author_names:
                name = name.replace("∗", "").strip()
                if author_already_exists(name):
                    continue
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

    @staticmethod
    def parse_aff_ids(aff_text, first=True):
        if matches := re.findall(r'([^a-zA-Z\d \':,/])|(\d+)', aff_text[:15]):
            matches = [item for sublist in matches for item in sublist if item]
            return matches[0] if first else matches
        return None if first else []

    def get_affiliations(self):
        aff_blacklist_prefixes = ['accepted',
                                  'received',
                                  'presented',
                                  'this',
                                  'revision',
                                  'disclosure',
                                  'reprint',
                                  'supported',
                                  'the authors',
                                  'patients have',
                                  'abbreviations',
                                  'funding']
        aff_blacklist_substr = ['contributed equally']

        def exclude_aff(aff_text):
            for prefix in aff_blacklist_prefixes:
                if aff_text.lower().startswith(prefix):
                    return True
            for substr in aff_blacklist_substr:
                if substr in aff_text.lower():
                    return True
            return False

        def cleanup_aff(aff_text):
            aff_text = aff_text.split(' to:')[-1]
            aff_text = re.split(r'correspondence', aff_text, flags=re.IGNORECASE)[-1]
            aff_text = aff_text.split('From')[-1]
            aff_text = strip_prefix(r'[0-9]+', aff_text)
            return aff_text.strip(' ,:')

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
            organization = cleanup_aff(aff.next_element.next_element)
            results.append(
                Affiliation(aff_id=aff_id, organization=organization))

        # affiliation with no ids
        affiliations = aff_soup.findAll("p")
        if ';' in affiliations[0].text:
            aff_texts = [txt.strip() for txt in affiliations[0].text.split(';')]
            for aff_text in aff_texts:
                aff_id = self.parse_aff_ids(aff_text)
                org = aff_text.split(aff_id)[-1]
                results.append(Affiliation(aff_id=aff_id, organization=org))
            return results

        for aff in affiliations:
            if aff.sup:
                continue
            organization = cleanup_aff(aff.text)
            aff_id = None
            if aff_id := self.parse_aff_ids(aff.text.strip()):
                organization = aff.text.strip().split(aff_id)[-1].strip()
            if 'financial disclosure' in organization.lower():
                continue
            results.append(
                Affiliation(aff_id=aff_id, organization=organization))

        return [result for result in results if not exclude_aff(result.organization)]

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
