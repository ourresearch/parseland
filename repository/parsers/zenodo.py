import json

from repository.parsers.parser import RepositoryParser


class Zenodo(RepositoryParser):
    parser_name = "Zenodo"

    def is_correct_parser(self):
        return self.domain_in_meta_og_url("zenodo.org/record/")

    def authors_found(self):
        return self.soup.find("script", {"type": "application/ld+json"})

    def parse(self):
        authors = []

        for ld_json in self.soup.find_all("script", {"type": "application/ld+json"}):
            article_metadata = json.loads(ld_json.text)
            for creator in article_metadata.get("creator", []):
                if creator.get("@type") == "Person":
                    name = creator.get("name")
                    affiliations = []

                    json_affiliation = creator.get("affiliation")
                    if isinstance(json_affiliation, str):
                        affiliations = [json_affiliation]
                    elif isinstance(json_affiliation, list):
                        affiliations = json_affiliation

                    authors.append({"name": name, "affiliations": affiliations})

        return {"authors": authors}

    test_cases = [
        {
            "page-id": "PPUy5baHbVk44dssWdcx",  # https://zenodo.org/record/5580983
            "result": {
                "authors": [
                    {
                        "name": "Gattu Vijaya Kumar",
                        "affiliations": [
                            "Department of Computer Science and  Engineering, Sreenidhi Institute of Science and Technology, Yamnampet,  Ghatkesar, Hyderabad, Telangana, India."
                        ],
                    },
                    {
                        "name": "Prasanta Kumar Sahoo",
                        "affiliations": [
                            "Department of Computer Science and  Engineering, Sreenidhi Institute of Science and Technology, Yamnampet,  Ghatkesar, Hyderabad, Telangana, India."
                        ],
                    },
                    {
                        "name": "K.Eswaran",
                        "affiliations": [
                            "Department of Computer Science and  Engineering, Sreenidhi Institute of Science and Technology, Yamnampet,  Ghatkesar, Hyderabad, Telangana, India."
                        ],
                    },
                ]
            },
        },
    ]
