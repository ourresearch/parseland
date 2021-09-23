import json

from parser import Parser


class ScienceDirect(Parser):
    def __init__(self, doi):
        super().__init__(doi)
        self.parser_name = "sciencedirect"

    def authors_affiliations(self):
        """Core function returning list of authors with their affiliations."""
        authors = self.get_authors()
        affiliations = self.get_affiliations()
        authors_affiliations = self.match_authors_to_affiliations(authors, affiliations)
        return authors_affiliations

    def get_authors(self):
        """Finds authors in sciencedirect using beautifulsoup."""
        authors = []
        author_soup = self.soup.find_all("a", class_="author")

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

    def find_affiliations(self, data):
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
                    aff_text = item_3["_"]
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

    def find_matching_ids(self, affiliations, affiliation_ids):
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
