import json
from datetime import datetime, timezone

import redis
import os


REDIS_CONN = redis.Redis.from_url(os.getenv('REDISCLOUD_URL'))


def set(doi, last_modified, response):
    obj = json.dumps([datetime.now(timezone.utc), last_modified, response], default=str)
    REDIS_CONN.set(doi, obj)


def get(doi):
    return REDIS_CONN.get(doi)


