from publisher.parsers.parser import PublisherParser


class Sage(PublisherParser):
    parser_name = "Sage"

    def is_correct_parser(self):
        return self.domain_in_meta_og_url("journals.sagepub.com")

    def authors_found(self):
        return self.soup.find("div", class_="authors")

    def parse(self):
        results = []
        author_section = self.soup.find("div", class_="authors")
        author_soup = author_section.findAll("div", class_="authorLayer")
        for author in author_soup:
            name = author.find("a", class_="entryAuthor").text
            affiliations = []

            # method 1
            affiliation_breaks = author.findAll("div", class_="aff-newLine")
            for aff_break in affiliation_breaks:
                affiliations.append(aff_break.next_sibling)

            # method 2
            if not affiliations:
                section_div = author.find("div", class_="author-section-div")
                if section_div:
                    affiliation = section_div.next_element
                    if isinstance(affiliation, str):
                        affiliations.append(affiliation)

            results.append({"name": name.strip(), "affiliations": affiliations})
        return results

    test_cases = [
        {
            "doi": "10.1177/1099636221998180",
            "result": [
                {
                    "name": "RS Jayaram",
                    "affiliations": [
                        "Department of Mechanical Engineering, Amrita College of Engineering and Technology, Nagercoil, Tamil Nadu, India"
                    ],
                },
                {
                    "name": "VA Nagarajan",
                    "affiliations": [
                        "Department of Mechanical Engineering, University College of Engineering, Konam Post, Tamil Nadu, India"
                    ],
                },
                {
                    "name": "KP Vinod Kumar",
                    "affiliations": [
                        "Department of Chemistry, University College of Engineering, Konam Post, Tamil Nadu, India"
                    ],
                },
            ],
        },
        {
            "doi": "10.1177/20514158211000196",
            "result": [
                {
                    "name": "Malik Abdul Rouf",
                    "affiliations": [],
                },
                {"name": "Venkatesh Kumar", "affiliations": []},
                {"name": "Anshuman Agarwal", "affiliations": []},
                {"name": "Suresh Rawat", "affiliations": []},
            ],
        },
        {
            "doi": "10.1177/0271678X211039593",
            "result": [
                {
                    "name": "Mehdi Taslimifar",
                    "affiliations": [
                        "The Interface Group, Institute of Physiology, University of Zürich, Zürich, Switzerland",
                        "Epithelial Transport Group, Institute of Physiology, University of Zürich, Zürich, Switzerland",
                    ],
                },
                {
                    "name": "Martin Faltys",
                    "affiliations": [
                        "Epithelial Transport Group, Institute of Physiology, University of Zürich, Zürich, Switzerland",
                        "Department of Intensive Care Medicine, University Hospital, University of Bern, Bern, Switzerland",
                    ],
                },
                {
                    "name": "Vartan Kurtcuoglu",
                    "affiliations": [
                        "The Interface Group, Institute of Physiology, University of Zürich, Zürich, Switzerland",
                        "National Center of Competence in Research, Kidney CH, Switzerland",
                    ],
                },
                {
                    "name": "François Verrey",
                    "affiliations": [
                        "Epithelial Transport Group, Institute of Physiology, University of Zürich, Zürich, Switzerland",
                        "National Center of Competence in Research, Kidney CH, Switzerland",
                    ],
                },
                {
                    "name": "Victoria Makrides",
                    "affiliations": [
                        "The Interface Group, Institute of Physiology, University of Zürich, Zürich, Switzerland",
                        "Epithelial Transport Group, Institute of Physiology, University of Zürich, Zürich, Switzerland",
                        "EIC BioMedical Labs, Norwood, MA, USA",
                    ],
                },
            ],
        },
        {
            "doi": "10.1177/00219096211045098",
            "result": [
                {
                    "name": "Muhammad Abdul Kamal",
                    "affiliations": [
                        "Department of Economics, Abdul Wali Khan University Mardan, KPK, Pakistan"
                    ],
                },
                {
                    "name": "Unbreen Qayyum",
                    "affiliations": [
                        "Department of Economics, Henan University, Kaifeng, P.R. China"
                    ],
                },
                {
                    "name": "Saleem Khan",
                    "affiliations": [
                        "Department of Economics, Abdul Wali Khan University Mardan, KPK, Pakistan"
                    ],
                },
                {
                    "name": "Bosede Ngozi Adeleye",
                    "affiliations": [
                        "Department of Economics and Development Studies, Covenant University, Nigeria"
                    ],
                },
            ],
        },
    ]
