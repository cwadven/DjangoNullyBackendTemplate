from rest_framework.exceptions import APIException


class OrderNotExists(APIException):
    status_code = 400
    default_detail = '존재하지 않는 주문입니다.'
    default_code = 'order-not-exists'

    @classmethod
    def to_message(cls):
        return {
            'message': cls.default_detail,
        }


class OrderAlreadyCanceled(APIException):
    status_code = 400
    default_detail = '이미 취소된 주문입니다.'
    default_code = 'order-already-canceled-exists'

    @classmethod
    def to_message(cls):
        return {
            'message': cls.default_detail,
        }


class OrderStatusUnavailableBehavior(APIException):
    status_code = 400
    default_detail = '주문의 상태가 유효하지 않습니다.'
    default_code = 'order-status-unavailable-behavior'

    @classmethod
    def to_message(cls):
        return {
            'message': cls.default_detail,
        }
