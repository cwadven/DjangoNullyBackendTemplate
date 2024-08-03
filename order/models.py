import random
import string

from django.db import (
    models,
    transaction,
)
from django.db.models import F
from django.utils import timezone
from order.consts import (
    OrderStatus,
    PaymentType,
    ProductType,
)


class Order(models.Model):
    """
    tid 없을 수 있습니다.

    total_price:
        total_tax_price + total_product_price + total_delivery_price
        총 결제 금액
    total_tax_price: 순수 세금 (할인 X)
    total_product_price: 순수 총 제품 금액 (할인 X)
    total_delivery_price: 순수 총 배달비 (할인 X)

    total_paid_price:
        total_tax_paid_price + total_product_paid_price + total_delivery_paid_price
        사용자가 실제 결제한 총 금액
    total_tax_paid_price: 사용자가 실제 결제한 세금 금액 (할인 O)
    total_product_paid_price: 사용자가 실제 결제한 상품 금액 (할인 O)
    total_delivery_paid_price: 사용자가 실제 결제한 배달비 금액 (할인 O)

    total_discounted_price:
        total_delivery_discounted_price + total_product_discounted_price
        사용자가 할인 받은 총 금액 (할인 O, 상품 + 배달비 등)
    total_delivery_discounted_price: 사용자가 할인 받은 배달비 할인 금액 (할인 O, 배달비 기준)
    total_product_discounted_price: 사용자가 제품 가격에서만 받은 총 금액 (할인 O, 제품 기준)

    total_refunded_price: 환불 받은 금액
    is_once_refunded: 한번이라도 환불을 했는지 여부 이것의 True False 기준으로 Refund 테이블을 조회합니다.

    order_phone_number
    address
    address_detail
    address_postcode
    delivery_memo
    payment_type
        Null 가능한 이유는 무료 결제가 가능, 즉 0원 결제
    """
    guest_id = models.BigIntegerField(verbose_name='Guest Id', db_index=True)
    member_id = models.BigIntegerField(verbose_name='Member Id', db_index=True, null=True)
    order_number = models.CharField(verbose_name='주문 번호', max_length=50, db_index=True)
    tid = models.CharField(verbose_name='결제 고유 번호', max_length=50, db_index=True, null=True, blank=True)
    total_price = models.IntegerField(verbose_name='총 결제 금액', default=0, db_index=True)
    total_tax_price = models.IntegerField(verbose_name='세금', default=0, db_index=True)
    total_product_price = models.IntegerField(verbose_name='제품 결제 금액', default=0, db_index=True)
    total_delivery_price = models.IntegerField(verbose_name='배달비', default=0, db_index=True)
    total_paid_price = models.IntegerField(verbose_name='사용자 총 결제 금액', default=0, db_index=True)
    total_tax_paid_price = models.IntegerField(verbose_name='사용자 세금 기준 결제 금액', default=0, db_index=True)
    total_product_paid_price = models.IntegerField(verbose_name='사용자 상품 기준 결제 금액', default=0, db_index=True)
    total_delivery_paid_price = models.IntegerField(verbose_name='사용자 배달비 기준 결제 금액', default=0, db_index=True)
    total_discounted_price = models.IntegerField(verbose_name='사용자 총 할인 금액', default=0, db_index=True)
    total_delivery_discounted_price = models.IntegerField(verbose_name='사용자 배달비 총 할인 금액', default=0, db_index=True)
    total_product_discounted_price = models.IntegerField(verbose_name='사용자 상품 기준 총 할인 금액', default=0, db_index=True)
    total_refunded_price = models.IntegerField(verbose_name='환불 금액', default=0, db_index=True)
    status = models.CharField(verbose_name='결제 상태', max_length=20, db_index=True, choices=OrderStatus.choices())
    order_phone_number = models.CharField(verbose_name='배송 관련 정보 전달을 위한 전화번호', max_length=50, db_index=True, null=True)
    address = models.CharField(verbose_name='배송지 주소', max_length=200, db_index=True, null=True)
    address_detail = models.CharField(verbose_name='배송지 상세 주소', max_length=200, null=True)
    address_postcode = models.CharField(verbose_name='배송지 우편번호', max_length=50, db_index=True, null=True)
    delivery_memo = models.TextField(verbose_name='배송 메모', null=True, blank=True)
    payment_type = models.CharField(verbose_name='결제 수단', max_length=20, db_index=True, choices=PaymentType.choices(), null=True)
    need_notification_sent = models.BooleanField(verbose_name='고객 알림 전송 필요 여부', default=False)
    is_notification_sent = models.BooleanField(verbose_name='고객 알림 전송 여부', default=False)
    is_once_refunded = models.BooleanField(verbose_name='한번이라도 환불 했는지 여부', default=False)
    canceled_at = models.DateTimeField(verbose_name='주문 취소 시간', null=True, blank=True, db_index=True)
    succeeded_at = models.DateTimeField(verbose_name='결제 성공 시간', null=True, blank=True, db_index=True)
    refunded_at = models.DateTimeField(verbose_name='환불 시간', null=True, blank=True, db_index=True)
    request_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True)

    class Meta:
        verbose_name = '주문 요약'
        verbose_name_plural = '주문 요약'

    def __str__(self):
        return f'사용자 주문 요약 / {self.order_number}'

    @staticmethod
    def create_order_number(prefix: str):
        valid_chars = [char for char in string.ascii_uppercase if char != 'O'] + \
                      [digit for digit in string.digits if digit != '0']
        while True:
            order_number = prefix + ''.join(
                random.choices(
                    valid_chars,
                    k=17 - len(prefix)
                )
            )
            if not Order.objects.filter(order_number=order_number).exists():
                break

        return order_number

    @classmethod
    @transaction.atomic
    def initialize(
            cls,
            product: 'Product',  # noqa
            guest: 'Guest',  # noqa
            order_phone_number: str,
            payment_type: str,
            total_price: int,
            total_tax_price: int,
            total_product_price: int,
            total_paid_price: int,
            total_tax_paid_price: int,
            total_product_paid_price: int,
            total_discounted_price: int,
            total_product_discounted_price: int,
            **kwargs
    ):
        order = cls.objects.create(
            guest_id=guest.id,
            member_id=guest.member_id,
            order_number=cls.create_order_number(product.order_number_prefix),
            tid=None,
            total_price=total_price,
            total_tax_price=total_tax_price,
            total_product_price=total_product_price,
            total_paid_price=total_paid_price,
            total_tax_paid_price=total_tax_paid_price,
            total_product_paid_price=total_product_paid_price,
            total_discounted_price=total_discounted_price,
            total_product_discounted_price=total_product_discounted_price,
            status=OrderStatus.READY.value,
            order_phone_number=order_phone_number,
            payment_type=payment_type,
            need_notification_sent=product.need_notification_sent,
        )
        # 상태 Log 생성
        OrderStatusLog.objects.create(
            order=order,
            status=OrderStatus.READY.value,
        )
        return order

    @transaction.atomic
    def approve(self, payment_type: str):
        """
        결제 승인
        """
        # 상태 업데이트
        now = timezone.now()
        self.status = OrderStatus.SUCCESS.value
        self.payment_type = payment_type
        self.succeeded_at = now
        self.save(update_fields=['status', 'payment_type', 'succeeded_at'])
        # 상태 Log 생성
        OrderStatusLog.objects.create(
            order=self,
            status=OrderStatus.SUCCESS.value,
        )

        # Item 상태 업데이트
        self.items.update(
            status=OrderStatus.SUCCESS.value,
            succeeded_at=now,
        )
        # Item 상태 Log 생성
        OrderItemStatusLog.objects.bulk_create(
            [
                OrderItemStatusLog(
                    order_item=item,
                    status=OrderStatus.SUCCESS.value,
                    request_at=now,
                )
                for item in self.items.all()
            ]
        )

    @transaction.atomic
    def cancel(self):
        """
        결제 취소 및 환불

        결제 취소 중 환불 같은 경우는 결제가 성공이 된 경우에만 일어날 수 있습니다.
        """
        # 상태 업데이트
        now = timezone.now()
        update_fields = ['status']

        if self.status == OrderStatus.SUCCESS.value:
            self.status = OrderStatus.REFUND.value
            self.refunded_at = now
            self.total_refunded_price = self.total_paid_price
            self.is_once_refunded = True
            update_fields.extend(
                [
                    'refunded_at',
                    'total_refunded_price',
                    'is_once_refunded',
                ]
            )
        else:
            self.status = OrderStatus.CANCEL.value
            self.canceled_at = now
            update_fields.append('canceled_at')
        self.save(update_fields=update_fields)

        OrderStatusLog.objects.create(
            order=self,
            status=self.status,
        )

        # Item 상태 업데이트
        if self.status == OrderStatus.REFUND.value:
            self.items.update(
                status=self.status,
                refunded_at=now,
                refunded_price=F('paid_price'),
                total_refunded_quantity=F('item_quantity'),
            )
            OrderItemRefund.objects.bulk_create(
                [
                    OrderItemRefund(
                        order_item=item,
                        refunded_price=item.paid_price,
                        refunded_quantity=item.item_quantity,
                    )
                    for item in self.items.all()
                ]
            )
        else:
            self.items.update(
                status=self.status,
                canceled_at=now,
            )
        # Item 상태 Log 생성
        OrderItemStatusLog.objects.bulk_create(
            [
                OrderItemStatusLog(
                    order_item=item,
                    status=self.status,
                    request_at=now,
                )
                for item in self.items.all()
            ]
        )

    @transaction.atomic
    def fail(self):
        """
        결제 실패
        """
        now = timezone.now()
        # 상태 업데이트
        self.status = OrderStatus.FAIL.value
        self.save(update_fields=['status'])
        # 상태 Log 생성
        OrderStatusLog.objects.create(
            order=self,
            status=OrderStatus.FAIL.value,
        )

        # Item 상태 업데이트
        self.items.update(
            status=OrderStatus.FAIL.value,
        )
        # Item 상태 Log 생성
        OrderItemStatusLog.objects.bulk_create(
            [
                OrderItemStatusLog(
                    order_item=item,
                    status=OrderStatus.FAIL.value,
                    request_at=now,
                )
                for item in self.items.all()
            ]
        )


class OrderStatusLog(models.Model):
    """
    주문 상태 로그
    상태가 변화할 때마다 로그를 남깁니다.
    """
    order = models.ForeignKey(Order, verbose_name='주문', on_delete=models.CASCADE)
    status = models.CharField(verbose_name='주문 상태', max_length=20, db_index=True, choices=OrderStatus.choices())
    request_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = '주문 상태 로그'
        verbose_name_plural = '주문 상태 로그'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='주문', on_delete=models.CASCADE, related_name='items')
    product_id = models.BigIntegerField(verbose_name='상품 ID', db_index=True)
    product_type = models.CharField(verbose_name='상품 타입', max_length=20, db_index=True, choices=ProductType.choices())
    product_price = models.IntegerField(verbose_name='제품 순수 금액', default=0, db_index=True)
    discounted_price = models.IntegerField(verbose_name='제품이 받은 할인 금액', default=0, db_index=True)
    paid_price = models.IntegerField(verbose_name='사용자 결제 금액', default=0, db_index=True)
    refunded_price = models.IntegerField(verbose_name='환불 금액', default=0, db_index=True)
    item_quantity = models.IntegerField(verbose_name='제품 구매 수량', default=0, db_index=True)
    total_refunded_quantity = models.IntegerField(verbose_name='제품 환불 수량', default=0, db_index=True)
    status = models.CharField(verbose_name='결제 상태', max_length=20, db_index=True, choices=OrderStatus.choices())
    canceled_at = models.DateTimeField(verbose_name='주문 취소 시간', null=True, blank=True, db_index=True)
    succeeded_at = models.DateTimeField(verbose_name='결제 성공 시간', null=True, blank=True, db_index=True)
    refunded_at = models.DateTimeField(verbose_name='환불 시간', null=True, blank=True, db_index=True)
    request_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True)

    class Meta:
        verbose_name = '주문 상세'
        verbose_name_plural = '주문 상세'

    def __str__(self):
        return f'사용자 주문 상세 상품 / {self.product_id}'

    @classmethod
    @transaction.atomic
    def initialize(
            cls,
            order_id: int,
            product_id: int,
            product_type: str,
            product_price: int,
            discounted_price: int,
            paid_price: int,
            item_quantity: int,
    ):
        """
        주문 상세 생성
        """
        order_item = cls(
            order_id=order_id,
            product_id=product_id,
            product_type=product_type,
            product_price=product_price,
            discounted_price=discounted_price,
            paid_price=paid_price,
            item_quantity=item_quantity,
            status=OrderStatus.READY.value,
        )
        order_item.save()
        OrderItemStatusLog.objects.create(
            order_item=order_item,
            status=OrderStatus.READY.value,
        )

        return order_item


class OrderItemRefund(models.Model):
    order_item = models.ForeignKey(OrderItem, verbose_name='주문 상세', on_delete=models.CASCADE)
    refunded_price = models.IntegerField(verbose_name='환불 금액', default=0, db_index=True)
    refunded_quantity = models.IntegerField(verbose_name='환불 수량', default=0, db_index=True)
    is_deleted = models.BooleanField(verbose_name='삭제 여부', default=False)
    request_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(verbose_name='수정일', auto_now=True)

    class Meta:
        verbose_name = '주문 상세 환불'
        verbose_name_plural = '주문 상세 환불'


class OrderItemStatusLog(models.Model):
    """
    주문 상세 상태 로그
    상태가 변화할 때마다 로그를 남깁니다.
    """
    order_item = models.ForeignKey(OrderItem, verbose_name='주문 상세', on_delete=models.CASCADE)
    status = models.CharField(verbose_name='주문 상태', max_length=20, db_index=True, choices=OrderStatus.choices())
    request_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = '주문 상세 상태 로그'
        verbose_name_plural = '주문 상세 상태 로그'


class OrderItemDiscount(models.Model):
    """
    적용된 할인
    """
    order_item = models.ForeignKey(OrderItem, verbose_name='주문 상세', on_delete=models.CASCADE)
    discount_pk = models.CharField(verbose_name='할인 PK', max_length=100, db_index=True)
    discount_type = models.CharField(verbose_name='할인 타입', max_length=20)
    discounted_price = models.IntegerField(verbose_name='할인 적용 금액', default=0, db_index=True)
    created_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True)

    class Meta:
        verbose_name = '주문 상세 할인'
        verbose_name_plural = '주문 상세 할인'
