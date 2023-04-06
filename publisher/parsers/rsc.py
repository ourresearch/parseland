import re

from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import is_h_tag


class RSC(PublisherParser):
    parser_name = "rsc"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url("pubs.rsc.org")

    def authors_found(self):
        return bool(self.soup.select('.article__author-link'))

    def parse_affiliations(self):
        aff_tags = self.soup.select('.article__author-affiliation')
        affs = {}
        for aff_tag in aff_tags:
            if 'Corresponding authors' in aff_tag.text:
                continue
            sup = aff_tag.find('sup')
            sup_letter = sup.text.strip('\n\r ')
            sup.decompose()
            affs[sup_letter] = next(aff_tag.find(
                lambda tag: bool(tag.text.strip())).children).text.strip(
                '\n\r ')
        return affs

    def parse_authors(self):
        affs = self.parse_affiliations()
        author_tags = self.soup.select('.article__author-link')
        authors = []
        for author_tag in author_tags:
            name = re.sub('[\n\r]', ' ', author_tag.find('a').text)
            name = re.sub(' +', ' ', name)
            author = {'name': name, 'affiliations': [],
                      'is_corresponding': '*' in author_tag.text}
            sups = author_tag.find_all('sup')
            sups = [sup.text.split(',') for sup in sups]
            sups = [item for sublist in sups for item in sublist]
            for letter in sups:
                author['affiliations'].append(affs[letter])
            authors.append(author)
        return authors

    def parse_abstract(self):
        if abs_tag := self.soup.select_one('.article-abstract__heading + div p'):
            return abs_tag.text

    def parse(self):
        return {'authors': self.parse_authors(), 'abstract': self.parse_abstract()}

    test_cases = [
        {
            "doi": "10.1039/d0cc04440g",
            "result": [
                {
                    "name": "Daqian Xu",
                    "affiliations": [
                        "State Key Laboratory for Oxo Synthesis and Selective Oxidation Department, Center for Excellence in Molecular Synthesis, Suzhou Research Institute of Lanzhou Institute of Chemical Physics (LICP), Chinese Academy of Sciences, Lanzhou 730000, China",
                        "School of Chemistry and Chemical Engineering, Lanzhou City University, Lanzhou 730070, China",
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Qiangsheng Sun",
                    "affiliations": [
                        "State Key Laboratory for Oxo Synthesis and Selective Oxidation Department, Center for Excellence in Molecular Synthesis, Suzhou Research Institute of Lanzhou Institute of Chemical Physics (LICP), Chinese Academy of Sciences, Lanzhou 730000, China"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Jin Lin",
                    "affiliations": [
                        "State Key Laboratory for Oxo Synthesis and Selective Oxidation Department, Center for Excellence in Molecular Synthesis, Suzhou Research Institute of Lanzhou Institute of Chemical Physics (LICP), Chinese Academy of Sciences, Lanzhou 730000, China"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Wei Sun",
                    "affiliations": [
                        "State Key Laboratory for Oxo Synthesis and Selective Oxidation Department, Center for Excellence in Molecular Synthesis, Suzhou Research Institute of Lanzhou Institute of Chemical Physics (LICP), Chinese Academy of Sciences, Lanzhou 730000, China"
                    ],
                    "is_corresponding": None,
                },
            ],
        },
        {
            "doi": "10.1039/d1bm00157d",
            "result": [
                {
                    "name": "Yin-Chu Ma",
                    "affiliations": [
                        "Zhuhai Interventional Medical Center, Zhuhai Precision Medical Center, Zhuhai People's Hospital, Zhuhai Hospital Affiliated with Jinan University, Zhuhai 519000, China"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Xin-Feng Tang",
                    "affiliations": [
                        "School of Life Sciences, University of Science and Technology of China, Hefei 230027, China"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "You-Cui Xu",
                    "affiliations": [
                        "School of Life Sciences, University of Science and Technology of China, Hefei 230027, China"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Wei Jiang",
                    "affiliations": [
                        "Zhuhai Interventional Medical Center, Zhuhai Precision Medical Center, Zhuhai People's Hospital, Zhuhai Hospital Affiliated with Jinan University, Zhuhai 519000, China"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Yong-Jie Xin",
                    "affiliations": [
                        "Zhuhai Interventional Medical Center, Zhuhai Precision Medical Center, Zhuhai People's Hospital, Zhuhai Hospital Affiliated with Jinan University, Zhuhai 519000, China"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Wei Zhao",
                    "affiliations": [
                        "Zhuhai Interventional Medical Center, Zhuhai Precision Medical Center, Zhuhai People's Hospital, Zhuhai Hospital Affiliated with Jinan University, Zhuhai 519000, China"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Xu He",
                    "affiliations": [
                        "Zhuhai Interventional Medical Center, Zhuhai Precision Medical Center, Zhuhai People's Hospital, Zhuhai Hospital Affiliated with Jinan University, Zhuhai 519000, China"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Li-Gong Lu",
                    "affiliations": [
                        "Zhuhai Interventional Medical Center, Zhuhai Precision Medical Center, Zhuhai People's Hospital, Zhuhai Hospital Affiliated with Jinan University, Zhuhai 519000, China"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Mei-Xiao Zhan",
                    "affiliations": [
                        "Zhuhai Interventional Medical Center, Zhuhai Precision Medical Center, Zhuhai People's Hospital, Zhuhai Hospital Affiliated with Jinan University, Zhuhai 519000, China"
                    ],
                    "is_corresponding": None,
                },
            ],
        },
    ]
