from parser import Parser


affiliation_dois = [
    {
        "doi": "10.1016/0022-247x(75)90149-3",
        "result": [
            {
                "id": "aep-affiliation-id2",
                "text": "Division of Mathematics, University of Maryland Baltimore County, Baltimore, Maryland 21228 USA",
            }
        ],
    },
    {
        "doi": "10.1016/0022-247x(78)90235-4",
        "result": [
            {
                "id": "aep-affiliation-id2",
                "text": "West Virginia University, Morgantown, West Virginia 26506 USA",
            }
        ],
    },
    {
        "doi": "10.1016/0022-247x(78)90250-0",
        "result": [
            {
                "id": "aep-affiliation-id4",  # id4 because two authors are id2 and id3
                "text": "Lefschetz Center for Dynamical Systems, Division of Applied Mathematics, Brown University, Providence, Rhode Island 02912 USA",
            }
        ],
    },
    {
        "doi": "10.1016/0022-247x(78)90205-6",
        "result": [
            {
                "id": "aep-affiliation-id2",
                "text": "U.E.R. de Mathématiques et Informatique et Laboratoire associé au C.N.R.S. n∘ 226, Université de Bordeaux 1, 33405 Talence, France",
            },
            {
                "id": "aep-affiliation-id4",
                "text": "Istituto Matematico, Universitá di Roma, 00185 Rome, Italy",
            },
        ],
    },
    {
        "doi": "10.1016/0022-247x(77)90164-0",
        "result": [
            {
                "id": "AFF1",
                "text": "Department of Mathematics, University of Lagos, Lagos, Nigeria",
            },
            {
                "id": "AFF2",
                "text": "Department of Mathematics, Kossuth Lajos University, Debrecen, Hungary",
            },
        ],
    },
    {
        "doi": "10.1016/0022-247x(81)90037-8",
        "result": [
            {
                "id": "AFF1",
                "text": "Institute of Mathematics, Academia Sinica, Peking, China",
            },
            {
                "id": "AFF2",
                "text": "Lefschetz Center for Dynamical Systems, Division of Applied Mathematics, Brown University, Providence, Rhode Island 02912 U.S.A.",
            },
            {
                "id": "aep-affiliation-id4",
                "text": "Institute of Mathematics, Academic Sinica, Peking, China",
            },
        ],
    },
    {
        "doi": "10.1016/0022-247x(83)90211-1",
        "result": [
            {
                "id": "aep-affiliation-id3",
                "text": "University of California at Los Angeles, Departments of Mathematics and System Science, Los Angeles, California 90024 U.S.A.",
            },
        ],
    },
    {
        "doi": "10.1016/0022-247x(87)90179-x",
        "result": [
            {
                "id": "aep-affiliation-id3",
                "text": "Department of Mathematics, University of North Carolina, Chapel Hill, North Carolina 27514 USA",
            },
        ],
    },
]

author_names_to_test = [
    {
        "doi": "10.1016/0022-247x(77)90164-0",
        "result": [
            {
                "author_name": "László Losonczi",
                "affiliation_ids": ["baep-author-id1", "bAFF1", "bAFF2", "bFN1"],
            },
        ],
    },
    {
        "doi": "10.1016/0022-247x(78)90205-6",
        "result": [
            {
                "author_name": "Pierre Charrier",
                "affiliation_ids": ["baep-author-id1"],
            },
            {
                "author_name": "Giovanni M Troianiello",
                "affiliation_ids": ["baep-author-id3"],
            },
        ],
    },
    {
        "doi": "10.1016/0022-247x(79)90002-7",
        "result": [
            {
                "author_name": "N Levan",
                "affiliation_ids": ["baep-author-id2", "bAFF1"],
            },
            {
                "author_name": "L Rigby",
                "affiliation_ids": ["baep-author-id3", "bAFF2"],
            },
        ],
    },
    {
        "doi": "10.1016/0024-3795(85)90062-x",
        "result": [
            {
                "author_name": "A. El Mossadeq",
                "affiliation_ids": ["baep-author-id1"],
            },
            {
                "author_name": "A. Kobilinsky",
                "affiliation_ids": ["baep-author-id3"],
            },
            {
                "author_name": "D. Collombier",
                "affiliation_ids": ["baep-author-id5"],
            },
        ],
    },
]

api_output = [
    {
        "doi": "10.1016/0022-247x(78)90205-6",
        "result": [
            {
                "author": "Pierre Charrier",
                "affiliations": [
                    "U.E.R. de Mathématiques et Informatique et Laboratoire associé au C.N.R.S. n∘ 226, Université de Bordeaux 1, 33405 Talence, France"
                ],
            },
            {
                "author": "Giovanni M Troianiello",
                "affiliations": [
                    "Istituto Matematico, Universitá di Roma, 00185 Rome, Italy"
                ],
            },
        ],
    },
    {
        "doi": "10.1016/0022-247x(79)90002-7",
        "result": [
            {
                "author": "N Levan",
                "affiliations": [
                    "Department of System Science, 4532 Boelter Hall, University of California, Los Angeles, California 90024 U.S.A."
                ],
            },
            {
                "author": "L Rigby",
                "affiliations": [
                    "Department of Computing and Control, Huxley Building, Imperial College, London SW7 2BZ, Great Britain"
                ],
            },
        ],
    },
    {
        "doi": "10.1016/0022-247x(77)90164-0",
        "result": [
            {
                "author": "László Losonczi",
                "affiliations": [
                    "Department of Mathematics, University of Lagos, Lagos, Nigeria",
                    "Department of Mathematics, Kossuth Lajos University, Debrecen, Hungary",
                ],
            },
        ],
    },
    {
        "doi": "10.1016/0024-3795(85)90253-8",
        "result": [
            {
                "author": "Donald W. Robinson",
                "affiliations": [
                    "Department of Mathematics Brigham Young University Provo, Utah 84602, USA"
                ],
            },
        ],
    },
    {
        "doi": "10.1016/0024-3795(86)90148-5",
        "result": [
            {
                "author": "Robert E. Hartwig",
                "affiliations": [
                    "Department of Mathematics North Carolina State University Box 8205 Raleigh, North Carolina 27695-820 USA"
                ],
            },
            {
                "author": "George P.H. Styan",
                "affiliations": [
                    "Department of Mathematics and Statistics McGill University 805 ouest, rue Sherbrooke Montréal, Québec, Canada H3A 2K6"
                ],
            },
        ],
    },
    {
        "doi": "10.1016/j.ab.2021.114100",
        "result": [
            {
                "author": "Emma Dreischmeier",
                "affiliations": [
                    "Wisconsin Institutes of Medical Research, University of Wisconsin-Madison, Madison, WI, USA"
                ],
            },
            {
                "author": "William E. Fahl",
                "affiliations": [
                    "Wisconsin Institutes of Medical Research, University of Wisconsin-Madison, Madison, WI, USA"
                ],
            },
        ],
    },
]


def test_affiliations():
    for doi in affiliation_dois:
        p = Parser(doi["doi"])
        affiliations = p.get_affiliations()
        assert affiliations == doi["result"]


def test_author_names():
    for doi in author_names_to_test:
        p = Parser(doi["doi"])
        authors = p.get_authors()
        assert authors == doi["result"]


def test_api_output():
    for doi in api_output:
        p = Parser(doi["doi"])
        response = p.authors_affiliations()
        assert response == doi["result"]
