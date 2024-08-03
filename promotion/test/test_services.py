from django.test import TestCase
from django.utils import timezone
from promotion.consts import BannerTargetLayer
from promotion.models import (
    Banner,
    PromotionRule,
)
from promotion.services import get_active_banners


class BannerTestCase(TestCase):
    def setUp(self):
        # Given: 테스트 배너 및 프로모션 규칙 설정
        self.target_layer = BannerTargetLayer('HOME_TOP')
        self.rule_displayable = PromotionRule.objects.create(
            displayable=True,
            display_start_time=timezone.now() - timezone.timedelta(days=1),
            display_end_time=timezone.now() + timezone.timedelta(days=1),
        )
        self.rule_not_displayable = PromotionRule.objects.create(
            displayable=False,
            display_start_time=timezone.now() - timezone.timedelta(days=1),
            display_end_time=timezone.now() + timezone.timedelta(days=1),
        )
        self.displayable_banner = Banner.objects.create(
            promotion_rule=self.rule_displayable,
            target_layer=self.target_layer.value
        )
        self.not_displayable_banner = Banner.objects.create(
            promotion_rule=self.rule_not_displayable,
            target_layer=self.target_layer.value,
        )

    def test_get_active_banners_should_return_one_active_banners(self):
        # Given:
        # When: get_active_banners 호출
        active_banners = get_active_banners(self.target_layer)

        # Then: 반환된 배너가 1개이어야 함
        self.assertEqual(len(active_banners), 1)
        # And: 반환된 배너가 displayable 이어야 함
        self.assertEqual(
            all(banner.promotion_rule.displayable for banner in active_banners),
            True,
        )
        # And: 반환된 배너가 target_layer 가 HOME_TOP 이어야 함
        self.assertEqual(
            all(banner.target_layer == self.target_layer.value for banner in active_banners),
            True,
        )
        # And: 반환된 배너가 id 가 displayable_banner.id 이어야 함
        self.assertEqual(self.displayable_banner.id, active_banners[0].id)

    def test_get_active_banners_should_return_one_active_banners_when_banner_start_time_is_null(self):
        # Given: display_start_time 이 None 인 배너를 생성
        self.rule_displayable.display_start_time = None
        self.rule_displayable.save()

        # When: get_active_banners 호출
        active_banners = get_active_banners(self.target_layer)

        # Then: 반환된 배너가 1개이어야 함
        self.assertEqual(len(active_banners), 1)
        # And: 반환된 배너가 displayable 이어야 함
        self.assertEqual(
            all(banner.promotion_rule.displayable for banner in active_banners),
            True,
        )
        # And: 반환된 배너가 target_layer 가 HOME_TOP 이어야 함
        self.assertEqual(
            all(banner.target_layer == self.target_layer.value for banner in active_banners),
            True,
        )
        # And: 반환된 배너가 id 가 displayable_banner.id 이어야 함
        self.assertEqual(self.displayable_banner.id, active_banners[0].id)

    def test_get_active_banners_should_return_one_active_banners_when_banner_end_time_is_null(self):
        # Given: display_end_time 이 None 인 배너를 생성
        self.rule_displayable.display_end_time = None
        self.rule_displayable.save()

        # When: get_active_banners 호출
        active_banners = get_active_banners(self.target_layer)

        # Then: 반환된 배너가 1개이어야 함
        self.assertEqual(len(active_banners), 1)
        # And: 반환된 배너가 displayable 이어야 함
        self.assertEqual(
            all(banner.promotion_rule.displayable for banner in active_banners),
            True,
        )
        # And: 반환된 배너가 target_layer 가 HOME_TOP 이어야 함
        self.assertEqual(
            all(banner.target_layer == self.target_layer.value for banner in active_banners),
            True,
        )
        # And: 반환된 배너가 id 가 displayable_banner.id 이어야 함
        self.assertEqual(self.displayable_banner.id, active_banners[0].id)

    def test_get_active_banners_should_return_no_banner_when_displayable_banner_not_exists(self):
        # Given: 모든 배너를 displayable=False 로 설정
        PromotionRule.objects.all().update(displayable=False)

        # When: get_active_banners 호출
        active_banners = get_active_banners(self.target_layer)

        # Then: 반환된 배너가 0개이어야 함
        self.assertEqual(len(active_banners), 0)

    def test_get_active_banners_should_return_no_banner_when_invalid_start_time_banner_exists(self):
        # Given: displayable=True 이지만 display_start_time 이 미래인 배너를 생성
        self.rule_displayable.display_start_time = timezone.now() + timezone.timedelta(days=1)
        self.rule_displayable.save()
        self.rule_not_displayable.displayable = True
        self.rule_not_displayable.display_start_time = timezone.now() + timezone.timedelta(days=1)
        self.rule_not_displayable.save()

        # When: get_active_banners 호출
        active_banners = get_active_banners(self.target_layer)

        # Then: 반환된 배너가 0개이어야 함
        self.assertEqual(len(active_banners), 0)

    def test_get_active_banners_should_return_no_banner_when_invalid_end_time_banner_exists(self):
        # Given: displayable=True 이지만 display_end_time 이 과거인 배너를 생성
        self.rule_displayable.display_end_time = timezone.now() - timezone.timedelta(days=1)
        self.rule_displayable.save()
        self.rule_not_displayable.displayable = True
        self.rule_not_displayable.display_end_time = timezone.now() - timezone.timedelta(days=1)
        self.rule_not_displayable.save()

        # When: get_active_banners 호출
        active_banners = get_active_banners(self.target_layer)

        # Then: 반환된 배너가 0개이어야 함
        self.assertEqual(len(active_banners), 0)

    def test_get_active_banners_should_return_no_banner_now_param_invalid(self):
        # Given: now 파라미터가 과거인 시간으로 설정
        now = timezone.now() - timezone.timedelta(days=100)

        # When: get_active_banners 호출
        active_banners = get_active_banners(self.target_layer, now)

        # Then: 반환된 배너가 0개이어야 함
        self.assertEqual(len(active_banners), 0)
