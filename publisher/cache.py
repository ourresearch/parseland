import json
from threading import Lock
from urllib.parse import quote

import boto3
import botocore
import redis
import os

from exceptions import S3FileNotFoundError

# S3_LOCK = Lock()
S3_LANDING_PAGE_BUCKET = os.getenv('AWS_S3_LANDING_PAGE_BUCKET')


def make_s3():
    session = boto3.session.Session()
    return session.client('s3',
                          aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.getenv(
                              'AWS_SECRET_ACCESS_KEY'))


S3 = make_s3()

REDIS_CONN = redis.Redis.from_url(os.getenv('REDISCLOUD_URL'))


def set(doi, last_modified, response):
    obj = json.dumps([last_modified, response], default=str)
    REDIS_CONN.set(doi, obj)


def get(doi):
    return REDIS_CONN.get(doi)


def doi_to_lp_key(doi):
    return quote(doi, safe='')


def s3_last_modified(doi):
    # with S3_LOCK:
    try:
        obj = S3.get_object(Bucket=S3_LANDING_PAGE_BUCKET,
                            Key=doi_to_lp_key(doi))
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] in {"404", "NoSuchKey"}:
            raise S3FileNotFoundError()
    return obj['LastModified']
