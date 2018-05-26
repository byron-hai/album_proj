# coding: utf-8
import boto3
from flask import current_app as app
import logging

fmt = '%(levelname)-6s %(message)s'
logging.basicConfig(level='INFO', format=fmt)

aws_key = 'AKIAOLEI3EIBHJN6EHHA'
aws_secret = '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'
region = 'cn-north-1'

class S3:
    def __init__(self, aws_key=None, aws_secret=None, region=None, logging=logging):
        self.key = aws_key
        self.secret = aws_secret
        self.region = region

        self.logger = logging.getLogger(self.__class__.__name__)
        self.s3 = boto3.client('s3',
                               self.region,
                               aws_access_key_id=self.key,
                               aws_secret_access_key=self.secret)

        if self.s3:
            self.logger.info("Sesion connected")
        else:
            self.logger.error("Session connection failed")
        return

    def get_buckets(self):
        try:
            buckets = self.s3.list_buckets()
            return buckets if buckets else None
        except Exception as err:
            self.logger.error(str(err))
            return

    def get_bucket_objs(self, bucket_name):
        try:
            objs = self.s3.list_objects(Bucket=bucket_name)
            return objs if objs else None
        except Exception as err:
            self.logger.error(str(err))
            return

    def upload_file_to_s3(self, filename, bucket_name, key):
        try:
            self.s3.upload_file(filename,
                                bucket_name,
                                key,
                                ExtraArgs={"ACL": 'public-read'})

        except Exception as err:
            self.logger.error(str(err))
            return err
        return "{}/{}/{}".format(self.s3.meta.endpoint_url, bucket_name, key)

