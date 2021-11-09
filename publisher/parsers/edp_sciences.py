from publisher.parsers.parser import PublisherParser


class EDPSciences(PublisherParser):
    parser_name = "edp_sciences"

    def is_publisher_specific_parser(self):
        for meta_citation_url in self.soup.find_all("meta", {"name": "citation_publisher"}):
            if 'EDP Sciences' in meta_citation_url.get("content", ""):
                return True

        return False

    def authors_found(self):
        return self.soup.find("meta", {"name": "citation_author"})

    def parse(self):
        return self.parse_meta_tags()

    test_cases = [
        {
            "doi": "10.1051/e3sconf/202126102087",
            "result": [
                {
                    "name": "Yunwu He",
                    "affiliations": [
                        "Shenzhen Tagen<group> Co., Ltd, 518034, Shenzhen, China"
                    ]
                },
                {
                    "name": "Tao Liu",
                    "affiliations": [
                        "Shenzhen Yuetong Construction Engineering Co., Ltd, 518019, Shenzhen, China"
                    ]
                },
                {
                    "name": "Tao Wang",
                    "affiliations": [
                        "Shenzhen Yuetong Construction Engineering Co., Ltd, 518019, Shenzhen, China"
                    ]
                },
                {
                    "name": "Xiayi Liang",
                    "affiliations": [
                        "Shenzhen Yuetong Construction Engineering Co., Ltd, 518019, Shenzhen, China"
                    ]
                },
                {
                    "name": "Hanxin Wei",
                    "affiliations": [
                        "Shenzhen Yuetong Construction Engineering Co., Ltd, 518019, Shenzhen, China"
                    ]
                },
                {
                    "name": "Zhigang Zheng",
                    "affiliations": [
                        "Shenzhen Yuetong Construction Engineering Co., Ltd, 518019, Shenzhen, China"
                    ]
                },
                {
                    "name": "Xin Xiao",
                    "affiliations": [
                        "Foshan University, 528000, Foshan, China"
                    ]
                }
            ]
        },
        {
            "doi": "10.1051/shsconf/20207301023",
            "result": [
                {
                    "name": "Pavel Rousek",
                    "affiliations": [
                        "Institute of Technology and Business, School of Expertness and Valuation, Okružní 517/10, 37001 české Budějovice Czech Republic"
                    ]
                },
                {
                    "name": "Simona Hašková",
                    "affiliations": [
                        "Institute of Technology and Business, School of Expertness and Valuation, Okružní 517/10, 37001 české Budějovice Czech Republic"
                    ]
                }
            ]
        }
    ]
