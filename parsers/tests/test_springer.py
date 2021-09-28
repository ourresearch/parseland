import pytest

from parsers.springer import Springer
from parsers.tests.utils import get_soup

api_output = [
    {
        "doi": "10.1007/978-0-387-39343-8_21",
        "result": [
            {
                "name": "Pascal Boileau",
                "affiliations": [
                    "Orthopaedic Surgery and Sports Traumatology, University of Nice-Sophia Antipolis, Nice, France"
                ],
            },
            {
                "name": "Christopher R. Chuinard",
                "affiliations": [
                    "Great Lakes Orthopaedic Center, Munson Medical Center, Traverse City, USA"
                ],
            },
        ],
    },
    {
        "doi": "10.1007/0-306-48581-8_22",
        "result": [
            {
                "name": "L. Michael Ascher",
                "affiliations": [
                    "Department of Psychology, Philadelphia College of Osteopathic Medicine, Philadelphia"
                ],
            },
            {
                "name": "Christina Esposito",
                "affiliations": [
                    "Department of Psychology, Philadelphia College of Osteopathic Medicine, Philadelphia"
                ],
            },
        ],
    },
    {
        "doi": "10.1007/0-306-48688-1_15",
        "result": [
            {
                "name": "Ping Zhang",
                "affiliations": [
                    "Department of Medicine, Section of Pulmonary and Critical Care Medicine, and Alcohol Research Center, Louisiana State University Health Sciences Center, New Orleans"
                ],
            },
            {
                "name": "Gregory J. Bagby",
                "affiliations": [
                    "Department of Medicine, Section of Pulmonary and Critical Care Medicine, Department of Physiology, and Alcohol Research Center, Louisiana State University Health Sciences Center, New Orleans"
                ],
            },
            {
                "name": "Jay K. Kolls",
                "affiliations": [
                    "Department of Medicine, Section of Pulmonary and Critical Care Medicine, Alcohol Research Center and Gene Therapy Programs, Louisiana State University Health Sciences Center, New Orleans"
                ],
            },
            {
                "name": "Lee J. Quinton",
                "affiliations": [
                    "Department of Physiology and Alcohol Research Center, Louisiana State University Health Sciences Center, New Orleans"
                ],
            },
            {
                "name": "Steve Nelson",
                "affiliations": [
                    "Department of Medicine, Section of Pulmonary and Critical Care Medicine, Department of Physiology, and Alcohol Research Center, Louisiana State University Health Sciences Center, New Orleans"
                ],
            },
        ],
    },
]


@pytest.mark.parametrize("doi", api_output)
def test_api_output(doi):
    soup = get_soup(doi)
    p = Springer(soup)
    response = p.parse()
    assert response == doi["result"]
