import json
import time
import timeit
from datetime import datetime, timedelta, timezone

from flask import jsonify, request

import util.s3
from app import app
from exceptions import APIError, BadLandingPageError
from pdf.controller import PDFController
from publisher.controller import PublisherController
from publisher.utils import prep_message, check_bad_landing_page
from repository.controller import RepositoryController
from publisher import cache
from dateutil.parser import parse


@app.route("/")
def home():
    return jsonify(
        {
            "version": "0.1",
            "app_name": "parseland",
            "msg": "Don't panic",
        }
    )


@app.route("/parse-publisher")
def parse_publisher():
    doi = request.args.get("doi")
    if doi.startswith('http'):
        doi = doi.split('doi.org/')[1]
    check_cache = request.args.get('check_cache', 'true')
    check_cache = check_cache.startswith('t') or check_cache == 1
    update_cache = False
    current_s3_last_modified = None
    if check_cache:
        cached = cache.get(doi)
        if cached:
            cached_obj = json.loads(cached)
            day_ago = datetime.now(timezone.utc) - timedelta(hours=24)
            if len(cached_obj) == 3:
                last_updated, cached_s3_last_modified, cached_response = cached_obj
                last_updated = parse(last_updated)
                if last_updated >= day_ago:
                    print(f'Cache hit - {doi}')
                    return jsonify(cached_response)
            else:
                cached_s3_last_modified, cached_response = cached_obj
                update_cache = True
            cached_s3_last_modified = parse(cached_s3_last_modified)
            if cached_s3_last_modified >= day_ago:
                if update_cache:
                    cache.set(doi, cached_s3_last_modified, cached_response)
                print(f'Cache hit - {doi}')
                return jsonify(cached_response)
            else:
                current_s3_last_modified = util.s3.s3_last_modified(doi)
                if cached_s3_last_modified >= current_s3_last_modified:
                    if update_cache:
                        cache.set(doi, current_s3_last_modified, cached_response)
                    return jsonify(cached_response)
                else:
                    update_cache = True
        else:
            update_cache = True

    pc = PublisherController(doi)
    if check_bad_landing_page(pc.soup):
        raise BadLandingPageError()
    parser = pc.find_parser()

    parsed_message = parser.parse()

    message = prep_message(parsed_message, parser)

    response = {
        "message": message,
        "metadata": {
            "parser": parser.parser_name,
            "doi": doi,
            "doi_url": f"https://doi.org/{doi}",
        },
    }
    if check_cache and update_cache:
        if current_s3_last_modified is None:
            tic = time.perf_counter()
            current_s3_last_modified = util.s3.s3_last_modified(doi)
            toc = time.perf_counter()
            print(f"S3 fetch took {toc - tic:0.4f} seconds")
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
    app.run()
