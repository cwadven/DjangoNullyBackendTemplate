from common.common_consts.common_error_messages import InvalidInputResponseErrorStatus
from common.common_exceptions import PydanticAPIException
from common.common_utils import generate_pre_signed_url_info
from common.consts import IMAGE_CONSTANCE_TYPES
from common.dtos.request_dtos import GetPreSignedURLRequest
from common.dtos.response_dtos import (
    ConstanceTypeResponse,
    GetPreSignedURLResponse,
    HealthCheckResponse,
)
from common.exceptions import (
    ExternalAPIException,
    InvalidPathParameterException,
)
from common.helpers.constance_helpers import (
    CONSTANCE_TYPE_HELPER_MAPPER,
)
from member.permissions import IsMemberLogin
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    def get(self, request):
        return Response(HealthCheckResponse(message='OK').model_dump(), status=200)


class ConstanceTypeView(APIView):
    def get(self, request, constance_type: str):
        constance_type_helper = CONSTANCE_TYPE_HELPER_MAPPER.get(constance_type)
        if not constance_type_helper:
            raise InvalidPathParameterException()
        return Response(
            ConstanceTypeResponse(data=constance_type_helper.get_constance_types()).model_dump(),
            status=200,
        )


class GetPreSignedURLView(APIView):
    permission_classes = [
        IsMemberLogin,
    ]

    def post(self, request, constance_type: str, transaction_pk: str):
        try:
            pre_signed_url_request = GetPreSignedURLRequest.of(request.data)
        except ValidationError as e:
            raise PydanticAPIException(
                status_code=400,
                error_summary=InvalidInputResponseErrorStatus.INVALID_PRE_SIGNED_URL_INPUT_DATA_400.label,
                error_code=InvalidInputResponseErrorStatus.INVALID_PRE_SIGNED_URL_INPUT_DATA_400.value,
                errors=e.errors(),
            )

        if constance_type not in IMAGE_CONSTANCE_TYPES:
            raise InvalidPathParameterException()

        try:
            info = generate_pre_signed_url_info(
                pre_signed_url_request.file_name,
                constance_type,
                transaction_pk,
                same_file_name=True,
            )
            url = info['url']
            data = info['fields']
        except Exception:
            raise ExternalAPIException()

        return Response(
            GetPreSignedURLResponse(
                url=url,
                data=data,
            ).model_dump(),
            status=200,
        )
