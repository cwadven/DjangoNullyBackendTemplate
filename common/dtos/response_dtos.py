from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from common.dtos.helper_dtos import (
    ConstanceDetailType,
    ConstanceType,
)
from pydantic import (
    BaseModel,
    Field,
)


class HealthCheckResponse(BaseModel):
    message: str = Field(...)


class ConstanceTypeResponse(BaseModel):
    data: List[ConstanceType] = Field(default_factory=list, description='Constance type list')


class ConstanceDetailTypeResponse(BaseModel):
    data: List[ConstanceDetailType] = Field(default_factory=list, description='Constance type detail list')


class GetPreSignedURLResponse(BaseModel):
    url: str = Field(...)
    data: Dict[str, Any] = Field(default_factory=dict)


class CursorPaginatorResponse(BaseModel):
    data: list = Field(...)
    next_cursor: Optional[str] = Field(None)
    has_more: bool = Field(...)
