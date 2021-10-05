import json

import pandas as pd
import requests


def run_dois():
    """Runs a sample of DOIs for a given publisher in order to determine accuracy of parsers."""
    samples_to_run = 10
    publisher = "Wiley"
    df = pd.read_csv("available-dois.csv")
    df = df[(df["publisher"] == publisher)]
    df = df[(df["published_date"].str.contains("2021", na=False))]

    for index, row in df.sample(frac=1).head(samples_to_run).iterrows():
        doi = row.doi
        r = requests.get(f"http://127.0.0.1:5000/parse?doi={doi}")
        print(f"doi: https://doi.org/{doi}")
        print(f"status code: {r.status_code}")
        print(f"result: {json.dumps(r.json(), indent=2)}")
        print("")


def test_coverage():
    """Runs a sample of DOIs for a given publisher in order to determine accuracy of parsers."""
    samples_to_run = 100
    df = pd.read_csv("available-dois.csv")
    df = df[(df["published_date"].str.contains("2021", na=False))]

    num_ran = 0
    num_not_found = 0
    publishers = {}
    for index, row in df.sample(frac=1).head(samples_to_run).iterrows():
        num_ran += 1
        doi = row.doi
        r = requests.get(f"http://127.0.0.1:5000/parse?doi={doi}")
        if r.status_code == 404:
            num_not_found += 1

            if row.publisher in publishers:
                publishers[row.publisher] += 1
            else:
                publishers[row.publisher] = 1
            print(row.publisher)
            print(f"doi: https://doi.org/{doi}")
            print(f"status code: {r.status_code}")
            print(f"result: {json.dumps(r.json(), indent=2)}")
            print("")
    sorted_publishers = dict(
        sorted(publishers.items(), key=lambda item: item[1], reverse=True)
    )
    print(sorted_publishers)
    print(f"Coverage is {num_not_found/num_ran}")


if __name__ == "__main__":
    test_coverage()
