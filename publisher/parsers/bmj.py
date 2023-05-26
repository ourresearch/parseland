from publisher.elements import Author, Affiliation, AuthorAffiliations
from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import name_in_text


class BMJ(PublisherParser):
    parser_name = "bmj"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url("bmj.com")

    def authors_found(self):
        return self.soup.find("ol",
                              class_="contributor-list") or self.soup.find(
            "meta", {"name": "citation_author"}
        )

    def parse(self):
        result_authors = None

        authors = self.get_authors()
        if authors:
            affiliations = self.get_affiliations()
            result_authors = self.merge_authors_affiliations(authors,
                                                             affiliations)
        else:
            result_authors = self.parse_author_meta_tags()

        return {"authors": result_authors,
                "abstract": self.parse_abstract_meta_tags()}

    def get_authors(self):
        authors = []
        corr_str = self.get_correspondence_str()
        corr_split = corr_str.split(',', 1)
        corr_name = corr_split[0]
        corr_aff = None
        if len(corr_split) == 2:
            corr_aff = corr_split[1].split(';')[0]
        author_soup = self.soup.find("ol", class_="contributor-list")
        if not author_soup:
            return None

        author_soup = author_soup.findAll("li")
        for author in author_soup:
            name_soup = author.find("span", class_="name")
            if not name_soup:
                continue
            name = name_soup.text.strip()
            aff_ids_raw = author.select('.xref-aff')
            aff_ids = []
            for aff_id_raw in aff_ids_raw:
                aff_id = aff_id_raw.text.strip()
                if aff_id:
                    aff_ids.append(aff_id)
            is_corresponding = False
            author = Author(name=name, aff_ids=aff_ids,
                            is_corresponding=is_corresponding)
            if name_in_text(name, corr_name) or len(author_soup) == 1:
                is_corresponding = True
                if corr_aff:
                    author = AuthorAffiliations(name=name,
                                                affiliations=[corr_aff],
                                                is_corresponding=is_corresponding)
                else:
                    author.is_corresponding = is_corresponding

            authors.append(author)
        return authors

    def get_affiliations(self):
        aff_soup = self.soup.find("ol", class_="affiliation-list")

        results = []
        if aff_soup:
            affiliations = aff_soup.findAll("li", class_="aff")
            for aff_raw in affiliations:
                # affiliation id
                aff_id_raw = aff_raw.find("sup")
                if aff_id_raw:
                    aff_id = aff_id_raw.text
                    aff_id_raw.clear()
                else:
                    aff_id = None

                # affiliation
                aff = aff_raw.text.strip()
                if len(affiliations) == 1:
                    aff_id = None
                results.append(Affiliation(organization=aff, aff_id=aff_id))
        return results

    def get_correspondence_str(self):
        corr_soup = self.soup.find("li", class_="corresp")
        corr_soup.select_one('.corresp-label').decompose()
        return corr_soup.text.strip() if corr_soup else None

    test_cases = [
        {
            "doi": "10.1136/bcr-2020-239618",
            "result": {
                "authors": [
                    {
                        "name": "Brian Alexander Hummel",
                        "affiliations": [
                            "Division of Infectious Diseases, Immunology and Allergy, Department of Pediatrics, University of Ottawa Faculty of Medicine, Ottawa, Ontario, Canada",
                        ],
                        "is_corresponding": True,
                    },
                    {
                        "name": "Julie Blackburn",
                        "affiliations": [
                            "Département de Microbiologie et Immunologie, University of Montreal Faculty of Medicine, Montreal, Quebec, Canada"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Anne Pham-Huy",
                        "affiliations": [
                            "Division of Infectious Diseases, Immunology and Allergy, Department of Pediatrics, University of Ottawa Faculty of Medicine, Ottawa, Ontario, Canada",
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Katherine Muir",
                        "affiliations": [
                            "Division of Neurology, Department of Pediatrics, University of Ottawa Faculty of Medicine, Ottawa, Ontario, Canada"
                        ],
                        "is_corresponding": False,
                    },
                ],
                "abstract": "<p>Cerebral vasculitis is a serious complication of bacterial meningitis that can cause significant morbidity and mortality due to stroke. Currently, there are no treatment guidelines or safety and efficacy studies on the management of cerebral vasculitis in this context. Herein, we report a case of a previously well 11-year-old girl who presented with acute otitis media that progressed to mastoiditis and fulminant meningitis. Group A <i>Streptococcus</i> was found in blood and ear-fluid cultures (lumbar puncture was unsuccessful). Her decreased level of consciousness persisted despite appropriate antimicrobial treatment, and repeat MRI revealed extensive large vessel cerebral vasculitis. Based on expert opinion and a presumed inflammatory mechanism, her cerebral vasculitis was treated with 7\u2009days of pulse intravenous methylprednisolone followed by oral prednisone taper. She was also treated with intravenous heparin. Following these therapies, she improved clinically and radiographically with no adverse events. She continues to undergo rehabilitation with improvement.</p>",
            },
        },
        {
            "doi": "10.1136/bmjopen-2020-043554",
            "result": {
                "authors": [
                    {
                        "name": "Kelly Teo",
                        "affiliations": [
                            "Department of Gerontology, Simon Fraser University, Vancouver, British Columbia, Canada",
                        ],
                        "is_corresponding": True,
                    },
                    {
                        "name": "Ryan Churchill",
                        "affiliations": [
                            "Department of Gerontology, Simon Fraser University, Vancouver, British Columbia, Canada"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Indira Riadi",
                        "affiliations": [
                            "Department of Gerontology, Simon Fraser University, Vancouver, British Columbia, Canada",
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Lucy Kervin",
                        "affiliations": [
                            "Department of Gerontology, Simon Fraser University, Vancouver, British Columbia, Canada"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Theodore Cosco",
                        "affiliations": [
                            "Department of Gerontology, Simon Fraser University, Vancouver, British Columbia, Canada",
                            "Oxford Institute of Population Ageing, University of Oxford, Oxford, Oxfordshire, UK",
                        ],
                        "is_corresponding": False,
                    },
                ],
                "abstract": "<h3>Introduction</h3>\n<p>Despite evidence that illustrates the unmet healthcare needs of older adults, there is limited research examining their help-seeking behaviour, of which direct intervention can improve patient outcomes. Research in this area conducted with a focus on ethnic minority older adults is also needed, as their help-seeking behaviours may be influenced by various cultural factors. This scoping review aims to explore the global literature on the factors associated with help-seeking behaviours of older adults and how cultural values and backgrounds may impact ethnic minority older adults\u2019 help-seeking behaviours in different ways.</p><h3>Methods and analysis</h3>\n<p>The scoping review process will be guided by the methodology framework of Arksey and O\u2019Malley and the Preferred Reporting Items for Systematic Reviews and Meta-analysis Protocols Extension for Scoping Reviews guidelines. The following electronic databases will be systematically searched from January 2005 onwards: MEDLINE/PubMed, Web of Science, PsycINFO, CINAHL and Scopus. Studies of various designs and methodologies consisting of older adults aged 65 years or older, who are exhibiting help-seeking behaviours for the purpose of remedying a physical or mental health challenge, will be considered for inclusion. Two reviewers will screen full texts and chart data. The results of this scoping review will be summarised quantitatively through numerical counts and qualitatively through a narrative synthesis.</p><h3>Ethics and dissemination</h3>\n<p>As this is a scoping review of published literature, ethics approval is not required. Results will be disseminated through publication in a peer-reviewed journal.</p><h3>Discussion</h3>\n<p>This scoping review will synthesise the current literature related to the help-seeking behaviours of older adults and ethnic minority older adults. It will identify current gaps in research and potential ways to move forward in developing or implementing strategies that support the various health needs of the diverse older adult population.</p><h3>Registration</h3>\n<p>This scoping review protocol has been registered with the Open Science Framework (https://osf.io/69kmx).</p>",
            },
        },
        {
            "doi": "10.1136/bcr-2021-243370",
            "result": {
                "authors": [
                    {
                        "name": "John Leso",
                        "affiliations": [
                            "Internal Medicine, Albany Medical College, Albany, New York, USA",
                        ],
                        "is_corresponding": True,
                    },
                    {
                        "name": "Majd Al-Ahmad",
                        "affiliations": [
                            "Internal Medicine, Albany Medical College, Albany, New York, USA"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Drinnon O Hand",
                        "affiliations": [
                            "Internal Medicine, Albany Medical College, Albany, New York, USA",
                        ],
                        "is_corresponding": False,
                    },
                ],
                "abstract": "<p>A 34-year-old man with a medical history of injection drug use presented with 2 weeks of weakness, nausea, vomiting and septic shock secondary to infective endocarditis of a native tricuspid valve. On admission, CT chest demonstrated multiple cavitary lesions as well as numerous small infarcts seen on MRI brain concerning for systemic septic emboli. Subsequent transthoracic echo with bubble study revealed a large patent foramen ovale (PFO). The patient later received surgical debulking of his tricuspid valve vegetation with AngioVac. Subsequently, PFO closure was performed with a NobleStitch device. The case presented here demonstrates the importance of having a high index of suspicion with right-sided endocarditis and the development of other systemic signs and symptoms. It also underscores the necessity of a multidisciplinary team of cardiologists, surgeons, infectious disease specialists and intensivists in the treatment of these complicated patients.</p>",
            },
        },
    ]
