from publisher.elements import Author, Affiliation
from publisher.parsers.parser import PublisherParser


class Copernicus(PublisherParser):
    parser_name = "copernicus"
    chars_to_ignore = ["*", "†", "‡", "§"]

    def is_publisher_specific_parser(self):
        link = self.soup.find("link", {"rel": "preconnect"})
        if link and "copernicus.org" in link.get("href"):
            return True

    def authors_found(self):
        return self.soup.find("span", class_="authors-full")

    def parse(self):
        authors = self.get_authors()
        affiliations = self.get_affiliations()
        authors_affiliations = self.merge_authors_affiliations(authors, affiliations)
        return authors_affiliations

    def get_authors(self):
        authors = []
        author_soup = self.soup.find("span", class_="authors-full")
        author_soup = author_soup.findAll("nobr")
        for author in author_soup:
            if author.sup:
                aff_ids = self.format_ids(author.sup.text, self.chars_to_ignore)
                author.sup.clear()
            else:
                aff_ids = []
            name = author.text
            # clean name
            if name.endswith(","):
                name = name[:-1].strip()
            if name.startswith("and"):
                name = name[3:].strip()
            authors.append(Author(name=name, aff_ids=aff_ids))
        return authors

    def get_affiliations(self):
        aff_soup = self.soup.find("ul", class_="affiliation-list")

        results = []
        if aff_soup:
            affiliations = aff_soup.findAll("li")
            for aff_raw in affiliations:
                # affiliation id
                aff_id_raw = aff_raw.find("sup")
                if aff_id_raw:
                    aff_id = aff_id_raw.text
                    aff_id_raw.clear()
                else:
                    aff_id = None

                # affiliation
                aff = aff_raw.text
                if aff_id and aff_id.isdigit():
                    aff_id = int(aff_id)
                results.append(Affiliation(organization=aff, aff_id=aff_id))
        return results

    test_cases = [
        {
            "doi": "10.5194/hess-2021-324-rc2",
            "result": [
                {
                    "name": "Jared D. Smith",
                    "affiliations": [
                        "Department of Engineering Systems and Environment, University of Virginia, Charlottesville, VA, USA",
                    ],
                },
                {
                    "name": "Laurence Lin",
                    "affiliations": [
                        "Department of Environmental Sciences, University of Virginia, Charlottesville, VA, USA"
                    ],
                },
                {
                    "name": "Julianne D. Quinn",
                    "affiliations": [
                        "Department of Engineering Systems and Environment, University of Virginia, Charlottesville, VA, USA",
                    ],
                },
                {
                    "name": "Lawrence E. Band",
                    "affiliations": [
                        "Department of Engineering Systems and Environment, University of Virginia, Charlottesville, VA, USA",
                        "Department of Environmental Sciences, University of Virginia, Charlottesville, VA, USA",
                    ],
                },
            ],
        },
        {
            "doi": "10.5194/egusphere-egu21-5804",
            "result": [
                {
                    "name": "Shahbaz Chaudhry",
                    "affiliations": [
                        "University of Warwick, Physics, United Kingdom of Great Britain – England, Scotland, Wales (shahbaz.chaudhry@warwick.ac.uk)",
                    ],
                },
                {
                    "name": "Sandra Chapman",
                    "affiliations": [
                        "University of Warwick, Physics, United Kingdom of Great Britain – England, Scotland, Wales (shahbaz.chaudhry@warwick.ac.uk)"
                    ],
                },
                {
                    "name": "Jesper Gjerloev",
                    "affiliations": [
                        "University of Warwick, Physics, United Kingdom of Great Britain – England, Scotland, Wales (shahbaz.chaudhry@warwick.ac.uk)",
                    ],
                },
            ],
        },
    ]
