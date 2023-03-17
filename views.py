from flask import jsonify, request

from app import app
from exceptions import APIError, BadLandingPageError
from publisher.controller import PublisherController
from publisher.utils import prep_message, check_bad_landing_page
from repository.controller import RepositoryController


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
    pc = PublisherController(doi)
    if check_bad_landing_page(pc.soup):
        raise BadLandingPageError()
    parser = pc.find_parser()

    parsed_message = parser.parse()

    message = prep_message(parsed_message, parser)

    if doi.startswith('http'):
        doi = doi.split('doi.org/')[1]
    response = {
        "message": message,
        "metadata": {
            "parser": parser.parser_name,
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


if __name__ == "__main__":
    app.run()
