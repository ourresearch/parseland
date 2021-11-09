from publisher.parsers.parser import PublisherParser


class RSC(PublisherParser):
    parser_name = 'rsc'

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('pubs.rsc.org')

    def authors_found(self):
        return self.soup.find('meta', {'name': 'citation_author'})

    def parse(self):
        return self.parse_meta_tags()

    test_cases = [
        {
            'doi': '10.1039/d0cc04440g',
            'result': [
                {
                    "name": "Daqian Xu",
                    "affiliations": [
                        "State Key Laboratory for Oxo Synthesis and Selective Oxidation Department, Center for Excellence in Molecular Synthesis, Suzhou Research Institute of Lanzhou Institute of Chemical Physics (LICP), Chinese Academy of Sciences, Lanzhou 730000, China",
                        "School of Chemistry and Chemical Engineering, Lanzhou City University, Lanzhou 730070, China"
                    ]
                },
                {
                    "name": "Qiangsheng Sun",
                    "affiliations": [
                        "State Key Laboratory for Oxo Synthesis and Selective Oxidation Department, Center for Excellence in Molecular Synthesis, Suzhou Research Institute of Lanzhou Institute of Chemical Physics (LICP), Chinese Academy of Sciences, Lanzhou 730000, China"
                    ]
                },
                {
                    "name": "Jin Lin",
                    "affiliations": [
                        "State Key Laboratory for Oxo Synthesis and Selective Oxidation Department, Center for Excellence in Molecular Synthesis, Suzhou Research Institute of Lanzhou Institute of Chemical Physics (LICP), Chinese Academy of Sciences, Lanzhou 730000, China"
                    ]
                },
                {
                    "name": "Wei Sun",
                    "affiliations": [
                        "State Key Laboratory for Oxo Synthesis and Selective Oxidation Department, Center for Excellence in Molecular Synthesis, Suzhou Research Institute of Lanzhou Institute of Chemical Physics (LICP), Chinese Academy of Sciences, Lanzhou 730000, China"
                    ]
                },
            ]
        },
        {
            'doi': '10.1039/d1bm00157d',
            'result': [
                {
                    "name": "Yin-Chu Ma",
                    "affiliations": [
                        "Zhuhai Interventional Medical Center, Zhuhai Precision Medical Center, Zhuhai People's Hospital, Zhuhai Hospital Affiliated with Jinan University, Zhuhai 519000, China"
                    ]
                },
                {
                    "name": "Xin-Feng Tang",
                    "affiliations": [
                        "School of Life Sciences, University of Science and Technology of China, Hefei 230027, China"
                    ]
                },
                {
                    "name": "You-Cui Xu",
                    "affiliations": [
                        "School of Life Sciences, University of Science and Technology of China, Hefei 230027, China"
                    ]
                },
                {
                    "name": "Wei Jiang",
                    "affiliations": [
                        "Zhuhai Interventional Medical Center, Zhuhai Precision Medical Center, Zhuhai People's Hospital, Zhuhai Hospital Affiliated with Jinan University, Zhuhai 519000, China"
                    ]
                },
                {
                    "name": "Yong-Jie Xin",
                    "affiliations": [
                        "Zhuhai Interventional Medical Center, Zhuhai Precision Medical Center, Zhuhai People's Hospital, Zhuhai Hospital Affiliated with Jinan University, Zhuhai 519000, China"
                    ]
                },
                {
                    "name": "Wei Zhao",
                    "affiliations": [
                        "Zhuhai Interventional Medical Center, Zhuhai Precision Medical Center, Zhuhai People's Hospital, Zhuhai Hospital Affiliated with Jinan University, Zhuhai 519000, China"
                    ]
                },
                {
                    "name": "Xu He",
                    "affiliations": [
                        "Zhuhai Interventional Medical Center, Zhuhai Precision Medical Center, Zhuhai People's Hospital, Zhuhai Hospital Affiliated with Jinan University, Zhuhai 519000, China"
                    ]
                },
                {
                    "name": "Li-Gong Lu",
                    "affiliations": [
                        "Zhuhai Interventional Medical Center, Zhuhai Precision Medical Center, Zhuhai People's Hospital, Zhuhai Hospital Affiliated with Jinan University, Zhuhai 519000, China"
                    ]
                },
                {
                    "name": "Mei-Xiao Zhan",
                    "affiliations": [
                        "Zhuhai Interventional Medical Center, Zhuhai Precision Medical Center, Zhuhai People's Hospital, Zhuhai Hospital Affiliated with Jinan University, Zhuhai 519000, China"
                    ]
                },
            ]
        },
    ]