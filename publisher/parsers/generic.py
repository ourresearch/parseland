from publisher.parsers.parser import PublisherParser


class GenericPublisherParser(PublisherParser):
    parser_name = "generic_publisher_parser"

    def __init__(self, soup):
        super().__init__(soup)
        self._parse_result = None

    def is_publisher_specific_parser(self):
        return False

    def authors_found(self):
        return self.parse() and (self.parse().get("authors") or self.parse().get("abstract"))

    def parse(self):
        if not self._parse_result:
            self._parse_result = {
                "authors": self.parse_meta_tags(),
                "abstract": self.parse_abstract_meta_tags()
            }

        return self._parse_result

    test_cases = [
        {
            "doi": "10.1158/1538-7445.sabcs18-4608",
            "result": {
                "authors": [
                    {
                        "name": "Shanshan Deng",
                        "affiliations": [
                            "University of Tennessee Health Science Center, Memphis, TN."
                        ]
                    },
                    {
                        "name": "Hao Chen",
                        "affiliations": [
                            "University of Tennessee Health Science Center, Memphis, TN."
                        ]
                    },
                    {
                        "name": "Raisa Krutilina",
                        "affiliations": [
                            "University of Tennessee Health Science Center, Memphis, TN."
                        ]
                    },
                    {
                        "name": "Najah G. Albadari",
                        "affiliations": [
                            "University of Tennessee Health Science Center, Memphis, TN."
                        ]
                    },
                    {
                        "name": "Tiffany N. Seagroves",
                        "affiliations": [
                            "University of Tennessee Health Science Center, Memphis, TN."
                        ]
                    },
                    {
                        "name": "Duane D. Miller",
                        "affiliations": [
                            "University of Tennessee Health Science Center, Memphis, TN."
                        ]
                    },
                    {
                        "name": "Wei Li",
                        "affiliations": [
                            "University of Tennessee Health Science Center, Memphis, TN."
                        ]
                    },
                ],
                "abstract": "Proceedings: AACR Annual Meeting 2019; March 29-April 3, 2019; Atlanta, GA\n\nTriple-negative breast cancer (TNBC) cases account for about 15% of all breast cancers in the United States and have poorer overall prognosis relative to other molecular subtypes, partially due to the rapid development of drug resistance to chemotherapies and the increased risk of visceral metastasis. One of the standard treatment regimens for TNBC is the use of a taxane-based chemotherapy, such as paclitaxel, which stabilizes microtubules. However, drug resistance and neurotoxicities often limit the clinical efficacy of taxanes. Therefore, there are continuous needs to develop more effective therapies that could overcome resistance to taxanes. In this study, a novel series of structurally related pyridine analogs based on our previously reported lead compound ABI-274, was designed and synthesized to identify a molecule with improved antiproliferative potency. Most of these pyridine compounds exhibited potent cytotoxicity when tested in a panel of melanoma and breast cancer cell lines, with IC50 values in the low nanomolar range. Among them, CH-II-77 is the most potent compound with an IC50 value of 1−3 nM against these cancer cell lines, including paclitaxel-resistant sublines. The high-resolution X-ray crystal structure of CH-II-77 in complex with tubulin protein confirmed its direct binding to the colchicine-binding site. It strongly induced apoptosis and produced G2/M phase cell cycle arrest in TNBC cells in a dose-dependent manner in vitro . In vivo , CH-II-77 inhibited tumor growth in A375 melanoma xenografts and MDA-MB-231 TNBC xenografts in a dose-dependent manner. CH-II-77 was able to induce tumor necrosis and apoptosis in vivo . Collectively, these studies strongly suggest that CH-II-77 is a potent inhibitor of the growth of TNBC in vitro and in vivo . Thus, CH-II-77 and optimization of this analog are promising new generation of tubulin inhibitors for the treatment of TNBC and other types of cancers where tubulin inhibitors are currently being used clinically.\n\nCitation Format: Shanshan Deng, Hao Chen, Raisa Krutilina, Najah G. Albadari, Tiffany N. Seagroves, Duane D. Miller, Wei Li. Colchicine binding site agents as potent tubulin inhibitors suppressing triple negative breast cancer [abstract]. In: Proceedings of the American Association for Cancer Research Annual Meeting 2019; 2019 Mar 29-Apr 3; Atlanta, GA. Philadelphia (PA): AACR; Cancer Res 2019;79(13 Suppl):Abstract nr 4608."
            },
        },
    ]
