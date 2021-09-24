from flask import jsonify, request

from app import app
from parsers.sciencedirect import ScienceDirect


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
    p = ScienceDirect(doi)
    response = {
        "message": p.parse(),
        "metadata": {
            "parser": p.parser_name,
            "doi": doi,
            "doi_url": f"https://doi.org/{doi}",
        },
    }
    return jsonify(response)


if __name__ == "__main__":
    app.run()
