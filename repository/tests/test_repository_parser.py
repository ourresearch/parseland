import pytest
import requests_cache

from repository.parsers.parser import RepositoryParser
from views import app


@pytest.fixture
def client():
    with app.test_client() as client:
        requests_cache.install_cache(
            cache_name="api_cache", backend="sqlite", expire_after=24 * 60 * 7  # 7 days
        )
        yield client


test_cases = []
parsers = RepositoryParser.__subclasses__()
for parser in parsers:
    test_cases.extend(parser.test_cases)


def idfn(val):
    return val["page-id"]


@pytest.mark.parametrize("test_case", test_cases, ids=idfn)
def test_parsers_api_output(test_case, client):
    rv = client.get(f'/parse-repository?page-id={test_case["page-id"]}')
    json_data = rv.get_json()
    assert json_data["message"] == test_case["result"]
