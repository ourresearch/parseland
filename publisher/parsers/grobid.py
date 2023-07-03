from io import BytesIO

from bs4 import BeautifulSoup
from grobid_client import Client
import os
from urllib.parse import urljoin

from grobid_client.models import ProcessForm
from tenacity import retry, stop_after_attempt, wait_fixed

from publisher.parsers.parser import Parser
from grobid_client.types import File
from grobid_client.api.pdf import process_fulltext_document


class GrobidParser(Parser):
    parser_name = "grobid"

    BASE_URL = os.getenv('GROBID_BASE_URL')

    # BASE_URL = 'https://kermitt2-grobid.hf.space/'

    def __init__(self, pdf_contents):
        base_api_url = GrobidParser.BASE_URL if GrobidParser.BASE_URL.endswith(
            '/api') else urljoin(GrobidParser.BASE_URL, 'api')
        self.client = Client(base_url=base_api_url, timeout=30)
        self.pdf_contents = pdf_contents

    @staticmethod
    def no_authors_output():
        return {"authors": [], "abstract": None, "published_date": None,
                "genre": None, 'references': []}

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(3))
    def get_grobid_soup(self):
        form = ProcessForm(
            segment_sentences="1",
            include_raw_citations="1",
            include_raw_affiliations="1",
            input_=File(file_name="contents.pdf",
                        payload=BytesIO(self.pdf_contents),
                        mime_type="application/pdf"),
        )
        r = process_fulltext_document.sync_detailed(client=self.client,
                                                    multipart_data=form)
        soup = BeautifulSoup(r.content, parser='lxml', features='lxml')

        if body_tag := soup.select_one('body'):
            if 'HTTP ERROR 503' in body_tag.text:
                raise Exception('503 error from GROBID')

    def parse(self):
        soup = self.get_grobid_soup()
        body = None
        if body_tag := soup.select_one('body'):
            body = body_tag.text
        authors = []
        author_tags = soup.select('sourceDesc author')
        universal_affs = []
        for tag in author_tags:
            author = {'name': None, 'affiliations': [],
                      'is_corresponding': tag.get('role', '') == 'corresp'}
            if first_name := tag.select_one('forename[type=first]'):
                last_name = tag.select_one('surname')
                author['name'] = f'{first_name.text} {last_name.text}'
                aff_tags = tag.select('note[type=raw_affiliation]')
                for aff_tag in aff_tags:
                    if label := aff_tag.find('label'):
                        label.decompose()
                    author['affiliations'].append(aff_tag.text.strip())
                authors.append(author)
            elif universal_aff_tag := tag.select_one(
                    'note[type=raw_affiliation]'):
                if label := universal_aff_tag.find('label'):
                    label.decompose()
                universal_affs.append(universal_aff_tag.text)
        for author in authors:
            if not author['affiliations']:
                author['affiliations'].extend(universal_affs)
        abstract = None
        if abstract_tag := soup.select_one('abstract'):
            abstract = abstract_tag.text

        ref_tags = soup.select(
            'div[type=references] listbibl biblstruct note[type=raw_reference]')
        refs = [tag.text for tag in ref_tags]
        return {'authors': authors,
                'abstract': abstract,
                'fulltext': body,
                'references': refs}
