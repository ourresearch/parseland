import json

from flask import jsonify, request

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
    cached = cache.get(doi)
    s3_last_modified = cache.s3_last_modified(doi)
    update_cache = False
    if cached:
        cached_last_modified, cached_response = json.loads(cached)
        cached_last_modified = parse(cached_last_modified)
        if cached_last_modified >= s3_last_modified:
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
    if update_cache:
        cache.set(doi, s3_last_modified, response)
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
