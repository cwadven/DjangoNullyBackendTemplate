from django.test import TestCase
from member.models import Guest
from product.dtos.model_dtos import PointProductItem
from product.models import PointProduct


class PointProductItemTest(TestCase):
    def setUp(self):
        self.guest = Guest.objects.all().first()
        self.point_1000_product = PointProduct.objects.create(
            title='포인트 1000',
            price=1000,
            point=1000,
            created_guest=self.guest,
        )

    def test_point_product_item_creation(self):
        # Given:
        # When: PointProductItem.of 메서드를 사용하여 Pydantic 모델 인스턴스를 생성
        point_product_item = PointProductItem.of(self.point_1000_product)

        # Then: PointProductItem 인스턴스의 필드가 기대하는 값과 일치하는지 검증
        self.assertEqual(point_product_item.product_id, self.point_1000_product.id)
        self.assertEqual(point_product_item.product_type, self.point_1000_product.product_type)
        self.assertEqual(point_product_item.title, self.point_1000_product.title)
        self.assertEqual(point_product_item.description, self.point_1000_product.description)
        self.assertEqual(point_product_item.price, self.point_1000_product.price)
        self.assertEqual(point_product_item.point, self.point_1000_product.point)
        self.assertFalse(point_product_item.is_sold_out, self.point_1000_product.is_sold_out)
        self.assertEqual(point_product_item.bought_count, self.point_1000_product.bought_count)
        self.assertEqual(point_product_item.review_count, self.point_1000_product.review_count)
        self.assertEqual(point_product_item.review_rate, self.point_1000_product.review_rate)
