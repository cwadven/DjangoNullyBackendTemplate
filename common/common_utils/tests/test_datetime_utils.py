from datetime import date

from common.common_utils.datetime_utils import get_date_diff_year_and_month
from django.test import TestCase
from freezegun import freeze_time


class TestGetDateDiffYearAndMonth(TestCase):
    def test_date_diff_normal_case(self):
        # Given: 정상적인 날짜 입력
        start_date = date(2022, 1, 1)
        end_date = date(2024, 5, 31)

        # When:
        years, months = get_date_diff_year_and_month(start_date, end_date)

        # Then:
        self.assertEqual((years, months), (2, 4))

    def test_date_diff_same_year(self):
        # Given: 같은 연도, 월 단위 차이
        start_date = date(2023, 3, 1)
        end_date = date(2023, 8, 1)

        # When:
        years, months = get_date_diff_year_and_month(start_date, end_date)

        # Then:
        self.assertEqual((years, months), (0, 5))

    def test_date_diff_no_difference(self):
        # Given: 연도 차이 없는 경우
        start_date = date(2023, 1, 1)
        end_date = date(2023, 1, 1)

        # When:
        years, months = get_date_diff_year_and_month(start_date, end_date)

        # Then:
        self.assertEqual((years, months), (0, 0))

    @freeze_time('2023-08-01')
    def test_date_diff_end_date_none(self):
        # Given: end_date가 제공되지 않은 경우
        start_date = date(2023, 3, 1)
        years, months = get_date_diff_year_and_month(start_date)
        self.assertEqual((years, months), (0, 5))
