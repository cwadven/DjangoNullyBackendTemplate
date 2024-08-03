import json
from unittest.mock import patch

from common.common_testcase_helpers.testcase_helpers import (
    GuestTokenMixin,
    test_case_create_order,
    test_case_create_order_item,
)
from common.common_utils.encrpt_utils import encrypt_integer
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from member.models import Guest
from order.consts import OrderStatus
from order.exceptions import (
    OrderAlreadyCanceled,
    OrderNotExists,
    OrderStatusUnavailableBehavior,
)
from payment.exceptions import KakaoPayCancelError
from product.consts import ProductGivenStatus
from product.models import (
    GiveProduct,
    PointProduct,
)


@freeze_time('2021-01-01')
class KakaoPayReadyForBuyProductAPIViewTestCase(GuestTokenMixin, TestCase):
    def setUp(self):
        super(KakaoPayReadyForBuyProductAPIViewTestCase, self).setUp()
        self.guest = Guest.objects.all().first()
        self.order = test_case_create_order(
            guest=self.guest,
            order_number='F1234512345',
            tid='test_tid',
            status=OrderStatus.READY.value,
            order_phone_number='01012341234',
            payment_type='',
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

    def test_product_buy_should_return_400_when_mandatory_not_exists(self):
        # Given: Each mandatory data is not exists
        data = [
            {
                'product_type': self.active_1000_point_product_ordering_1.product_type,
                'quantity': 1,
                'payment_type': 'TEST',
                'order_phone_number': '01012345678',
            },
            {
                'product_id': self.active_1000_point_product_ordering_1.id,
                'quantity': 1,
                'payment_type': 'TEST',
                'order_phone_number': '01012345678',
            },
            {
                'product_id': self.active_1000_point_product_ordering_1.id,
                'product_type': self.active_1000_point_product_ordering_1.product_type,
                'payment_type': 'TEST',
                'order_phone_number': '01012345678',
            },
            {
                'product_id': self.active_1000_point_product_ordering_1.id,
                'product_type': self.active_1000_point_product_ordering_1.product_type,
                'quantity': 1,
                'order_phone_number': '01012345678',
            },
            {
                'product_id': self.active_1000_point_product_ordering_1.id,
                'product_type': self.active_1000_point_product_ordering_1.product_type,
                'quantity': 1,
                'payment_type': 'TEST',
            },
        ]

        # When:
        for d in data:
            response = self.client.post(reverse('payment:product_buy'), data=d)
            content = json.loads(response.content)

            # Then: Response 400
            self.assertEqual(response.status_code, 400)
            self.assertEqual(content['message'], '입력값을 다시 확인해주세요.')

    def test_product_buy_should_return_400_when_unavailable_kakaopay_handler(self):
        # Given: Unavailable product_type for kakaopay product handler
        data = {
            'product_id': self.active_1000_point_product_ordering_1.id,
            'product_type': 'TEST',
            'quantity': 1,
            'payment_type': 'TEST',
            'order_phone_number': '01012345678',
        }

        # When:
        response = self.client.post(reverse('payment:product_buy'), data=data)
        content = json.loads(response.content)

        # Then: Response 400
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content['message'], '해당 결제로 구매할 수 없는 상품입니다.')

    def test_product_buy_should_return_400_when_product_id_is_not_exists(self):
        # Given: Product id is not exists
        data = {
            'product_id': 0,
            'product_type': self.active_1000_point_product_ordering_1.product_type,
            'quantity': 1,
            'payment_type': 'TEST',
            'order_phone_number': '01012345678',
        }

        # When:
        response = self.client.post(reverse('payment:product_buy'), data=data)
        content = json.loads(response.content)

        # Then: Response 400
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content['message'], '상품이 존재하지 않습니다.')

    @patch('payment.views.PointProduct.initialize_order')
    @patch('payment.views.KakaoPay.ready_to_pay')
    def test_product_buy_should_success(self,
                                        mock_kakaopay_ready_to_pay,
                                        mock_point_product_initialize_order):
        # Given: Success data
        data = {
            'product_id': self.active_1000_point_product_ordering_1.id,
            'product_type': self.active_1000_point_product_ordering_1.product_type,
            'quantity': 3,
            'payment_type': 'TEST',
            'order_phone_number': '01012345678',
        }
        self.login_guest(self.guest)
        self.order.total_paid_price = 3000
        self.order.save()
        mock_point_product_initialize_order.return_value = self.order
        mock_kakaopay_ready_to_pay.return_value = {
            "tid": "T469b847306d7b2dc394",
            "tms_result": False,
            "next_redirect_app_url": "https://online-pay.kakao.com/mockup/v1/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46/aInfo",
            "next_redirect_mobile_url": "https://online-pay.kakao.com/mockup/v1/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46/mInfo",
            "next_redirect_pc_url": "https://online-pay.kakao.com/mockup/v1/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46/info",
            "android_app_scheme": "kakaotalk://kakaopay/pg?url=https://online-pay.kakao.com/pay/mockup/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46",
            "ios_app_scheme": "kakaotalk://kakaopay/pg?url=https://online-pay.kakao.com/pay/mockup/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46",
            "created_at": "2023-05-21T15:20:55"
        }

        # When:
        response = self.client.post(reverse('payment:product_buy'), data=data)
        content = json.loads(response.content)

        # Then: Response 200
        self.assertEqual(response.status_code, 200)
        mock_point_product_initialize_order.assert_called_once_with(
            guest=self.guest,
            order_phone_number='01012345678',
            payment_type='TEST',
            quantity=3,
        )
        mock_kakaopay_ready_to_pay.assert_called_once_with(
            order_id=f'{self.order.id}',
            guest_id=f'{self.guest.id}',
            product_name=f'{self.active_1000_point_product_ordering_1.title} (3개)',
            quantity='1',
            total_amount=self.active_1000_point_product_ordering_1.price * 3,
            tax_free_amount=0,
        )
        self.assertDictEqual(
            content,
            {
                'next_redirect_app_url': 'https://online-pay.kakao.com/mockup/v1/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46/aInfo',
                'next_redirect_mobile_url': 'https://online-pay.kakao.com/mockup/v1/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46/mInfo',
                'next_redirect_pc_url': 'https://online-pay.kakao.com/mockup/v1/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46/info',
                'tid': 'T469b847306d7b2dc394'
            }
        )


@freeze_time('2021-01-01')
class KakaoPayApproveForBuyProductAPIViewTestCase(GuestTokenMixin, TestCase):
    def setUp(self):
        super(KakaoPayApproveForBuyProductAPIViewTestCase, self).setUp()
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
    def test_kakao_pay_approve_for_buy_product_api_when_success(self,
                                                                mock_approve_payment,
                                                                mock_give_product_give):
        # Given:
        self.login_guest(self.guest)
        data = {
            'pg_token': 'test_token',
        }
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
        response = self.client.get(reverse('payment:product_approve', args=[self.order.id]), data=data)
        content = json.loads(response.content)

        # Then: 주문 성공
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            content['message'],
            '결제가 완료되었습니다.'
        )
        mock_approve_payment.assert_called_once_with(
            tid='test_tid',
            pg_token='test_token',
            order_id=self.order.id,
            guest_id=self.guest.id,
        )
        mock_give_product_give.assert_called_once_with()

    def test_kakao_pay_approve_for_buy_product_api_when_fail_due_order_not_exists(self):
        # Given:
        self.login_guest(self.guest)
        data = {
            'pg_token': 'test_token',
        }

        # When:
        response = self.client.get(reverse('payment:product_approve', args=[0]), data=data)
        content = json.loads(response.content)

        # Then: Order가 없어서 주문 실패
        self.assertEqual(response.status_code, OrderNotExists.status_code)
        self.assertEqual(content['message'], OrderNotExists.default_detail)


@freeze_time('2021-01-01')
class KakaoPayCancelForBuyProductAPIViewTestCase(GuestTokenMixin, TestCase):
    def setUp(self):
        super(KakaoPayCancelForBuyProductAPIViewTestCase, self).setUp()
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
    def test_kakao_pay_cancel_for_buy_product_api_when_success(self,
                                                               mock_order_cancel,
                                                               mock_give_product_cancel,
                                                               mock_cancel_payment):
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
        # And: token 생성
        token = encrypt_integer(self.order.id)

        # When:
        response = self.client.post(reverse('payment:product_cancel', args=[token]))
        content = json.loads(response.content)

        # Then: 주문 취소 성공
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            content['message'],
            '결제가 취소되었습니다.'
        )
        mock_order_cancel.assert_called_once_with()
        mock_give_product_cancel.assert_called_once_with()
        mock_cancel_payment.assert_called_once_with(
            tid=self.order.tid,
            cancel_price=self.order.total_paid_price,
            cancel_tax_free_price=self.order.total_tax_paid_price,
            payload=json.dumps({'cancel_reason': '결제 취소'}),
        )

    def test_kakao_pay_cancel_for_buy_product_api_when_fail_due_order_not_exists(self):
        # Given:
        self.login_guest(self.guest)
        # And: token 생성
        token = encrypt_integer(0)

        # When: 없는 주문 id 로 결제 신청
        response = self.client.post(reverse('payment:product_cancel', args=[token]))
        content = json.loads(response.content)

        # Then: Order가 없어서 주문 취소 실패
        self.assertEqual(response.status_code, OrderNotExists.status_code)
        self.assertEqual(content['message'], OrderNotExists.default_detail)

    def test_kakao_pay_cancel_for_buy_product_api_when_fail_when_already_canceled(self):
        # Given: 이미 취소함
        self.login_guest(self.guest)
        self.order.status = OrderStatus.CANCEL.value
        self.order.save()
        # And: token 생성
        token = encrypt_integer(self.order.id)

        # When: 이미 취소 상태
        response = self.client.post(reverse('payment:product_cancel', args=[token]))
        content = json.loads(response.content)

        # Then: 이미 취소 상태로 주문 취소 실패
        self.assertEqual(response.status_code, OrderAlreadyCanceled.status_code)
        self.assertEqual(content['message'], OrderAlreadyCanceled.default_detail)

    def test_kakao_pay_cancel_for_buy_product_api_when_fail_when_invalid_status(self):
        # Given: Fail 상태
        self.login_guest(self.guest)
        self.order.status = OrderStatus.FAIL.value
        self.order.save()
        # And: token 생성
        token = encrypt_integer(self.order.id)

        # When: 유효하지 않은 status
        response = self.client.post(reverse('payment:product_cancel', args=[token]))
        content = json.loads(response.content)

        # Then: 유효하지 않은 status로 주문 취소 실패
        self.assertEqual(response.status_code, OrderStatusUnavailableBehavior.status_code)
        self.assertEqual(content['message'], OrderStatusUnavailableBehavior.default_detail)


@freeze_time('2021-01-01')
class KakaoPayFailForBuyProductAPIViewTestCase(GuestTokenMixin, TestCase):
    def setUp(self):
        super(KakaoPayFailForBuyProductAPIViewTestCase, self).setUp()
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
    def test_kakao_pay_fail_for_buy_product_api_when_success(self,
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
        response = self.client.post(reverse('payment:product_fail', args=[token]))
        content = json.loads(response.content)

        # Then: 주문 실패 성공
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            content['message'],
            '결제가 실패되었습니다.'
        )
        mock_order_fail.assert_called_once_with()
        mock_give_product_fail.assert_called_once_with()

    def test_kakao_pay_fail_for_buy_product_api_when_fail_due_order_not_exists(self):
        # Given:
        self.login_guest(self.guest)
        # And: 주문 id 암호화
        token = encrypt_integer(0)

        # When: 없는 주문 id 로 결제 신청
        response = self.client.post(reverse('payment:product_fail', args=[token]))
        content = json.loads(response.content)

        # Then: Order가 없어서 주문실패 실패
        self.assertEqual(response.status_code, OrderNotExists.status_code)
        self.assertEqual(content['message'], OrderNotExists.default_detail)


@freeze_time('2021-01-01')
class ApproveGiveProductSuccessByTemplateTestCase(GuestTokenMixin, TestCase):
    def setUp(self):
        super(ApproveGiveProductSuccessByTemplateTestCase, self).setUp()
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
    def test_kakao_pay_approve_for_buy_product_template_when_success(self,
                                                                     mock_approve_payment,
                                                                     mock_give_product_give):
        # Given:
        self.login_guest(self.guest)
        data = {
            'pg_token': 'test_token',
        }
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
        response = self.client.get(reverse('payment:product_approve_template', args=[self.order.id]), data=data)

        # Then: 주문 성공
        self.assertTemplateUsed(response, 'payment/pay_success/success.html')
        mock_approve_payment.assert_called_once_with(
            tid='test_tid',
            pg_token='test_token',
            order_id=self.order.id,
            guest_id=self.guest.id,
        )
        mock_give_product_give.assert_called_once_with()

    def test_kakao_pay_approve_for_buy_product_template_when_fail_due_order_not_exists(self):
        # Given:
        self.login_guest(self.guest)
        data = {
            'pg_token': 'test_token',
        }

        # When:
        response = self.client.get(reverse('payment:product_approve_template', args=[0]), data=data)

        # Then: Order가 없어서 주문 실패
        self.assertTemplateUsed(response, 'payment/pay_abused/not_found.html')


@freeze_time('2021-01-01')
class ApproveGiveProductCancelByTemplateTestCase(GuestTokenMixin, TestCase):
    def setUp(self):
        super(ApproveGiveProductCancelByTemplateTestCase, self).setUp()
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
    def test_kakao_pay_cancel_for_buy_product_template_when_success(self,
                                                                    mock_order_cancel,
                                                                    mock_give_product_cancel,
                                                                    mock_cancel_payment):
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
        # And: token 생성
        token = encrypt_integer(self.order.id)

        # When:
        response = self.client.post(reverse('payment:product_cancel_template', args=[token]))

        # Then: 주문 취소 성공
        self.assertTemplateUsed(response, 'payment/pay_cancel/cancel.html')
        mock_order_cancel.assert_called_once_with()
        mock_give_product_cancel.assert_called_once_with()
        mock_cancel_payment.assert_called_once_with(
            tid=self.order.tid,
            cancel_price=self.order.total_paid_price,
            cancel_tax_free_price=self.order.total_tax_paid_price,
            payload=json.dumps({'cancel_reason': '결제 취소'}),
        )

    def test_kakao_pay_cancel_for_buy_product_template_when_fail_due_order_not_exists(self):
        # Given:
        self.login_guest(self.guest)
        # And: token 생성
        token = encrypt_integer(0)

        # When: 없는 주문 id 로 결제 신청
        response = self.client.post(reverse('payment:product_cancel_template', args=[token]))

        # Then: Order가 없어서 주문 취소 실패
        self.assertTemplateUsed(response, 'payment/pay_abused/not_found.html')

    def test_kakao_pay_cancel_for_buy_product_template_when_fail_when_already_canceled(self):
        # Given: 이미 취소함
        self.login_guest(self.guest)
        self.order.status = OrderStatus.CANCEL.value
        self.order.save()
        # And: token 생성
        token = encrypt_integer(self.order.id)

        # When: 이미 Canceled 된 주문
        response = self.client.post(reverse('payment:product_cancel_template', args=[token]))

        # Then: 이미 Canceled 된 주문으로 fail
        self.assertTemplateUsed(response, 'payment/pay_abused/not_found.html')

    def test_kakao_pay_cancel_for_buy_product_template_when_fail_when_invalid_status(self):
        # Given: Fail 상태
        self.login_guest(self.guest)
        self.order.status = OrderStatus.FAIL.value
        self.order.save()
        # And: token 생성
        token = encrypt_integer(self.order.id)

        # When: 유효하지 않은 주문 status 로 요청
        response = self.client.post(reverse('payment:product_cancel_template', args=[token]))

        # Then: 유효하지 않은 주문 status 로 요청 취소 실패
        self.assertTemplateUsed(response, 'payment/pay_abused/not_found.html')

    @patch('payment.views.kakao_pay_approve_give_product_cancel')
    def test_kakao_pay_cancel_for_buy_product_template_when_unexpected_response_from_kakao(self, mock_kakao_pay_approve_give_product_cancel):
        # Given:
        self.login_guest(self.guest)
        # And: token 생성
        token = encrypt_integer(self.order.id)
        # And: 모킹 - KakaoPayCancelError
        mock_kakao_pay_approve_give_product_cancel.side_effect = KakaoPayCancelError

        # When:
        response = self.client.post(reverse('payment:product_cancel_template', args=[token]))

        # Then: cancel html 사용
        self.assertTemplateUsed(response, 'payment/pay_cancel/cancel.html')


@freeze_time('2021-01-01')
class ApproveGiveProductFailByTemplateTestCase(GuestTokenMixin, TestCase):
    def setUp(self):
        super(ApproveGiveProductFailByTemplateTestCase, self).setUp()
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
    def test_kakao_pay_fail_for_buy_product_template_when_success(self,
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
        response = self.client.post(reverse('payment:product_fail_template', args=[token]))

        # Then: 주문 실패 성공
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment/pay_fail/fail.html')
        mock_order_fail.assert_called_once_with()
        mock_give_product_fail.assert_called_once_with()

    def test_kakao_pay_fail_for_buy_product_template_when_fail_due_order_not_exists(self):
        # Given:
        self.login_guest(self.guest)
        # And: 주문 id 암호화
        token = encrypt_integer(0)

        # When: 없는 주문 id 로 결제 신청
        response = self.client.post(reverse('payment:product_fail_template', args=[token]))

        # Then: Order가 없어서 주문실패 실패
        self.assertTemplateUsed(response, 'payment/pay_abused/not_found.html')
