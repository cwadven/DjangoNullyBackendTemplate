from typing import (
    Any,
    List,
    Type,
)

from common.common_criteria.cursor_criteria import CursorCriteria
from django.db.models import (
    QuerySet,
)


def get_objects_with_cursor_pagination(qs: QuerySet,
                                       cursor_criteria: Type[CursorCriteria],
                                       filtering_operator: dict,
                                       size: int) -> tuple[List[Any], bool, str]:
    objects = list(
        qs.filter(
            **filtering_operator
        ).order_by(
            *cursor_criteria.get_ordering_data()
        )[:size + 1]
    )
    has_more = bool(len(objects) > size)
    paginated_objects = objects[:size]
    return (
        paginated_objects,
        has_more,
        (
            cursor_criteria.get_encoded_base64_cursor_data(paginated_objects[-1])
            if has_more else None
        ),
    )
