import base64
import json
from typing import Any


def urlsafe_base64_to_data(base64_str: str) -> Any:
    try:
        json_bytes = base64.urlsafe_b64decode(base64_str.encode('utf-8'))
        json_str = json_bytes.decode('utf-8')
        data = json.loads(json_str)
    except Exception:
        raise ValueError
    return data
