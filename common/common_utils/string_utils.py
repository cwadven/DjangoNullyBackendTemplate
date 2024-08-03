import random
import string
from datetime import (
    date,
    datetime,
    timedelta,
    timezone,
)
from typing import (
    List,
    Sequence,
    Union,
)


def generate_random_string_digits(length: int = 4) -> str:
    return ''.join(random.choice(string.digits) for _ in range(length))


def get_filtered_by_startswith_text_and_convert_to_standards(startswith_text: str, keys: Sequence, is_integer=False) -> List[Union[str, int]]:
    """
    Filters keys that start with a specific text from an iterable type,
    and converts the values of specific portions of the keys to integers based on the provided condition.

    [ Example ]
    If startswith_text is 'home_popup_modal_':
    Input: ['home_popup_modal_1', 'home_popup_modal_2', 'home_popup_modal_3', 'home_popup_modal_4', 'k_popup_modal_10']
    Output (if is_integer=True): [1, 2, 3, 4]
    Output (if is_integer=False): ['1', '2', '3', '4']

    :param startswith_text: The text that the keys should start with for filtering.
    :param keys: An iterable containing keys to be filtered and processed.
    :param is_integer: Determines whether the extracted values should be converted to integers.
    :return: A list containing filtered and processed values based on the specified conditions.
    """
    return [
        int(key.replace(startswith_text, '')) if is_integer else key.replace(startswith_text, '')
        for key in keys if key.startswith(startswith_text)
    ]


def format_iso8601(dt: Union[datetime, date], date_timezone: str = '+09:00'):
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
        formatted = dt.strftime('%Y-%m-%dT%H:%M:%S%z')
        return formatted[:-2] + ':' + formatted[-2:]
    elif isinstance(dt, date):
        formatted = dt.strftime('%Y-%m-%d')
        return f'{formatted}T00:00:00{date_timezone}'
    else:
        raise TypeError("Unsupported type")


def format_utc(dt: Union[datetime, date], adjust_hours=9) -> str:
    """
    Adjust Hour for default value is 9 due to KST
    """
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    elif isinstance(dt, date):
        _timezone = timezone(timedelta(hours=adjust_hours))
        timezone_datetime = datetime.combine(dt, datetime.min.time(), _timezone)
        utc_datetime = timezone_datetime.astimezone(timezone.utc)
        return utc_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
    else:
        raise TypeError("Unsupported type")


def string_to_list(input_string: str, separator: str = ',') -> list:
    """
    Convert a string separated by a specified separator into a list of strings,
    each element being stripped of surrounding whitespace and ignoring empty strings.

    Args:
    input_string (str): A string separated by the specified separator.
    separator (str): The character used to split the input string. Default is ','.

    Returns:
    list: A list of strings where each string is stripped of any surrounding whitespace and not empty.
    """
    return [item.strip() for item in input_string.split(separator) if item.strip()]
