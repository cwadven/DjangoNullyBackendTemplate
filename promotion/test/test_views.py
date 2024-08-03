from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from promotion.consts import BannerTargetLayer
from promotion.models import (
    Banner,
    PromotionRule,
    PromotionTag,
)


class PromotionBannerAPITests(TestCase):
    def setUp(self):
        # Given: 테스트용 URL 설정
        self.url = reverse('promotion:banners')

        # And: 테스트 배너 및 프로모션 규칙 설정
        self.target_layer = BannerTargetLayer.HOME_TOP.value
        self.rule = PromotionRule.objects.create(
            displayable=True,
            display_start_time=timezone.now() - timezone.timedelta(days=1),
            display_end_time=timezone.now() + timezone.timedelta(days=1),
        )
        self.banner = Banner.objects.create(
            promotion_rule=self.rule,
            target_layer=self.target_layer,
        )
        # And: Tag 설정
        self.tag = PromotionTag.objects.create(name='test_tag')
        # And: Banner 에 Tag 추가
        self.banner.tags.add(self.tag)

    def test_get_promotion_banner_should_return_200(self):
        # Given: target_layer 를 전달
        param = {
            'target_layer': self.target_layer,
        }

        # When: PromotionBannerAPIView 호출
        response = self.client.get(self.url, param)

        # Then: 200 상태코드 반환
        self.assertEqual(response.status_code, 200)
        # And: 반환된 데이터가 기대하는 값과 일치하는지 검증
        self.assertDictEqual(
            response.json(),
            {
                'banners': [
                    {
                        'banner_id': self.banner.id,
                        'title': self.banner.title,
                        'title_font_color': self.banner.title_font_color,
                        'description': self.banner.description,
                        'description_font_color': self.banner.description_font_color,
                        'background_color': self.banner.background_color,
                        'big_image': self.banner.big_image,
                        'middle_image': self.banner.middle_image,
                        'small_image': self.banner.small_image,
                        'action_page': self.banner.promotion_rule.action_page,
                        'target_pk': self.banner.promotion_rule.target_pk,
                        'target_type': self.banner.promotion_rule.target_type,
                        'external_target_url': self.banner.promotion_rule.external_target_url,
                        'tags': ['test_tag'],
                    }
                ]
            }
        )

    def test_get_promotion_banner_should_return_400_when_mandatory_key_is_not_exists(self):
        # Given: mandatory key not exists
        param = {}

        # When: PromotionBannerAPIView 호출
        response = self.client.get(self.url, param)

        # Then: 400 상태코드 반환
        self.assertEqual(response.status_code, 400)
        # And: 반환된 데이터가 기대하는 값과 일치하는지 검증
        self.assertDictEqual(
            response.json(),
            {
                'message': '입력값을 다시 확인해주세요.',
                'error_code': 'missing-mandatory-parameter',
                'errors': {
                    'target_layer': ['target_layer 입력값을 확인해주세요.']
                },
            }
        )

    def test_get_promotion_banner_should_return_400_when_target_layer_invalid(self):
        # Given: invalid target_layer
        param = {
            'target_layer': 'invalid_target_layer',
        }

        # When: PromotionBannerAPIView 호출
        response = self.client.get(self.url, param)

        # Then: 400 상태코드 반환
        self.assertEqual(response.status_code, 400)
        # And: 반환된 데이터가 기대하는 값과 일치하는지 검증
        self.assertDictEqual(
            response.json(),
            {'message': '잘못된 target_layer 입니다.'}
        )
