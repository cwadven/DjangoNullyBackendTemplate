from datetime import datetime

from django.db.models import (
    Q,
    QuerySet,
)
from django.utils import timezone
from promotion.consts import BannerTargetLayer
from promotion.models import Banner


def get_active_banners(target_layer: BannerTargetLayer, now: datetime = None) -> QuerySet[Banner]:
    if now is None:
        now = timezone.now()

    return Banner.objects.select_related(
        'promotion_rule'
    ).filter(
        Q(promotion_rule__displayable=True),
        Q(target_layer=target_layer.value),
        Q(promotion_rule__display_start_time__lte=now) | Q(promotion_rule__display_start_time__isnull=True),
        Q(promotion_rule__display_end_time__gte=now) | Q(promotion_rule__display_end_time__isnull=True),
    ).prefetch_related(
        'tags'
    )
