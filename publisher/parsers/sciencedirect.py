import json

from publisher.parsers.parser import PublisherParser


class ScienceDirect(PublisherParser):
    parser_name = "sciencedirect"

    def is_publisher_specific_parser(self):
        return self.domain_in_canonical_link("sciencedirect.com")

    def authors_found(self):
        return self.soup.find_all("a", class_="author")

    def parse(self):
        """Core function returning list of authors with their affiliations."""
        return self.get_json_authors_affiliations()

    def get_json_authors_affiliations(self):
        if not (science_direct_json := self.extract_json()):
            return {"authors": []}

        all_authors = []

        authors_content = science_direct_json.get('authors', {}).get('content', {})

        for author_group in [ac for ac in authors_content if ac.get('#name') == 'author-group']:
            group_authors = []
            group_affiliation_labels = {}

            affiliation_dicts = [x for x in author_group.get('$$', []) if x.get('#name') == 'affiliation']

            for affiliation in affiliation_dicts:
                affiliation_label = affiliation.get('$', {}).get('id')
                for affiliation_property in affiliation.get('$$', []):
                    if affiliation_property.get('#name') == 'textfn':
                        if affiliation_label and affiliation_property.get('_'):
                            group_affiliation_labels[affiliation_label] = affiliation_property['_']

            author_dicts = [x for x in author_group.get('$$', []) if x.get('#name') == 'author']

            for author in author_dicts:
                given = None
                family = None
                affiliation_labels = []
                for author_property in author.get('$$', []):
                    if author_property.get('#name') == 'given-name':
                        given = author_property.get('_')
                    elif author_property.get('#name') == 'surname':
                        family = author_property.get('_')
                    elif author_property.get('#name') == 'cross-ref':
                        affiliation_label = author_property.get('$', {}).get('refid')
                        if affiliation_label in group_affiliation_labels:
                            affiliation_labels.append(affiliation_label)

                if given or family:
                    group_authors.append({
                        'name': ' '.join([n for n in [given, family] if n]),
                        'affiliation_labels': affiliation_labels
                    })

            if any(author.get('affiliation_labels') for author in group_authors):
                # assign affiliations by label
                for author in group_authors:
                    affiliations = [group_affiliation_labels[label] for label in author['affiliation_labels']]
                    all_authors.append({
                        'name': author['name'],
                        'affiliations': affiliations
                    })
            else:
                # assign all affiliations to all authors
                for author in group_authors:
                    all_authors.append({
                        'name': author['name'],
                        'affiliations': list(group_affiliation_labels.values())
                    })

        return {
            "authors": all_authors
        }

    def extract_json(self):
        """Finds and loads json that contains affiliation data."""
        raw_json = self.soup.find("script", type="application/json").text
        loaded_json = json.loads(raw_json)
        return loaded_json

    test_cases = [
        {
            "doi": "10.1016/0022-247x(78)90205-6",
            "result": {
                "authors": [
                    {
                        "name": "Pierre Charrier",
                        "affiliations": [
                            "U.E.R. de Mathématiques et Informatique et Laboratoire associé au C.N.R.S. n∘ 226, Université de Bordeaux 1, 33405 Talence, France"
                        ],
                    },
                    {
                        "name": "Giovanni M Troianiello",
                        "affiliations": [
                            "Istituto Matematico, Universitá di Roma, 00185 Rome, Italy"
                        ],
                    },
                ],
            }
        },
        {
            "doi": "10.1016/0022-247x(79)90002-7",
            "result": {
                "authors": [
                    {
                        "name": "N Levan",
                        "affiliations": [
                            "Department of System Science, 4532 Boelter Hall, University of California, Los Angeles, California 90024 U.S.A."
                        ],
                    },
                    {
                        "name": "L Rigby",
                        "affiliations": [
                            "Department of Computing and Control, Huxley Building, Imperial College, London SW7 2BZ, Great Britain"
                        ],
                    },
                ],
            }
        },
        {
            "doi": "10.1016/0022-247x(77)90164-0",
            "result": {
                "authors": [
                    {
                        "name": "László Losonczi",
                        "affiliations": [
                            "Department of Mathematics, University of Lagos, Lagos, Nigeria",
                            "Department of Mathematics, Kossuth Lajos University, Debrecen, Hungary",
                        ],
                    },
                ],
            }
        },
        {
            "doi": "10.1016/0024-3795(85)90253-8",
            "result": {
                "authors": [
                    {
                        "name": "Donald W. Robinson",
                        "affiliations": [
                            "Department of Mathematics Brigham Young University Provo, Utah 84602, USA"
                        ],
                    },
                ],
            }
        },
        {
            "doi": "10.1016/0024-3795(86)90148-5",
            "result": {
                "authors": [
                    {
                        "name": "Robert E. Hartwig",
                        "affiliations": [
                            "Department of Mathematics North Carolina State University Box 8205 Raleigh, North Carolina 27695-820 USA"
                        ],
                    },
                    {
                        "name": "George P.H. Styan",
                        "affiliations": [
                            "Department of Mathematics and Statistics McGill University 805 ouest, rue Sherbrooke Montréal, Québec, Canada H3A 2K6"
                        ],
                    },
                ],
            }
        },
        {
            "doi": "10.1016/j.ab.2021.114100",
            "result": {
                "authors": [
                    {
                        "name": "Emma Dreischmeier",
                        "affiliations": [
                            "Wisconsin Institutes of Medical Research, University of Wisconsin-Madison, Madison, WI, USA"
                        ],
                    },
                    {
                        "name": "William E. Fahl",
                        "affiliations": [
                            "Wisconsin Institutes of Medical Research, University of Wisconsin-Madison, Madison, WI, USA"
                        ],
                    },
                ],
            }
        },
        {
            "doi": "10.1016/j.ab.2021.114241",
            "result": {
                "authors": [
                    {
                        "name": "Jun Hu",
                        "affiliations": [
                            "College of Information Engineering, Zhejiang University of Technology, Hangzhou, 310023, China"
                        ],
                    },
                    {
                        "name": "Lin-Lin Zheng",
                        "affiliations": [
                            "College of Information Engineering, Zhejiang University of Technology, Hangzhou, 310023, China"
                        ],
                    },
                    {
                        "name": "Yan-Song Bai",
                        "affiliations": [
                            "College of Information Engineering, Zhejiang University of Technology, Hangzhou, 310023, China"
                        ],
                    },
                    {
                        "name": "Ke-Wen Zhang",
                        "affiliations": [
                            "College of Mechanical Engineering, Zhejiang University of Technology, Hangzhou, 310023, China"
                        ],
                    },
                    {
                        "name": "Dong-Jun Yu",
                        "affiliations": [
                            "School of Computer Science and Engineering, Nanjing University of Science and Technology,Xiaolingwei 200, Nanjing, 210094, China"
                        ],
                    },
                    {
                        "name": "Gui-Jun Zhang",
                        "affiliations": [
                            "College of Information Engineering, Zhejiang University of Technology, Hangzhou, 310023, China"
                        ],
                    },
                ],
            }
        },
    ]
