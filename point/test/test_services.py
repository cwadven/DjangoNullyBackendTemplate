from datetime import datetime

from django.test import TestCase
from freezegun import freeze_time
from member.models import Guest
from point.exceptions import NotEnoughGuestPoints
from point.models import GuestPoint
from point.services import (
    get_guest_available_total_point,
    give_point,
    use_point,
)


class GuestPointTestCase(TestCase):
    def setUp(self):
        super(GuestPointTestCase, self).setUp()
        self.guest = Guest.objects.all().first()

    @staticmethod
    def _give_guest_points(guest, point):
        return GuestPoint.objects.create(
            guest=guest,
            point=point,
            reason='test 포인트 지급',
        )

    def test_get_guest_available_total_point(self):
        # Given: Point 2번 각각 지급
        self._give_guest_points(self.guest, 100)
        self._give_guest_points(self.guest, 200)

        # When:
        total_point = get_guest_available_total_point(self.guest.id)

        # Then:
        self.assertEqual(total_point, 300)

    def test_get_guest_available_total_point_when_point_is_minus(self):
        # Given: Point 2번 각각 지급 (마이너스 값)
        self._give_guest_points(self.guest, 100)
        self._give_guest_points(self.guest, -200)

        # When:
        total_point = get_guest_available_total_point(self.guest.id)

        # Then: 0 반환
        self.assertEqual(total_point, 0)

    def test_get_guest_available_total_point_when_point_is_not_active(self):
        # Given: Point 생성 후, is_active False 로 전환
        user_point1 = self._give_guest_points(self.guest, 100)
        user_point1.is_active = False
        user_point1.save()

        # When:
        total_point = get_guest_available_total_point(self.guest.id)

        # Then: 0 반환
        self.assertEqual(total_point, 0)

    @freeze_time('2020-01-02 00:00:00')
    def test_get_guest_available_total_point_when_point_valid_until_is_invalid(self):
        # Given: Point 생성
        user_point1 = self._give_guest_points(self.guest, 100)
        # And: is_active True
        user_point1.is_active = True
        # And: Set valid_from None 언제나 사용 가능
        user_point1.valid_from = None
        # And: Set valid_until 과거 시간
        user_point1.valid_until = datetime(2020, 1, 1)
        user_point1.save()

        # When:
        total_point = get_guest_available_total_point(self.guest.id)

        # Then: 0 반환
        self.assertEqual(total_point, 0)

    @freeze_time('2020-01-01 00:00:00')
    def test_get_guest_available_total_point_when_point_valid_from_is_invalid(self):
        # Given: Point 생성
        user_point1 = self._give_guest_points(self.guest, 100)
        # And: is_active True
        user_point1.is_active = True
        # And: Set valid_from 미래 시간
        user_point1.valid_from = datetime(2020, 1, 2)
        # And: Set valid_until None 언제나 사용 가능
        user_point1.valid_until = None
        user_point1.save()

        # When:
        total_point = get_guest_available_total_point(self.guest.id)

        # Then: 0 반환
        self.assertEqual(total_point, 0)

    @freeze_time('2020-01-02 00:00:00')
    def test_get_guest_available_total_point_when_point_valid_from_and_valid_until_is_valid(self):
        # Given: Point 생성
        user_point1 = self._give_guest_points(self.guest, 100)
        # And: is_active True
        user_point1.is_active = True
        # And: Set valid_from 과거 시간
        user_point1.valid_from = datetime(2020, 1, 2)
        # And: Set valid_until 미래 시간
        user_point1.valid_until = datetime(2020, 1, 3)
        user_point1.save()

        # When:
        total_point = get_guest_available_total_point(self.guest.id)

        # Then: 100 반환
        self.assertEqual(total_point, 100)

    def test_use_point_should_raise_error_when_user_has_not_enough_point(self):
        # Given:
        # Expect:
        with self.assertRaises(NotEnoughGuestPoints):
            use_point(self.guest.id, 100, 'test')

    def test_use_point_should_success_when_user_has_enough_point(self):
        # Given: 포인트 지급
        self._give_guest_points(self.guest, 100)
        # And: 100 받음
        self.assertEqual(get_guest_available_total_point(self.guest.id), 100)

        # When:
        guest_point = use_point(self.guest.id, 100, 'test')

        # Then: 100 을 사용하여 0 원 남았습니다.
        self.assertEqual(get_guest_available_total_point(self.guest.id), 0)
        # And: -100
        self.assertEqual(GuestPoint.objects.get(id=guest_point.id).point, -100)

    def test_give_point(self):
        reason = 'aaaa'
        point = 100

        guest_point = give_point(self.guest.id, point, reason)

        guest_point = GuestPoint.objects.get(id=guest_point.id)
        self.assertEqual(guest_point.guest_id, self.guest.id)
        self.assertEqual(guest_point.reason, reason)
        self.assertEqual(guest_point.point, point)
