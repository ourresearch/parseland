from publisher.elements import AuthorAffiliations
from publisher.parsers.parser import PublisherParser


class WorldScientific(PublisherParser):
    parser_name = "world_scientific"

    def is_publisher_specific_parser(self):
        if pub_name_tag := self.soup.select_one("meta[name='dc.Publisher']"):
            return 'World Scientific' in pub_name_tag['content']
        return False

    def authors_found(self):
        return self.soup.find("div", class_="loa-wrapper")

    def parse_authors(self):
        result_authors = []
        author_soup = self.soup.find("div", class_="loa-wrapper")
        authors = author_soup.findAll("div",
                                      class_="accordion-tabbed__tab-mobile")
        for author in authors:
            name = author.a.text.strip()

            affiliations = []
            affiliation_soup = author.find("div", class_="author-info")
            if affiliation_soup:
                author.find("div", class_="bottom-info").decompose()
                if bottom_info := affiliation_soup.find('a'):
                    bottom_info.decompose()
                aff_tag = affiliation_soup.find(lambda
                                                    tag: tag.name == 'p' and 'corresponding' not in tag.text.lower() and len(
                    tag.text) > 3)
                affiliations.append(aff_tag.text.strip())

            result_authors.append(
                AuthorAffiliations(name=name,
                                   affiliations=affiliations,
                                   is_corresponding='corresponding' in affiliation_soup.text.lower())
            )
        return result_authors

    def parse_abstract(self):
        if abs_tag := self.soup.select_one('.abstractInFull'):
            return abs_tag.text
        return None

    def parse(self):

        return {"authors": self.parse_authors(),
                "abstract": self.parse_abstract()}

    test_cases = [
        {
            "doi": "10.5465/AMBPP.2021.16285abstract",
            "result": {
                "authors": [
                    {
                        "name": "Paula Maria Infantes Sanchez",
                        "affiliations": [
                            "ESADE Business School",
                        ],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Bartolome Pascual-Fuster",
                        "affiliations": ["U. de les Illes Balears"],
                        "is_corresponding": None,
                    },
                ],
                "abstract": "This study explores the cascading effect of board gender diversity within business groups. In particular, we empirically test whether board gender diversity in headquarters is positively associated with board gender diversity in lower layers of hierarchical business groups. We, moreover, analyze the empowerment of women directors in the boardroom, and we moderate by some business groups characteristics that may impact the influence of headquarters. We find a positive relationship between board gender diversity in headquarters and affiliates. This suggests that the existence of women at the top stimulates gender diversity in affiliates, and that this finding is influenced by several business group characteristics. However, the presence of women in board executive positions is not associated with an increase in gender diversity across business groups’ affiliates.",
            },
        },
    ]
