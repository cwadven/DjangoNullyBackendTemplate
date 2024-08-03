from unittest.mock import patch

from common.common_utils.io_utils import send_email
from django.conf import settings
from django.test import TestCase


class EmailSendingTestCase(TestCase):
    @patch('common.common_utils.io_utils.send_mail')
    @patch('common.common_utils.io_utils.render_to_string')
    def test_send_email(self, mock_render_to_string, mock_send_mail):
        # Given: 모킹된 send_mail 함수의 반환값 설정
        mock_send_mail.return_value = 1
        mock_render_to_string.return_value = 'test'
        # And: 테스트 이메일 데이터 설정
        title = 'Test Email'
        html_body_content = 'your_template.html'
        payload = {'variable1': 'value1', 'variable2': 'value2'}
        to = ['test@example.com']

        # When: 이메일 보내기 함수 호출
        send_email(title, html_body_content, payload, to)

        # Then: send_mail 함수가 예상대로 호출되었는지 확인
        mock_send_mail.assert_called_once_with(
            title,
            'test',
            settings.EMAIL_HOST_USER,
            to,
            html_message='test',
            fail_silently=False,
        )
