from common.common_decorators.request_decorators import pagination
from product.dtos.model_dtos import PointProductItem
from product.dtos.response_dtos import PointProductListResponse
from product.models import PointProduct
from rest_framework.response import Response
from rest_framework.views import APIView


class PointProductListAPIView(APIView):
    @pagination(default_size=10)
    def get(self, request, start_row, end_row):
        point_products = [
            PointProductItem.of(point_product).model_dump()
            for point_product in PointProduct.objects.get_actives().order_by('ordering')[start_row:end_row]
        ]
        return Response(
            data=PointProductListResponse(
                products=point_products
            ).model_dump(),
            status=200
        )
