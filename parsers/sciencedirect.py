import json

from exceptions import AuthorNotFoundError
from parser import Parser


class ScienceDirect(Parser):
    parser_name = "sciencedirect"

    def is_correct_parser(self):
        header_link = self.soup.find("link", {"rel": "canonical"})
        if header_link and "sciencedirect.com" in header_link["href"]:
            return True

    def parse(self):
        """Core function returning list of authors with their affiliations."""
        authors = self.get_authors()
        affiliations = self.get_affiliations()
        authors_affiliations = self.match_authors_to_affiliations(authors, affiliations)
        return authors_affiliations

    def get_authors(self):
        """Finds authors in sciencedirect using beautifulsoup."""
        authors = []
        author_soup = self.soup.find_all("a", class_="author")

        if not author_soup:
            raise AuthorNotFoundError("Authors not found within sciencedirect parser.")

        for a in author_soup:
            affiliation_id_1 = a["name"]
            affiliations_ids = [affiliation_id_1]
            author_name = ""

            for item in a.span:
                if item.has_attr("class") and item["class"][0] == "author-ref":
                    affiliation_id_2 = item["id"]
                    affiliations_ids.append(affiliation_id_2)
                else:
                    author_name = author_name + " " + item.text
            author_name = author_name.strip()
            authors.append(
                {"author_name": author_name, "affiliation_ids": affiliations_ids}
            )
        return authors

    def get_affiliations(self):
        """Returns affiliation data in form of {"id": "asdf", "text": "asdf"}"""
        science_direct_json = self.extract_json()
        affiliations = self.find_affiliations(science_direct_json)
        return affiliations

    def extract_json(self):
        """Finds and loads json that contains affiliation data."""
        raw_json = self.soup.find("script", type="application/json").text
        loaded_json = json.loads(raw_json)
        return loaded_json

    @staticmethod
    def find_affiliations(data):
        """Parse the json data to find affiliations along with their IDs."""
        level_1 = data["authors"]["content"]

        level_2 = []
        for item_1 in level_1:
            for item_2 in item_1["$$"]:
                if item_2.get("#name") == "affiliation":
                    level_2.append(item_2)

        affiliations = []
        for aff in level_2:
            aff_text = None
            aff_id = aff["$"]["id"]

            for item_3 in aff["$$"]:
                if item_3["#name"] == "textfn":
                    aff_text = item_3.get("_")
                    if not aff_text:
                        # alternate method
                        level_4 = item_3.get("$$")
                        if level_4:
                            aff_text = []
                            for item_4 in level_4:
                                if item_4["#name"] == "__text__":
                                    aff_text.append(item_4["_"])
                            aff_text = "".join(aff_text)
            affiliations.append({"id": aff_id, "text": aff_text})
        return affiliations

    def match_authors_to_affiliations(self, authors, affiliations):
        """Go through authors and affiliates and match them up using IDs."""
        authors_affiliations = []
        for author in authors:
            affiliation_list = []
            matching_ids = self.find_matching_ids(
                affiliations, author["affiliation_ids"]
            )
            for a in affiliations:
                for matching_id in matching_ids:
                    if a["id"] == matching_id:
                        found_affiliation = a["text"]
                        affiliation_list.append(found_affiliation)

                # default scenario assign to aff
                if (
                    not matching_ids
                    and len(affiliations) == 1
                    and affiliations[0]["id"].startswith("aff")
                ):
                    affiliation_list.append(affiliations[0]["text"])
            authors_affiliations.append(
                {"name": author["author_name"], "affiliations": affiliation_list}
            )
        return authors_affiliations

    @staticmethod
    def find_matching_ids(affiliations, affiliation_ids):
        matching_ids = []
        # option 1 AFF1
        for aff_id in affiliation_ids:
            for aff in affiliations:
                if aff_id[1:].lower().startswith("af") and aff_id[1:] == aff["id"]:
                    matching_ids.append(aff_id[1:])

        # option 2 aep-author-id2
        for aff_id in affiliation_ids:
            for aff in affiliations:
                if not matching_ids and aff_id.startswith("baep-author-id"):
                    ref_id_num = int(aff_id[-1])
                    aff_id = aff["id"].rstrip(aff["id"][-1]) + str(ref_id_num + 1)
                    matching_ids.append(aff_id)

        matching_ids = list(set(matching_ids))  # remove duplicates
        return matching_ids


test_cases = [
    {
        "doi": "10.1016/0022-247x(78)90205-6",
        "result": [
            {
                "name": "Pierre Charrier",
                "affiliations": [
                    "U.E.R. de Mathématiques et Informatique et Laboratoire associé au C.N.R.S. n∘ 226, Université de Bordeaux 1, 33405 Talence, France"
                ],
            },
            {
                "name": "Giovanni M Troianiello",
                "affiliations": [
                    "Istituto Matematico, Universitá di Roma, 00185 Rome, Italy"
                ],
            },
        ],
    },
    {
        "doi": "10.1016/0022-247x(79)90002-7",
        "result": [
            {
                "name": "N Levan",
                "affiliations": [
                    "Department of System Science, 4532 Boelter Hall, University of California, Los Angeles, California 90024 U.S.A."
                ],
            },
            {
                "name": "L Rigby",
                "affiliations": [
                    "Department of Computing and Control, Huxley Building, Imperial College, London SW7 2BZ, Great Britain"
                ],
            },
        ],
    },
    {
        "doi": "10.1016/0022-247x(77)90164-0",
        "result": [
            {
                "name": "László Losonczi",
                "affiliations": [
                    "Department of Mathematics, University of Lagos, Lagos, Nigeria",
                    "Department of Mathematics, Kossuth Lajos University, Debrecen, Hungary",
                ],
            },
        ],
    },
    {
        "doi": "10.1016/0024-3795(85)90253-8",
        "result": [
            {
                "name": "Donald W. Robinson",
                "affiliations": [
                    "Department of Mathematics Brigham Young University Provo, Utah 84602, USA"
                ],
            },
        ],
    },
    {
        "doi": "10.1016/0024-3795(86)90148-5",
        "result": [
            {
                "name": "Robert E. Hartwig",
                "affiliations": [
                    "Department of Mathematics North Carolina State University Box 8205 Raleigh, North Carolina 27695-820 USA"
                ],
            },
            {
                "name": "George P.H. Styan",
                "affiliations": [
                    "Department of Mathematics and Statistics McGill University 805 ouest, rue Sherbrooke Montréal, Québec, Canada H3A 2K6"
                ],
            },
        ],
    },
    {
        "doi": "10.1016/j.ab.2021.114100",
        "result": [
            {
                "name": "Emma Dreischmeier",
                "affiliations": [
                    "Wisconsin Institutes of Medical Research, University of Wisconsin-Madison, Madison, WI, USA"
                ],
            },
            {
                "name": "William E. Fahl",
                "affiliations": [
                    "Wisconsin Institutes of Medical Research, University of Wisconsin-Madison, Madison, WI, USA"
                ],
            },
        ],
    },
    {
        "doi": "10.1016/j.ab.2021.114241",
        "result": [
            {
                "name": "Jun Hu",
                "affiliations": [
                    "College of Information Engineering, Zhejiang University of Technology, Hangzhou, 310023, China"
                ],
            },
            {
                "name": "Lin-Lin Zheng",
                "affiliations": [
                    "College of Information Engineering, Zhejiang University of Technology, Hangzhou, 310023, China"
                ],
            },
            {
                "name": "Yan-Song Bai",
                "affiliations": [
                    "College of Information Engineering, Zhejiang University of Technology, Hangzhou, 310023, China"
                ],
            },
            {
                "name": "Ke-Wen Zhang",
                "affiliations": [
                    "College of Mechanical Engineering, Zhejiang University of Technology, Hangzhou, 310023, China"
                ],
            },
            {
                "name": "Dong-Jun Yu",
                "affiliations": [
                    "School of Computer Science and Engineering, Nanjing University of Science and Technology,Xiaolingwei 200, Nanjing, 210094, China"
                ],
            },
            {
                "name": "Gui-Jun Zhang",
                "affiliations": [
                    "College of Information Engineering, Zhejiang University of Technology, Hangzhou, 310023, China"
                ],
            },
        ],
    },
]
