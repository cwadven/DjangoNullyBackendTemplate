from unittest.mock import patch

from django.test import TestCase
from member.consts import (
    MemberStatusEnum,
    MemberTypeEnum,
)
from member.models import Member


class TestMemberManagerManager(TestCase):
    def setUp(self):
        pass

    @patch('member.managers.SocialLoginHandler.validate')
    @patch('member.managers.generate_random_string_digits')
    def test_get_or_create_member_by_token_when_create_user_email_and_nickname_not_exists(self, mock_random_string, mock_validate):
        # Given:
        token = 'test_token'
        provider = 3
        # And: validate 결과 값 모킹
        mock_validate.return_value = {
            'id': 'test_id',
            'email': None,
            'nickname': None,
        }
        # And: 닉네임 생성 모킹
        mock_random_string.return_value = '12345'

        # When: get_or_create_member_by_token
        member, is_created = Member.objects.get_or_create_member_by_token(token, provider)

        # Then:
        self.assertTrue(is_created)
        self.assertEqual(member.username, 'test_id')
        self.assertEqual(member.member_provider_id, provider)
        self.assertEqual(member.member_type_id, MemberTypeEnum.NORMAL_MEMBER.value)
        self.assertEqual(member.member_status_id, MemberStatusEnum.NORMAL_MEMBER.value)
        self.assertEqual(member.email, '')
        self.assertEqual(member.nickname, 'Random12345')

    @patch('member.managers.SocialLoginHandler.validate')
    def test_get_or_create_member_by_token_when_create_user_email_and_nickname_exists(self, mock_validate):
        # Given:
        token = 'test_token'
        provider = 3
        # And: validate 결과 값 모킹
        mock_validate.return_value = {
            'id': 'test_id',
            'email': 'test_email',
            'nickname': 'test_nickname',
        }

        # When: get_or_create_member_by_token
        member, is_created = Member.objects.get_or_create_member_by_token(token, provider)

        # Then:
        self.assertTrue(is_created)
        self.assertEqual(member.username, 'test_id')
        self.assertEqual(member.member_provider_id, provider)
        self.assertEqual(member.member_type_id, MemberTypeEnum.NORMAL_MEMBER.value)
        self.assertEqual(member.member_status_id, MemberStatusEnum.NORMAL_MEMBER.value)
        self.assertEqual(member.email, 'test_email')
        self.assertEqual(member.nickname, 'test_nickname')

    @patch('member.managers.SocialLoginHandler.validate')
    def test_get_or_create_member_by_token_when_already_member_exists(self, mock_validate):
        # Given:
        token = 'test_token'
        provider = 3
        # And: validate 결과 값 모킹
        mock_validate.return_value = {
            'id': 'test_id',
            'email': 'test_email',
            'nickname': 'test_nickname',
        }
        # And: 1번 미리 생성 get_or_create_member_by_token
        Member.objects.get_or_create_member_by_token(token, provider)

        # When: 2번째 email 과 nickname 기존과 다르게 하고 실행
        mock_validate.return_value = {
            'id': 'test_id',
            'email': 'test_email2',
            'nickname': 'test_nickname2',
        }
        member, is_created = Member.objects.get_or_create_member_by_token(token, provider)

        # Then:
        self.assertFalse(is_created)
        self.assertEqual(member.username, 'test_id')
        self.assertEqual(member.member_provider_id, provider)
        self.assertEqual(member.member_type_id, MemberTypeEnum.NORMAL_MEMBER.value)
        self.assertEqual(member.member_status_id, MemberStatusEnum.NORMAL_MEMBER.value)
        # And: 처음에 만들었던 것으로 반환
        self.assertEqual(member.email, 'test_email')
        self.assertEqual(member.nickname, 'test_nickname')

    @patch('member.managers.SocialLoginHandler.validate')
    def test_get_member_by_token_when_member_exists(self, mock_validate):
        # Given:
        token = 'test_token'
        provider = 3
        # And: member 생성
        Member.objects.create_user(
            username='test_id',
            member_provider_id=provider,
            member_type_id=MemberTypeEnum.NORMAL_MEMBER.value,
            member_status_id=MemberStatusEnum.NORMAL_MEMBER.value,
            email='test_email',
            nickname='test_nickname',
        )
        # And: validate 결과 값 모킹
        mock_validate.return_value = {
            'id': 'test_id',
            'email': 'test_email',
            'nickname': 'test_nickname',
        }

        # When: get_member_by_token
        member = Member.objects.get_member_by_token(token, provider)

        # Then:
        self.assertIsInstance(member, Member)
        self.assertEqual(member.username, 'test_id')
        self.assertEqual(member.member_provider_id, provider)

    @patch('member.managers.SocialLoginHandler.validate')
    def test_get_member_by_token_when_member_not_exists(self, mock_validate):
        # Given:
        token = 'test_token'
        provider = 3
        # And: member 제거
        # And: validate 결과 값 모킹
        mock_validate.return_value = {
            'id': 'test_id',
            'email': 'test_email',
            'nickname': 'test_nickname',
        }

        # When: get_member_by_token
        member = Member.objects.get_member_by_token(token, provider)

        # Then:
        self.assertEqual(member, None)
