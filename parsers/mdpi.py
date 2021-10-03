from parser import Parser


class MDPI(Parser):
    parser_name = "mdpi"

    def is_correct_parser(self):
        url = self.soup.find("meta", property="og:url")
        if url and "mdpi.com" in url.get("content"):
            return True

    def authors_found(self):
        return self.soup.find("div", class_="art-authors")

    def parse(self):
        authors = self.get_authors()
        affiliations = self.get_affiliations()
        authors_affiliations = self.get_authors_affiliations(authors, affiliations)
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
            authors.append({"name": name, "aff_ids": self.format_ids(author.sup.text)})
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
                if aff_id != "*" and aff_id != "†":
                    aff_id = int(aff_id) if aff_id else None
                    results.append({"aff_id": aff_id, "affiliation": aff})
        return results

    def get_authors_affiliations(self, authors, affiliations):
        results = []
        for author in authors:
            author_affiliations = []

            # scenario 1 affiliations with ids
            for aff_id in author["aff_ids"]:
                for affiliation in affiliations:
                    if aff_id == affiliation["aff_id"]:
                        author_affiliations.append(affiliation["affiliation"])

            # scenario 2 affiliations with no ids (applied to all authors)
            for affiliation in affiliations:
                if len(author["aff_ids"]) == 0 and affiliation["aff_id"] is None:
                    author_affiliations.append(affiliation["affiliation"])

            results.append(
                {"name": author["name"], "affiliations": author_affiliations}
            )
        return results

    @staticmethod
    def format_ids(ids):
        ids_cleaned = (
            ids.strip()
            .replace(",*", "")
            .replace("*", "")
            .replace(",†", "")
            .replace("†", "")
        )
        ids_split = ids_cleaned.split(",")
        aff_ids = []
        for aff_id in ids_split:
            if aff_id:
                aff_ids.append(int(aff_id))
        return aff_ids

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
