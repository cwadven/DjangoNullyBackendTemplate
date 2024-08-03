from rest_framework.exceptions import APIException


class ProductNotExists(APIException):
    status_code = 400
    default_detail = '상품이 존재하지 않습니다.'
    default_code = 'product-not-exists'

    @classmethod
    def to_message(cls):
        return {
            'message': cls.default_detail,
        }


class ProductStockNotEnough(APIException):
    status_code = 400
    default_detail = '상품 재고가 부족합니다.'
    default_code = 'product-stock-not-enough'

    @classmethod
    def to_message(cls):
        return {
            'message': cls.default_detail,
        }
