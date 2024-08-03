from rest_framework.exceptions import APIException


class NotEnoughGuestPoints(APIException):
    status_code = 400
    default_detail = '포인트가 부족합니다.'
    default_code = 'not-enough-guest-points'

    @classmethod
    def to_message(cls):
        return {
            'message': cls.default_detail,
        }


class NotEnoughGuestPointsForCancelOrder(APIException):
    status_code = 400
    default_detail = '사용한 포인트가 존재하여 주문 취소를 실패했습니다.'
    default_code = 'cannot-cancel-order-with-guest-points'

    @classmethod
    def to_message(cls):
        return {
            'message': cls.default_detail,
        }
