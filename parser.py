from gzip import decompress
import json

from bs4 import BeautifulSoup
import requests


class Parser:
    def __init__(self, doi):
        self.landing_page_endpoint = f"https://api.unpaywall.org/doi_page/{doi}"
        self.soup = self.get_soup()

    def get_html(self):
        r = requests.get(self.landing_page_endpoint)
        html = decompress(r.content)
        return html

    def get_soup(self):
        soup = BeautifulSoup(self.get_html(), "html.parser")
        return soup

    def authors_affiliations(self):
        """Core function returning list of authors with their affiliations."""
        authors = self.get_authors()
        affiliations = self.get_affiliations()
        authors_affiliations = self.match_authors_to_affiliations(authors, affiliations)
        return authors_affiliations

    def match_authors_to_affiliations(self, authors, affiliations):
        """Go through authors and affiliates and match them up using IDs."""
        authors_affiliations = []
        for author in authors:
            affiliation_list = []
            matching_id = self.find_matching_id(affiliations, author["references"])
            for a in affiliations:
                if a["id"] == matching_id:
                    found_affiliation = a["text"]
                    affiliation_list.append(found_affiliation)
            authors_affiliations.append(
                {"author": author["name"], "affiliations": affiliation_list}
            )
        return authors_affiliations

    def find_matching_id(self, affiliations, references):
        for ref in references:
            for aff in affiliations:
                ref_id = ref
                if ref_id.startswith("baep-author-id"):
                    ref_id_num = int(ref_id[-1])
                    aff_id = aff["id"].rstrip(aff["id"][-1]) + str(ref_id_num + 1)
                    return aff_id

    def get_affiliations(self):
        """
        Returns affiliation data in form of {"id": "asdf", "text": "asdf"}
        """
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

    def get_authors(self):
        """Finds authors in sciencedirect using beautifulsoup."""
        authors = []
        author_soup = self.soup.find_all("a", class_="author")

        for a in author_soup:
            ref_id = a["name"]
            author_references = [ref_id]
            name = ""

            for item in a.span:
                if item.has_attr("class") and item["class"][0] == "author-ref":
                    author_references.append(item["id"])
                else:
                    name = name + " " + item.text
            name = name.strip()
            authors.append({"name": name, "references": author_references})
        return authors


if __name__ == "__main__":
    p = Parser("10.1016/0022-247x(78)90205-6")
    p.authors_affiliations()
