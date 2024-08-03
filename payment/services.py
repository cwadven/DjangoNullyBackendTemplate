import json

from common.common_utils.encrpt_utils import decrypt_integer
from cryptography.fernet import InvalidToken
from django.db import transaction
from order.consts import (
    OrderStatus,
    PaymentType,
)
from order.exceptions import (
    OrderAlreadyCanceled,
    OrderNotExists,
    OrderStatusUnavailableBehavior,
)
from order.models import (
    Order,
    OrderItem,
)
from payment.helpers.kakaopay_helpers import (
    KakaoPay,
    KakaoPayProductHandler,
)
from product.models import GiveProduct


def kakao_pay_approve_give_product_success(order_id: int, pg_token: str) -> None:
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        raise OrderNotExists()

    kakao_pay = KakaoPay(
        KakaoPayProductHandler(order_id=order.id)
    )
    response = kakao_pay.approve_payment(
        tid=order.tid,
        pg_token=pg_token,
        order_id=order.id,
        guest_id=order.guest_id,
    )

    with transaction.atomic():
        if response['payment_method_type'] == 'MONEY':
            order.approve(PaymentType.KAKAOPAY_MONEY.value)
        else:
            order.approve(PaymentType.KAKAOPAY_CARD.value)

        order_items = OrderItem.objects.filter(
            order_id=order.id
        ).values_list(
            'id',
            flat=True,
        )
        give_products = GiveProduct.objects.filter(order_item_id__in=order_items)
        for give_product in give_products:
            give_product.give()


def kakao_pay_approve_give_product_cancel(order_id_token: str, cancel_reason: str) -> None:
    try:
        order_id = decrypt_integer(order_id_token)
    except InvalidToken:
        raise OrderNotExists()
    try:
        order = Order.objects.get(
            id=order_id,
        )
    except Order.DoesNotExist:
        raise OrderNotExists()

    if order.status == OrderStatus.CANCEL.value:
        raise OrderAlreadyCanceled()
    elif order.status not in (OrderStatus.SUCCESS.value, OrderStatus.READY.value):
        raise OrderStatusUnavailableBehavior()

    with transaction.atomic():
        order.cancel()
        order_items = OrderItem.objects.filter(
            order_id=order.id
        ).values_list(
            'id',
            flat=True,
        )
        give_products = GiveProduct.objects.filter(order_item_id__in=order_items)
        for give_product in give_products:
            give_product.cancel()

    kakao_pay = KakaoPay(
        KakaoPayProductHandler(order_id=order.id)
    )
    kakao_pay.cancel_payment(
        tid=order.tid,
        cancel_price=order.total_paid_price,
        cancel_tax_free_price=order.total_tax_paid_price,
        payload=json.dumps({'cancel_reason': cancel_reason}),
    )


def kakao_pay_approve_give_product_fail(order_id_token: str) -> None:
    try:
        order_id = decrypt_integer(order_id_token)
    except InvalidToken:
        raise OrderNotExists()
    try:
        order = Order.objects.get(
            id=order_id,
        )
    except Order.DoesNotExist:
        raise OrderNotExists()

    with transaction.atomic():
        order.fail()
        order_items = OrderItem.objects.filter(
            order_id=order.id
        ).values_list(
            'id',
            flat=True,
        )
        give_products = GiveProduct.objects.filter(order_item_id__in=order_items)
        for give_product in give_products:
            give_product.fail()
