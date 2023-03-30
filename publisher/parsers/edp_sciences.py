from publisher.parsers.parser import PublisherParser


class EDPSciences(PublisherParser):
    parser_name = "edp_sciences"

    def is_publisher_specific_parser(self):
        for meta_citation_url in self.soup.find_all(
            "meta", {"name": "citation_publisher"}
        ):
            if "EDP Sciences" in meta_citation_url.get("content", ""):
                return True

        return False

    def authors_found(self):
        return self.soup.find("meta", {"name": "citation_author"}) and self.soup.select('.article-authors')

    def parse_abstract(self):
        if abs_heading := self.soup.select_one("a[name='abs']"):
            return abs_heading.parent.find_next_sibling('p').text

    def parse(self):
        authors = self.parse_author_meta_tags()
        author_tags = self.soup.select('.article-authors span')
        for tag in author_tags:
            name = tag.text.strip()
            if tag.next_sibling and '*' in tag.next_sibling.text:
                for author in authors:
                    if author['name'] == name:
                        author['is_corresponding'] = True
        return {'authors': authors, 'abstract': self.parse_abstract()}

    test_cases = [
        {
            "doi": "10.1051/e3sconf/202126102087",
            "result": [
                {
                    "name": "Yunwu He",
                    "affiliations": [
                        "Shenzhen Tagen<group> Co., Ltd, 518034, Shenzhen, China"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Tao Liu",
                    "affiliations": [
                        "Shenzhen Yuetong Construction Engineering Co., Ltd, 518019, Shenzhen, China"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Tao Wang",
                    "affiliations": [
                        "Shenzhen Yuetong Construction Engineering Co., Ltd, 518019, Shenzhen, China"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Xiayi Liang",
                    "affiliations": [
                        "Shenzhen Yuetong Construction Engineering Co., Ltd, 518019, Shenzhen, China"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Hanxin Wei",
                    "affiliations": [
                        "Shenzhen Yuetong Construction Engineering Co., Ltd, 518019, Shenzhen, China"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Zhigang Zheng",
                    "affiliations": [
                        "Shenzhen Yuetong Construction Engineering Co., Ltd, 518019, Shenzhen, China"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Xin Xiao",
                    "affiliations": ["Foshan University, 528000, Foshan, China"],
                    "is_corresponding": None,
                },
            ],
        },
        {
            "doi": "10.1051/shsconf/20207301023",
            "result": [
                {
                    "name": "Pavel Rousek",
                    "affiliations": [
                        "Institute of Technology and Business, School of Expertness and Valuation, Okružní 517/10, 37001 české Budějovice Czech Republic"
                    ],
                    "is_corresponding": None,
                },
                {
                    "name": "Simona Hašková",
                    "affiliations": [
                        "Institute of Technology and Business, School of Expertness and Valuation, Okružní 517/10, 37001 české Budějovice Czech Republic"
                    ],
                    "is_corresponding": None,
                },
            ],
        },
    ]
