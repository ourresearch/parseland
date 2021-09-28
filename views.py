from flask import jsonify, request

from app import app
from parser import ParserController


@app.route("/")
def home():
    return jsonify(
        {
            "version": "0.1",
            "app_name": "parseland",
            "msg": "Don't panic",
        }
    )


@app.route("/parse")
def parse():
    doi = request.args.get("doi")
    p = ParserController(doi)
    parser = p.find_parser()
    response = {
        "message": parser.parse(),
        "metadata": {
            "parser": parser.parser_name,
            "doi": doi,
            "doi_url": f"https://doi.org/{doi}",
        },
    }
    return jsonify(response)


if __name__ == "__main__":
    app.run()
