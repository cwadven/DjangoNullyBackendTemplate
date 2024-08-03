from common.common_consts.common_error_messages import ErrorMessage
from django.test import TestCase
from member.dtos.request_dtos import SocialSignUpRequest
from pydantic import ValidationError


class SocialSignUpRequestTest(TestCase):
    def setUp(self):
        self.payload = {
            'token': 'test_token',
            'provider': 1,
            'jobs_info': None,
        }

    def test_check_jobs_info_value_should_not_raise_error(self):
        # Given:
        # When: SocialSignUpRequest.of
        social_sign_up = SocialSignUpRequest.of(self.payload)

        # Then: Validate the error details
        self.assertEqual(social_sign_up.token, 'test_token')
        self.assertEqual(social_sign_up.provider, 1)
        self.assertEqual(social_sign_up.jobs_info, None)

    def test_check_jobs_info_value_should_raise_error_when_invalid_length(self):
        # Given: jobs length is 0
        self.payload['jobs_info'] = []

        # When: Expecting a ValidationError to be raised
        with self.assertRaises(ValidationError) as context:
            SocialSignUpRequest.of(self.payload)

        # Then: Validate the error details
        errors = context.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['loc'], ('jobs_info',))
        self.assertEqual(
            errors[0]['msg'].split(',')[1].strip(),
            ErrorMessage.INVALID_MINIMUM_ITEM_SIZE.label.format(1),
        )

    def test_check_jobs_info_value_should_raise_error_when_invalid_values(self):
        # Given: jobs invalid keys
        self.payload['jobs_info'] = [
            {'invalid': 10},
            {'invalid': 10},
        ]

        # When: Expecting a ValidationError to be raised
        with self.assertRaises(ValidationError) as context:
            SocialSignUpRequest.of(self.payload)

        # Then: Validate the error details
        errors = context.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['loc'], ('jobs_info',))
        self.assertEqual(
            errors[0]['msg'].split(',')[1].strip(),
            ErrorMessage.INVALID_INPUT_ERROR_MESSAGE.label,
        )
