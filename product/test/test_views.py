import json

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from member.models import Guest
from product.models import PointProduct


@freeze_time('2021-01-01')
class PointProductListAPIViewTestCase(TestCase):
    def setUp(self):
        super(PointProductListAPIViewTestCase, self).setUp()
        self.guest = Guest.objects.all().first()
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
        self.active_1000_point_product_ordering_2 = PointProduct.objects.create(
            title='Active Point Product2',
            price=1000,
            start_time=timezone.now() - timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            total_quantity=10,
            left_quantity=10,
            point=1000,
            ordering=2,
            created_guest=self.guest
        )

    def test_point_product_list(self):
        # Given:
        # When:
        response = self.client.get(reverse('product:points'))
        content = json.loads(response.content)

        # Then: product excepted list
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content['products']), 2)
        self.assertDictEqual(
            content['products'][0],
            {
                'product_id': self.active_1000_point_product_ordering_1.id,
                'title': 'Active Point Product1',
                'description': None,
                'is_sold_out': False,
                'price': 1000,
                'point': 1000,
                'product_type': self.active_1000_point_product_ordering_1.product_type,
                'review_count': 0,
                'review_rate': 0.0,
                'bought_count': 0,
            }
        )
        self.assertDictEqual(
            content['products'][1],
            {
                'product_id': self.active_1000_point_product_ordering_2.id,
                'title': 'Active Point Product2',
                'description': None,
                'is_sold_out': False,
                'price': 1000,
                'point': 1000,
                'product_type': self.active_1000_point_product_ordering_2.product_type,
                'review_count': 0,
                'review_rate': 0.0,
                'bought_count': 0,
            }
        )

    def test_point_product_list_with_pagination(self):
        # Given:
        params = {
            'page': 1,
            'size': 1,
        }
        # When:
        response = self.client.get(reverse('product:points'), data=params)
        content = json.loads(response.content)

        # Then: product excepted list
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content['products']), 1)
        self.assertDictEqual(
            content['products'][0],
            {
                'product_id': self.active_1000_point_product_ordering_1.id,
                'title': 'Active Point Product1',
                'description': None,
                'is_sold_out': False,
                'price': 1000,
                'point': 1000,
                'product_type': self.active_1000_point_product_ordering_1.product_type,
                'review_count': 0,
                'review_rate': 0.0,
                'bought_count': 0,
            }
        )
