import pytest
import requests_cache

from views import app

from publisher.parsers.parser import PublisherParser


@pytest.fixture
def client():
    with app.test_client() as client:
        requests_cache.install_cache(
            cache_name="api_cache", backend="sqlite", expire_after=24 * 60 * 7  # 7 days
        )
        yield client


def test_api_root(client):
    rv = client.get("/")
    json_data = rv.get_json()
    assert json_data["app_name"] == "parseland"


def test_no_authors_found(client):
    rv = client.get("/parse-publisher?doi=10.1007/0-387-27160-0_33")
    json_data = rv.get_json()
    assert json_data["message"] == [] or (
        not json_data["message"].get("authors")
        and not json_data["message"].get("abstract")
        and not json_data["message"].get("published_date")
        and not json_data["message"].get("genre")
    )


test_cases = []
parsers = PublisherParser.__subclasses__()
for parser in parsers:
    test_cases.extend(parser.test_cases)


def idfn(val):
    return val["doi"]


@pytest.mark.parametrize("test_case", test_cases, ids=idfn)
def test_parsers_api_output(test_case, client):
    rv = client.get(f'/parse-publisher?doi={test_case["doi"]}')
    json_data = rv.get_json()
    assert json_data["message"] == test_case["result"]
