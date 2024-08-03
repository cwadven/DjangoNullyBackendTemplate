from datetime import datetime

from common.common_testcase_helpers.testcase_helpers import (
    test_case_create_order,
    test_case_create_order_item,
)
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time
from member.models import Guest
from order.consts import (
    OrderStatus,
    PaymentType,
)
from order.models import (
    Order,
    OrderItem,
    OrderItemRefund,
    OrderItemStatusLog,
    OrderStatusLog,
)
from product.models import PointProduct


@freeze_time('2022-01-01')
class OrderMethodTestCase(TestCase):
    def setUp(self):
        self.guest = Guest.objects.first()
        self.order = test_case_create_order(
            guest=self.guest,
            order_number='F1234512345',
            tid='test_tid',
            status=OrderStatus.READY.value,
            order_phone_number='01012341234',
            payment_type='',
        )
        self.order_item1 = test_case_create_order_item(
            order=self.order,
            product_type='POINT',
            product_id=1,
            item_quantity=1,
            status=OrderStatus.READY.value,
        )
        self.order_item2 = test_case_create_order_item(
            order=self.order,
            product_type='POINT',
            product_id=2,
            item_quantity=1,
            status=OrderStatus.READY.value,
        )

        self.prefix = "XYZ"
        self.create_order_number_function = Order.create_order_number

    def test_initialize(self):
        # Given: Create Product
        point_product = PointProduct()

        # When:
        order = Order.initialize(
            product=point_product,
            guest=self.guest,
            order_phone_number='01012341234',
            payment_type=PaymentType.KAKAOPAY_CARD.value,
            total_price=0,
            total_tax_price=0,
            total_product_price=0,
            total_paid_price=0,
            total_tax_paid_price=0,
            total_product_paid_price=0,
            total_discounted_price=0,
            total_product_discounted_price=0,
        )

        # Then:
        self.assertEqual(
            Order.objects.filter(
                guest_id=self.guest.id,
                member_id=self.guest.member_id,
                order_phone_number='01012341234',
                payment_type=PaymentType.KAKAOPAY_CARD.value,
                status=OrderStatus.READY.value,
            ).exists(),
            True
        )
        # And: Order Status Log 생성
        self.assertEqual(
            OrderStatusLog.objects.filter(
                order_id=order.id,
                status=OrderStatus.READY.value,
                request_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )

    def test_approve(self):
        # Given:
        # When: approved with KAKAOPAY_CARD
        self.order.approve(PaymentType.KAKAOPAY_CARD.value)

        # Then: Order SUCCESS 변경
        self.assertEqual(
            Order.objects.filter(
                id=self.order.id,
                status=OrderStatus.SUCCESS.value,
                payment_type=PaymentType.KAKAOPAY_CARD.value,
                succeeded_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        # And: Order Status Log 생성
        self.assertEqual(
            OrderStatusLog.objects.filter(
                order_id=self.order.id,
                status=OrderStatus.SUCCESS.value,
                request_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        # And: OrderItem SUCCESS 변경
        self.assertEqual(
            OrderItem.objects.filter(
                id=self.order_item1.id,
                status=OrderStatus.SUCCESS.value,
                succeeded_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        self.assertEqual(
            OrderItem.objects.filter(
                id=self.order_item2.id,
                status=OrderStatus.SUCCESS.value,
                succeeded_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        # And: OrderItem Status Log 생성
        self.assertEqual(
            OrderItemStatusLog.objects.filter(
                order_item_id=self.order_item1.id,
                status=OrderStatus.SUCCESS.value,
                request_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        self.assertEqual(
            OrderItemStatusLog.objects.filter(
                order_item_id=self.order_item2.id,
                status=OrderStatus.SUCCESS.value,
                request_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )

    def test_cancel_when_order_was_ready_should_status_cancel(self):
        # Given: approved with KAKAOPAY_CARD
        self.order.approve(PaymentType.KAKAOPAY_CARD.value)
        # And: Order READY 변경
        self.order.status = OrderStatus.READY.value
        self.order.save()

        # When: cancel
        self.order.cancel()

        # Then: Order CANCEL 변경
        self.assertEqual(
            Order.objects.filter(
                id=self.order.id,
                status=OrderStatus.CANCEL.value,
                payment_type=PaymentType.KAKAOPAY_CARD.value,
                succeeded_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
                canceled_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        # And: Order Status Log 생성
        self.assertEqual(
            OrderStatusLog.objects.filter(
                order_id=self.order.id,
                status=OrderStatus.CANCEL.value,
                request_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        # And: OrderItem CANCEL 변경
        self.assertEqual(
            OrderItem.objects.filter(
                id=self.order_item1.id,
                status=OrderStatus.CANCEL.value,
                succeeded_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
                canceled_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        self.assertEqual(
            OrderItem.objects.filter(
                id=self.order_item2.id,
                status=OrderStatus.CANCEL.value,
                succeeded_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
                canceled_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        # And: OrderItem Status Log 생성
        self.assertEqual(
            OrderItemStatusLog.objects.filter(
                order_item_id=self.order_item1.id,
                status=OrderStatus.CANCEL.value,
                request_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        self.assertEqual(
            OrderItemStatusLog.objects.filter(
                order_item_id=self.order_item2.id,
                status=OrderStatus.CANCEL.value,
                request_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )

    def test_cancel_when_order_was_success_should_change_refund_case(self):
        # Given: approved with KAKAOPAY_CARD
        self.order.approve(PaymentType.KAKAOPAY_CARD.value)

        # When: cancel
        self.order.cancel()

        # Then: Order REFUND 변경
        self.assertEqual(
            Order.objects.filter(
                id=self.order.id,
                status=OrderStatus.REFUND.value,
                payment_type=PaymentType.KAKAOPAY_CARD.value,
                succeeded_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
                total_refunded_price=self.order.total_paid_price,
                is_once_refunded=True,
                refunded_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        # And: Order Status Log 생성
        self.assertEqual(
            OrderStatusLog.objects.filter(
                order_id=self.order.id,
                status=OrderStatus.REFUND.value,
                request_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        # And: OrderItem REFUND 변경
        self.assertEqual(
            OrderItem.objects.filter(
                id=self.order_item1.id,
                status=OrderStatus.REFUND.value,
                succeeded_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
                refunded_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
                refunded_price=self.order_item1.paid_price,
                total_refunded_quantity=self.order_item1.item_quantity,
            ).exists(),
            True
        )
        self.assertEqual(
            OrderItem.objects.filter(
                id=self.order_item2.id,
                status=OrderStatus.REFUND.value,
                succeeded_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
                refunded_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
                refunded_price=self.order_item2.paid_price,
                total_refunded_quantity=self.order_item2.item_quantity,
            ).exists(),
            True
        )
        # And: OrderItemRefund 생성
        self.assertEqual(
            OrderItemRefund.objects.filter(
                order_item_id=self.order_item1.id,
                refunded_price=self.order_item1.paid_price,
                refunded_quantity=self.order_item1.item_quantity,
                request_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        self.assertEqual(
            OrderItemRefund.objects.filter(
                order_item_id=self.order_item2.id,
                refunded_price=self.order_item2.paid_price,
                refunded_quantity=self.order_item2.item_quantity,
                request_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        # And: OrderItem Status Log 생성
        self.assertEqual(
            OrderItemStatusLog.objects.filter(
                order_item_id=self.order_item1.id,
                status=OrderStatus.REFUND.value,
                request_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        self.assertEqual(
            OrderItemStatusLog.objects.filter(
                order_item_id=self.order_item2.id,
                status=OrderStatus.REFUND.value,
                request_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )

    def test_fail(self):
        # Given: approved with KAKAOPAY_CARD
        self.order.approve(PaymentType.KAKAOPAY_CARD.value)

        # When: fail
        self.order.fail()

        # Then: Order FAIL 변경
        self.assertEqual(
            Order.objects.filter(
                id=self.order.id,
                status=OrderStatus.FAIL.value,
                payment_type=PaymentType.KAKAOPAY_CARD.value,
                succeeded_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        # And: Order Status Log 생성
        self.assertEqual(
            OrderStatusLog.objects.filter(
                order_id=self.order.id,
                status=OrderStatus.FAIL.value,
                request_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        # And: OrderItem FAIL 변경
        self.assertEqual(
            OrderItem.objects.filter(
                id=self.order_item1.id,
                status=OrderStatus.FAIL.value,
                succeeded_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        self.assertEqual(
            OrderItem.objects.filter(
                id=self.order_item2.id,
                status=OrderStatus.FAIL.value,
                succeeded_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        # And: OrderItem Status Log 생성
        self.assertEqual(
            OrderItemStatusLog.objects.filter(
                order_item_id=self.order_item1.id,
                status=OrderStatus.FAIL.value,
                request_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        self.assertEqual(
            OrderItemStatusLog.objects.filter(
                order_item_id=self.order_item2.id,
                status=OrderStatus.FAIL.value,
                request_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )

    def test_create_order_number_length(self):
        # When: create order number
        order_number = self.create_order_number_function(self.prefix)
        # Then:
        self.assertEqual(
            len(order_number),
            17,
        )

    def test_create_order_number_prefix(self):
        # When: create order number
        order_number = self.create_order_number_function(self.prefix)
        # Then:
        self.assertEqual(
            order_number.startswith(self.prefix),
            True
        )


@freeze_time('2022-01-01')
class OrderItemMethodTestCase(TestCase):
    def setUp(self):
        self.guest = Guest.objects.first()
        self.order = test_case_create_order(
            guest=self.guest,
            order_number='F1234512345',
            tid='test_tid',
            status=OrderStatus.READY.value,
            order_phone_number='01012341234',
            payment_type='',
        )
        self.order_item1 = test_case_create_order_item(
            order=self.order,
            product_type='POINT',
            product_id=1,
            item_quantity=1,
            status=OrderStatus.READY.value,
        )
        self.order_item2 = test_case_create_order_item(
            order=self.order,
            product_type='POINT',
            product_id=2,
            item_quantity=1,
            status=OrderStatus.READY.value,
        )

    def test_initialize(self):
        # Given: Create Product

        # When:
        order_item = OrderItem.initialize(
            order_id=self.order.id,
            product_id=999,
            product_type='TEST',
            product_price=0,
            discounted_price=0,
            paid_price=0,
            item_quantity=0,
        )

        # Then:
        self.assertEqual(
            OrderItem.objects.filter(
                product_id=999,
                product_type='TEST',
                product_price=0,
                discounted_price=0,
                paid_price=0,
                item_quantity=0,
                status=OrderStatus.READY.value,
            ).exists(),
            True
        )
        # And: OrderItem Status Log 생성
        self.assertEqual(
            OrderItemStatusLog.objects.filter(
                order_item_id=order_item.id,
                status=OrderStatus.READY.value,
                request_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
