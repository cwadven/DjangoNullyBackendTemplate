from unittest.mock import patch

from common.models import (
    BlackListSection,
    BlackListWord,
)
from django.test import TestCase
from member.models import (
    Member,
    MemberExtraLink,
    MemberInformation,
)
from member.services import (
    check_email_exists,
    check_nickname_exists,
    check_nickname_valid,
    check_only_alphanumeric,
    check_only_korean_english_alphanumeric,
    check_username_exists,
    get_active_member_extra_link_qa,
    get_active_member_information_qs,
)


class MemberCheckMemberInfoTestCase(TestCase):
    def setUp(self):
        pass

    def test_check_username_exists_should_return_true_when_username_exists(self):
        # Given: test 라는 이름을 가진 Member 생성
        Member.objects.create_user(username='test')

        # Expected:
        self.assertEqual(check_username_exists('test'), True)

    def test_check_username_exists_should_return_false_when_username_not_exists(self):
        # Expected:
        self.assertEqual(check_username_exists('test'), False)

    def test_check_nickname_exists_should_return_true_when_username_exists(self):
        # Given: test 라는 nickname 을 가진 Member 생성
        Member.objects.create_user(username='aaaa', nickname='test')

        # Expected:
        self.assertEqual(check_nickname_exists('test'), True)

    def test_check_nickname_exists_should_return_false_when_username_not_exists(self):
        # Expected:
        self.assertEqual(check_nickname_exists('test'), False)

    def test_check_email_exists_should_return_true_when_username_exists(self):
        # Given: test 라는 email 을 가진 Member 생성
        Member.objects.create_user(username='aaaa', email='test@naver.com')

        # Expected:
        self.assertEqual(check_email_exists('test@naver.com'), True)

    def test_check_email_exists_should_return_false_when_username_not_exists(self):
        # Expected:
        self.assertEqual(check_email_exists('test@naver.com'), False)

    def test_check_nickname_valid_when_valid(self):
        # Given: test 라는 nickname 을 가진 Member 생성
        # Expected:
        self.assertEqual(check_nickname_valid('test'), True)

    def test_check_nickname_valid_when_invalid(self):
        # Given: test 라는 nickname 을 가진 Member 생성
        black_list_section, _ = BlackListSection.objects.get_or_create(
            name='닉네임',
            defaults={
                'description': '닉네임 블랙리스트',
            }
        )
        BlackListWord.objects.get_or_create(
            black_list_section=black_list_section,
            wording='test',
        )

        # Expected:
        self.assertEqual(check_nickname_valid('123test'), False)


class CheckRegexTestCase(TestCase):
    def test_check_only_alphanumeric(self):
        self.assertEqual(check_only_alphanumeric("abc123"), True)
        self.assertEqual(check_only_alphanumeric("abc@123"), False)
        self.assertEqual(check_only_alphanumeric("한글123"), False)

    def test_check_only_korean_english_alphanumeric(self):
        self.assertEqual(check_only_korean_english_alphanumeric("안녕abc123"), True)
        self.assertEqual(check_only_korean_english_alphanumeric("안녕abc@123"), False)
        self.assertEqual(check_only_korean_english_alphanumeric("가나다ABC123"), True)


class GetActiveMemberInformationQuerySetTestCase(TestCase):

    def setUp(self):
        self.member1 = Member.objects.create_user(username='test1', nickname='test1')
        self.member_information1 = MemberInformation.objects.create(
            member=self.member1,
            description='test1',
        )
        self.member_information2 = MemberInformation.objects.create(
            member=self.member1,
            description='test2',
        )

    @patch('member.services.MemberInformation.objects.filter')
    def test_get_active_member_information_qs(self,
                                              mock_filter):
        # Given:
        # When:
        get_active_member_information_qs(self.member1.id)

        # Then: Assert that MemberInformation.objects.filter is called with the correct data
        mock_filter.assert_called_once_with(
            member_id=self.member1.id, is_deleted=False
        )


class GetActiveMemberExtraLinkQuerySetTestCase(TestCase):
    def setUp(self):
        self.member1 = Member.objects.create_user(username='test1', nickname='test1')
        self.member_extra_link1 = MemberExtraLink.objects.create(
            member=self.member1,
            description='test1',
        )
        self.member_extra_link2 = MemberExtraLink.objects.create(
            member=self.member1,
            description='test2',
        )

    @patch('member.services.MemberExtraLink.objects.filter')
    def test_get_active_member_extra_link_qa(self,
                                             mock_filter):
        # Given:
        # When:
        get_active_member_extra_link_qa(self.member1.id)

        # Then: Assert that MemberInformation.objects.filter is called with the correct data
        mock_filter.assert_called_once_with(
            member_id=self.member1.id, is_deleted=False
        )
