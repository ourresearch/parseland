import os
from gzip import decompress
from urllib.parse import quote

import boto3
import botocore

from exceptions import S3FileNotFoundError

S3_LANDING_PAGE_BUCKET = os.getenv('AWS_S3_LANDING_PAGE_BUCKET')


def make_s3():
    session = boto3.session.Session()
    return session.client('s3',
                          aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.getenv(
                              'AWS_SECRET_ACCESS_KEY'),
                          region_name=os.getenv('AWS_DEFAULT_REGION'))


DEFAULT_S3 = make_s3()


def s3_last_modified(doi, s3=DEFAULT_S3):
    return get_obj(S3_LANDING_PAGE_BUCKET, doi_to_lp_key(doi), s3)[
        'LastModified']


def get_obj(bucket, key, s3=DEFAULT_S3):
    try:
        obj = s3.get_object(Bucket=bucket,
                            Key=key)
        return obj
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] in {"404", "NoSuchKey"}:
            raise S3FileNotFoundError()


def doi_to_lp_key(doi: str):
    return quote(doi.lower(), safe='')


def get_landing_page(doi, s3=DEFAULT_S3):
    key = doi_to_lp_key(doi)
    obj = get_obj(S3_LANDING_PAGE_BUCKET, key, s3)
    contents = decompress(obj['Body'].read())
    return contents


def is_pdf(contents: bytes):
    return contents.startswith(b"%PDF-")
