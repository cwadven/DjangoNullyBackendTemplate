from typing import List

from promotion.consts import BannerTargetLayer
from pydantic import (
    BaseModel,
    Field,
)


class GetBannerRequest(BaseModel):
    target_layer: BannerTargetLayer = Field(...)


class GetBannerResponse(BaseModel):
    banners: List = Field(...)
