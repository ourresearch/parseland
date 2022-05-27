from publisher.elements import AuthorAffiliations
from publisher.parsers.parser import PublisherParser


class Taylor(PublisherParser):
    parser_name = "taylor"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url("tandfonline.com")

    def authors_found(self):
        return self.soup.find("div", class_="publicationContentAuthors")

    def parse(self):
        results = []
        author_soup = self.soup.find("div", class_="publicationContentAuthors")
        authors = author_soup.findAll("div", class_="entryAuthor")
        for author in authors:
            name = author.a.text

            correspondence_header = author.find("span", class_="heading")
            if (
                correspondence_header
                and correspondence_header.text.lower() == "correspondence"
            ):
                is_corresponding = True
            else:
                is_corresponding = False

            affiliations = []
            affiliation = author.find("span", class_="overlay")
            if affiliation:
                affiliation_trimmed = affiliation.contents[0].text[2:]
                affiliations.append(affiliation_trimmed)
            results.append(
                AuthorAffiliations(
                    name=name,
                    affiliations=affiliations,
                    is_corresponding_author=is_corresponding,
                )
            )
        return results

    test_cases = [
        {
            "doi": "10.1080/23311932.2021.1910156",
            "result": [
                {
                    "name": "Joseph Alulu",
                    "affiliations": [
                        "Department of Agricultural Economics, Faculty of Agriculture, University of Nairobi, Nairobi, Kenya"
                    ],
                },
                {
                    "name": "David Jakinda Otieno",
                    "affiliations": [
                        "Department of Agricultural Economics, Faculty of Agriculture, University of Nairobi, Nairobi, Kenya"
                    ],
                },
                {
                    "name": "Willis Oluoch-Kosura",
                    "affiliations": [
                        "Department of Agricultural Economics, Faculty of Agriculture, University of Nairobi, Nairobi, Kenya"
                    ],
                },
                {
                    "name": "Justus Ochieng",
                    "affiliations": ["World Vegetable Center, Arusha, Tanzania"],
                },
                {
                    "name": "Manuel Tejada Moral",
                    "affiliations": ["University of Seville, Seville, SPAIN"],
                },
            ],
        },
    ]
