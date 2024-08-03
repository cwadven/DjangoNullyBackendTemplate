from io import BytesIO
from unittest.mock import (
    Mock,
    patch
)

from PIL import Image
from common.common_utils.openai_utils import generate_ai_image
from django.test import TestCase


class GenerateAIImageTestCase(TestCase):
    @patch('common.common_utils.openai_utils.OpenAI')
    @patch('common.common_utils.openai_utils.requests.get')
    def test_generate_ai_image_when_success(self, mock_requests_get, mock_openai_client):
        # Given: Prompt and size
        prompt = "A beautiful landscape with mountains and rivers"
        size = "1024x1024"
        generated_image_url = "https://fakeurl.com/generated_image.png"

        # And: Mocking OpenAI client response
        mock_response = Mock()
        mock_response.data = [Mock(url=generated_image_url)]
        mock_openai_client.return_value.images.generate.return_value = mock_response

        # And: Mocking requests.get response
        mock_image_response = Mock()
        mock_image_response.status_code = 200
        mock_image_response.content = BytesIO()
        mock_requests_get.return_value = mock_image_response

        # And: Generating a fake image
        image = Image.new('RGB', (1024, 1024), color=(73, 109, 137))
        byte_arr = BytesIO()
        image.save(byte_arr, format='PNG')
        byte_arr = byte_arr.getvalue()
        mock_image_response.content = byte_arr

        # When: Generate AI image
        image_io = generate_ai_image(prompt, size)

        # Then: Check if the image is generated and saved successfully
        self.assertEqual(image_io.getvalue(), mock_image_response.content)
        mock_openai_client.return_value.images.generate.assert_called_once_with(
            model="dall-e-3",
            prompt=prompt + "\n\n위 내용은 프로젝트를 같이할 사람을 모집하기 위한 내용입니다.\n\n내용을 기반으로 자연스러운 메인 이미지를 생성해주세요.\n\n이미지에는 글자가 들어가면 안됩니다.",
            n=1,
            size=size,
            quality="standard",
        )
        mock_requests_get.assert_called_once_with(generated_image_url)
        self.assertEqual(mock_requests_get.return_value.status_code, 200)

    @patch('common.common_utils.openai_utils.OpenAI')
    @patch('common.common_utils.openai_utils.requests.get')
    def test_generate_ai_image_should_return_error_when_invalid_size(self, mock_requests_get, mock_openai_client):
        # Given: Prompt and size
        prompt = "A beautiful landscape with mountains and rivers"
        size = "Invalid Size"

        # When: Generate AI image
        with self.assertRaises(ValueError) as e:
            generate_ai_image(prompt, size)

        # Then: Check if the error is raised
        self.assertEqual(e.exception.args[0], f"Invalid size: {size}")
        mock_openai_client.return_value.images.generate.assert_not_called()
        mock_requests_get.assert_not_called()

    @patch('common.common_utils.openai_utils.OpenAI')
    @patch('common.common_utils.openai_utils.requests.get')
    def test_generate_ai_image_should_return_error_when_image_generate_error(self, mock_requests_get, mock_openai_client):
        # Given: Prompt and size
        prompt = "A beautiful landscape with mountains and rivers"
        size = "1024x1024"
        generated_image_url = "https://fakeurl.com/generated_image.png"

        # And: Mocking OpenAI client response
        mock_response = Mock()
        # And: Attribute Error
        mock_response.data = [{"url": generated_image_url}]
        mock_openai_client.return_value.images.generate.return_value = mock_response

        # When: Generate AI image
        with self.assertRaises(ValueError) as e:
            generate_ai_image(prompt, size)

        # Then: Check if the error is raised
        self.assertEqual(e.exception.args[0], "Image URL Error: 'dict' object has no attribute 'url'")
        mock_openai_client.return_value.images.generate.assert_called_once_with(
            model="dall-e-3",
            prompt=prompt + "\n\n위 내용은 프로젝트를 같이할 사람을 모집하기 위한 내용입니다.\n\n내용을 기반으로 자연스러운 메인 이미지를 생성해주세요.\n\n이미지에는 글자가 들어가면 안됩니다.",
            n=1,
            size=size,
            quality="standard",
        )
        mock_requests_get.assert_not_called()
