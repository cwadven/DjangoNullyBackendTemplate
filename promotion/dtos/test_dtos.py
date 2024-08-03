from django.test import TestCase
from django.utils import timezone
from promotion.consts import BannerTargetLayer
from promotion.dtos.model_dtos import PromotionBanner
from promotion.models import (
    Banner,
    PromotionRule,
    PromotionTag,
)


class PromotionBannerTest(TestCase):
    def setUp(self):
        # Given: 테스트 배너 및 프로모션 규칙 설정
        self.target_layer = BannerTargetLayer.HOME_TOP.value
        self.rule = PromotionRule.objects.create(
            displayable=True,
            display_start_time=timezone.now() - timezone.timedelta(days=1),
            display_end_time=timezone.now() + timezone.timedelta(days=1),
            action_page='action_page_test',
            target_pk='target_pk_test',
            target_type='target_type_test',
            external_target_url='external_target_url_test',
        )
        self.banner = Banner.objects.create(
            promotion_rule=self.rule,
            target_layer=self.target_layer,
        )
        # And: Tag 설정
        self.tag = PromotionTag.objects.create(name='test_tag')
        # And: Banner 에 Tag 추가
        self.banner.tags.add(self.tag)

    def test_promotion_banner_of_method(self):
        # Given:

        # When: PromotionBanner.of 메서드를 사용하여 Pydantic 모델 인스턴스를 생성
        promotion_banner = PromotionBanner.of(self.banner)

        # Then: PromotionBanner 인스턴스의 필드가 기대하는 값과 일치하는지 검증
        self.assertEqual(promotion_banner.banner_id, self.banner.id)
        self.assertEqual(promotion_banner.title, self.banner.title)
        self.assertEqual(promotion_banner.title_font_color, self.banner.title_font_color)
        self.assertEqual(promotion_banner.description, self.banner.description)
        self.assertEqual(promotion_banner.description_font_color, self.banner.description_font_color)
        self.assertEqual(promotion_banner.background_color, self.banner.background_color)
        self.assertEqual(promotion_banner.big_image, self.banner.big_image)
        self.assertEqual(promotion_banner.middle_image, self.banner.middle_image)
        self.assertEqual(promotion_banner.small_image, self.banner.small_image)
        self.assertEqual(promotion_banner.action_page, self.banner.promotion_rule.action_page)
        self.assertEqual(promotion_banner.target_pk, self.banner.promotion_rule.target_pk)
        self.assertEqual(promotion_banner.target_type, self.banner.promotion_rule.target_type)
        self.assertEqual(promotion_banner.external_target_url, self.banner.promotion_rule.external_target_url)
        self.assertEqual(promotion_banner.tags, ['test_tag'])
