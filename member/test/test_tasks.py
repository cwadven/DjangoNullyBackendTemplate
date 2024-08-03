from unittest.mock import patch

from django.test import TestCase
from member.tasks import send_welcome_email


class EmailTestCase(TestCase):
    @patch('member.tasks.send_email')
    def test_send_welcome_email_with_nickname(self, mock_send_email):
        # Given
        email = 'test@example.com'
        nickname = 'John'

        # When
        send_welcome_email(email, nickname)

        # Then
        mock_send_email.assert_called_once_with(
            '회원가입을 환영합니다.',
            'email/member/welcome_member.html',
            {'body': f'{nickname} 님 진심으로 환영합니다~!', 'message': '많은 밈을 확인해보세요!'},
            [email]
        )

    @patch('member.tasks.send_email')
    def test_send_welcome_email_without_nickname(self, mock_send_email):
        # Given
        email = 'test@example.com'

        # When
        send_welcome_email(email)

        # Then
        mock_send_email.assert_called_once_with(
            '회원가입을 환영합니다.',
            'email/member/welcome_member.html',
            {'body': '사용자 님 진심으로 환영합니다~!', 'message': '많은 밈을 확인해보세요!'},
            [email]
        )
