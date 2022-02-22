import boto3
from botocore.exceptions import ClientError
import os


def upload_to_bucket_by_id(id: str, bucket='aicorebucket828') -> bool:
    s3_client = boto3.client('s3')
    folder = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), f'../raw_data/{id}')
    for x in os.listdir(folder):
        if x.startswith(id):
            try:
                s3_client.upload_file(
                    os.path.join(folder, x),
                    bucket,
                    os.path.split(x)[1]
                )
            except ClientError as e:
                print(e)
                return False
    return True


def upload_folder_to_bucket(bucket='aicorebucket828'):
    folder = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '../raw_data/')
    for x in os.listdir(folder):
        upload_to_bucket_by_id(x)
