import json
import re

from publisher.elements import AuthorAffiliations
from publisher.parsers.parser import PublisherParser


class IEEE(PublisherParser):
    parser_name = "IEEE"

    def is_publisher_specific_parser(self):
        return self.domain_in_canonical_link("ieee.org")

    def authors_found(self):
        json_data = self.get_json_data()
        if json_data:
            authors = json_data.get("authors")
            if authors:
                return True

    def parse(self):
        authors = []

        json_authors = []
        if json_data := self.get_json_data():
            json_authors = json_data.get("authors", [])

        for json_author in json_authors:
            name = json_author.get("name")
            affiliations = json_author.get("affiliation", [])
            authors.append(AuthorAffiliations(name=name, affiliations=affiliations))

        return {"authors": authors, "abstract": self.get_abstract()}

    def get_json_data(self):
        raw_script = re.search("xplGlobal.document.metadata=.*", str(self.soup))

        if raw_script:
            raw_json = raw_script.group()
            trimmed_json = raw_json.replace("xplGlobal.document.metadata=", "").replace(
                "};", "}"
            )
            json_data = json.loads(trimmed_json)
        else:
            json_data = None
        return json_data

    def get_abstract(self):
        if og_description := self.soup.find("meta", {"property": "og:description"}):
            if description := og_description.get("content").strip():
                return description

        return None

    test_cases = [
        {
            "doi": "10.1109/TAC.2021.3105318",
            "result": {
                "authors": [
                    {
                        "name": "Masih Haseli",
                        "affiliations": [
                            "Mechanical and Aerospace Engineering, University of California, San Diego, La Jolla, CA, United States of America, 92037 (e-mail: mhaseli@ucsd.edu)"
                        ],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Jorge Cortes",
                        "affiliations": [
                            "Mechanical and Aerospace Engineering, University of California, San Diego, La Jolla, California, United States of America, 92093 (e-mail: cortes@ucsd.edu)"
                        ],
                        "is_corresponding": None,
                    },
                ],
                "abstract": "This paper develops data-driven methods to identify eigenfunctions of the Koopman operator associated to a dynamical system and subspaces that are invariant under the operator. We build on Extended Dynamic Mode Decomposition (EDMD), a data-driven method that finds a finite-dimensional approximation of the Koopman operator on the span of a predefined dictionary of functions. We propose a necessary and sufficient condition to identify Koopman eigenfunctions based on the application of EDMD forward and backward in time. Moreover, we propose the Symmetric Subspace Decomposition (SSD) algorithm, an iterative method which provably identifies the maximal Koopman-invariant subspace and the Koopman eigenfunctions in the span of the dictionary. We also introduce the Streaming Symmetric Subspace Decomposition (SSSD) algorithm, an online extension of SSD that only requires a small, fixed memory and incorporates new data as is received. Finally, we propose an extension of SSD that approximates Koopman eigenfunctions and invariant subspaces when the dictionary does not contain sufficient informative eigenfunctions.",
            },
        },
        {
            "doi": "10.1109/agro-geoinformatics50104.2021.9530299",
            "result": PublisherParser.no_authors_output(),
        },
        {
            "doi": "10.1109/acirs52449.2021",
            "result": PublisherParser.no_authors_output(),
        },
        {
            "doi": "10.1109/sti50764.2020.9350398",
            "result": {
                "authors": [
                    {
                        "name": "Redwan Ahmed",
                        "affiliations": [
                            "Rajshahi University of Engineering & Technology, Rajshahi, Bangladesh"
                        ],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Shadhon Chandra Mohonta",
                        "affiliations": [
                            "Rajshahi University of Engineering & Technology, Rajshahi, Bangladesh"
                        ],
                        "is_corresponding": None,
                    },
                ],
                "abstract": "An efficient maximum power point tracking (MPPT) controller is a crucial part of solar photovoltaic (PV) system, which can handle the non-linear characteristics of a solar PV array. In this study, a proposed solar PV system with boost converter and dc load is modeled and compared according to the operating characteristics (i.e. voltage, current, power and efficiency under varying solar irradiance and cell temperature) using five conventional and modern MPPT techniques. The proposed solar PV system and MPPT controllers are modeled and simulated in MATLAB Simulink platform. Among these five MPPT controllers, artificial neural network (ANN) MPPT controller provides the highest efficiency of 97.55% and produces less voltage and power fluctuations. The novelty of this paper is that it focuses on the key characteristics and simulated results of the five MPPT techniques to make a comparison between them.",
            },
        },
        {
            "doi": "10.1109/infocom.2019.8737570",
            "result": PublisherParser.no_authors_output(),
        },
        {
            "doi": "10.1109/eftf/ifcs52194.2021.9604295",
            "result": {
                "authors": [
                    {
                        "name": "Wen-Hung Tseng",
                        "affiliations": [
                            "Telecommunication Laboratories, Chunghwa Telecom Co., Ltd., Taoyuan City, Taiwan"
                        ],
                        "is_corresponding": None,
                    }
                ],
                "abstract": 'This study compares the difference between the GNSS P3 code-based time transfer data of the all-in-view (AV) and the proposed upsampled common-view (UCV) methods. The results show that the modified Allan deviations (MDEVs) of the AV and UCV difference for the TL-PTB link are 1.1×10\n<sup xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">-15</sup>\n at 1 day averaging time and 9.3×10\n<sup xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">-17</sup>\n at 1 week averaging time. The difference distribution appears as a bell curve with a mean of - 0.128 ns. For the OP-PTB link, the mean of the difference between the AV and UCV data is only 0.02 ns. The MDEVs of the difference are 1.28×10\n<sup xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">-15</sup>\n at 1 day averaging time and 3.27×10\n<sup xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">-17</sup>\n at 10-day averaging time.',
            },
        },
    ]
