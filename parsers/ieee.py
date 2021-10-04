import json
import re

from parser import Parser


class IEEE(Parser):
    parser_name = "IEEE"

    def is_correct_parser(self):
        if self.domain_in_canonical_link("ieee.org"):
            return True

    def authors_found(self):
        return True

    def parse(self):
        authors = self.get_authors()
        return authors

    def get_authors(self):
        results = []
        json_data = self.get_json_data()
        authors = json_data["authors"]
        for author in authors:
            results.append(
                {"name": author["name"], "affiliations": author["affiliation"]}
            )
        return results

    def get_json_data(self):
        raw_script = re.search("xplGlobal.document.metadata=.*", str(self.soup))
        raw_json = raw_script.group()
        trimmed_json = raw_json.replace("xplGlobal.document.metadata=", "").replace(
            "};", "}"
        )
        json_data = json.loads(trimmed_json)
        return json_data

    test_cases = [
        {
            "doi": "10.1109/TAC.2021.3105318",
            "result": [
                {
                    "name": "Masih Haseli",
                    "affiliations": [
                        "Mechanical and Aerospace Engineering, University of California, San Diego, La Jolla, CA, United States of America, 92037 (e-mail: mhaseli@ucsd.edu)"
                    ],
                },
                {
                    "name": "Jorge Cortes",
                    "affiliations": [
                        "Mechanical and Aerospace Engineering, University of California, San Diego, La Jolla, California, United States of America, 92093 (e-mail: cortes@ucsd.edu)"
                    ],
                },
            ],
        },
    ]
