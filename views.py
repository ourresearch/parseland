from flask import request

from app import app
from parser import Parser


@app.route("/")
def hello_world():  # put application's code here
    return "Hello World!"


@app.route("/parse")
def parse():
    doi = request.args.get("doi")
    p = Parser(doi)
    p.get_authors()
    return "parsing!"


if __name__ == "__main__":
    app.run()
