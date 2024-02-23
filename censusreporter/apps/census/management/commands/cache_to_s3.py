from django.core.management.base import BaseCommand
from multiprocessing import Pool
from traceback import format_exc
import boto3
import json
import io
import gzip

from ...profile import geo_profile, enhance_api_data

import logging
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

# Initialize the S3 resource using boto3
s3 = boto3.resource('s3')

def s3_keyname(geoid):
    return '/1.0/data/profiles/%s.json' % geoid

def key(geoid):
    bucket_name = 'embed.censusreporter.org'
    keyname = s3_keyname(geoid)
    # Use the Object method to access the specific S3 object
    return s3.Object(bucket_name, keyname)

def write_profile_json(s3_key, data):
    # Since we are working with boto3, modify the way metadata is handled
    # and how the file is uploaded
    metadata = {'Content-Type': 'application/json', 'Content-Encoding': 'gzip'}

    # Create gzipped version of json in memory
    memfile = io.BytesIO()
    with gzip.GzipFile(mode='wb', fileobj=memfile) as gzip_data:
        gzip_data.write(data.encode('utf-8'))
    memfile.seek(0)

    # Store static version on S3 using put method
    s3_key.put(Body=memfile, Metadata=metadata)

def seed(geoid):
    logger.info("Working on {}".format(geoid))
    try:
        api_data = geo_profile(geoid)
        api_data = enhance_api_data(api_data)

        s3key = key(geoid)
        write_profile_json(s3key, json.dumps(api_data))
        logger.info("Wrote to key {}".format(s3key.key))
    except Exception as e:
        logger.error("Problem caching {}".format(geoid))
        logger.exception(e)
    logger.info("Done working on {}".format(geoid))


class Command(BaseCommand):
    help = 'Pre-generates some Census Reporter content and places it on S3.'

    def add_arguments(self, parser):
        parser.add_argument('seed_file', type=str, help='The name of a file containing the seed geo_ids.')

    def handle(self, *args, **options):
        seed_file_path = options['seed_file']
        if not seed_file_path:
            print("Please include the name of a file containing the seed geo_ids.")
            return False

        parallelism = 4
        if 'parallelism' in options:
            parallelism = int(options.get('parallelism'))

        pool = Pool(parallelism)

        with open(seed_file_path, 'r') as seed_file:
            for geoid in seed_file:
                pool.apply_async(seed, (geoid.strip(),))

        pool.close()
        pool.join()
