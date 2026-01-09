from datetime import (
    date,
    datetime,
)
from typing import Any

from common.common_interfaces.cursor_criteria_interfaces import CursorCriteriaInterface
from common.common_utils import format_iso8601
from common.common_utils.encode_utils import data_to_urlsafe_base64
from django.db.models import (
    F,
    Q,
)


class CursorCriteria(CursorCriteriaInterface):
    cursor_keys = []

    @classmethod
    def is_valid_decoded_cursor(cls, decoded_cursor: dict) -> bool:
        for cursor_key in cls.cursor_keys:
            if decoded_cursor.get(cursor_key, 'None') == 'None':
                return False
        return True

    @classmethod
    def get_filter_q(cls, decoded_next_cursor: dict) -> Q:
        """
        Cursor pagination filter for composite ordering keys.

        For ordering keys (k1, k2, ... kn), the next page should be selected by a lexicographic
        "strictly after" condition:

        (k1 < v1) OR (k1 = v1 AND k2 < v2) OR ... OR (k1 = v1 AND ... AND k(n-1) = v(n-1) AND kn < vn)

        Direction is derived from the operator in cursor_keys:
        - lt/lte => DESC ordering => use __lt for the pivot comparison
        - gt/gte => ASC ordering  => use __gt for the pivot comparison

        If cursor value is None for a key, we stop building deeper conditions.
        """
        if not decoded_next_cursor:
            return Q()

        keys: list[tuple[str, str, Any]] = []
        for cursor_key in cls.cursor_keys:
            if '__' not in cursor_key:
                # Non-operator keys are ignored for ordering and cursor filtering.
                continue
            attribute, operator = cursor_key.split('__')
            value = decoded_next_cursor.get(cursor_key)
            keys.append((attribute, operator, value))

        # Build lexicographic OR conditions.
        q = Q()
        for i in range(len(keys)):
            attribute_i, operator_i, value_i = keys[i]
            if value_i is None:
                break

            term = Q()
            # equality on previous keys
            valid_prefix = True
            for j in range(i):
                attribute_j, _operator_j, value_j = keys[j]
                if value_j is None:
                    valid_prefix = False
                    break
                term &= Q(**{attribute_j: value_j})
            if not valid_prefix:
                break

            # strict comparison at pivot key based on ordering direction
            if operator_i in {'lt', 'lte'}:
                pivot_lookup = f"{attribute_i}__lt"
            elif operator_i in {'gt', 'gte'}:
                pivot_lookup = f"{attribute_i}__gt"
            else:
                # Unknown operator; skip
                continue

            term &= Q(**{pivot_lookup: value_i})
            q |= term

        return q if q else Q()

    @classmethod
    def get_encoded_base64_cursor_data(cls, data: Any) -> str:
        encoding_data = {}

        for cursor_key in cls.cursor_keys:
            attribute = cursor_key.split('__')[0]
            try:
                value = getattr(data, attribute)
            except AttributeError:
                raise ValueError(f"Attribute '{attribute}' not found in '{data.__class__.__name__}'")
            if isinstance(value, (datetime, date)):
                encoding_data[cursor_key] = format_iso8601(value)
            else:
                encoding_data[cursor_key] = value

        return data_to_urlsafe_base64(encoding_data)

    @classmethod
    def get_ordering_data(cls):
        ordering_data = []
        for cursor_key in cls.cursor_keys:
            if '__' in cursor_key:
                attribute, operator = cursor_key.split('__')
                if operator in {'lt', 'lte'}:
                    ordering_data.append(F(attribute).desc(nulls_last=True))
                elif operator in {'gt', 'gte'}:
                    ordering_data.append(F(attribute).asc(nulls_last=True))
        return ordering_data
