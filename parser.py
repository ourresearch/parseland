from gzip import decompress
import json

from bs4 import BeautifulSoup
import requests


class Parser:
    def __init__(self, doi):
        self.landing_page_endpoint = f"https://api.unpaywall.org/doi_page/{doi}"

    def get_html(self):
        r = requests.get(self.landing_page_endpoint)
        html = decompress(r.content)
        return html

    def get_soup(self):
        soup = BeautifulSoup(self.get_html(), "html.parser")
        return soup

    def get_affiliations(self):
        soup = self.get_soup()
        raw_json = soup.find("script", type="application/json").text
        data = json.loads(raw_json)

        results = self.parse_json(data)
        return results

    def parse_json(self, data):
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
