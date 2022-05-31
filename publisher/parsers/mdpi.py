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
        return {
            "authors": authors_affiliations,
            "abstract": self.parse_abstract_meta_tags(),
        }

    def get_authors(self):
        authors = []
        author_soup = self.soup.find("div", class_="art-authors")
        author_soup = author_soup.findAll("span", class_="inlineblock")
        for author in author_soup:
            if author.div:
                name = author.div.text
            else:
                name = author.a.text
            if "*" in author.sup.text:
                is_corresponding = True
            else:
                is_corresponding = False
            aff_ids = self.format_ids(author.sup.text, self.chars_to_ignore)
            authors.append(
                Author(
                    name=name, aff_ids=aff_ids, is_corresponding_author=is_corresponding
                )
            )
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
            "result": {
                "authors": [
                    {
                        "name": "Wenfei Li",
                        "affiliations": [
                            "Shenzhen Institutes of Advanced Technology, Chinese Academy of Sciences, Shenzhen 518055, China",
                            "SIAT Branch, Shenzhen Institute of Artificial Intelligence and Robotics for Society, Shenzhen 518055, China",
                            "Guangdong-Hong Kong-Macao Joint Laboratory of Human-Machine Intelligence-Synergy Systems, Shenzhen 518055, China",
                        ],
                        "is_corresponding_author": False,
                    },
                    {
                        "name": "Huiyun Li",
                        "affiliations": [
                            "Shenzhen Institutes of Advanced Technology, Chinese Academy of Sciences, Shenzhen 518055, China",
                            "SIAT Branch, Shenzhen Institute of Artificial Intelligence and Robotics for Society, Shenzhen 518055, China",
                            "Guangdong-Hong Kong-Macao Joint Laboratory of Human-Machine Intelligence-Synergy Systems, Shenzhen 518055, China",
                        ],
                        "is_corresponding_author": True,
                    },
                    {
                        "name": "Chao Huang",
                        "affiliations": [
                            "Department of Industrial and Systems Engineering, The Hong Kong Polytechnic University, Hong Kong 999077, China"
                        ],
                        "is_corresponding_author": False,
                    },
                    {
                        "name": "Kun Xu",
                        "affiliations": [
                            "Shenzhen Institutes of Advanced Technology, Chinese Academy of Sciences, Shenzhen 518055, China"
                        ],
                        "is_corresponding_author": False,
                    },
                    {
                        "name": "Tianfu Sun",
                        "affiliations": [
                            "Shenzhen Institutes of Advanced Technology, Chinese Academy of Sciences, Shenzhen 518055, China"
                        ],
                        "is_corresponding_author": False,
                    },
                    {
                        "name": "Haiping Du",
                        "affiliations": [
                            "School of Electrical, Computer and Telecommunications Engineering, University of Wollongong, Wollongong 2522, Australia"
                        ],
                        "is_corresponding_author": False,
                    },
                ],
                "abstract": "The coordinated control of a blended braking system is always a difficult task. In particular, blended braking control becomes more challenging when the braking actuator has an input time-delay and some states of the braking system cannot be measured. In order to improve the tracking performance, a coordinated control system was designed based on the input time-delay and state observation for a blended braking system comprising a motor braking system and friction braking system. The coordinated control consists of three parts: Sliding mode control, a multi-input single-output observer, and time-delay estimation-based Smith Predictor control. The sliding mode control is used to calculate the total command braking torque according to the desired braking performance and vehicle states. The multi-input single-output observer is used to simultaneously estimate the input time-delay and output braking torque of the friction braking system. With time-delay estimation-based Smith Predictor control, the friction braking system is able to effectively track the command braking torque of the friction braking system. The tracking of command braking torque is realized through the coordinated control of the motor braking system and friction braking system. In order to validate the effectiveness of the proposed approach, numerical simulations on a quarter-vehicle braking model were performed.",
            },
        }
    ]
