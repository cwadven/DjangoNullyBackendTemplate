from typing import Optional

from pydantic import (
    BaseModel,
    Field,
)


class PointProductItem(BaseModel):
    product_id: int = Field(...)
    product_type: str = Field(...)
    title: str = Field(...)
    description: Optional[str] = None
    price: int = Field(...)
    point: int = Field(...)
    is_sold_out: bool = Field(...)
    bought_count: int = Field(...)
    review_count: int = Field(...)
    review_rate: float = Field(...)

    @classmethod
    def of(cls, point_product: 'PointProduct') -> 'PointProductItem':  # noqa
        return cls(
            product_id=point_product.id,
            product_type=point_product.product_type,
            title=point_product.title,
            description=point_product.description,
            price=point_product.price,
            point=point_product.point,
            is_sold_out=point_product.is_sold_out,
            bought_count=point_product.bought_count,
            review_count=point_product.review_count,
            review_rate=point_product.review_rate,
        )
