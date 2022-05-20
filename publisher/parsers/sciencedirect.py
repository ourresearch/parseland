import json
import re

from publisher.parsers.parser import PublisherParser


class ScienceDirect(PublisherParser):
    parser_name = "sciencedirect"

    def is_publisher_specific_parser(self):
        return self.domain_in_canonical_link("sciencedirect.com")

    def authors_found(self):
        return self.soup.find_all("a", class_="author")

    def parse(self):
        """Core function returning list of authors with their affiliations."""
        return self.get_json_authors_affiliations_abstract()

    def get_json_authors_affiliations_abstract(self):
        if not (science_direct_json := self.extract_json()):
            return {}

        all_authors = []

        authors_content = science_direct_json.get("authors", {}).get("content", {})

        for author_group in [
            ac for ac in authors_content if ac.get("#name") == "author-group"
        ]:
            group_authors = []
            group_affiliation_labels = {}

            affiliation_dicts = [
                x for x in author_group.get("$$", []) if x.get("#name") == "affiliation"
            ]

            for affiliation in affiliation_dicts:
                affiliation_label = affiliation.get("$", {}).get("id")
                for affiliation_property in affiliation.get("$$", []):
                    if affiliation_property.get("#name") == "textfn":
                        if affiliation_label and affiliation_property.get("_"):
                            group_affiliation_labels[
                                affiliation_label
                            ] = affiliation_property["_"]

            author_dicts = [
                x for x in author_group.get("$$", []) if x.get("#name") == "author"
            ]

            for author in author_dicts:
                given = None
                family = None
                affiliation_labels = []
                for author_property in author.get("$$", []):
                    if author_property.get("#name") == "given-name":
                        given = author_property.get("_")
                    elif author_property.get("#name") == "surname":
                        family = author_property.get("_")
                    elif author_property.get("#name") == "cross-ref":
                        affiliation_label = author_property.get("$", {}).get("refid")
                        if affiliation_label in group_affiliation_labels:
                            affiliation_labels.append(affiliation_label)

                if given or family:
                    group_authors.append(
                        {
                            "name": " ".join([n for n in [given, family] if n]),
                            "affiliation_labels": affiliation_labels,
                        }
                    )

            if any(author.get("affiliation_labels") for author in group_authors):
                # assign affiliations by label
                for author in group_authors:
                    affiliations = [
                        group_affiliation_labels[label]
                        for label in author["affiliation_labels"]
                    ]
                    all_authors.append(
                        {"name": author["name"], "affiliations": affiliations}
                    )
            else:
                # assign all affiliations to all authors
                for author in group_authors:
                    all_authors.append(
                        {
                            "name": author["name"],
                            "affiliations": list(group_affiliation_labels.values()),
                        }
                    )

        abstract = None
        abstracts_content = science_direct_json.get("abstracts", {}).get("content", [])
        if abstracts_content:
            abstract = self.abstract_text(abstracts_content)
            abstract = re.sub(r" +", " ", abstract).strip()

        return {"authors": all_authors, "abstract": abstract}

    def abstract_text(self, abstracts_json):
        if isinstance(abstracts_json, list):
            return " ".join([self.abstract_text(x) for x in abstracts_json])

        if isinstance(abstracts_json, dict):
            if (text_content := abstracts_json.get("_")) and isinstance(
                text_content, str
            ):
                if abstracts_json.get("#name") in ["section-title", "alt-text"]:
                    return ""

                return text_content

            if "$$" in abstracts_json:
                return self.abstract_text(abstracts_json["$$"])

        return ""

    def extract_json(self):
        """Finds and loads json that contains affiliation data."""
        raw_json = self.soup.find("script", type="application/json").text
        loaded_json = json.loads(raw_json)
        return loaded_json

    test_cases = [
        {
            "doi": "10.1016/0022-247x(78)90205-6",
            "result": {
                "authors": [
                    {
                        "name": "Pierre Charrier",
                        "affiliations": [
                            "U.E.R. de Mathématiques et Informatique et Laboratoire associé au C.N.R.S. n∘ 226, Université de Bordeaux 1, 33405 Talence, France"
                        ],
                    },
                    {
                        "name": "Giovanni M Troianiello",
                        "affiliations": [
                            "Istituto Matematico, Universitá di Roma, 00185 Rome, Italy"
                        ],
                    },
                ],
                "abstract": None,
            },
        },
        {
            "doi": "10.1016/0022-247x(79)90002-7",
            "result": {
                "authors": [
                    {
                        "name": "N Levan",
                        "affiliations": [
                            "Department of System Science, 4532 Boelter Hall, University of California, Los Angeles, California 90024 U.S.A."
                        ],
                    },
                    {
                        "name": "L Rigby",
                        "affiliations": [
                            "Department of Computing and Control, Huxley Building, Imperial College, London SW7 2BZ, Great Britain"
                        ],
                    },
                ],
                "abstract": "According to a Theorem of B. Sz.-Nagy and C. Foiaş, every strongly continuous semigroup of contraction operators on a Hilbert space, can be decomposed into a completely non unitary part and a unitary part. In this note we wish to show that by appropriately perturbing its generator, a contraction semigroup can be reduced to a completely non unitary one. In control theory, such a perturbation is related to the so called state feedback, and the reduction presented here has application in the problem of stabilizing linear control systems on a Hilbert space. This will be briefly discussed.",
            },
        },
        {
            "doi": "10.1016/0022-247x(77)90164-0",
            "result": {
                "authors": [
                    {
                        "name": "László Losonczi",
                        "affiliations": [
                            "Department of Mathematics, University of Lagos, Lagos, Nigeria",
                            "Department of Mathematics, Kossuth Lajos University, Debrecen, Hungary",
                        ],
                    },
                ],
                "abstract": None,
            },
        },
        {
            "doi": "10.1016/0024-3795(85)90253-8",
            "result": {
                "authors": [
                    {
                        "name": "Donald W. Robinson",
                        "affiliations": [
                            "Department of Mathematics Brigham Young University Provo, Utah 84602, USA"
                        ],
                    },
                ],
                "abstract": "Given an invertible complex matrix T , a description is given of those matrices A with Moore-Penrose inverse A † such that ( TAT -1 ) † = TA † T -1 .",
            },
        },
        {
            "doi": "10.1016/0024-3795(86)90148-5",
            "result": {
                "authors": [
                    {
                        "name": "Robert E. Hartwig",
                        "affiliations": [
                            "Department of Mathematics North Carolina State University Box 8205 Raleigh, North Carolina 27695-820 USA"
                        ],
                    },
                    {
                        "name": "George P.H. Styan",
                        "affiliations": [
                            "Department of Mathematics and Statistics McGill University 805 ouest, rue Sherbrooke Montréal, Québec, Canada H3A 2K6"
                        ],
                    },
                ],
                "abstract": "The main result is that Drazin's “star” partial ordering A ⩽ ∗ B holds if and only if A ∠ B and B † −A † =(B−A) † , where A ⩽ ∗ B is defined by A ∗ A = A ∗ B and AA ∗ = BA ∗ , and where A ∠ B denotes rank subtractivity. Here A and B are m × n complex matrices and the superscript † denotes the Moore-Penrose inverse. Several other characterizations of A ⩽ ∗ B are given, with particular emphasis on what extra condition must be added in order that rank subtractivity becomes the stronger “star” order; a key tool is a new canonical form for rank subtractivity. Connections with simultaneous singular-value decompositions, Schur complements, and idempotent matrices are also mentioned.",
            },
        },
        {
            "doi": "10.1016/j.ab.2021.114100",
            "result": {
                "authors": [
                    {
                        "name": "Emma Dreischmeier",
                        "affiliations": [
                            "Wisconsin Institutes of Medical Research, University of Wisconsin-Madison, Madison, WI, USA"
                        ],
                    },
                    {
                        "name": "William E. Fahl",
                        "affiliations": [
                            "Wisconsin Institutes of Medical Research, University of Wisconsin-Madison, Madison, WI, USA"
                        ],
                    },
                ],
                "abstract": "PrC-210 is a direct-acting ROS-scavenger. It's active when administered orally, IV, or topically; it has none of the nausea/emesis nor hypotension side effects that have precluded human amifostine use. PrC-210 confers 100% survival to mice and rats that received an otherwise 100% lethal radiation dose and 36% reduction of ischemia-reperfusion-induced mouse myocardial infarct damage, and thus is a viable candidate to prevent human ROS-induced ischemia-reperfusion and ionizing radiation toxicities. We report the first assay for the pharmacologically active PrC-210 thiol in blood. PrC-210 has no double-bonds nor light absorption, so derivatizing the thiol with a UV-absorbing fluorochrome enables quantification. This assay: i) is done on the benchtop; it's read with a fluorescence plate reader, ii) provides linear product formation through 60\xa0min, iii) quantifies μM to low mM rodent blood levels of PrC-210 that confer complete radioprotection, iv) accurately reflects PrC-210 thiol formation of mixed disulfides with other thiols in blood, and v) shows excellent between-day assay outcome with very low standard deviation and coefficient of variation. A fluorescence assay quantifying formation of a PrC-210 thiol-bimane adduct enables measurement of blood PrC-210 thiol. A blood assay will help in the development of PrC-210 for use in the human clinical setting. • Assay quantifies μM-low mM PrC-210 blood concentration that confers 100% radioprotection. • No UV light absorbance, so chemically derivitize PrC-210 to yield a fluorochrome. • Derivitization reaction is specific to active-form PrC-210 thiol in blood. • Assay has very low coefficient of variation, same-day and between-days.",
            },
        },
        {
            "doi": "10.1016/j.ab.2021.114241",
            "result": {
                "authors": [
                    {
                        "name": "Jun Hu",
                        "affiliations": [
                            "College of Information Engineering, Zhejiang University of Technology, Hangzhou, 310023, China"
                        ],
                    },
                    {
                        "name": "Lin-Lin Zheng",
                        "affiliations": [
                            "College of Information Engineering, Zhejiang University of Technology, Hangzhou, 310023, China"
                        ],
                    },
                    {
                        "name": "Yan-Song Bai",
                        "affiliations": [
                            "College of Information Engineering, Zhejiang University of Technology, Hangzhou, 310023, China"
                        ],
                    },
                    {
                        "name": "Ke-Wen Zhang",
                        "affiliations": [
                            "College of Mechanical Engineering, Zhejiang University of Technology, Hangzhou, 310023, China"
                        ],
                    },
                    {
                        "name": "Dong-Jun Yu",
                        "affiliations": [
                            "School of Computer Science and Engineering, Nanjing University of Science and Technology,Xiaolingwei 200, Nanjing, 210094, China"
                        ],
                    },
                    {
                        "name": "Gui-Jun Zhang",
                        "affiliations": [
                            "College of Information Engineering, Zhejiang University of Technology, Hangzhou, 310023, China"
                        ],
                    },
                ],
                "abstract": "Knowledge of protein-ATP interaction can help for protein functional annotation and drug discovery. Accurately identifying protein-ATP binding residues is an important but challenging task to gain the knowledge of protein-ATP interactions, especially for the case where only protein sequence information is given. In this study, we propose a novel method, named DeepATPseq, to predict protein-ATP binding residues without using any information about protein three-dimension structure or sequence-derived structural information. In DeepATPseq, the HHBlits-generated position-specific frequency matrix (PSFM) profile is first employed to extract the feature information of each residue. Then, for each residue, the PSFM-based feature is fed into two prediction models, which are generated by the algorithms of deep convolutional neural network (DCNN) and support vector machine (SVM) separately. The final ATP-binding probability of the corresponding residue is calculated by the weighted sum of the outputted values of DCNN-based and SVM-based models. Experimental results on the independent validation data set demonstrate that DeepATPseq could achieve an accuracy of 77.71%, covering 57.42% of all ATP-binding residues, while achieving a Matthew's correlation coefficient value (0.655) that is significantly higher than that of existing sequence-based methods and comparable to that of the state-of-the-art structure-based predictors. Detailed data analysis show that the major advantage of DeepATPseq lies at the combination utilization of DCNN and SVM that helps dig out more discriminative information from the PSFM profiles. The online server and standalone package of DeepATPseq are freely available at: https://jun-csbio.github.io/DeepATPseq/ for academic use. • DeepATPseq is a novel method for predicting protein-ATP binding residues using position-specific frequency matrix. • The combination utilization of DCNN and SVM helps to dig out more discriminative information from the PSFM profiles. • DeepATPseq could achieve a higher performance than the existing sequence-based methods.",
            },
        },
    ]
