from publisher.elements import Author, Affiliation
from publisher.parsers.parser import PublisherParser


class SPIE(PublisherParser):
    parser_name = "SPIE"

    def is_publisher_specific_parser(self):
        link = self.soup.find("a", class_="logo")
        return link and "spie.org" in link.get("href")

    def authors_found(self):
        return self.soup.find(id="affiliations")

    def parse(self):
        authors = self.get_authors()
        affiliations = self.get_affiliations()
        authors_affiliations = self.merge_authors_affiliations(authors, affiliations)
        return authors_affiliations

    def get_authors(self):
        authors = []
        author_soup = self.soup.find(id="affiliations")
        # find and remove orcid link
        links = author_soup.findAll("a")
        for link in links:
            if "orcid.org" in link.get("href"):
                link.decompose()

        author_soup = author_soup.b.findAll("sup")
        for author in author_soup:
            name = str(author.previous_sibling).strip()
            if name.endswith(","):
                name = name[:-1]
            aff_ids_raw = author.text
            aff_ids = []
            for aff_id_raw in aff_ids_raw:
                aff_id = aff_id_raw.strip()
                if aff_id:
                    aff_ids.append(aff_id)
            authors.append(Author(name=name, aff_ids=aff_ids))
        return authors

    def get_affiliations(self):
        aff_soup = self.soup.find(id="affiliations")

        results = []
        if aff_soup:
            affiliations = aff_soup.find("br").find_next_siblings("sup")
            for affiliation in affiliations:
                # affiliation id
                aff_id = affiliation.text
                affiliation.clear()

                # affiliation
                aff = affiliation.next_element.strip()
                results.append(Affiliation(organization=aff, aff_id=aff_id))
        return results

    test_cases = [
        {
            "doi": "10.1117/12.2602977",
            "result": [
                {
                    "name": "Le Li",
                    "affiliations": [
                        "Naval Univ. of Engineering (China)",
                    ],
                },
                {
                    "name": "Zhi-hao Ye",
                    "affiliations": ["Naval Univ. of Engineering (China)"],
                },
                {
                    "name": "Yi-hui Xia",
                    "affiliations": [
                        "Naval Univ. of Engineering (China)",
                    ],
                },
            ],
        },
    ]
