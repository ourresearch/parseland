from publisher.parsers.parser import PublisherParser


class EgyptianKnowledgeBank(PublisherParser):
    parser_name = "egyptian_knowledge_bank"

    def is_publisher_specific_parser(self):
        for meta_citation_url in self.soup.find_all(
            "meta", {"name": "citation_abstract_html_url"}
        ):
            if "journals.ekb.eg" in meta_citation_url.get("content", ""):
                return True

        return False

    def authors_found(self):
        return self.soup.find("meta", {"name": "citation_author"})

    def parse(self):
        return self.parse_meta_tags()

    test_cases = [
        {
            "doi": "10.21608/ejchem.2021.93025.4397",
            "result": [
                {
                    "name": "Ahmed Ahmed",
                    "affiliations": [
                        "Department of Chemistry, College of Science, Al-Nahrain University, Baghdad, Iraq."
                    ],
                    "is_corresponding": False,
                },
                {
                    "name": "Ismaeel Y. Majeed",
                    "affiliations": [
                        "Department of Chemistry, College of Education for Pure Science Ibn-Al-Haitham, University of\r\nBaghdad, Iraq"
                    ],
                    "is_corresponding": False,
                },
                {
                    "name": "Noora Asaad",
                    "affiliations": [
                        "Department of Chemistry, College of Science, Al-Nahrain University, Baghdad, Iraq."
                    ],
                    "is_corresponding": False,
                },
                {
                    "name": "Riyadh Mahmood Ahmed",
                    "affiliations": [
                        "Department of Chemistry, College of Education for Pure Science Ibn-Al-Haitham, University of\nBaghdad, Iraq."
                    ],
                    "is_corresponding": False,
                },
                {
                    "name": "Ghada M. Kamil",
                    "affiliations": [
                        "Department Of Applied sciences, Branch of Applied Chemistry, University Of Technology, Baghdad, Iraq."
                    ],
                    "is_corresponding": False,
                },
                {
                    "name": "Sarah Abdul Rahman",
                    "affiliations": [
                        "Department of Chemistry, College of Education for Pure Science Ibn-Al-Haitham, University of\nBaghdad, Iraq."
                    ],
                    "is_corresponding": False,
                },
            ],
        },
        {
            "doi": "10.21608/jlaw.2021.190634",
            "result": [
                {
                    "name": "حسين السيد حسين محمد",
                    "affiliations": [],
                    "is_corresponding": False,
                }
            ],
        },
        {
            "doi": "10.21608/jstc.2021.191414",
            "result": [
                {
                    "name": "محمد الهادي",
                    "affiliations": [
                        "أستاذ متفرغ الحاسب الآلى ونظم المعلومات\nقسم الحاسب الآلى ونظم المعلومات\nأکاديمية السادات للعلوم الادارية"
                    ],
                    "is_corresponding": False,
                }
            ],
        },
        {
            "doi": "10.21608/mnase.2021.70758.1148",
            "result": [
                {
                    "name": "محمود حسن الحوفي",
                    "affiliations": ["کلية التربية الرياضيه جامعه مدينه السادات"],
                    "is_corresponding": False,
                },
                {
                    "name": "محمد صلاح ابوسريع",
                    "affiliations": ["کلية التربية الرياضيه جامعه مدينه السادات"],
                    "is_corresponding": False,
                },
                {
                    "name": "Mohamed Zaki",
                    "affiliations": ["مدينة السادات - المنطقة الرابعة - کشک الکاشف"],
                    "is_corresponding": False,
                },
            ],
        },
    ]
