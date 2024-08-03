from typing import Optional

from pydantic import (
    BaseModel,
    Field,
)


class ConstanceType(BaseModel):
    id: int = Field(description='상수 ID')
    name: Optional[str] = Field(description='상수 이름')
    display_name: Optional[str] = Field(description='상수 표시 이름')


class ConstanceDetailType(BaseModel):
    id: int = Field(description='상수 상세 ID')
    name: Optional[str] = Field(description='상수 상세 이름')
    display_name: Optional[str] = Field(description='상수 상세 표시 이름')
    parent_id: Optional[int] = Field(description='상위 상위 ID')
    parent_name: Optional[str] = Field(description='상위 상위 이름')
    parent_display_name: Optional[str] = Field(description='상위 상위 표시 이름')
