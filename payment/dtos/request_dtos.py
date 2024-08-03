from pydantic import BaseModel, Field


class KakaoPayReadyForBuyProductRequest(BaseModel):
    product_id: int = Field(...)
    product_type: str = Field(...)
    payment_type: str = Field(...)
    quantity: int = Field(...)
    order_phone_number: str = Field(...)
