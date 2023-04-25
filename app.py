from flask import Flask
from flask_cors import CORS
import sentry_sdk

sentry_sdk.init(
    dsn="https://f662d716c94f459ab2eacaed33a95c43@o4504922615775232.ingest.sentry.io/4504922615775232",

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=0.2
)

app = Flask(__name__)
CORS(app)

app.config["JSON_SORT_KEYS"] = False
