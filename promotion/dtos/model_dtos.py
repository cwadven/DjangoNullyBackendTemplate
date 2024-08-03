from typing import (
    List,
    Optional,
)

from pydantic import (
    BaseModel,
    Field,
)


class PromotionBanner(BaseModel):
    banner_id: int = Field(...)
    title: Optional[str] = None
    title_font_color: Optional[str] = None
    description: Optional[str] = None
    description_font_color: Optional[str] = None
    background_color: Optional[str] = None
    big_image: Optional[str] = None
    middle_image: Optional[str] = None
    small_image: Optional[str] = None
    action_page: Optional[str] = None
    target_pk: Optional[str] = None
    target_type: Optional[str] = None
    external_target_url: Optional[str] = None
    tags: List[str] = Field(...)

    @classmethod
    def of(cls, banner: 'Banner') -> 'PromotionBanner':  # noqa
        return cls(
            banner_id=banner.id,
            title=banner.title,
            title_font_color=banner.title_font_color,
            description=banner.description,
            description_font_color=banner.description_font_color,
            background_color=banner.background_color,
            big_image=banner.big_image,
            middle_image=banner.middle_image,
            small_image=banner.small_image,
            action_page=banner.promotion_rule.action_page,
            target_pk=banner.promotion_rule.target_pk,
            target_type=banner.promotion_rule.target_type,
            external_target_url=banner.promotion_rule.external_target_url,
            tags=list(banner.tags.values_list('name', flat=True))
        )
