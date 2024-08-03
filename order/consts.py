from common.common_consts.common_enums import StrValueLabel


class OrderStatus(StrValueLabel):
    READY = ('READY', '주문 준비중')
    FAIL = ('FAIL', '주문 실패')
    CANCEL = ('CANCEL', '주문 취소')
    SUCCESS = ('SUCCESS', '주문 성공')
    REFUND = ('REFUND', '환불')
    PARTIAL_REFUND = ('PARTIAL_REFUND', '부분 환불')


class DeliveryStatus(StrValueLabel):
    READY = ('READY', '배송 준비중')
    DELIVERING = ('DELIVERING', '배송 중')
    DELIVERED = ('DELIVERED', '배송 완료')
    FAIL = ('FAIL', '배송 실패')
    CANCEL = ('CANCEL', '배송 취소')
    REFUND = ('REFUND', '반품')
    EXCHANGE = ('EXCHANGE', '교환')


class ProductType(StrValueLabel):
    POINT = ('POINT', '포인트')


class PaymentType(StrValueLabel):
    KAKAOPAY = ('KAKAOPAY', '카카오페이')
    KAKAOPAY_CARD = ('KAKAOPAY_CARD', '카카오페이-카드')
    KAKAOPAY_MONEY = ('KAKAOPAY_MONEY', '카카오페이-머니')
