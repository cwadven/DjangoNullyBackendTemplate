from typing import (
    Any,
)

from pydantic_core import (
    InitErrorDetails,
    PydanticCustomError,
)


def generate_pydantic_error_detail(error_type: str, message: str, input_key: str, input_value: Any) -> InitErrorDetails:
    return InitErrorDetails(
        type=PydanticCustomError(
            error_type,
            f', {message}',
        ),
        loc=(input_key,),
        input=input_value,
        ctx={},
    )
