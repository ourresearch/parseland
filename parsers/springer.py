from collections import defaultdict
from unicodedata import normalize

from exceptions import AuthorNotFoundError


class Springer:
    def __init__(self, soup):
        self.soup = soup
        self.parser_name = "springer"

    def is_correct_parser(self):
        header_link = self.soup.find("link", {"rel": "canonical"})
        if header_link and "link.springer.com" in header_link["href"]:
            return True

    def parse(self):
        authors = self.get_authors()
        if authors:
            affiliations = self.get_affiliations()
            authors_affiliations = self.combine_authors_affiliations(
                authors, affiliations
            )
        else:
            authors_affiliations = self.get_authors_method_2()

        if not authors_affiliations:
            raise AuthorNotFoundError(f"Author not found within parser {self.parser_name}")
        return authors_affiliations

    def get_authors(self):
        authors = []
        section = self.soup.find(id="authorsandaffiliations")
        if not section:
            return None
        author_soup = section.findAll("li", {"itemprop": "author"})
        for author in author_soup:
            ref_ids = []
            references = author.find("ul", {"data-role": "AuthorsIndexes"})
            if references:
                for reference in references:
                    ref_ids.append(int(reference.text))
            name = normalize("NFKD", author.span.text)
            authors.append({"name": name, "ref_ids": ref_ids})
        return authors

    def get_affiliations(self):
        affiliations = {}
        section = self.soup.find(id="authorsandaffiliations")
        aff_soup = section.findAll("li", class_="affiliation")
        for aff in aff_soup:
            aff_id = int(aff["data-affiliation-highlight"][-1])

            # get affiliations
            spans = aff.findAll("span")
            affiliation_data = []
            for span in spans:
                if span.has_attr("itemprop") and span["itemprop"] != "address":
                    affiliation_data.append(span.text)
            affiliation = ", ".join(affiliation_data)

            affiliations[aff_id] = affiliation
        return affiliations

    def combine_authors_affiliations(self, authors, affiliations):
        results = []
        for author in authors:
            matched_affiliations = []
            for ref_id in author["ref_ids"]:
                if ref_id in affiliations.keys():
                    matched_affiliations.append(affiliations[ref_id])
            results.append(
                {"name": author["name"], "affiliations": matched_affiliations}
            )
        return results

    def get_authors_method_2(self):
        """Loop through meta tags to build author and affiliations."""
        results = []
        metas = self.soup.findAll("meta")

        result = None
        for meta in metas:
            if meta.get("name", None) and meta["name"] == "citation_author":
                if result:
                    # reset for next author
                    results.append(result)
                    result = None
                name = self.format_name(meta["content"])
                result = {"name": name, "affiliations": [], }
            if meta.get("name", None) and meta["name"] == "citation_author_institution":
                result["affiliations"].append(meta["content"])

        # append name from last loop
        if result:
            results.append(result)

        print(results)
        return results

    @staticmethod
    def format_name(name):
        return ' '.join(reversed(name.split(', ')))

test_cases = [
    {
        "doi": "10.1007/978-0-387-39343-8_21",
        "result": [
            {
                "name": "Pascal Boileau",
                "affiliations": [
                    "Orthopaedic Surgery and Sports Traumatology, University of Nice-Sophia Antipolis, Nice, France"
                ],
            },
            {
                "name": "Christopher R. Chuinard",
                "affiliations": [
                    "Great Lakes Orthopaedic Center, Munson Medical Center, Traverse City, USA"
                ],
            },
        ],
    },
    {
        "doi": "10.1007/0-306-48581-8_22",
        "result": [
            {
                "name": "L. Michael Ascher",
                "affiliations": [
                    "Department of Psychology, Philadelphia College of Osteopathic Medicine, Philadelphia"
                ],
            },
            {
                "name": "Christina Esposito",
                "affiliations": [
                    "Department of Psychology, Philadelphia College of Osteopathic Medicine, Philadelphia"
                ],
            },
        ],
    },
    {
        "doi": "10.1007/0-306-48688-1_15",
        "result": [
            {
                "name": "Ping Zhang",
                "affiliations": [
                    "Department of Medicine, Section of Pulmonary and Critical Care Medicine, and Alcohol Research Center, Louisiana State University Health Sciences Center, New Orleans"
                ],
            },
            {
                "name": "Gregory J. Bagby",
                "affiliations": [
                    "Department of Medicine, Section of Pulmonary and Critical Care Medicine, Department of Physiology, and Alcohol Research Center, Louisiana State University Health Sciences Center, New Orleans"
                ],
            },
            {
                "name": "Jay K. Kolls",
                "affiliations": [
                    "Department of Medicine, Section of Pulmonary and Critical Care Medicine, Alcohol Research Center and Gene Therapy Programs, Louisiana State University Health Sciences Center, New Orleans"
                ],
            },
            {
                "name": "Lee J. Quinton",
                "affiliations": [
                    "Department of Physiology and Alcohol Research Center, Louisiana State University Health Sciences Center, New Orleans"
                ],
            },
            {
                "name": "Steve Nelson",
                "affiliations": [
                    "Department of Medicine, Section of Pulmonary and Critical Care Medicine, Department of Physiology, and Alcohol Research Center, Louisiana State University Health Sciences Center, New Orleans"
                ],
            },
        ],
    },
    {
        "doi": "10.1007/0-306-48581-8_7",
        "result": [
            {
                "name": "Christine Bowman Edmondson",
                "affiliations": [],
            },
            {
                "name": "Daniel Joseph Cahill",
                "affiliations": [
                    "Department of Psychology, California State University, Fresno, Fresno"
                ],
            },
        ],
    },
    {
        "doi": "10.3758/s13414-014-0792-2",
        "result": [
            {
                "name": "Odette Scharenborg",
                "affiliations": [
                    "Centre for Language Studies, Radboud University Nijmegen, Nijmegen, The Netherlands",
                    "Donders Institute for Brain, Cognition, and Behaviour, Radboud University Nijmegen, Nijmegen, The Netherlands"
                ],
            },
            {
                "name": "Andrea Weber",
                "affiliations": [
                    "Max Planck Institute for Psycholinguistics, Nijmegen, The Netherlands",
                    "Donders Institute for Brain, Cognition, and Behaviour, Radboud University Nijmegen, Nijmegen, The Netherlands"
                ],
            },
            {
                "name": "Esther Janse",
                "affiliations": [
                    "Centre for Language Studies, Radboud University Nijmegen, Nijmegen, The Netherlands",
                    "Donders Institute for Brain, Cognition, and Behaviour, Radboud University Nijmegen, Nijmegen, The Netherlands",
                    "Max Planck Institute for Psycholinguistics, Nijmegen, The Netherlands"
                ],
            },

        ]
    }
]