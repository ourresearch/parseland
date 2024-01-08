import json
import os
import time
from datetime import datetime, timedelta, timezone
from io import BytesIO
from urllib.parse import urljoin, urlencode

from flask import jsonify, request, redirect, send_file

from publisher.parsers.grobid import GrobidParser
from util import s3
from app import app
from exceptions import APIError, BadLandingPageError
from publisher.controller import PublisherController
from publisher.utils import prep_message, check_bad_landing_page
from repository.controller import RepositoryController
from publisher import cache
from dateutil.parser import parse
from bs4 import BeautifulSoup

from util.grobid import html_to_pdf, clean_soup
from util.s3 import s3_last_modified, get_landing_page, is_pdf


@app.route("/")
def home():
    return jsonify(
        {
            "version": "0.1",
            "app_name": "parseland",
            "msg": "Don't panic",
        }
    )


@app.route('/grobid-parse')
def grobid_parse():
    doi = request.args.get("doi")
    if doi.startswith('http'):
        doi = doi.split('doi.org/')[1]
    forward = request.args.get('forward', True)
    params = request.args.copy()
    if 'forward' in params:
        del params['forward']
    del params['doi']
    params['doi'] = doi
    params['api_key'] = os.getenv("OPENALEX_PDF_PARSER_API_KEY")
    qs = urlencode(params)
    if forward:
        path = urljoin(os.getenv('OPENALEX_PDF_PARSER_URL'), 'parse-html')
        url = f'{path}?{qs}'
        return redirect(url)
    html = get_landing_page(doi)
    pdf = html_to_pdf(html)
    parser = GrobidParser(pdf)
    return parser.parse()


def is_true(value: str):
    return value.lower().startswith('t') or value == '1'


@app.route('/view')
def view():
    doi = request.args.get("doi")
    try_stylize = request.args.get('try_stylize', default=False, type=is_true)
    if doi.startswith('http'):
        doi = doi.split('doi.org/')[1]
    lp_contents = s3.get_landing_page(doi)
    if is_pdf(lp_contents):
        # Specify the mimetype as 'application/pdf' and set as_attachment to False
        return send_file(BytesIO(lp_contents), mimetype='application/pdf',
                         as_attachment=False)
    soup = BeautifulSoup(lp_contents.decode(), features='lxml', parser='lxml')
    cleaned, _ = clean_soup(soup, try_stylize)
    return str(cleaned)


@app.route("/parse-publisher")
def parse_publisher():
    doi = request.args.get("doi")
    if doi.startswith('http'):
        doi = doi.split('doi.org/')[-1]
    check_cache = request.args.get('check_cache', 'true')
    check_cache = check_cache.startswith('t') or check_cache == 1
    update_cache = False
    current_s3_last_modified = None
    if check_cache:
        cached = cache.get(doi)
        if cached:
            cached_obj = json.loads(cached)
            five_min_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
            if len(cached_obj) == 3:
                last_updated, cached_s3_last_modified, cached_response = cached_obj
                last_updated = parse(last_updated)
                if last_updated >= five_min_ago:
                    print(f'Cache hit - {doi}')
                    return jsonify(cached_response)
            else:
                cached_s3_last_modified, cached_response = cached_obj
                update_cache = True
            cached_s3_last_modified = parse(cached_s3_last_modified)
            if cached_s3_last_modified >= five_min_ago:
                if update_cache:
                    cache.set(doi, cached_s3_last_modified, cached_response)
                print(f'Cache hit - {doi}')
                return jsonify(cached_response)
            else:
                current_s3_last_modified = s3_last_modified(doi)
                if cached_s3_last_modified >= current_s3_last_modified:
                    if update_cache:
                        cache.set(doi, current_s3_last_modified,
                                  cached_response)
                    return jsonify(cached_response)
                else:
                    update_cache = True
        else:
            update_cache = True
    lp_contents = get_landing_page(doi)
    grobid_parse_url = 'https://parseland.herokuapp.com/grobid-parse?doi=' + doi
    if is_pdf(lp_contents):
        params = {'doi': doi,
                  'api_key': os.getenv("OPENALEX_PDF_PARSER_API_KEY"),
                  'include_raw': 'false'}
        qs = urlencode(params)
        path = urljoin(os.getenv('OPENALEX_PDF_PARSER_URL'), 'parse')
        url = f'{path}?{qs}'
        return redirect(url)
    else:
        pc = PublisherController(lp_contents, doi)
        if check_bad_landing_page(pc.soup):
            raise BadLandingPageError()
        parser = pc.find_parser()

    parsed_message = parser.parse()

    message = prep_message(parsed_message, parser)

    response = {
        "message": message,
        "metadata": {
            "parser": parser.parser_name,
            "grobid_parse_url": grobid_parse_url,
            "doi": doi,
            "doi_url": f"https://doi.org/{doi}",
        },
    }
    if check_cache and update_cache:
        if current_s3_last_modified is None:
            current_s3_last_modified = s3_last_modified(doi)
        cache.set(doi, current_s3_last_modified, response)
    return jsonify(response)


@app.route("/parse-repository")
def parse_repository():
    page_id = request.args.get("page-id")
    rc = RepositoryController(page_id)
    parser = rc.find_parser()
    if parser.authors_found():
        message = parser.parse()
    else:
        message = parser.no_authors_output()
    response = {
        "message": message,
        "metadata": {
            "parser": parser.parser_name,
            "page_id": page_id,
        },
    }
    return jsonify(response)


@app.errorhandler(APIError)
def handle_exception(err):
    """Return custom JSON when APIError or its children are raised"""
    response = {"error": err.description, "message": ""}
    if len(err.args) > 0:
        response["message"] = err.args[0]
    # Add some logging so that we can monitor different types of errors
    app.logger.error("{}: {}".format(err.description, response["message"]))
    return jsonify(response), err.code


@app.route('/debug-sentry')
def trigger_error():
    division_by_zero = 1 / 0


if __name__ == "__main__":
    app.run(port=5001)
