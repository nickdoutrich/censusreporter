"""Updated script for clearing out cached profiles using boto3."""

import boto3
from gzip import GzipFile
from io import BytesIO  # Changed from cStringIO import StringIO for Python 3 compatibility
import json
import re
import requests
import time
import os

# Constants and configurations
CACHE_KEY_YEAR = '2016'
OBSOLETE_YEAR = '2015'
GEOID_LIST = '/tmp/2016_1yr_geoids.txt'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = 'embed.censusreporter.org'  # Example bucket name

# Ensure AWS credentials are set
if AWS_ACCESS_KEY_ID is None or AWS_SECRET_ACCESS_KEY is None:
    print("You must define AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY as environment variables")
    sys.exit()

# Initialize boto3
s3_resource = boto3.resource('s3')
bucket = s3_resource.Bucket(BUCKET_NAME)

def decode_key(key_object):
    """Decode GZIP content from S3 key object."""
    gzipfile = GzipFile(fileobj=BytesIO(key_object.get()['Body'].read()))
    return gzipfile.read()

# Example function to delete profiles based on a pattern
def delete_by_pattern(key_prefix, patterns, do_it=False):
    """Delete keys by pattern."""
    compiled_patterns = [re.compile(pattern) for pattern in patterns]
    delete_count = 0

    for obj in bucket.objects.filter(Prefix=key_prefix):
        key_name = obj.key[len(key_prefix):]
        if any(pat.match(key_name) for pat in compiled_patterns):
            if do_it:
                obj.delete()
                print(f"Deleted {obj.key}")
            else:
                print(f"Would delete {obj.key}")
            delete_count += 1

    print(f"Total deleted (or would be deleted) files: {delete_count}")

if __name__ == '__main__':
    # Example usage
    delete_by_pattern(
        '1.0/data/profiles/2018/',
        [
            r'05000US.*',
            r'31000US.*',
            r'33000US.*',
        ],
        do_it=False  # Change to True to actually perform deletion
    )
    delete_by_pattern(
        'tiger2018/show/',
        [
            r'05000US.*parents.json',
            r'31000US.*parents.json',
        ],
        do_it=False  # Change to True to actually perform deletion
    )
