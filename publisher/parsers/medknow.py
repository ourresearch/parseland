from publisher.elements import Author, Affiliation
from publisher.parsers.parser import PublisherParser


class MedKnow(PublisherParser):
    parser_name = "medknow"

    def is_publisher_specific_parser(self):
        script_url = "https://www.medknow.com/ss/ftr.js"
        return script_url in str(self.soup)

    def authors_found(self):
        return self.soup.find("font", class_="articleAuthor")

    def parse(self):
        authors = self.get_authors()
        if not authors:
            # try meta tags
            return self.parse_meta_tags()

        affiliations = self.get_affiliations()
        authors_affiliations = self.merge_authors_affiliations(authors, affiliations)
        return authors_affiliations

    def get_authors(self):
        results = []
        author_soup = self.soup.find("font", class_="articleAuthor")
        if not author_soup:
            return None

        authors = author_soup.findAll("a")
        affiliations = author_soup.findAll("sup")

        # method 1
        if not authors and not affiliations:
            authors = author_soup.text.split(",")
            if authors:
                for author in authors:
                    name = author.strip()
                    results.append(Author(name=name, aff_ids=[]))
            return results

        # method 2
        for author, affiliation in zip(authors, affiliations):
            name = author.text.strip()
            aff_ids = self.format_ids(affiliation.text.strip())
            results.append(Author(name=name, aff_ids=aff_ids))
        return results

    def get_affiliations(self):
        aff_soup = self.soup.find("font", class_="AuthorAff")

        results = []
        if aff_soup:
            affiliations = aff_soup.findAll("sup")
            # method 1
            if not affiliations:
                organization = aff_soup.text.strip()
                results.append(Affiliation(organization=organization, aff_id=None))

            # method 2
            for aff in affiliations:
                # affiliation id
                aff_id = aff.text
                if aff_id.isdigit():
                    aff_id = int(aff_id)

                # affiliation
                organization = aff.next_sibling.text.strip()
                results.append(Affiliation(organization=organization, aff_id=aff_id))
        return results

    test_cases = [
        {
            "doi": "10.4103/djo.djo_93_20",
            "result": [
                {
                    "name": "Saleh A Naguib",
                    "affiliations": [
                        "Ophthalmology Department, Imbaba Ophthalmology Hospital, Cairo, Egypt"
                    ],
                },
                {
                    "name": "Omar A Barada",
                    "affiliations": [
                        "Ophthalmology Department, Faculty of Medicine, Cairo University, Cairo, Egypt"
                    ],
                },
                {
                    "name": "Esraa El-Mayah",
                    "affiliations": [
                        "Ophthalmology Department, Faculty of Medicine, Cairo University, Cairo, Egypt"
                    ],
                },
                {
                    "name": "Hany E Elmekawey",
                    "affiliations": [
                        "Ophthalmology Department, Faculty of Medicine, Cairo University, Cairo, Egypt"
                    ],
                },
            ],
        },
    ]
