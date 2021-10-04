from unicodedata import normalize

from parser import Parser


class Wiley(Parser):
    parser_name = "wiley"

    def is_correct_parser(self):
        if self.domain_in_meta_og_url("onlinelibrary.wiley.com"):
            return True

    def authors_found(self):
        return self.soup.find("div", class_="loa-authors")

    def parse(self):
        authors = self.get_authors()
        return authors

    def get_authors(self):
        results = []
        author_soup = self.soup.find("div", class_="loa-authors")
        authors = author_soup.findAll("span", class_="accordion__closed")
        for author in authors:
            affiliations = []
            name = author.a.text
            aff_soup = author.findAll("p", class_=None)
            for aff in aff_soup:
                if (
                    "correspondence" in aff.text.lower()[:25]
                    or "address reprint" in aff.text.lower()[:40]
                    or "author deceased" in aff.text.lower()
                    or "e-mail:" in aff.text.lower()
                    or aff.text.lower().startswith("contribution")
                    or aff.text.lower().startswith("joint first authors")
                    or aff.text.lower().startswith("†joint")
                ):
                    break
                affiliations.append(normalize("NFKD", aff.text))
            results.append({"name": name, "affiliations": affiliations})
        return results

    test_cases = [
        {
            "doi": "10.1096/fba.2020-00145",
            "result": [
                {
                    "name": "Lia Tadesse Gebremedhin",
                    "affiliations": ["Minister of Health, Addis Ababa, Ethiopia"],
                },
                {
                    "name": "Tedla W. Giorgis",
                    "affiliations": [
                        "Advisor to the Minister, Ministry of Health, Addis Ababa, Ethiopia"
                    ],
                },
                {
                    "name": "Heran Gerba",
                    "affiliations": [
                        "Director-General, Ethiopian Food and Drug Administration, Addis Ababa, Ethiopia"
                    ],
                },
            ],
        },
    ]
