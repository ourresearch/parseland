import os

import pdfkit
from bs4 import BeautifulSoup
from pdfkit.configuration import Configuration

pdfkit_config = Configuration(wkhtmltopdf=os.getenv('WKHTMLTOPDF'))


def clean_html(soup: BeautifulSoup):
    for tag in soup.select('[src]'):
        tag.decompose()
    for tag in soup.select('[href]'):
        tag['href'] = ''
    return soup


def html_to_pdf(html_str: str):
    soup = BeautifulSoup(html_str, parser='lxml', features='lxml')
    cleaned = clean_html(soup)
    body = soup.find('body')
    return pdfkit.from_string(str(body) if body else str(cleaned),
                              configuration=pdfkit_config,
                              options={"load-error-handling": "ignore",
                                       'load-media-error-handling': 'ignore',
                                       'no-images': "",
                                       'disable-javascript': '',
                                       'disable-external-links': '',
                                       'disable-internal-links': '',
                                       'log-level': 'info'})
