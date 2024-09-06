import uuid

import boto3
import requests
from botocore.exceptions import ClientError


def generate_pre_signed_url_info(
        s3_client: boto3.client,
        bucket_name: str,
        file_name: str,
        _type: str = 'common',
        unique: str = '0',
        expires_in: int = 1000,
        same_file_name: bool = False
) -> dict:
    try:
        key = f'{_type}/{unique}/'
        if same_file_name:
            key += f'{file_name}'
        else:
            key += f'{uuid.uuid4()}_{file_name}'
        response = s3_client.generate_presigned_post(
            Bucket=bucket_name,
            Key=key,
            Conditions=[
                ['content-length-range', 0, 10485760]
            ],
            ExpiresIn=expires_in
        )
        return response
    except ClientError as e:
        raise Exception(e)


def upload_file_to_pre_signed_url(pre_signed_url: str, pre_signed_data: dict, file: bytes) -> int:
    try:
        response = requests.post(
            url=pre_signed_url,
            data=pre_signed_data,
            files={'file': file},
        )
        return response.status_code == 204
    except Exception:
        return False
