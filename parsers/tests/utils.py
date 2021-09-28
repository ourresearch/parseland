from gzip import decompress

from bs4 import BeautifulSoup
import requests


def get_soup(doi):
    doi = doi["doi"]
    r = requests.get(f"https://api.unpaywall.org/doi_page/{doi}")
    html = decompress(r.content)
    soup = BeautifulSoup(html, "html.parser")
    return soup
