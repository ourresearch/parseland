import os
import re
from collections import Counter
from urllib.parse import urlparse

import pdfkit
from bs4 import BeautifulSoup
from pdfkit.configuration import Configuration


def most_frequent_domain(html_string):
    url_pattern = re.compile(r'https?://([a-zA-Z0-9.-]+)')
    matches = re.findall(url_pattern, html_string)
    domain_counter = Counter(matches)
    mfd = domain_counter.most_common(1)
    return mfd[0][0] if mfd else None


def try_get_base_url(soup: BeautifulSoup):
    if canonical := soup.find("link", {"rel": "canonical"}):
        return urlparse(canonical.get('href')).netloc
    elif base := soup.find('base'):
        return urlparse(base.get('href')).netloc
    elif meta := soup.select_one('meta[name*=url]'):
        return urlparse(meta.get('content')).netloc
    return most_frequent_domain(str(soup))


def clean_soup(soup: BeautifulSoup, try_stylize=False):
    if try_stylize and (domain := try_get_base_url(soup)):
        tag = soup.new_tag(name='base', attrs={'href': 'https://' + domain})
        soup.select_one('html').insert(0, tag)
        stylized = True
    else:
        for tag in soup.select('[src]'):
            tag.decompose()
        for tag in soup.select('[href]'):
            tag['href'] = ''
        stylized = False
    return soup, stylized

