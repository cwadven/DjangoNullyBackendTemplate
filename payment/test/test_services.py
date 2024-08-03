import json
from unittest.mock import patch

from common.common_testcase_helpers.testcase_helpers import (
    GuestTokenMixin,
    test_case_create_order,
    test_case_create_order_item,
)
from common.common_utils.encrpt_utils import encrypt_integer
from cryptography.fernet import InvalidToken
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time
from member.models import Guest
from order.consts import OrderStatus
from order.exceptions import (
    OrderAlreadyCanceled,
    OrderNotExists,
    OrderStatusUnavailableBehavior,
)
from payment.services import (
    kakao_pay_approve_give_product_cancel,
    kakao_pay_approve_give_product_fail,
    kakao_pay_approve_give_product_success,
)
from product.consts import ProductGivenStatus
from product.models import (
    GiveProduct,
    PointProduct,
)


@freeze_time('2021-01-01')
class KakaoPayApproveGiveProductSuccessTestCase(TestCase):
    def setUp(self):
        super(KakaoPayApproveGiveProductSuccessTestCase, self).setUp()
        self.guest = Guest.objects.all().first()
        self.order = test_case_create_order(
            guest=self.guest,
            order_number='F1234512345',
            tid='test_tid',
            status=OrderStatus.READY.value,
            order_phone_number='01012341234',
            payment_type='',
            total_paid_price=3000,
        )
        self.active_1000_point_product_ordering_1 = PointProduct.objects.create(
            title='Active Point Product1',
            price=1000,
            start_time=timezone.now() - timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            total_quantity=10,
            left_quantity=10,
            point=1000,
            ordering=1,
            created_guest=self.guest
        )
        self.order_item = test_case_create_order_item(
            order=self.order,
            product_type=self.active_1000_point_product_ordering_1.product_type,
            product_id=self.active_1000_point_product_ordering_1.id,
            item_quantity=3,
            status=OrderStatus.READY.value,
            paid_price=self.active_1000_point_product_ordering_1.price * 3,
        )

    @patch('payment.services.GiveProduct.give')
    @patch('payment.services.KakaoPay.approve_payment')
    def test_kakao_pay_approve_give_product_success_when_success(self,
                                                                 mock_approve_payment,
                                                                 mock_give_product_give):
        # Given:
        pg_token = 'test_token'
        # And: GiveProduct Ready 생성
        GiveProduct.objects.create(
            order_item_id=self.order_item.id,
            guest_id=self.guest.id,
            product_pk=self.active_1000_point_product_ordering_1.id,
            product_type=self.active_1000_point_product_ordering_1.product_type,
            quantity=1,
            meta_data=json.dumps(
                {
                    'point': self.active_1000_point_product_ordering_1.point,
                    'quantity': 3,
                    'total_point': self.active_1000_point_product_ordering_1.point * 3,
                }
            ),
            status=ProductGivenStatus.READY.value,
        )
        # And: 모킹
        mock_approve_payment.return_value = {
            "aid": "A469b85a306d7b2dc395",
            "tid": "T469b847306d7b2dc394",
            "cid": "TC0ONETIME",
            "partner_order_id": "test1",
            "partner_user_id": "1",
            "payment_method_type": "MONEY",
            "item_name": "1000 포인트",
            "item_code": "",
            "quantity": 1,
            "amount": {
                "total": 3000,
                "tax_free": 0,
                "vat": 91,
                "point": 0,
                "discount": 0,
                "green_deposit": 0
            },
            "created_at": "2023-05-21T15:20:55",
            "approved_at": "2023-05-21T15:25:31"
        }

        # When:
        kakao_pay_approve_give_product_success(self.order.id, pg_token)

        # Then: 주문 성공
        mock_approve_payment.assert_called_once_with(
            tid='test_tid',
            pg_token='test_token',
            order_id=self.order.id,
            guest_id=self.guest.id,
        )
        mock_give_product_give.assert_called_once_with()

    def test_kakao_pay_approve_give_product_success_when_fail_due_order_not_exists(self):
        # Given:
        pg_token = 'test_token'

        # Expected:
        with self.assertRaises(OrderNotExists):
            kakao_pay_approve_give_product_success(0, pg_token)


@freeze_time('2021-01-01')
class KakaoPayApproveGiveProductCancelTestCase(TestCase):
    def setUp(self):
        super(KakaoPayApproveGiveProductCancelTestCase, self).setUp()
        self.guest = Guest.objects.all().first()
        self.order = test_case_create_order(
            guest=self.guest,
            order_number='F1234512345',
            tid='test_tid',
            status=OrderStatus.READY.value,
            order_phone_number='01012341234',
            payment_type='',
            total_paid_price=3000,
        )
        self.active_1000_point_product_ordering_1 = PointProduct.objects.create(
            title='Active Point Product1',
            price=1000,
            start_time=timezone.now() - timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            total_quantity=10,
            left_quantity=10,
            point=1000,
            ordering=1,
            created_guest=self.guest
        )
        self.order_item = test_case_create_order_item(
            order=self.order,
            product_type=self.active_1000_point_product_ordering_1.product_type,
            product_id=self.active_1000_point_product_ordering_1.id,
            item_quantity=3,
            status=OrderStatus.READY.value,
            paid_price=self.active_1000_point_product_ordering_1.price * 3,
        )

    @patch('payment.services.KakaoPay.cancel_payment')
    @patch('payment.services.GiveProduct.cancel')
    @patch('payment.services.Order.cancel')
    def test_kakao_pay_approve_give_product_cancel_when_success(self,
                                                                mock_order_cancel,
                                                                mock_give_product_cancel,
                                                                mock_cancel_payment):
        # Given:
        # And: GiveProduct Ready 생성
        GiveProduct.objects.create(
            order_item_id=self.order_item.id,
            guest_id=self.guest.id,
            product_pk=self.active_1000_point_product_ordering_1.id,
            product_type=self.active_1000_point_product_ordering_1.product_type,
            quantity=1,
            meta_data=json.dumps(
                {
                    'point': self.active_1000_point_product_ordering_1.point,
                    'quantity': 3,
                    'total_point': self.active_1000_point_product_ordering_1.point * 3,
                }
            ),
            status=ProductGivenStatus.READY.value,
        )
        # And:
        mock_cancel_payment.return_value = {
            "aid": "A5922f8a3ad74821a2cf",
            "tid": "T591a8da3ad748219fdf",
            "cid": "TC0ONETIME",
            "status": "CANCEL_PAYMENT",
            "partner_order_id": "6",
            "partner_user_id": "4",
            "payment_method_type": "MONEY",
            "item_name": "G-point 1000",
            "quantity": 10,
            "amount": {
                "total": 10000,
                "tax_free": 0,
                "vat": 909,
                "point": 0,
                "discount": 0,
                "green_deposit": 0
            },
            "approved_cancel_amount": {
                "total": 10000,
                "tax_free": 0,
                "vat": 909,
                "point": 0,
                "discount": 0,
                "green_deposit": 0
            },
            "canceled_amount": {
                "total": 10000,
                "tax_free": 0,
                "vat": 909,
                "point": 0,
                "discount": 0,
                "green_deposit": 0
            },
            "cancel_available_amount": {
                "total": 0,
                "tax_free": 0,
                "vat": 0,
                "point": 0,
                "discount": 0,
                "green_deposit": 0
            },
            "created_at": "2024-01-01T02:46:03",
            "approved_at": "2024-01-01T02:46:34",
            "canceled_at": "2024-01-01T12:20:42",
            "payload": "테스"
        }
        # And: 주문 id 암호화
        token = encrypt_integer(self.order.id)

        # When:
        kakao_pay_approve_give_product_cancel(token, '결제 취소')

        # Then: 주문 취소 성공
        mock_order_cancel.assert_called_once_with()
        mock_give_product_cancel.assert_called_once_with()
        mock_cancel_payment.assert_called_once_with(
            tid=self.order.tid,
            cancel_price=self.order.total_paid_price,
            cancel_tax_free_price=self.order.total_tax_paid_price,
            payload=json.dumps({'cancel_reason': '결제 취소'}),
        )

    def test_kakao_pay_approve_give_product_cancel_when_fail_due_order_not_exists(self):
        # Given: 주문 id 암호화
        token = encrypt_integer(0)

        # Expected: 없는 주문 id 로 결제 신청
        with self.assertRaises(OrderNotExists):
            kakao_pay_approve_give_product_cancel(token, '결제 취소')

    def test_kakao_pay_approve_give_product_cancel_when_fail_when_already_canceled(self):
        # Given: 이미 취소함
        self.order.status = OrderStatus.CANCEL.value
        self.order.save()
        # And: 주문 id 암호화
        token = encrypt_integer(self.order.id)

        # Expected: 이미 취소
        with self.assertRaises(OrderAlreadyCanceled):
            kakao_pay_approve_give_product_cancel(token, '결제 취소')

    def test_kakao_pay_approve_give_product_cancel_when_fail_when_invalid_status(self):
        # Given: Fail 상태
        self.order.status = OrderStatus.FAIL.value
        self.order.save()
        # And: 주문 id 암호화
        token = encrypt_integer(self.order.id)

        # Expected: 주문 상태가 유효하지 않은 Status 이라서 취소 불가
        with self.assertRaises(OrderStatusUnavailableBehavior):
            kakao_pay_approve_give_product_cancel(token, '결제 취소')

    @patch('payment.services.decrypt_integer')
    def test_kakao_pay_approve_give_product_cancel_when_fail_when_invalid_token(self, mock_decrypt_integer):
        # Given: Invalid token
        mock_decrypt_integer.side_effect = InvalidToken

        # Expected: Token 이 유효하지 않아서 주문 취소 불가
        with self.assertRaises(OrderNotExists):
            kakao_pay_approve_give_product_cancel('invalid_token', '결제 취소')


@freeze_time('2021-01-01')
class KakaoPayApproveGiveProductFailTestCase(GuestTokenMixin, TestCase):
    def setUp(self):
        super(KakaoPayApproveGiveProductFailTestCase, self).setUp()
        self.guest = Guest.objects.all().first()
        self.order = test_case_create_order(
            guest=self.guest,
            order_number='F1234512345',
            tid='test_tid',
            status=OrderStatus.READY.value,
            order_phone_number='01012341234',
            payment_type='',
            total_paid_price=3000,
        )
        self.active_1000_point_product_ordering_1 = PointProduct.objects.create(
            title='Active Point Product1',
            price=1000,
            start_time=timezone.now() - timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            total_quantity=10,
            left_quantity=10,
            point=1000,
            ordering=1,
            created_guest=self.guest
        )
        self.order_item = test_case_create_order_item(
            order=self.order,
            product_type=self.active_1000_point_product_ordering_1.product_type,
            product_id=self.active_1000_point_product_ordering_1.id,
            item_quantity=3,
            status=OrderStatus.READY.value,
            paid_price=self.active_1000_point_product_ordering_1.price * 3,
        )

    @patch('payment.services.GiveProduct.fail')
    @patch('payment.services.Order.fail')
    def test_kakao_pay_fail_for_buy_product_when_success(self,
                                                         mock_order_fail,
                                                         mock_give_product_fail):
        # Given:
        self.login_guest(self.guest)
        # And: GiveProduct Ready 생성
        GiveProduct.objects.create(
            order_item_id=self.order_item.id,
            guest_id=self.guest.id,
            product_pk=self.active_1000_point_product_ordering_1.id,
            product_type=self.active_1000_point_product_ordering_1.product_type,
            quantity=1,
            meta_data=json.dumps(
                {
                    'point': self.active_1000_point_product_ordering_1.point,
                    'quantity': 3,
                    'total_point': self.active_1000_point_product_ordering_1.point * 3,
                }
            ),
            status=ProductGivenStatus.READY.value,
        )
        # And: 주문 id 암호화
        token = encrypt_integer(self.order.id)

        # When:
        kakao_pay_approve_give_product_fail(token)

        # Then: 주문 실패 성공
        mock_order_fail.assert_called_once_with()
        mock_give_product_fail.assert_called_once_with()

    def test_kakao_pay_fail_for_buy_product_when_fail_due_order_not_exists(self):
        # Given: 주문 id 암호화
        token = encrypt_integer(0)

        # Expected: 없는 주문 id 로 결제 신청
        with self.assertRaises(OrderNotExists):
            kakao_pay_approve_give_product_fail(token)

    @patch('payment.services.decrypt_integer')
    def test_kakao_pay_fail_for_buy_product_when_invalid_token(self, mock_decrypt_integer):
        # Given: Invalid token
        mock_decrypt_integer.side_effect = InvalidToken

        # Expected: Token 이 유효하지 않아서 주문 실패 불가
        with self.assertRaises(OrderNotExists):
            kakao_pay_approve_give_product_fail('invalid_token')
