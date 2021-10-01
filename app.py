from flask import Flask
from flask_cors import CORS
import requests_cache

app = Flask(__name__)
CORS(app)

# requests_cache.install_cache(
#     cache_name="api_cache", backend="sqlite", expire_after=3000
# )

app.config["JSON_SORT_KEYS"] = False
