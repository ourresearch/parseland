from publisher.elements import AuthorAffiliations
from publisher.parsers.parser import PublisherParser


class RXIV(PublisherParser):
    parser_name = "RXIV (Cold Spring Harbor Laboratory)"

    def is_correct_parser(self):
        return self.domain_in_meta_og_url("medrxiv.org") or self.domain_in_meta_og_url(
            "biorxiv.org"
        )

    def authors_found(self):
        return self.soup.find("div", class_="author-tooltip-0") or self.soup.find(
            "meta", {"name": "citation_author"}
        )

    def parse(self):
        results = self.get_authors_method_1()
        if not results:
            # about 25% of rxiv files do not have affiliations in html, only in meta tags
            results = self.parse_meta_tags()
        return results

    def get_authors_method_1(self):
        results = []
        i = 0
        while True:
            author = self.soup.find("div", class_=f"author-tooltip-{i}")
            if author:
                name = author.find("div", class_="author-tooltip-name").text.strip()

                # affiliations
                affiliations = []
                affiliations_soup = author.findAll("div", class_="author-affiliation")
                for affiliation in affiliations_soup:
                    organization = affiliation.text.strip()

                    # replace sup text
                    sup = affiliation.find("span", class_="nlm-sup")
                    if sup:
                        organization = organization.replace(sup.text, "")

                    affiliations.append(organization)

                results.append(AuthorAffiliations(name=name, affiliations=affiliations))
                i += 1
            else:
                break
        return results

    test_cases = [
        {
            "doi": "10.1101/2021.04.22.21255924",
            "result": [
                {
                    "name": "Norman Scheel",
                    "affiliations": [
                        "Department of Radiology and Cognitive Imaging Research Center, Michigan State University, East Lansing, MI, USA"
                    ],
                },
                {
                    "name": "Takashi Tarumi",
                    "affiliations": [
                        "Institute for Exercise and Environmental Medicine, Texas Health Presbyterian Hospital, Dallas, TX, USA",
                        "Human Informatics and Interaction Research Institute, National Institute of Advanced Industrial Science and Technology, Tsukuba, Ibaraki, Japan",
                    ],
                },
                {
                    "name": "Tsubasa Tomoto",
                    "affiliations": [
                        "Institute for Exercise and Environmental Medicine, Texas Health Presbyterian Hospital, Dallas, TX, USA",
                        "Department of Neurology, University of Texas Southwestern Medical Center, Dallas, TX, USA",
                    ],
                },
                {
                    "name": "C. Munro Cullum",
                    "affiliations": [
                        "Department of Psychiatry, University of Texas Southwestern Medical Center, Dallas, TX, USA",
                        "Department of Neurology, University of Texas Southwestern Medical Center, Dallas, TX, USA",
                        "Department of Neurological Surgery, University of Texas Southwestern Medical Center, Dallas, TX, USA",
                    ],
                },
                {
                    "name": "Rong Zhang",
                    "affiliations": [
                        "Institute for Exercise and Environmental Medicine, Texas Health Presbyterian Hospital, Dallas, TX, USA",
                        "Department of Neurology, University of Texas Southwestern Medical Center, Dallas, TX, USA",
                    ],
                },
                {
                    "name": "David C. Zhu",
                    "affiliations": [
                        "Department of Radiology and Cognitive Imaging Research Center, Michigan State University, East Lansing, MI, USA"
                    ],
                },
            ],
        },
        {
            "doi": "10.1101/2021.03.04.433953",
            "result": [
                {
                    "name": "Nadya Povysheva",
                    "affiliations": [
                        "Department of Neuroscience, University of Pittsburgh"
                    ],
                },
                {
                    "name": "Huiyuan Zheng",
                    "affiliations": [
                        "Department of Psychology, Program in Neuroscience, Florida State University",
                    ],
                },
                {
                    "name": "Linda Rinaman",
                    "affiliations": [
                        "Department of Psychology, Program in Neuroscience, Florida State University",
                    ],
                },
            ],
        },
    ]
