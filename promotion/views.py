from common.common_decorators.request_decorators import (
    mandatories,
    pagination,
)
from promotion.consts import BannerTargetLayer
from promotion.dtos.model_dtos import PromotionBanner
from promotion.dtos.request_dtos import (
    GetBannerRequest,
    GetBannerResponse,
)
from promotion.services import get_active_banners
from rest_framework.response import Response
from rest_framework.views import APIView


class PromotionBannerAPIView(APIView):
    @pagination(default_size=10)
    @mandatories('target_layer')
    def get(self, request, start_row, end_row, m):
        try:
            banner_request = GetBannerRequest(target_layer=BannerTargetLayer(m['target_layer']))
        except ValueError:
            return Response({'message': '잘못된 target_layer 입니다.'}, status=400)

        banners = get_active_banners(banner_request.target_layer)[start_row:end_row]
        return Response(
            GetBannerResponse(banners=[PromotionBanner.of(banner) for banner in banners]).model_dump(),
            status=200,
        )
