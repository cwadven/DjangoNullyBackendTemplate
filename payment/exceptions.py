from rest_framework.exceptions import APIException


class UnavailablePayHandler(APIException):
    status_code = 400
    default_detail = '해당 결제로 구매할 수 없는 상품입니다.'
    default_code = 'cannot-buy-with-specific-payment'

    @classmethod
    def to_message(cls):
        return {
            'message': cls.default_detail,
        }


class KakaoPaySuccessError(APIException):
    status_code = 400
    default_detail = '카카오페이 결제에 실패하였습니다.'
    default_code = 'kakao-pay-success-failed'

    @classmethod
    def to_message(cls):
        return {
            'message': cls.default_detail,
        }


class KakaoPayCancelError(APIException):
    status_code = 400
    default_detail = '카카오페이 결제 취소에 실패하였습니다.'
    default_code = 'kakao-pay-cancel-failed'

    @classmethod
    def to_message(cls):
        return {
            'message': cls.default_detail,
        }
