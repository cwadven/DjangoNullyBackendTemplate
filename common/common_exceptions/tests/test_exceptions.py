from common.common_exceptions import (
    CommonAPIException,
    PydanticAPIException,
)
from common.common_pydantic.custom_error_messages import ERROR_MESSAGE_CONVERSION
from django.test import TestCase
from rest_framework.exceptions import ErrorDetail


class PydanticAPIExceptionTest(TestCase):
    def test_format_errors_with_valid_errors(self):
        # Given: valid errors
        errors = [
            {
                'type': 'value_error',
                'loc': ('experience',),
                'msg': 'Value error, None is not a valid ProjectJobExperienceType',
                'input': None,
                'ctx': {'error': ValueError('None is not a valid ProjectJobExperienceType')},
                'url': 'https://errors.pydantic.dev/2.4/v/value_error'
            }
        ]

        # When: format_errors 함수 실행
        formatted_errors = PydanticAPIException.format_errors(errors)

        # Then: 정상적으로 포맷팅된 에러 반환
        expected_errors = {
            'experience': ['None is not a valid ProjectJobExperienceType']
        }
        self.assertEqual(formatted_errors, expected_errors)

    def test_format_errors_custom_error_message_mapper(self):
        # Given: valid errors
        for key, value in ERROR_MESSAGE_CONVERSION.items():
            errors = [
                {
                    'type': 'value_error',
                    'loc': ('experience',),
                    'msg': f'Value error, {key}',
                    'input': None,
                    'ctx': {'error': ValueError('None is not a valid ProjectJobExperienceType')},
                    'url': 'https://errors.pydantic.dev/2.4/v/value_error'
                }
            ]

            # When: format_errors 함수 실행
            formatted_errors = PydanticAPIException.format_errors(errors)

            # Then: 정상적으로 포맷팅된 에러 반환
            expected_errors = {
                'experience': [value]
            }
            self.assertEqual(formatted_errors, expected_errors)

    def test_format_errors_with_no_errors(self):
        # Given: no errors
        errors = None

        # When: format_errors 함수 실행
        formatted_errors = PydanticAPIException.format_errors(errors)

        # Then: None 반환
        self.assertIsNone(formatted_errors)

    def test_exception_initialization_with_errors(self):
        # Given: valid errors
        status_code = 400
        detail = "A validation error occurred."
        code = "validation_error"
        errors = [
            {
                'type': 'value_error',
                'loc': ('experience',),
                'msg': 'Value error, None is not a valid ProjectJobExperienceType',
                'input': None,
                'ctx': {'error': ValueError('None is not a valid ProjectJobExperienceType')},
                'url': 'https://errors.pydantic.dev/2.4/v/value_error'
            }
        ]

        # When: PydanticAPIException 객체 생성
        exception = PydanticAPIException(status_code, detail, code, errors)

        # Then: 정상적으로 객체 생성
        expected_errors = {
            'experience': ['None is not a valid ProjectJobExperienceType']
        }
        self.assertEqual(exception.status_code, status_code)
        self.assertEqual(exception.default_detail, detail)
        self.assertEqual(exception.default_code, code)
        self.assertEqual(exception.errors, expected_errors)
        self.assertEqual(exception.detail, ErrorDetail(detail, code))

    def test_exception_initialization_without_errors(self):
        # Given: no errors
        status_code = 400
        detail = "A validation error occurred."
        code = "validation_error"
        errors = None

        # When: PydanticAPIException 객체 생성
        exception = PydanticAPIException(status_code, detail, code, errors)

        # Then: 정상적으로 객체 생성
        self.assertEqual(exception.status_code, status_code)
        self.assertEqual(exception.default_detail, detail)
        self.assertEqual(exception.default_code, code)
        self.assertIsNone(exception.errors)
        self.assertEqual(exception.detail, ErrorDetail(detail, code))


class CommonAPIExceptionTest(TestCase):
    def test_common_api_exception_initialization(self):
        # Given
        status_code = 400
        error_summary = '잘못된 요청입니다.'
        error_code = 'bad-request'
        errors = {
            'field1': ['error1', 'error2'],
            'field2': ['error3']
        }

        # When
        exception = CommonAPIException(status_code, error_summary, error_code, errors)

        # Then
        self.assertEqual(exception.status_code, status_code)
        self.assertEqual(exception.default_detail, error_summary)
        self.assertEqual(exception.default_code, error_code)
        self.assertEqual(exception.errors, errors)

    def test_common_api_exception_initialization_without_errors(self):
        # Given
        status_code = 404
        error_summary = '리소스를 찾을 수 없습니다.'
        error_code = 'not-found'

        # When
        exception = CommonAPIException(status_code, error_summary, error_code)

        # Then
        self.assertEqual(exception.status_code, status_code)
        self.assertEqual(exception.default_detail, error_summary)
        self.assertEqual(exception.default_code, error_code)
        self.assertIsNone(exception.errors)

    def test_common_api_exception_default_values(self):
        # Given
        status_code = 500
        error_summary = '서버 오류입니다.'
        error_code = 'server-error'

        # When
        exception = CommonAPIException(status_code, error_summary, error_code)

        # Then
        self.assertEqual(exception.status_code, status_code)
        self.assertEqual(exception.default_detail, error_summary)
        self.assertEqual(exception.default_code, error_code)
        self.assertIsNone(exception.errors)

    def test_common_api_exception_none_value(self):
        # Given:
        # When
        exception = CommonAPIException()

        # Then
        self.assertEqual(exception.status_code, CommonAPIException.status_code)
        self.assertEqual(exception.default_detail, CommonAPIException.default_detail)
        self.assertEqual(exception.default_code, CommonAPIException.default_code)
        self.assertIsNone(exception.errors)
