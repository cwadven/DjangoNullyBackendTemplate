from pydantic import BaseModel, Field


class KakaoPayReadyForBuyProductResponse(BaseModel):
    tid: str = Field(...)
    next_redirect_app_url: str = Field(...)
    next_redirect_mobile_url: str = Field(...)
    next_redirect_pc_url: str = Field(...)
