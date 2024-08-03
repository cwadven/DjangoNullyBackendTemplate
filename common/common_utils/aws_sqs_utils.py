import json

import boto3
from django.conf import settings


def create_sqs_event(queue_url: str, event_data: dict):
    sqs = boto3.client(
        'sqs',
        region_name='ap-northeast-2',
        aws_access_key_id=settings.AWS_IAM_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_IAM_SECRET_ACCESS_KEY,
    )
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(event_data)
    )
    return response


def get_sqs_messages(queue_url: str) -> dict:
    sqs = boto3.client(
        'sqs',
        region_name='ap-northeast-2',
        aws_access_key_id=settings.AWS_IAM_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_IAM_SECRET_ACCESS_KEY,
    )
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1
    )
    messages = response.get('Messages', [])
    message_body = '{}'

    for message in messages:
        message_body = message.get('Body', {})
        receipt_handle = message.get('ReceiptHandle')
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
    return json.loads(message_body)
