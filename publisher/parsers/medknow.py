import re

from bs4 import BeautifulSoup

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
        if authors:
            affiliations = self.get_affiliations()
            authors_affiliations = self.merge_authors_affiliations(
                authors, affiliations
            )
        else:
            # try meta tags
            authors_affiliations = self.parse_meta_tags(
                corresponding_tag="font", corresponding_class="CorrsAdd"
            )

        abstract = self.parse_abstract_meta_tags()
        try:
            abstract = BeautifulSoup(abstract, "html.parser").text
            abstract = re.sub(r"^abstract[:.]?\s*", "", abstract, flags=re.I)
        except Exception:
            pass

        return {"authors": authors_affiliations, "abstract": abstract}

    def get_authors(self):
        results = []
        author_soup = self.soup.find("font", class_="articleAuthor")
        if not author_soup:
            return None

        authors = author_soup.findAll("a")
        affiliations = author_soup.findAll("sup")
        corresponding_text = self.get_corresponding_text("font", "CorrsAdd")
        is_corresponding = False

        # method 1
        if not authors and not affiliations:
            authors = author_soup.text.split(",")
            if authors:
                for author in authors:
                    name = author.strip()
                    if corresponding_text and name.lower() in corresponding_text:
                        is_corresponding = True
                    results.append(
                        Author(
                            name=name,
                            aff_ids=[],
                            is_corresponding=is_corresponding,
                        )
                    )
            return results

        # method 2
        for author, affiliation in zip(authors, affiliations):
            name = author.text.strip()
            if corresponding_text and name.lower() in corresponding_text:
                is_corresponding = True
            aff_ids = self.format_ids(affiliation.text.strip())
            results.append(
                Author(name=name, aff_ids=aff_ids, is_corresponding=is_corresponding)
            )
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

    def get_corresponding_text(self, html_tag, class_name):
        text = None
        corresponding_soup = self.soup.find(html_tag, class_=class_name)
        if corresponding_soup:
            text = corresponding_soup.text
            text = text.replace("  ", " ").lower()
        return text

    test_cases = [
        {
            "doi": "10.4103/djo.djo_93_20",
            "result": {
                "authors": [
                    {
                        "name": "Saleh A Naguib",
                        "affiliations": [
                            "Ophthalmology Department, Imbaba Ophthalmology Hospital, Cairo, Egypt"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Omar A Barada",
                        "affiliations": [
                            "Ophthalmology Department, Faculty of Medicine, Cairo University, Cairo, Egypt"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Esraa El-Mayah",
                        "affiliations": [
                            "Ophthalmology Department, Faculty of Medicine, Cairo University, Cairo, Egypt"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Hany E Elmekawey",
                        "affiliations": [
                            "Ophthalmology Department, Faculty of Medicine, Cairo University, Cairo, Egypt"
                        ],
                        "is_corresponding": True,
                    },
                ],
                "abstract": "Purpose The purpose of this study was to detect single or multiple best-performing parameters of corneal tomography and dynamic corneal biomechanics with high sensitivity and specificity in the diagnosis of keratoconus, subclinical keratoconus (SCKC), and forme fruste keratoconus (FFKC).Design This was a prospective observational study.Patients and methods In this study, one eye of each of 40 participants was included. They were divided into four groups: keratoconus, SCKC, FFKC, and a normal control group, with 10 participants in each group. All participants underwent a full ophthalmologic examination, analysis of corneal tomography using Pentacam HR and analysis of corneal biomechanical response using the Corvis ST at the initial visit and after 3 months.Results For the diagnosis of keratoconus, the 100% sensitive and specific parameters were Belin/Ambrósio Enhanced Ectasia Display (BAD d), Ambrósio’s relational thickness maximum (ARTmax), and tomographic biomechanical index (TBI) with cutoff values of 1.905, 344, and 0.785, respectively. For detection of SCKC, the 100% sensitive parameters were maximum keratometry and thickness profile index with cutoff values of 44.7 and 0.945, respectively. After 3 months of follow-up, maximum keratometry, index of surface variance, deflection amplitude, and deflection area showed 100% sensitivity with specificities of 90, 80, 70, and 60%, respectively. The highest percentage of change over time was for the index of highest decentration by 200%, followed by TBI by 133%. For FFKC, the deformation amplitude and corneal velocity 1 showed sensitivity of 90 and 80%, respectively, and specificity of 83 and 90%, respectively. After follow-up BAD d, deformation amplitude, deformation amplitude ratio, and TBI showed 100% sensitivity and specificity.Conclusion This study illustrated the efficacy of Corvis parameters for the diagnosis of keratoconus, but with lower discriminative ability than corneal tomography. It could also be used as a supplementary tool for the diagnosis and follow-up of SCKC and FFKC patients.",
            },
        },
    ]
