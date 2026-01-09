from typing import (
    Any,
    List,
    Type,
)

from common.common_criteria.cursor_criteria import CursorCriteria
from django.db.models import (
    QuerySet,
    Q,
)


def get_objects_with_cursor_pagination(
        qs: QuerySet,
        decoded_next_cursor: dict,
        size: int,
        cursor_criteria: Type[CursorCriteria],
) -> tuple[List[Any], bool, str]:
    if decoded_next_cursor:
        filter_q: Q = cursor_criteria.get_filter_q(decoded_next_cursor)
        if filter_q:
            qs = qs.filter(filter_q)
    ordering_data = cursor_criteria.get_ordering_data()
    if ordering_data:
        qs = qs.order_by(*ordering_data)

    objects = list(
        qs[:size + 1]
    )
    has_more = bool(len(objects) > size)
    paginated_objects = objects[:size]
    return (
        paginated_objects,
        has_more,
        (
            cursor_criteria().get_encoded_base64_cursor_data(paginated_objects[-1])
            if has_more else None
        ),
    )
