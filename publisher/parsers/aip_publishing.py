import re

from publisher.elements import Author, Affiliation
from publisher.parsers.parser import PublisherParser


class AIPPublishing(PublisherParser):
    parser_name = "aip_publishing"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url("aip.scitation.org")

    def authors_found(self):
        return self.soup.find("div", class_="publicationContentAuthors")

    def parse(self):
        if self.soup.select("li.author-affiliation"):
            author_affiliations = self.get_authors_2()
        else:
            authors = self.get_authors()
            affiliations = self.get_affiliations()
            author_affiliations = self.merge_authors_affiliations(authors,
                                                                  affiliations)
        return {
            "authors": author_affiliations,
            "abstract": self.parse_abstract_meta_tags(),
        }

    def get_authors_2(self):
        authors_tag = self.soup.select_one('.entryAuthor')
        authors = []
        in_aff_list = False
        aff_group = []
        for child in authors_tag.children:
            if 'contrib-author' in child['class']:
                if in_aff_list:
                    for author in authors:
                        if not author['affiliations']:
                            author['affiliations'] = aff_group
                    aff_group = []
                in_aff_list = False
                name = child.find('a').text.strip()
                author = {'name': name,
                          'affiliations': [],
                          'is_corresponding': None}
                authors.append(author)
            elif 'author-affiliation' in child['class']:
                in_aff_list = True
                aff_group.append(child.text.strip())
        if aff_group:
            for author in authors:
                if not author['affiliations']:
                    author['affiliations'] = aff_group
        return authors

    def get_authors(self):
        authors = []

        # find corresponding author
        corresp = self.soup.find("corresp")
        corresp_id = (
            corresp.find("sup").text if corresp and corresp.find(
                "sup") else None
        )

        if authors_div := self.soup.find("div",
                                         class_="publicationContentAuthors"):
            for author_span in authors_div.find_all("span",
                                                    class_="contrib-author"):
                if author_a := author_span.find("a",
                                                href=re.compile(r"^/author/")):
                    if author_a.text and (author_name := author_a.text.strip()):
                        affiliation_ids = []

                        for affiliation_sup in author_span.find_all("sup"):
                            if (
                                    sup_text := affiliation_sup.text
                                                and affiliation_sup.text.strip()
                            ):
                                for sup_split_part in sup_text.split(","):
                                    if affiliation_id := sup_split_part.strip():
                                        affiliation_ids.append(affiliation_id)

                        if corresp_id and corresp_id in affiliation_ids:
                            is_corresponding = True
                        else:
                            is_corresponding = False

                        authors.append(
                            Author(
                                name=author_name,
                                aff_ids=affiliation_ids,
                                is_corresponding=is_corresponding,
                            )
                        )
        return authors

    def get_affiliations(self):
        affiliations = []

        if affiliations_div := self.soup.find("div",
                                              class_="affiliations-list"):
            for affiliation_li in affiliations_div.find_all(
                    "li", class_="author-affiliation"
            ):
                if institution_a := affiliation_li.find("a",
                                                        class_="institution"):
                    if (
                            institution_name := institution_a.text
                                                and institution_a.text.strip()
                    ):
                        if id_sup := affiliation_li.find("sup"):
                            if affiliation_id := id_sup.text and id_sup.text.strip():
                                affiliations.append(
                                    Affiliation(
                                        aff_id=affiliation_id,
                                        organization=institution_name,
                                    )
                                )

        return affiliations

    test_cases = [
        {
            "doi": "10.1063/5.0002598",
            "result": {
                "authors": [
                    {
                        "name": "Muhamad Sahlan",
                        "affiliations": [
                            "Department of Chemical Engineering, Faculty of Engineering, Universitas Indonesia"
                        ],
                        "is_corresponding": True,
                    },
                    {
                        "name": "Etin Rohmatin",
                        "affiliations": [
                            "Department of Health Polytechnic Republic of Indonesia\u2019s Health Ministry Tasikmalaya"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Dita Amalia Wijanarko",
                        "affiliations": [
                            "Department of Chemical Engineering, Faculty of Engineering, Universitas Indonesia"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Kenny Lischer",
                        "affiliations": [
                            "Department of Chemical Engineering, Faculty of Engineering, Universitas Indonesia"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Anondho Wijanarko",
                        "affiliations": [
                            "Department of Chemical Engineering, Faculty of Engineering, Universitas Indonesia"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Ananda Bagus Richky Digdaya Putra",
                        "affiliations": [
                            "Department of Chemical Engineering, Faculty of Engineering, Universitas Indonesia"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Nunuk Widhyastuti",
                        "affiliations": [
                            "Research center for Biology, Indonesian Institute of science, Bogor"
                        ],
                        "is_corresponding": False,
                    },
                ],
                "abstract": "Based on research conducted by various researchers showing that sea cucumbers are high in nutrients needed by the body such as proteins, polysaccharides, fats, amino acids, and show anti-bacterial activity, anti-fungi and antioxidant which are good for the body. From the information above, supplement with sea cucumber-based ingredients can produce supplements that rich in nutrients. In this study, the authors has done the production of supplements with the main ingredients is sea cucumber that most common found in Indonesia which is Holothuria scabra in the same form as commercial products and has conducted a comparative test, composition identification and test of anti-bacterial, anti-fungi and antioxidant activity. The result of the composition obtained are jelly made from 35% hydrolysate, 45% water, 15% gelatin and 5% sugar. The results of sample jelly protein 5.1% and commercial jelly protein 0.175%, result of sample jelly fat 0.03% and commercial jelly fat 0.06%, and result of sample jelly carbohydrate 2.6% and commercial jelly carbohydrate 2.9%. Antioxidant and anti-bacterial tests also show that artificial sea cucumber jelly has a higher activity. It can be concluded that sea cucumber jelly has good nutrients and good antioxidant activity and good anti-microbial activity.",
            },
        },
        {
            "doi": "10.1063/5.0051325",
            "result": {
                "authors": [
                    {
                        "name": "M. Cavaiola",
                        "affiliations": [
                            "Department of Civil, Chemical and Environmental Engineering (DICCA), University of Genova",
                            "INFN, Genova Section",
                        ],
                        "is_corresponding": True,
                    },
                    {
                        "name": "A. Mazzino",
                        "affiliations": [
                            "Department of Civil, Chemical and Environmental Engineering (DICCA), University of Genova",
                            "INFN, Genova Section",
                        ],
                        "is_corresponding": False,
                    },
                ],
                "abstract": "The perception of hydrodynamic signals by self-propelled objects is a problem of paramount importance ranging from the field of bio-medical engineering to bio-inspired intelligent navigation. By means of a state-of-the-art fully resolved immersed boundary method, we propose different models for fully coupled self-propelled objects (swimmers, in short), behaving either as “pusher” or as “puller.” The proposed models have been tested against known analytical results in the limit of Stokes flow, finding excellent agreement. Once tested, our more realistic model has been exploited in a chaotic flow field up to a flow Reynolds number of 10, a swimming number ranging between zero (i.e., the swimmer is freely moving under the action of the underlying flow in the absence of propulsion) and one (i.e., the swimmer has a relative velocity with respect to the underlying flow velocity of the same order of magnitude as the underlying flow), and different swimmer inertia measured in terms of a suitable definition of the swimmer Stokes number. Our results show the following: (i) pusher and puller reach different swimming velocities for the same, given, propulsive force: while for pusher swimmers, an effective slender body theory captures the relationship between swimming velocity and propulsive force, this is not for puller swimmers. (ii) While swimming, pusher and puller swimmers possess a different distribution of the vorticity within the wake. (iii) For a wide range of flow/swimmer Reynolds numbers, both pusher and puller swimmers are able to sense hydrodynamic signals with good accuracy.",
            },
        },
        {
            "doi": "10.1063/5.0028171",
            "result": {
                "authors": [
                    {
                        "name": "E. N. Eremin",
                        "affiliations": [
                            "Department of Mechanical Engineering and Material Science, Machine-Building Institute, Omsk State Technical University"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "V. M. Yurov",
                        "affiliations": [
                            "Department of Ion-Plasma Technologies, Karaganda State University E.A. Buketova"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "V. S. Oleshko",
                        "affiliations": [
                            "Military Training Center, Moscow Aviation Institute (National Research University)"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "S. A. Guchenko",
                        "affiliations": [
                            "Department of Ion-Plasma Technologies, Karaganda State University E.A. Buketova"
                        ],
                        "is_corresponding": True,
                    },
                ],
                "abstract": "The surface energy, contact potential difference, and electron work function for highly entropic coatings were first determined in the work. These coatings were applied by the magnetron method in a high vacuum installation. The targets themselves were fabricated by mechanical alloying followed by heat treatment. The measurements were carried out at facilities developed by the authors.",
            },
        },
        {
            "doi": "10.1063/1.5129000",
            "result": {
                "authors": [
                    {
                        "name": "Tushar Tyagi",
                        "affiliations": [
                            "Department of Electrical Engineering, Indian Institute of Technology Gandhinagar"
                        ],
                        "is_corresponding": None,
                    },
                    {
                        "name": "P. Sumathi",
                        "affiliations": [
                            "Department of Electrical Engineering, Indian Institute of Technology Roorkee"
                        ],
                        "is_corresponding": None,
                    },
                ],
                "abstract": "The process of capacitance measurement consists of converting the capacitance under measurement into a secondary variable such as voltage, time-period, and frequency. This paper lays special focus on the capacitance-frequency measurement due to the offered advantages by this technique over the other methods. For this purpose, a review of the various frequency estimation techniques is presented while exploring the possibility of applying them for capacitance measurement. These techniques are mainly classified as phase-locked loop, frequency-locked loop (FLL), parameter estimation methods, and discrete Fourier transform (DFT) based FLL structures. Furthermore, the possibility of integrating computationally efficient DFT structures in frequency locked loops has been investigated. The performance comparison of these techniques proves that a more accurate measurement of capacitance could be achieved through them. The proposed methodology of capacitance measurement offers good accuracy, wider range, quick convergence, and system-on-chip implementation. Moreover, FLLs could be applied for the capacitance measurement when the input signal is nonsinusoidal.",
            },
        },
    ]
