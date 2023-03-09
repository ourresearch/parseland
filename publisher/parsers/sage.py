import re

from publisher.parsers.parser import PublisherParser
from publisher.utils import remove_parents


class Sage(PublisherParser):
    parser_name = "Sage"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url("journals.sagepub.com")

    def authors_found(self):
        return any([self.soup.find("div", class_="authors"),
                    self.soup.select('section.core-authors'),
                    self.soup.select('div.author.name')])

    def parse_abstract(self):
        if abs_header := self.soup.find(lambda tag: re.match('^h[1-6]$',
                                                             tag.name) and tag.text.strip().lower() == 'abstract'):
            if abs_tag := abs_header.find_next_sibling(
                    lambda tag: len(tag.text) > 100):
                return abs_tag.text.strip()
        selectors = ['section#abstract div', '.abstractInFull']
        for selector in selectors:
            if abs_tag := self.soup.select_one(selector):
                return abs_tag.text.strip()

        return None

    def _make_affiliations_list(self):
        affs = []
        aff_tags = self.soup.select('div.artice-info-affiliation')
        for i, aff_tag in enumerate(aff_tags):
            if aff_tag.sup:
                aff_tag.sup.decompose()
            name = aff_tag.text.strip()
            affs.append(name)
        return affs

    def _parse_sup_affiliations(self, author_tag):
        affiliations = []
        affs = self._make_affiliations_list()
        aff_sups = author_tag.find_all(
            lambda
                tag: tag.name == 'sup' and tag.text.strip().isnumeric())
        # if aff_sups:
        #     if len(author_tags) == 1:
        #         affiliations.extend(affs)
        #     else:
        for aff_sup in aff_sups:
            affiliations.append(
                affs[int(aff_sup.text.strip()) - 1])
        return affiliations

    def parse_authors_1(self):
        author_tags = self.soup.select('div.author.name .contribDegrees')
        authors = []
        for a_tag in author_tags:
            affiliations = []
            is_corresponding = None
            name = a_tag.select_one('.entryAuthor').text.strip()
            if 'no-aff' in a_tag['class']:
                aff_tags = []
                for tag in a_tag.find_next_siblings():
                    if 'artice-info-affiliation' not in tag.get('class', ''):
                        break
                    aff_tags.append(tag)
            else:
                aff_tags = a_tag.select('.artice-info-affiliation')

            for aff in aff_tags:
                affiliations.append(aff.text)

            if not affiliations:
                affiliations = self._parse_sup_affiliations(a_tag)

            authors.append({'name': name, 'affiliations': affiliations,
                            'is_corresponding': is_corresponding})

        corresponding_tags = self.soup.find_all(
            lambda tag: 'corresponding author' in tag.text.lower())
        corresponding_tags = remove_parents(corresponding_tags)
        corresponding_text = '\n'.join([tag.text for tag in corresponding_tags])
        if corresponding_text:
            for author in authors:
                if author['name'] in corresponding_text:
                    author['is_corresponding'] = True
                else:
                    author['is_corresponding'] = False
        return authors

    def parse_authors_2(self):
        author_tags = self.soup.select(
            'section.core-authors div[typeof=Person]')
        authors = []
        for author_tag in author_tags:
            given_name = author_tag.select_one(
                'span[property=givenName]').text
            family_name = author_tag.select_one(
                'span[property=familyName]').text
            name = f'{given_name} {family_name}'
            if hon_suffix_tag := author_tag.select_one(
                    'span[property=honorificSuffix]'):
                hon_suffix = hon_suffix_tag.text
                name += ', ' + hon_suffix
            aff_tags = author_tag.select('[property=affiliation]')
            affs = [aff_tag.text for aff_tag in aff_tags]
            is_corresponding = bool(author_tag.select_one('a[property=email]'))
            authors.append({'name': name, 'affiliations': affs,
                            'is_corresponding': is_corresponding})
        return authors

    def parse_authors_3(self):
        results = []
        if author_section := self.soup.select_one('.authors'):
            author_soup = author_section.findAll("div", class_="authorLayer")
        else:
            return results
        corresponding_text = self.get_corresponding_text()
        for author in author_soup:
            name = author.find("a", class_="entryAuthor").text.strip()
            if (
                    corresponding_text
                    and name.lower() in corresponding_text
                    and "corresponding" in corresponding_text
            ):
                is_corresponding = True
            elif corresponding_text:
                is_corresponding = False
            else:
                is_corresponding = None

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

            results.append(
                {
                    "name": name.strip(),
                    "affiliations": affiliations,
                    "is_corresponding": is_corresponding,
                }
            )
        return results

    def parse(self):
        authors = []
        for method in [self.parse_authors_1,
                       self.parse_authors_2,
                       self.parse_authors_3]:
            result = method.__call__()
            if result and not authors:
                authors = result
            if any([author['affiliations'] for author in result]):
                authors = result
                break
        return {"authors": authors, "abstract": self.parse_abstract()}

    def get_corresponding_text(self):
        article_notes = self.soup.find("div", class_="artice-notes")
        if article_notes:
            article_notes_text = article_notes.text.lower()
            return article_notes_text

    test_cases = [
        {
            "doi": "10.1177/1099636221998180",
            "result": [
                {
                    "name": "RS Jayaram",
                    "affiliations": [
                        "Department of Mechanical Engineering, Amrita College of Engineering and Technology, Nagercoil, Tamil Nadu, India"
                    ],
                    "is_corresponding": True,
                },
                {
                    "name": "VA Nagarajan",
                    "affiliations": [
                        "Department of Mechanical Engineering, University College of Engineering, Konam Post, Tamil Nadu, India"
                    ],
                    "is_corresponding": False,
                },
                {
                    "name": "KP Vinod Kumar",
                    "affiliations": [
                        "Department of Chemistry, University College of Engineering, Konam Post, Tamil Nadu, India"
                    ],
                    "is_corresponding": False,
                },
            ],
        },
        {
            "doi": "10.1177/20514158211000196",
            "result": [
                {
                    "name": "Malik Abdul Rouf",
                    "affiliations": [],
                    "is_corresponding": True,
                },
                {
                    "name": "Venkatesh Kumar",
                    "affiliations": [],
                    "is_corresponding": False,
                },
                {
                    "name": "Anshuman Agarwal",
                    "affiliations": [],
                    "is_corresponding": False,
                },
                {
                    "name": "Suresh Rawat",
                    "affiliations": [],
                    "is_corresponding": False,
                },
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
                    "is_corresponding": False,
                },
                {
                    "name": "Martin Faltys",
                    "affiliations": [
                        "Epithelial Transport Group, Institute of Physiology, University of Zürich, Zürich, Switzerland",
                        "Department of Intensive Care Medicine, University Hospital, University of Bern, Bern, Switzerland",
                    ],
                    "is_corresponding": False,
                },
                {
                    "name": "Vartan Kurtcuoglu",
                    "affiliations": [
                        "The Interface Group, Institute of Physiology, University of Zürich, Zürich, Switzerland",
                        "National Center of Competence in Research, Kidney CH, Switzerland",
                    ],
                    "is_corresponding": False,
                },
                {
                    "name": "François Verrey",
                    "affiliations": [
                        "Epithelial Transport Group, Institute of Physiology, University of Zürich, Zürich, Switzerland",
                        "National Center of Competence in Research, Kidney CH, Switzerland",
                    ],
                    "is_corresponding": False,
                },
                {
                    "name": "Victoria Makrides",
                    "affiliations": [
                        "The Interface Group, Institute of Physiology, University of Zürich, Zürich, Switzerland",
                        "Epithelial Transport Group, Institute of Physiology, University of Zürich, Zürich, Switzerland",
                        "EIC BioMedical Labs, Norwood, MA, USA",
                    ],
                    "is_corresponding": True,
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
                    "is_corresponding": True,
                },
                {
                    "name": "Unbreen Qayyum",
                    "affiliations": [
                        "Department of Economics, Henan University, Kaifeng, P.R. China"
                    ],
                    "is_corresponding": False,
                },
                {
                    "name": "Saleem Khan",
                    "affiliations": [
                        "Department of Economics, Abdul Wali Khan University Mardan, KPK, Pakistan"
                    ],
                    "is_corresponding": False,
                },
                {
                    "name": "Bosede Ngozi Adeleye",
                    "affiliations": [
                        "Department of Economics and Development Studies, Covenant University, Nigeria"
                    ],
                    "is_corresponding": False,
                },
            ],
        },
    ]
