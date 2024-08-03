import uuid

import boto3
import requests
from botocore.config import Config
from botocore.exceptions import ClientError
from django.conf import settings


def generate_pre_signed_url_info(
        file_name: str,
        _type: str = 'common',
        unique: str = '0',
        expires_in: int = 1000,
        same_file_name: bool = False
) -> dict:
    s3_client = boto3.client(
        's3',
        region_name='ap-northeast-2',
        aws_access_key_id=settings.AWS_IAM_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_IAM_SECRET_ACCESS_KEY,
        config=Config(signature_version='s3v4')
    )
    try:
        key = f'{_type}/{unique}/'
        if same_file_name:
            key += f'{file_name}'
        else:
            key += f'{uuid.uuid4()}_{file_name}'
        response = s3_client.generate_presigned_post(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=key,
            Conditions=[
                ['content-length-range', 0, 10485760]
            ],
            ExpiresIn=expires_in
        )
        return response
    except ClientError as e:
        raise Exception(e)


def upload_file_to_presigned_url(presined_url: str, presigned_data: dict, file: bytes) -> int:
    try:
        response = requests.post(
            url=presined_url,
            data=presigned_data,
            files={'file': file},
        )
        return response.status_code == 204
    except Exception:
        return False
