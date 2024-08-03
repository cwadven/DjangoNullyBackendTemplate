import base64
import json
from typing import Any


def data_to_urlsafe_base64(data: Any) -> str:
    json_str = json.dumps(data)
    json_bytes = json_str.encode('utf-8')
    base64_str = base64.urlsafe_b64encode(json_bytes).decode('utf-8')
    return base64_str
