from django.test import TestCase
from django.utils import timezone
from member.models import Guest
from product.models import PointProduct


class TestProductQuerySet(TestCase):
    def setUp(self):
        # Set up data for the test
        self.guest = Guest.objects.all().first()
        self.active_product = PointProduct.objects.create(
            title='Active Product',
            total_quantity=10,
            left_quantity=10,
            price=1000,
            start_time=timezone.now() - timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            point=1000,
            created_guest=self.guest,
        )

        self.inactive_product_future = PointProduct.objects.create(
            title='Inactive Product Future',
            price=1000,
            start_time=timezone.now() + timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=2),
            total_quantity=10,
            left_quantity=10,
            point=1000,
            created_guest=self.guest,
        )

        self.inactive_product_past = PointProduct.objects.create(
            title='Inactive Product Past',
            price=1000,
            start_time=timezone.now() - timezone.timedelta(hours=2),
            end_time=timezone.now() - timezone.timedelta(hours=1),
            total_quantity=10,
            left_quantity=10,
            point=1000,
            created_guest=self.guest,
        )

        self.inactive_product_sold_out = PointProduct.objects.create(
            title='Inactive Product Sold Out',
            price=1000,
            start_time=timezone.now() - timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            total_quantity=10,
            left_quantity=0,
            is_sold_out=True,
            point=1000,
            created_guest=self.guest,
        )

    def test_get_actives(self):
        # Test get_actives method
        # When: 실행
        active_products = PointProduct.objects.get_actives()

        # Then:
        self.assertEqual(active_products.count(), 1)
        self.assertEqual(active_products.first(), self.active_product)

    def test_get_active_products_when_end_date_is_not_exists(self):
        # Given: end_time Null 생성
        self.active_product.end_time = None
        self.active_product.save()

        # When: 실행
        active_products = PointProduct.objects.get_actives()

        # Then:
        self.assertEqual(active_products.count(), 1)
        self.assertEqual(active_products.first(), self.active_product)

    def test_inactive_product_future(self):
        # Check that the product with future start time is not included
        # When: 실행
        active_products = PointProduct.objects.get_actives()

        # Then:
        self.assertNotIn(self.inactive_product_future, active_products)

    def test_inactive_product_past(self):
        # Check that the product with past end time is not included
        # When: 실행
        active_products = PointProduct.objects.get_actives()

        # Then:
        self.assertNotIn(self.inactive_product_past, active_products)

    def test_inactive_product_sold_out(self):
        # Check that the sold out product is not included
        # When: 실행
        active_products = PointProduct.objects.get_actives()

        # Then:
        self.assertNotIn(self.inactive_product_sold_out, active_products)
