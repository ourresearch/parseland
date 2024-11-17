import json
import os
from datetime import datetime, timedelta, timezone
from io import BytesIO
from urllib.parse import urljoin, urlencode

from bs4 import BeautifulSoup
from dateutil.parser import parse
from flask import jsonify, request, redirect, send_file

from app import app
from exceptions import APIError, BadLandingPageError
from find_pdf import find_pdf_link
from find_license import find_license_in_html
from find_bronze_hybrid import check_access_type
from publisher import cache
from publisher.controller import PublisherController
from publisher.utils import prep_message, check_bad_landing_page
from repository.controller import RepositoryController
from util import s3
from util.grobid import clean_soup
from util.s3 import get_landing_page, is_pdf


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
    params = request.args.copy()
    if 'forward' in params:
        del params['forward']
    del params['doi']
    params['doi'] = doi
    params['api_key'] = os.getenv("OPENALEX_PDF_PARSER_API_KEY")
    qs = urlencode(params)
    path = urljoin(os.getenv('OPENALEX_PDF_PARSER_URL'), 'parse-html')
    url = f'{path}?{qs}'
    return redirect(url)


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
    check_cache = request.args.get('check_cache', 't')
    check_cache = check_cache.lower().startswith('t') or check_cache == '1'
    update_cache = False

    if check_cache:
        cached = cache.get(doi)
        if cached:
            cached_obj = json.loads(cached)
            five_min_ago = datetime.now(timezone.utc) - timedelta(minutes=5)

            last_updated, _, cached_response = cached_obj
            last_updated = parse(last_updated)

            if last_updated >= five_min_ago:
                print(f'Cache hit - {doi}')
                return jsonify(cached_response)
            else:
                update_cache = True
        else:
            update_cache = True

    lp_contents = get_landing_page(doi)
    grobid_parse_url = 'https://parseland.herokuapp.com/grobid-parse?doi=' + doi

    if is_pdf(lp_contents):
        params = {
            'doi': doi,
            'api_key': os.getenv("OPENALEX_PDF_PARSER_API_KEY"),
            'include_raw': 'false'
        }
        qs = urlencode(params)
        path = urljoin(os.getenv('OPENALEX_PDF_PARSER_URL'), 'parse')
        url = f'{path}?{qs}'
        return redirect(url)
    pc = PublisherController(lp_contents.decode(), doi)

    if check_bad_landing_page(pc.soup):
        raise BadLandingPageError()

    parser, parsed_msg = pc.best_parser_msg()

    message = prep_message(parsed_msg, parser)

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
        cache.set(doi, None,
                  response)  # Setting current_s3_last_modified to None when updating the cache

    return jsonify(response)


@app.route("/parse-oa")
def parse_oa():
    doi = request.args.get("doi")
    if doi.startswith('http'):
        doi = doi.split('doi.org/')[-1]

    lp_contents = get_landing_page(doi)
    soup = BeautifulSoup(lp_contents.decode(), features='lxml', parser='lxml')

    if check_bad_landing_page(soup):
        raise BadLandingPageError()

    pdf_link = find_pdf_link(soup)
    oa_license = find_license_in_html(lp_contents.decode())

    bronze_hybrid = check_access_type(lp_contents.decode(), soup)

    pdf = {
        "href": pdf_link.href,
        "anchor": pdf_link.anchor,
        "source": pdf_link.source,
    } if pdf_link else None

    print(f"PDF link: {pdf_link}")

    response = {
        "pdf": pdf,
        "license": oa_license,
        "bronze_hybrid": bronze_hybrid,
        "metadata": {
            "doi": doi,
            "doi_url": f"https://doi.org/{doi}",
        },
    }

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
