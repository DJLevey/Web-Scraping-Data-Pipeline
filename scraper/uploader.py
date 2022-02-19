import boto3
from botocore.exceptions import ClientError
import logging
import tempfile
import shutil
import os


def upload_to_bucket(id: str, bucket):
    s3_client = boto3.client('s3')
    folder = f'../raw_data/{id}'
    with tempfile.TemporaryDirectory() as tmp:
        shutil.make_archive(os.path.join(tmp, id), 'zip', folder)
        try:
            s3_client.upload_file(
                f'{os.path.join(tmp, id)}.zip',
                'aicorebucket828',
                f'{id}.zip')
        except ClientError as e:
            logging.error(e)
            return False
        return True
