from pydantic import BaseModel, Field


class PointProductListResponse(BaseModel):
    products: list = Field(...)
