import json

import requests


def notify_slack_simple_text(channel_url: str, text: str):
    requests.post(
        url=channel_url,
        data=json.dumps({'text': text}),
    )
