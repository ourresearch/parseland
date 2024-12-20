import json
import re
from collections import defaultdict
from unicodedata import normalize

from publisher.elements import Author, Affiliation, AuthorAffiliations
from publisher.parsers.parser import PublisherParser


class Springer(PublisherParser):
    parser_name = "springer"

    def is_publisher_specific_parser(self):
        if (
                self.domain_in_canonical_link("link.springer.com")
                or self.domain_in_canonical_link("springeropen.com")
                or self.domain_in_meta_og_url("nature.com")
                or self.domain_in_meta_og_url("biomedcentral.com")
        ):
            return True

    def authors_found(self):
        return True

    @staticmethod
    def _try_find_abstract_in_metadatas(metadatas):
        for md in metadatas:
            if 'description' in md:
                return md['description']
        return None

    def parse_authors_method_3(self):
        author_tags = self.soup.select('li.c-article-authors-listing__item')
        authors = []
        for tag in author_tags:
            name_tag = tag.select_one('span[class*=search-name]')
            name = name_tag.text.strip()
            is_corr = bool(name_tag.select_one('a[id*=corresp]'))
            affs = [aff_tag.text.strip() for aff_tag in
                    tag.select('ol[class*=affiliation__list] li p')]
            authors.append({
                'name': name,
                'affiliations': affs,
                'is_corresponding': is_corr,
            })
        return authors

    @classmethod
    def _split(cls, input_string, split_char=',', min_length=5):
        substrings = []
        current_substr = ''
        for char in input_string:
            current_substr += char
            if char == split_char:
                if len(current_substr.strip()) >= min_length or not substrings:
                    substrings.append(current_substr)
                elif substrings:
                    substrings[-1] += current_substr
                current_substr = ''
        if current_substr:
            if len(current_substr.strip()) >= min_length:
                substrings.append(current_substr)
            elif substrings:
                substrings[-1] += current_substr

        return substrings

    def parse_authors_method_2(self):
        author_tags = self.soup.select(
            'ol.c-article-author-affiliation__list li[id*=A]'
        )
        authors = {}

        for author_tag in author_tags:
            aff_tag = author_tag.select_one('p[class*=affiliation__address]')
            aff_text = aff_tag.text.strip().split('E-mail')[0]
            authors_tag = author_tag.select_one('p[class*=authors-list]')
            author_names = list(set([name.strip(' ,') for name in
                                     self._split(authors_tag.text.replace('&',
                                                                          ',').strip())
                                     if
                                     '(' not in name]))

            for name in author_names:
                if name in authors:
                    if aff_text not in authors[name]['affiliations']:
                        authors[name]['affiliations'].append(aff_text)
                else:
                    authors[name] = {
                        'name': name,
                        'affiliations': [aff_text],
                        'is_corresponding': None
                    }

        return list(authors.values())

    def parse(self):
        article_metadatas = self.parse_article_metadatas()
        abstract = self._try_find_abstract_in_metadatas(article_metadatas)
        authors_affiliations = None
        if self.soup.select('li.c-article-authors-listing__item'):
            authors_affiliations = self.parse_authors_method_3()

        if not authors_affiliations:
            authors = self.get_authors()
            if authors:
                affiliations = self.get_affiliations()
                authors_affiliations = self.merge_authors_affiliations(
                    authors, affiliations
                )

        if not authors_affiliations:
            authors_affiliations = self.parse_authors_method_2()

        if not authors_affiliations:
            authors_affiliations = self.parse_author_meta_tags()
            for author in authors_affiliations:
                author['affiliations'] = [aff.split('Fax')[0] for aff in author['affiliations']]

        if not authors_affiliations:
            authors = self.get_authors(try_editors=True)
            if authors:
                affiliations = self.get_affiliations(try_editors=True)
                authors_affiliations = self.merge_authors_affiliations(
                    authors, affiliations
                )

        if not authors_affiliations:
            authors_affiliations = self.parse_ld_json(article_metadatas)

        return {"authors": authors_affiliations,
                "abstract": abstract or self.parse_abstract(), }

    def parse_abstract(self):
        if abstract_soup := self.soup.find("section", class_="Abstract"):
            if abstract_heading := abstract_soup.find(
                    class_="Heading", string="Abstract"
            ):
                abstract_heading.decompose()

            for citation in abstract_soup.find_all("span",
                                                   class_="CitationRef"):
                citation.decompose()

            return abstract_soup.text.strip()

        elif abstract_soup := self.soup.select_one(
                'section[data-title=Abstract] div[class*=c-article-section] p'):
            for abstract_heading in abstract_soup.find_all(
                    re.compile("^h[1-6]$"), string="Abstract"
            ):
                abstract_heading.decompose()

            return abstract_soup.text.strip()

        return None

    def parse_article_metadatas(self):
        metadatas = []
        for ld_json in self.soup.find_all("script",
                                          {"type": "application/ld+json"}):
            article_metadata = json.loads(ld_json.text)
            if 'mainEntity' in article_metadata:
                article_metadata = article_metadata['mainEntity']
            metadatas.append(article_metadata)
        return metadatas

    @staticmethod
    def parse_ld_json(metadatas):
        authors = []

        for article_metadata in metadatas:
            for author in article_metadata.get("author", []):
                if author.get("@type") == "Person":
                    name = author.get("name")
                    affiliations = []

                    json_affiliations = author.get("affiliation")
                    is_corresponding = True if author.get("email") else False
                    if isinstance(json_affiliations, str):
                        affiliations = [json_affiliations]
                    elif (
                            isinstance(json_affiliations, dict)
                            and "name" in json_affiliations
                    ):
                        affiliations = [
                            json_affiliations.get('address', {}).get('name') or
                            json_affiliations['name']]
                    elif isinstance(json_affiliations, list):
                        for json_affiliation in json_affiliations:
                            if (
                                    isinstance(json_affiliation, str)
                                    and json_affiliation not in affiliations
                            ):
                                affiliations.append(json_affiliation)
                            elif (
                                    isinstance(json_affiliation, dict)
                                    and "name" in json_affiliation
                            ):
                                if json_affiliation["name"] not in affiliations:
                                    affiliations.append(
                                        json_affiliation.get('address', {}).get(
                                            'name') or json_affiliation['name'])

                    authors.append(
                        AuthorAffiliations(
                            name=name,
                            affiliations=affiliations,
                            is_corresponding=is_corresponding,
                        )
                    )

        return authors

    def get_authors(self, try_editors=False):
        authors = []

        section_id = (
            "editorsandaffiliations" if try_editors else "authorsandaffiliations"
        )
        section = self.soup.find(id=section_id)

        if not section:
            return None

        author_itemprop = "editor" if try_editors else "author"
        author_soup = section.findAll("li", {"itemprop": author_itemprop})

        for author in author_soup:
            ref_ids = []
            references = author.find("ul", {"data-role": "AuthorsIndexes"})
            if references:
                for reference in references:
                    ref_ids.append(int(reference.text))
            name = normalize("NFKD", author.span.text)
            authors.append(Author(name=name, aff_ids=ref_ids))

        return authors

    def get_affiliations(self, try_editors=False):
        affiliations = []

        section_id = (
            "editorsandaffiliations" if try_editors else "authorsandaffiliations"
        )
        section = self.soup.find(id=section_id)

        aff_soup = section.findAll("li", class_="affiliation")
        for aff in aff_soup:
            aff_id = int(aff["data-affiliation-highlight"][-1])

            # get affiliations
            spans = aff.findAll("span")
            affiliation_data = []
            for span in spans:
                if span.has_attr("itemprop") and span["itemprop"] != "address":
                    affiliation_data.append(span.text)

            affiliation = ", ".join(affiliation_data)

            affiliations.append(
                Affiliation(aff_id=aff_id, organization=affiliation))

        return affiliations

    test_cases = [
        {
            "doi": "10.1007/978-0-387-39343-8_21",
            "result": {
                "authors": [
                    {
                        "name": "Pascal Boileau MD",
                        "affiliations": [
                            "Professor,        Orthopaedic Surgery and Sports Traumatology, University of Nice-Sophia Antipolis, L’Archet 2 Hospital, Nice, 06200, France"
                        ],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Christopher R. Chuinard MD, MPH",
                        "affiliations": [],
                        "is_corresponding": None,
                    },
                ],
                "abstract": "The tendon of the long head of the biceps (LHB) is a frequent source of pain in the shoulder and is subject to numerous pathologies.1\u20133 Treatment of pathology of the LHB involves resection of the intra-articular portion with a simple tenotomy or a tenodesis. Tenodesis of the LHB, with or without a rotator cuff repair, is an intervention known to reliably and effectively reduce the pain.4,5 We were not satisfied with the results obtained with other techniques. Because of our experience with the use of interference screw for surgery of the anterior cruciate ligament (ACL), we developed a technique for tenodesis of the biceps utilizing a bioresorbable interference screw.6,7\nKeywordsAnterior Cruciate LigamentRotator CuffBone TunnelInterference ScrewRotator Cuff RepairThese keywords were added by machine and not by the authors. This process is experimental and the keywords may be updated as the learning algorithm improves.",
            },
        },
        {
            "doi": "10.1007/0-306-48581-8_22",
            "result": {
                "authors": [
                    {
                        "name": "L. Michael Ascher",
                        "affiliations": [
                            "Department of Psychology, Philadelphia College of Osteopathic Medicine, Philadelphia"
                        ],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Christina Esposito",
                        "affiliations": [
                            "Department of Psychology, Philadelphia College of Osteopathic Medicine, Philadelphia"
                        ],
                        "is_corresponding": None,
                    },
                ],
                "abstract": None,
            },
        },
        {
            "doi": "10.1007/0-306-48688-1_15",
            "result": {
                "authors": [
                    {
                        "name": "Ping Zhang",
                        "affiliations": [
                            "Department of Medicine, Section of Pulmonary and Critical Care Medicine, and Alcohol Research Center, Louisiana State University Health Sciences Center, New Orleans, LA, 70112"
                        ],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Gregory J. Bagby",
                        "affiliations": [
                            "Department of Medicine, Section of Pulmonary and Critical Care Medicine, Department of Physiology, and Alcohol Research Center, Louisiana State University Health Sciences Center, New Orleans, LA, 70112"
                        ],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Jay K. Kolls",
                        "affiliations": [
                            "Department of Medicine, Section of Pulmonary and Critical Care Medicine, Alcohol Research Center and Gene Therapy Programs, Louisiana State University Health Sciences Center, New Orleans, LA, 70112"
                        ],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Lee J. Quinton",
                        "affiliations": [
                            "Department of Physiology and Alcohol Research Center, Louisiana State University Health Sciences Center, New Orleans, LA, 70112"
                        ],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Steve Nelson",
                        "affiliations": [
                            "Department of Medicine, Section of Pulmonary and Critical Care Medicine, Department of Physiology, and Alcohol Research Center, Louisiana State University Health Sciences Center, New Orleans, LA, 70112"
                        ],
                        "is_corresponding": None,
                    },
                ],
                "abstract": None,
            },
        },
        {
            "doi": "10.1007/0-306-48581-8_7",
            "result": {
                "authors": [
                    {
                        "name": "Christine Bowman Edmondson",
                        "affiliations": [],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Daniel Joseph Cahill",
                        "affiliations": [
                            "Department of Psychology, California State University, Fresno, Fresno, California"
                        ],
                        "is_corresponding": None,
                    },
                ],
                "abstract": None,
            },
        },
        {
            "doi": "10.3758/s13414-014-0792-2",
            "result": {
                "authors": [
                    {
                        "name": "Scharenborg, Odette",
                        "affiliations": ["Radboud University Nijmegen"],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Weber, Andrea",
                        "affiliations": [
                            "Max Planck Institute for Psycholinguistics",
                            "Radboud University Nijmegen",
                        ],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Janse, Esther",
                        "affiliations": [
                            "Radboud University Nijmegen",
                            "Max Planck Institute for Psycholinguistics",
                        ],
                        "is_corresponding": None,
                    },
                ],
                "abstract": "This study investigates two variables that may modify lexically guided perceptual learning: individual hearing sensitivity and attentional abilities. Older Dutch listeners (aged 60+ years, varying from good hearing to mild-to-moderate high-frequency hearing loss) were tested on a lexically guided perceptual learning task using the contrast [f]-[s]. This contrast mainly differentiates between the two consonants in the higher frequencies, and thus is supposedly challenging for listeners with hearing loss. The analyses showed that older listeners generally engage in lexically guided perceptual learning. Hearing loss and selective attention did not modify perceptual learning in our participant sample, while attention-switching control did: listeners with poorer attention-switching control showed a stronger perceptual learning effect. We postulate that listeners with better attention-switching control may, in general, rely more strongly on bottom-up acoustic information compared to listeners with poorer attention-switching control, making them in turn less susceptible to lexically guided perceptual learning. Our results, moreover, clearly show that lexically guided perceptual learning is not lost when acoustic processing is less accurate.",
            },
        },
        {
            "doi": "10.1038/s41417-021-00297-6",
            "result": {
                "authors": [
                    {
                        "name": "Hong, Yanni",
                        "affiliations": [
                            "Quanzhou First Hospital Affiliated Fujian Medical University"
                        ],
                        "is_corresponding": True,
                    },
                    {
                        "name": "Li, Xiaofeng",
                        "affiliations": [
                            "Quanzhou First Hospital Affiliated Fujian Medical University"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Zhu, Jinfeng",
                        "affiliations": [
                            "Quanzhou First Hospital Affiliated Fujian Medical University"
                        ],
                        "is_corresponding": False,
                    },
                ],
                "abstract": "Non-small cell lung cancer (NSCLC) is a prevalent cancer with unfavorable prognosis. Over the past decade accumulating studies have reported an involvement of lysine-specific histone demethylase 1 (LSD1) in NSCLC development. Here, we aimed to explore whether LSD1 affects the metastasis of NSCLC by mediating Septin 6 (SEPT6) through the TGF-β1 pathway. RT-qPCR was used to determine LSD1 and SEPT6 expression in NSCLC tissues and cells. Interactions between LSD1, SEPT6, and TGF-β1 were detected using lentivirus-mediated silencing of LSD1 and overexpression of SEPT6. The role of LSD1 and SEPT6 in mediating the biological behavior of NSCLC cells was determined using the EdU proliferation assay, Transwell assay, and flow cytometry. Thereafter, transplanted cell tumors into nude mice were used to explore the in vivo effects of LSD1 and SEPT6 on metastasis of NSCLC. LSD1 and SEPT6 were overexpressed in NSCLC tissue and cell samples. LSD1 could demethylate the promoter of the SEPT6 to positively regulate SEPT6 expression. LSD1 promoted proliferation, migration, and invasion, while suppressing the apoptosis of NSCLC cells by increasing SEPT6 expression. LSD1-mediated SEPT6 accelerated in vivo NSCLC metastasis through the TGF-β1/Smad pathway. Collectively, LSD1 demethylates SEPT6 promoter to upregulate SEPT6, which activates TGF-β1 pathway, thereby promoting metastasis of NSCLC.",
            },
        },
        {
            "doi": "10.1038/s41416-020-01139-2",
            "result": {
                "authors": [
                    {
                        "name": "Miligy, Islam M.",
                        "affiliations": ["The University of Nottingham"],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Toss, Michael S.",
                        "affiliations": ["The University of Nottingham"],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Shiino, Sho",
                        "affiliations": ["The University of Nottingham"],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Oni, Georgette",
                        "affiliations": [
                            "Nottingham University Hospitals NHS Trust"],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Syed, Binafsha M.",
                        "affiliations": [
                            "Liaquat University of Medical & Health Sciences"
                        ],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Khout, Hazem",
                        "affiliations": [
                            "Nottingham University Hospitals NHS Trust"],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Tan, Qing Ting",
                        "affiliations": [
                            "Nottingham University Hospitals NHS Trust"],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Green, Andrew R.",
                        "affiliations": ["The University of Nottingham"],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Macmillan, R. Douglas",
                        "affiliations": [
                            "Nottingham University Hospitals NHS Trust"],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Robertson, John F. R.",
                        "affiliations": [
                            "University of Nottingham Royal Derby Hospital"
                        ],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Rakha, Emad A.",
                        "affiliations": ["The University of Nottingham"],
                        "is_corresponding": None,
                    },
                ],
                "abstract": None,
            },
        },
        {
            "doi": "10.1007/978-3-030-50899-9",
            "result": {
                "authors": [
                    {
                        "name": "Cemal Cingi",
                        "affiliations": [
                            "Department of Otolaryngology, Eskisehir Osmangazi University, Eskisehir, Turkey"
                        ],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Nuray Bayar Muluk",
                        "affiliations": [
                            "Otolaryngology Department, Kırıkkale University, Faculty Medicine, Kirikkale, Turkey"
                        ],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Glenis K Scadding",
                        "affiliations": [
                            "Royal National ENT Hospital, London, UK"],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Ranko Mladina",
                        "affiliations": [
                            "Croatian Academy of Medical Sciences, Zagreb, Croatia"
                        ],
                        "is_corresponding": None,
                    },
                ],
                "abstract": None,
            },
        },
    ]
