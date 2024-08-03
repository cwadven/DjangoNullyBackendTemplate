from common.common_utils import get_jwt_guest_token
from django.test import (
    Client,
    TestCase,
)
from member.models import Guest
from order.models import (
    Order,
    OrderItem,
)


def test_case_create_order(
        guest: Guest,
        order_number: str,
        tid: str,
        status: str,  # OrderStatus
        order_phone_number: str,
        payment_type: str,  # PaymentType
        **kwargs
):
    return Order.objects.create(
        guest_id=guest.id,
        member_id=guest.member_id,
        order_number=order_number,
        tid=tid,
        total_price=kwargs.get('total_price', 0),
        total_tax_price=kwargs.get('total_tax_price', 0),
        total_product_price=kwargs.get('total_product_price', 0),
        total_delivery_price=kwargs.get('total_delivery_price', 0),
        total_paid_price=kwargs.get('total_paid_price', 0),
        total_tax_paid_price=kwargs.get('total_tax_paid_price', 0),
        total_product_paid_price=kwargs.get('total_product_paid_price', 0),
        total_delivery_paid_price=kwargs.get('total_delivery_paid_price', 0),
        total_discounted_price=kwargs.get('total_discounted_price', 0),
        total_delivery_discounted_price=kwargs.get('total_delivery_discounted_price', 0),
        total_product_discounted_price=kwargs.get('total_product_discounted_price', 0),
        status=status,
        order_phone_number=order_phone_number,
        address=kwargs.get('address'),
        address_detail=kwargs.get('address_detail'),
        address_postcode=kwargs.get('address_postcode'),
        delivery_memo=kwargs.get('delivery_memo'),
        payment_type=payment_type,
    )


def test_case_create_order_item(
        order: Order,
        product_type: str,  # ProductType
        product_id: int,
        item_quantity: int,
        status: str,  # OrderStatus
        **kwargs
):
    return OrderItem.objects.create(
        order=order,
        product_type=product_type,
        product_id=product_id,
        product_price=kwargs.get('product_price', 0),
        discounted_price=kwargs.get('discounted_price', 0),
        paid_price=kwargs.get('paid_price', 0),
        item_quantity=item_quantity,
        status=status,
    )


class GuestTokenMixin(TestCase):
    # 모킹할 메서드 생성
    def setUp(self):
        super(GuestTokenMixin, self).setUp()
        self.c = Client()

    def login_guest(self, guest=None):
        if guest is None:
            guest = Guest.objects.all().first()

        self.client.defaults['HTTP_AUTHORIZATION'] = f'jwt {get_jwt_guest_token(guest)}'


class SampleModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
