from publisher.elements import Author, Affiliation
from publisher.parsers.parser import PublisherParser


class MDPI(PublisherParser):
    parser_name = "mdpi"
    chars_to_ignore = ["*", "†", "‡", "§"]

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url("mdpi.com")

    def authors_found(self):
        return self.soup.find("div", class_="art-authors")

    def parse(self):
        authors = self.get_authors()
        affiliations = self.get_affiliations()
        authors_affiliations = self.merge_authors_affiliations(authors, affiliations)
        return authors_affiliations

    def get_authors(self):
        authors = []
        author_soup = self.soup.find("div", class_="art-authors")
        author_soup = author_soup.findAll("span", class_="inlineblock")
        for author in author_soup:
            if author.div:
                name = author.div.text
            else:
                name = author.a.text
            aff_ids = self.format_ids(author.sup.text, self.chars_to_ignore)
            authors.append(Author(name=name, aff_ids=aff_ids))
        return authors

    def get_affiliations(self):
        aff_soup = self.soup.find("div", class_="art-affiliations")

        results = []
        if aff_soup:
            affiliations = aff_soup.findAll("div", class_="affiliation")
            for aff_raw in affiliations:
                aff_id_raw = aff_raw.find("sup")
                if aff_id_raw:
                    aff_id = aff_id_raw.text
                else:
                    aff_id = None
                aff = aff_raw.find("div", class_="affiliation-name").text
                if aff_id not in self.chars_to_ignore:
                    aff_id = int(aff_id) if aff_id else None
                    results.append(Affiliation(organization=aff, aff_id=aff_id))
        return results

    test_cases = [
        {
            "doi": "10.3390/act10080193",
            "result": [
                {
                    "name": "Wenfei Li",
                    "affiliations": [
                        "Shenzhen Institutes of Advanced Technology, Chinese Academy of Sciences, Shenzhen 518055, China",
                        "SIAT Branch, Shenzhen Institute of Artificial Intelligence and Robotics for Society, Shenzhen 518055, China",
                        "Guangdong-Hong Kong-Macao Joint Laboratory of Human-Machine Intelligence-Synergy Systems, Shenzhen 518055, China",
                    ],
                },
                {
                    "name": "Huiyun Li",
                    "affiliations": [
                        "Shenzhen Institutes of Advanced Technology, Chinese Academy of Sciences, Shenzhen 518055, China",
                        "SIAT Branch, Shenzhen Institute of Artificial Intelligence and Robotics for Society, Shenzhen 518055, China",
                        "Guangdong-Hong Kong-Macao Joint Laboratory of Human-Machine Intelligence-Synergy Systems, Shenzhen 518055, China",
                    ],
                },
                {
                    "name": "Chao Huang",
                    "affiliations": [
                        "Department of Industrial and Systems Engineering, The Hong Kong Polytechnic University, Hong Kong 999077, China"
                    ],
                },
                {
                    "name": "Kun Xu",
                    "affiliations": [
                        "Shenzhen Institutes of Advanced Technology, Chinese Academy of Sciences, Shenzhen 518055, China"
                    ],
                },
                {
                    "name": "Tianfu Sun",
                    "affiliations": [
                        "Shenzhen Institutes of Advanced Technology, Chinese Academy of Sciences, Shenzhen 518055, China"
                    ],
                },
                {
                    "name": "Haiping Du",
                    "affiliations": [
                        "School of Electrical, Computer and Telecommunications Engineering, University of Wollongong, Wollongong 2522, Australia"
                    ],
                },
            ],
        }
    ]
