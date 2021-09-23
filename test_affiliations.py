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
                "name": "László Losonczi",
                "references": ["bAFF1", "bAFF2", "bFN1"],
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
