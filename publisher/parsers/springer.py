import json
import re
from collections import defaultdict
from unicodedata import normalize

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

    def parse(self):
        authors_affiliations = self.parse_ld_json()

        if not authors_affiliations:
            authors = self.get_authors()
            if authors:
                affiliations = self.get_affiliations()
                authors_affiliations = self.combine_authors_affiliations(
                    authors, affiliations
                )

        if not authors_affiliations:
            authors_affiliations = self.get_authors_method_2()

        if not authors_affiliations:
            authors_affiliations = self.parse_meta_tags()

        if not authors_affiliations:
            authors_affiliations = []

        if not authors_affiliations:
            authors = self.get_authors(try_editors=True)
            if authors:
                affiliations = self.get_affiliations(try_editors=True)
                authors_affiliations = self.combine_authors_affiliations(
                    authors, affiliations
                )

        return {"authors": authors_affiliations, "abstract": self.parse_abstract()}

    def parse_abstract(self):
        if abstract_soup := self.soup.find("section", class_="Abstract"):
            if abstract_heading := abstract_soup.find(
                class_="Heading", text="Abstract"
            ):
                abstract_heading.decompose()

            for citation in abstract_soup.find_all("span", class_="CitationRef"):
                citation.decompose()

            return abstract_soup.text.strip()

        if abstract_soup := self.soup.find("section", {"data-title": "Abstract"}):
            for abstract_heading in abstract_soup.find_all(
                re.compile("^h[1-6]$"), text="Abstract"
            ):
                abstract_heading.decompose()

            return abstract_soup.text.strip()

        return None

    def parse_ld_json(self):
        authors = []

        for ld_json in self.soup.find_all("script", {"type": "application/ld+json"}):
            article_metadata = json.loads(ld_json.text)
            for author in article_metadata.get("mainEntity", {}).get("author", []):
                if author.get("@type") == "Person":
                    name = author.get("name")
                    affiliations = []

                    json_affiliations = author.get("affiliation")
                    if isinstance(json_affiliations, str):
                        affiliations = [json_affiliations]
                    elif (
                        isinstance(json_affiliations, dict)
                        and "name" in json_affiliations
                    ):
                        affiliations = [json_affiliations["name"]]
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
                                    affiliations.append(json_affiliation["name"])

                    authors.append({"name": name, "affiliations": affiliations})

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
            authors.append({"name": name, "ref_ids": ref_ids})

        return authors

    def get_affiliations(self, try_editors=False):
        affiliations = {}

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

            affiliations[aff_id] = affiliation

        return affiliations

    def combine_authors_affiliations(self, authors, affiliations):
        results = []
        for author in authors:
            matched_affiliations = []
            for ref_id in author["ref_ids"]:
                if ref_id in affiliations.keys():
                    matched_affiliations.append(affiliations[ref_id])
            results.append(
                {"name": author["name"], "affiliations": matched_affiliations}
            )
        return results

    def get_authors_method_2(self):
        author_soup = self.soup.find(id="author-information-content")
        if not author_soup:
            return None
        list_items = author_soup.ol.findAll("li")

        # get mapping of affiliation -> authors
        results = []
        for item in list_items:
            affiliation = item.p.text
            authors = item.p.findNext("p").text
            result = {
                "affiliation": affiliation,
                "authors": self.parser_author_list(authors),
            }
            results.append(result)

        response = defaultdict(list)
        for row in results:
            for author in row["authors"]:
                response[author].append(row["affiliation"])

        # get proper order of author names
        name_soup = self.soup.findAll("span", class_="js-search-name")
        ordered_names = []
        for name in name_soup:
            ordered_names.append(normalize("NFKD", name.text))

        # build new author list with proper order
        ordered_response = []
        for name in ordered_names:
            ordered_response.append({"name": name, "affiliations": response[name]})

        return ordered_response

    @staticmethod
    def parser_author_list(authors):
        authors_split = authors.replace("&", ",").split(",")
        authors_normalized = [
            normalize("NFKD", author).strip() for author in authors_split
        ]
        return authors_normalized

    test_cases = [
        {
            "doi": "10.1007/978-0-387-39343-8_21",
            "result": {
                "authors": [
                    {
                        "name": "Pascal Boileau",
                        "affiliations": [
                            "Orthopaedic Surgery and Sports Traumatology, University of Nice-Sophia Antipolis, Nice, France"
                        ],
                    },
                    {
                        "name": "Christopher R. Chuinard",
                        "affiliations": [
                            "Great Lakes Orthopaedic Center, Munson Medical Center, Traverse City, USA"
                        ],
                    },
                ],
                "abstract": "The tendon of the long head of the biceps (LHB) is a frequent source of pain in the shoulder and is subject to numerous pathologies., ,  Treatment of pathology of the LHB involves resection of the intra-articular portion with a simple tenotomy or a tenodesis. Tenodesis of the LHB, with or without a rotator cuff repair, is an intervention known to reliably and effectively reduce the pain., We were not satisfied with the results obtained with other techniques. Because of our experience with the use of interference screw for surgery of the anterior cruciate ligament (ACL), we developed a technique for tenodesis of the biceps utilizing a bioresorbable interference screw.,",
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
                    },
                    {
                        "name": "Christina Esposito",
                        "affiliations": [
                            "Department of Psychology, Philadelphia College of Osteopathic Medicine, Philadelphia"
                        ],
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
                            "Department of Medicine, Section of Pulmonary and Critical Care Medicine, and Alcohol Research Center, Louisiana State University Health Sciences Center, New Orleans"
                        ],
                    },
                    {
                        "name": "Gregory J. Bagby",
                        "affiliations": [
                            "Department of Medicine, Section of Pulmonary and Critical Care Medicine, Department of Physiology, and Alcohol Research Center, Louisiana State University Health Sciences Center, New Orleans"
                        ],
                    },
                    {
                        "name": "Jay K. Kolls",
                        "affiliations": [
                            "Department of Medicine, Section of Pulmonary and Critical Care Medicine, Alcohol Research Center and Gene Therapy Programs, Louisiana State University Health Sciences Center, New Orleans"
                        ],
                    },
                    {
                        "name": "Lee J. Quinton",
                        "affiliations": [
                            "Department of Physiology and Alcohol Research Center, Louisiana State University Health Sciences Center, New Orleans"
                        ],
                    },
                    {
                        "name": "Steve Nelson",
                        "affiliations": [
                            "Department of Medicine, Section of Pulmonary and Critical Care Medicine, Department of Physiology, and Alcohol Research Center, Louisiana State University Health Sciences Center, New Orleans"
                        ],
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
                    },
                    {
                        "name": "Daniel Joseph Cahill",
                        "affiliations": [
                            "Department of Psychology, California State University, Fresno, Fresno"
                        ],
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
                    },
                    {
                        "name": "Weber, Andrea",
                        "affiliations": [
                            "Max Planck Institute for Psycholinguistics",
                            "Radboud University Nijmegen",
                        ],
                    },
                    {
                        "name": "Janse, Esther",
                        "affiliations": [
                            "Radboud University Nijmegen",
                            "Max Planck Institute for Psycholinguistics",
                        ],
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
                    },
                    {
                        "name": "Li, Xiaofeng",
                        "affiliations": [
                            "Quanzhou First Hospital Affiliated Fujian Medical University"
                        ],
                    },
                    {
                        "name": "Zhu, Jinfeng",
                        "affiliations": [
                            "Quanzhou First Hospital Affiliated Fujian Medical University"
                        ],
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
                    },
                    {
                        "name": "Toss, Michael S.",
                        "affiliations": ["The University of Nottingham"],
                    },
                    {
                        "name": "Shiino, Sho",
                        "affiliations": ["The University of Nottingham"],
                    },
                    {
                        "name": "Oni, Georgette",
                        "affiliations": ["Nottingham University Hospitals NHS Trust"],
                    },
                    {
                        "name": "Syed, Binafsha M.",
                        "affiliations": [
                            "Liaquat University of Medical & Health Sciences"
                        ],
                    },
                    {
                        "name": "Khout, Hazem",
                        "affiliations": ["Nottingham University Hospitals NHS Trust"],
                    },
                    {
                        "name": "Tan, Qing Ting",
                        "affiliations": ["Nottingham University Hospitals NHS Trust"],
                    },
                    {
                        "name": "Green, Andrew R.",
                        "affiliations": ["The University of Nottingham"],
                    },
                    {
                        "name": "Macmillan, R. Douglas",
                        "affiliations": ["Nottingham University Hospitals NHS Trust"],
                    },
                    {
                        "name": "Robertson, John F. R.",
                        "affiliations": [
                            "University of Nottingham Royal Derby Hospital"
                        ],
                    },
                    {
                        "name": "Rakha, Emad A.",
                        "affiliations": ["The University of Nottingham"],
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
                    },
                    {
                        "name": "Nuray Bayar Muluk",
                        "affiliations": [
                            "Otolaryngology Department, Kırıkkale University, Faculty Medicine, Kirikkale, Turkey"
                        ],
                    },
                    {
                        "name": "Glenis K Scadding",
                        "affiliations": ["Royal National ENT Hospital, London, UK"],
                    },
                    {
                        "name": "Ranko Mladina",
                        "affiliations": [
                            "Croatian Academy of Medical Sciences, Zagreb, Croatia"
                        ],
                    },
                ],
                "abstract": None,
            },
        },
    ]
