import pytest

from views import app
from parsers.sciencedirect import test_cases as science_direct_test_cases
from parsers.springer import test_cases as springer_test_cases


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_api_root(client):
    rv = client.get("/")
    json_data = rv.get_json()
    assert json_data["app_name"] == "parseland"


def test_no_authors_found(client):
    rv = client.get("/parse?doi=10.1007/0-387-27160-0_33")
    json_data = rv.get_json()
    assert json_data["error"] == "Authors not found."


test_cases = science_direct_test_cases + springer_test_cases


@pytest.mark.parametrize("test_case", test_cases)
def test_parsers_api_output(test_case, client):
    rv = client.get(f'/parse?doi={test_case["doi"]}')
    json_data = rv.get_json()
    assert json_data["message"] == test_case["result"]
