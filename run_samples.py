import pandas as pd
import requests


def run_dois():
    """Runs a sample of DOIs for a given publisher in order to determine accuracy of parsers."""
    samples_to_run = 10
    publisher = "Springer-Verlag"
    df = pd.read_csv("available-dois.csv")
    df = df[(df["publisher"] == publisher)]

    for index, row in df.sample(frac=1).head(samples_to_run).iterrows():
        doi = row.doi
        r = requests.get(f"http://127.0.0.1:5000/parse?doi={doi}")
        print(r.status_code)
        print(r.json())


if __name__ == "__main__":
    run_dois()
