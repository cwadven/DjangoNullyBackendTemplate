import json
from datetime import datetime
from unittest.mock import (
    patch,
)

from common.common_testcase_helpers.testcase_helpers import (
    test_case_create_order,
    test_case_create_order_item,
)
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time
from member.models import Guest
from order.consts import OrderStatus
from point.exceptions import NotEnoughGuestPointsForCancelOrder
from product.consts import (
    ProductGivenStatus,
    ProductType,
)
from product.exceptions import ProductStockNotEnough
from product.models import (
    GiveProduct,
    GiveProductLog,
    PointProduct,
    ProductImage,
)
from product.test import ConcreteProductTestModel


@freeze_time('2022-01-01')
class GiveProductMethodTestCase(TestCase):
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

    def test_ready(self):
        # Given:
        quantity = 10

        # When:
        give_product_ready_status = GiveProduct.ready(
            order_item_id=self.order_item1.id,
            guest_id=self.guest.id,
            product_pk=999,
            quantity=quantity,
            product_type='TEST',
            data={'point': 10000},
        )

        # Then:
        self.assertEqual(
            GiveProduct.objects.filter(
                id=give_product_ready_status.id,
                status=OrderStatus.READY.value,
                order_item_id=self.order_item1.id,
                product_type='TEST',
                meta_data=json.dumps({'point': 10000}),
                created_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        # And: Log 생성
        self.assertEqual(
            GiveProductLog.objects.filter(
                give_product_id=give_product_ready_status.id,
                status=OrderStatus.READY.value,
                created_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )

    def test_cancel(self):
        # Given:
        quantity = 10
        give_product_ready_status = GiveProduct.ready(
            order_item_id=self.order_item1.id,
            guest_id=self.guest.id,
            product_pk=999,
            quantity=quantity,
            product_type='TEST',
            data={'point': 10000},
        )

        # When:
        give_product_ready_status.cancel()

        # Then:
        self.assertEqual(
            GiveProduct.objects.filter(
                id=give_product_ready_status.id,
                status=OrderStatus.CANCEL.value,
                created_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        # And: Log 생성
        self.assertEqual(
            GiveProductLog.objects.filter(
                give_product_id=give_product_ready_status.id,
                status=OrderStatus.CANCEL.value,
                created_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )

    def test_cancel_when_product_is_point_should_raise_error_when_point_is_not_enough(self):
        # Given:
        point_1000_product = PointProduct.objects.create(
            title='포인트 1000',
            price=1000,
            point=1000,
            created_guest=self.guest,
        )
        quantity = 10
        give_product_ready_status = GiveProduct.ready(
            order_item_id=self.order_item1.id,
            guest_id=self.guest.id,
            product_pk=point_1000_product.id,
            quantity=quantity,
            product_type=point_1000_product.product_type,
            data={
                'point': point_1000_product.point,
                'total_point': point_1000_product.point * quantity,
            },
        )
        # And: Make as success
        give_product_ready_status.status = ProductGivenStatus.SUCCESS.value
        give_product_ready_status.save()

        # When: raise
        with self.assertRaises(NotEnoughGuestPointsForCancelOrder):
            give_product_ready_status.cancel()

        # Then:
        self.assertEqual(
            GiveProduct.objects.filter(
                id=give_product_ready_status.id,
                status=OrderStatus.CANCEL.value,
                created_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            False
        )
        # And: 에러로 Log 생성 불가
        self.assertEqual(
            GiveProductLog.objects.filter(
                give_product_id=give_product_ready_status.id,
                status=OrderStatus.CANCEL.value,
                created_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            False
        )

    @patch('product.models.give_point')
    @patch('product.models.get_guest_available_total_point')
    def test_cancel_when_product_is_point_success(self,
                                                  mock_get_guest_available_total_point,
                                                  mock_give_point):
        # Given:
        point_1000_product = PointProduct.objects.create(
            title='포인트 1000',
            price=1000,
            point=1000,
            created_guest=self.guest,
        )
        quantity = 10
        give_product_ready_status = GiveProduct.ready(
            order_item_id=self.order_item1.id,
            guest_id=self.guest.id,
            product_pk=point_1000_product.id,
            quantity=quantity,
            product_type=point_1000_product.product_type,
            data={
                'point': point_1000_product.point,
                'total_point': point_1000_product.point * quantity,
            },
        )
        mock_get_guest_available_total_point.return_value = point_1000_product.point * quantity
        # And: Set as success
        give_product_ready_status.status = ProductGivenStatus.SUCCESS.value
        give_product_ready_status.save()

        # When:
        give_product_ready_status.cancel()

        # Then:
        self.assertEqual(
            GiveProduct.objects.filter(
                id=give_product_ready_status.id,
                status=OrderStatus.CANCEL.value,
                created_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        # And: 에러로 Log 생성 불가
        self.assertEqual(
            GiveProductLog.objects.filter(
                give_product_id=give_product_ready_status.id,
                status=OrderStatus.CANCEL.value,
                created_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        mock_give_point.assert_called_once_with(
            guest_id=self.guest.id,
            point=json.loads(give_product_ready_status.meta_data)['total_point'] * -1,
            reason='결제 취소로 포인트 회수',
        )

    def test_fail(self):
        # Given:
        quantity = 10
        give_product_ready_status = GiveProduct.ready(
            order_item_id=self.order_item1.id,
            guest_id=self.guest.id,
            product_pk=999,
            quantity=quantity,
            product_type='TEST',
            data={'point': 10000},
        )

        # When:
        give_product_ready_status.fail()

        # Then:
        self.assertEqual(
            GiveProduct.objects.filter(
                id=give_product_ready_status.id,
                status=OrderStatus.FAIL.value,
                created_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        # And: Log 생성
        self.assertEqual(
            GiveProductLog.objects.filter(
                give_product_id=give_product_ready_status.id,
                status=OrderStatus.FAIL.value,
                created_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )

    @patch('product.models.give_point')
    def test_give_when_point_product_exists(self, mock_give_point):
        # Given:
        point_1000_product = PointProduct.objects.create(
            title='포인트 1000',
            price=1000,
            point=1000,
            created_guest=self.guest,
        )
        quantity = 10

        give_product_ready_status = GiveProduct.ready(
            order_item_id=self.order_item1.id,
            guest_id=self.guest.id,
            quantity=quantity,
            product_pk=point_1000_product.id,
            product_type=point_1000_product.product_type,
            data={'point': 10000},
        )

        # When:
        give_product_ready_status.give()

        # Then:
        self.assertEqual(
            GiveProduct.objects.filter(
                id=give_product_ready_status.id,
                status=OrderStatus.SUCCESS.value,
                created_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        # And: Log 생성
        self.assertEqual(
            GiveProductLog.objects.filter(
                give_product_id=give_product_ready_status.id,
                status=OrderStatus.SUCCESS.value,
                created_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        mock_give_point.assert_called_once_with(
            guest_id=self.guest.id,
            point=point_1000_product.point * quantity,
            reason='포인트 지급',
        )

    @patch('product.models.give_point')
    def test_give_when_point_product_not_exists(self, mock_give_point):
        # Given:
        quantity = 10
        meta_data = {
            'point': 1000,
            'quantity': quantity,
            'total_point': 1000 * 10,
        }
        # And: PointProduct 가 없음
        give_product_ready_status = GiveProduct.ready(
            order_item_id=self.order_item1.id,
            guest_id=self.guest.id,
            quantity=quantity,
            product_pk=0,
            product_type=PointProduct.product_type,
            data=meta_data,
        )

        # When:
        give_product_ready_status.give()

        # Then:
        self.assertEqual(
            GiveProduct.objects.filter(
                id=give_product_ready_status.id,
                status=OrderStatus.SUCCESS.value,
                created_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        # And: Log 생성
        self.assertEqual(
            GiveProductLog.objects.filter(
                give_product_id=give_product_ready_status.id,
                status=OrderStatus.SUCCESS.value,
                created_at=datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
            ).exists(),
            True
        )
        mock_give_point.assert_called_once_with(
            guest_id=self.guest.id,
            point=meta_data['point'] * quantity,
            reason='포인트 지급',
        )


class PointProductMethodTestCase(TestCase):
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
        self.point_1000_product = PointProduct.objects.create(
            title='포인트 1000',
            price=1000,
            point=1000,
            created_guest=self.guest,
        )

    @patch('product.models.GiveProduct.ready')
    @patch('product.models.OrderItem.initialize')
    @patch('product.models.Order.initialize')
    def test_initialize_order(self, mock_order_initialize, mock_order_item_initialize, mock_give_point_product_ready):
        # Given: Make mock
        mock_order_initialize.return_value = self.order
        mock_order_item_initialize.return_value = self.order_item1
        quantity = 10

        # When:
        self.point_1000_product._initialize_order(
            guest=self.guest,
            order_phone_number='01012341234',
            payment_type='KAKAO',
            quantity=quantity,
        )

        # Then:
        mock_order_initialize.assert_called_once_with(
            product=self.point_1000_product,
            guest=self.guest,
            order_phone_number='01012341234',
            payment_type='KAKAO',
            total_price=self.point_1000_product.price * quantity,
            total_tax_price=0,
            total_product_price=self.point_1000_product.price * quantity,
            total_paid_price=self.point_1000_product.price * quantity,
            total_tax_paid_price=0,
            total_product_paid_price=self.point_1000_product.price * quantity,
            total_discounted_price=0,
            total_product_discounted_price=0,
        )
        mock_order_item_initialize.assert_called_once_with(
            order_id=self.order.id,
            product_id=self.point_1000_product.id,
            product_type=self.point_1000_product.product_type,
            product_price=self.point_1000_product.price * quantity,
            discounted_price=0,
            paid_price=self.point_1000_product.price * quantity,
            item_quantity=quantity,
        )
        mock_give_point_product_ready.assert_called_once_with(
            order_item_id=self.order_item1.id,
            guest_id=self.guest.id,
            product_pk=self.point_1000_product.id,
            product_type=self.point_1000_product.product_type,
            quantity=quantity,
            data={
                'point': self.point_1000_product.point,
                'total_point': self.point_1000_product.point * quantity,
                'quantity': quantity,
            },
        )


class ProductMethodTestCase(TestCase):
    def setUp(self):
        self.guest = Guest.objects.first()
        self.point_1000_product = PointProduct.objects.create(
            title='포인트 1000',
            price=1000,
            point=1000,
            created_guest=self.guest,
        )
        self.point_1000_product_image1 = ProductImage.objects.create(
            product_pk=self.point_1000_product.id,
            product_type=ProductType.POINT.value,
            ordering=1,
            created_guest=self.guest,
            image_url='image1',
        )
        self.point_1000_product_image2 = ProductImage.objects.create(
            product_pk=self.point_1000_product.id,
            product_type=ProductType.POINT.value,
            ordering=2,
            created_guest=self.guest,
            image_url='image2',
        )
        self.point_1000_product_deleted_image1 = ProductImage.objects.create(
            product_pk=self.point_1000_product.id,
            product_type=ProductType.POINT.value,
            ordering=1,
            created_guest=self.guest,
            image_url='deleted_image1',
            is_deleted=True,
        )

    @patch('product.models.Product.save')
    def test_adjust_stock_after_sale_should_not_call_save_when_total_quantity_is_false_type(self, mock_save):
        # Given:
        expected_total_quantities = [
            0,
            None
        ]
        for expected_total_quantity in expected_total_quantities:
            # And: Product total_quantity is None
            product = ConcreteProductTestModel(
                title='포인트 1000',
                price=1000,
                created_guest=self.guest,
                total_quantity=expected_total_quantity,
            )

            # When:
            product._adjust_stock_after_sale(
                quantity=1,
            )

            # Then:
            mock_save.assert_not_called()

    @patch('product.models.Product.save')
    def test_adjust_stock_after_sale_should_not_call_save_when_left_quantity_is_false_type(self, mock_save):
        # Given:
        expected_left_quantities = [
            0,
            None
        ]
        for expected_left_quantity in expected_left_quantities:
            # And: Product total_quantity is None
            product = ConcreteProductTestModel(
                title='포인트 1000',
                price=1000,
                created_guest=self.guest,
                left_quantity=expected_left_quantity,
            )

            # When:
            product._adjust_stock_after_sale(
                quantity=1,
            )

            # Then:
            mock_save.assert_not_called()

    @patch('product.models.Product.save')
    def test_adjust_stock_after_sale_should_raise_error_when_left_quantity_is_less_then_zero(self, mock_save):
        # Given:
        product = ConcreteProductTestModel(
            title='포인트 1000',
            price=1000,
            created_guest=self.guest,
            total_quantity=80,
            left_quantity=10,
        )

        # When: left_quantity over than quantity
        with self.assertRaises(ProductStockNotEnough) as e:
            product._adjust_stock_after_sale(
                quantity=11,
            )
            self.assertEqual(e.exception.detail, '상품 재고가 부족합니다.')

        # Then:
        mock_save.assert_not_called()

    @patch('product.models.Product.save')
    def test_adjust_stock_after_sale_should_success_save_with_increase_bought_count(self, mock_save):
        # Given:
        product = ConcreteProductTestModel(
            title='포인트 1000',
            price=1000,
            created_guest=self.guest,
            total_quantity=80,
            left_quantity=10,
        )

        # When:
        product._adjust_stock_after_sale(
            quantity=5,
        )

        # Then: bought_count should be increased
        self.assertEqual(product.bought_count, 1)
        self.assertEqual(product.left_quantity, 5)
        # And: save should be called
        mock_save.assert_called_once_with(
            update_fields=['left_quantity', 'bought_count', 'is_sold_out']
        )

    @patch('product.models.Product.save')
    def test_adjust_stock_after_sale_should_make_sold_out_when_left_quantity_is_zero(self, mock_save):
        # Given:
        product = ConcreteProductTestModel(
            title='포인트 1000',
            price=1000,
            created_guest=self.guest,
            total_quantity=80,
            left_quantity=10,
        )

        # When:
        product._adjust_stock_after_sale(
            quantity=10,
        )

        # Then: bought_count should be increased
        self.assertEqual(product.bought_count, 1)
        self.assertEqual(product.left_quantity, 0)
        # And: is_sold_out should be True
        self.assertEqual(product.is_sold_out, True)
        # And: save should be called
        mock_save.assert_called_once_with(
            update_fields=['left_quantity', 'bought_count', 'is_sold_out']
        )

    @patch('product.models.Product._adjust_stock_after_sale')
    @patch('product.models.Product._initialize_order')
    def test_initialize_order(self, mock_initialize_order, mock_adjust_stock_after_sale):
        # Given: Product
        product = ConcreteProductTestModel(
            title='포인트 1000',
            price=1000,
            created_guest=self.guest,
        )

        # When:
        product.initialize_order(
            guest=self.guest,
            order_phone_number='01012341234',
            payment_type='KAKAO',
            quantity=1,
        )

        # Then:
        mock_initialize_order.assert_called_once_with(
            self.guest,
            '01012341234',
            'KAKAO',
            1,
            None,
        )
        mock_adjust_stock_after_sale.assert_called_once_with(1)

    def test_get_product_images(self):
        # Given:
        # When:
        product_images = self.point_1000_product.get_product_images()

        # Then: Deleted should be excluded and sorted by sequence
        self.assertEqual(
            product_images,
            [
                self.point_1000_product_image1,
                self.point_1000_product_image2,
            ]
        )
