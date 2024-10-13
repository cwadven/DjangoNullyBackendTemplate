from io import BytesIO
from unittest.mock import patch

from common.common_utils.google_utils.google_drive_utils import (
    GoogleDriveService,
    GoogleDriveServiceGenerator,
)
from django.test import TestCase


class GoogleDriveServiceGeneratorTests(TestCase):
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    @patch('common.common_utils.google_utils.google_drive_utils.build')
    def test_generate_service_success(self,
                                      mock_build,
                                      mock_from_service_account_file):
        # Given: 유효한 account_file_path와 scopes가 있을 때
        account_file_path = 'fake_path_to_credentials.json'
        scopes = ['https://www.googleapis.com/auth/drive.file']
        generator = GoogleDriveServiceGenerator(account_file_path, scopes)

        # When: 서비스 생성 메서드를 호출하면
        service = generator.generate_service()

        # Then: 서비스가 성공적으로 생성되어야 함
        mock_from_service_account_file.assert_called_once_with(
            filename=account_file_path,
            scopes=scopes,
        )
        mock_build.assert_called_once_with('drive', 'v3', credentials=mock_from_service_account_file.return_value)
        self.assertIsNotNone(service)


class GoogleDriveServiceTests(TestCase):
    @patch('googleapiclient.discovery.Resource')
    def test_get_file_list_success(self, mock_service):
        # Given: Google Drive에서 파일 목록을 가져오려고 할 때
        mock_service.files().list().execute.return_value = {
            'files': [
                {'id': 'file_id_1', 'name': 'file_1', 'mimeType': 'application/vnd.google-apps.document'},
                {'id': 'file_id_2', 'name': 'file_2', 'mimeType': 'application/pdf'},
            ]
        }
        service = GoogleDriveService(mock_service)
        query = "mimeType='application/pdf'"

        # When: 파일 목록을 요청하면
        file_list = service.get_file_list(query=query)

        # Then: 결과로 2개의 파일이 반환되어야 함
        self.assertEqual(len(file_list), 2)
        self.assertEqual(file_list[0]['id'], 'file_id_1')
        self.assertEqual(file_list[1]['name'], 'file_2')

    @patch('googleapiclient.discovery.Resource')
    @patch('common.common_utils.google_utils.google_drive_utils.MediaFileUpload')
    def test_upload_file_by_file_path_success(self, mock_media_upload, mock_service):
        # Given: 유효한 파일 경로와 업로드 대상 Google Drive 폴더가 있을 때
        mock_service.files().create().execute.return_value = {'id': 'uploaded_file_id'}
        service = GoogleDriveService(mock_service)
        file_name = 'test_file.txt'
        file_path = '/fake/path/test_file.txt'
        upload_folder_id = 'fake_folder_id'

        # When: 파일을 업로드하면
        file_id = service.upload_file_by_file_path(file_name, file_path, upload_folder_id)

        # Then: 반환된 파일 ID가 기대한 값이어야 함
        self.assertEqual(file_id, 'uploaded_file_id')

    @patch('googleapiclient.discovery.Resource')
    @patch('common.common_utils.google_utils.google_drive_utils.MediaIoBaseUpload')
    def test_upload_file_by_file_obj_success(self, mock_media_upload, mock_service):
        # Given: 파일 객체와 업로드 대상 Google Drive 폴더가 있을 때
        mock_service.files().create().execute.return_value = {'id': 'uploaded_file_id'}
        service = GoogleDriveService(mock_service)
        file_obj = BytesIO(b"test content")
        file_obj.name = 'test_file.txt'
        upload_folder_id = 'fake_folder_id'

        # When: 파일 객체를 업로드하면
        file_id = service.upload_file_by_file_obj(file_obj, upload_folder_id)

        # Then: 반환된 파일 ID가 기대한 값이어야 함
        self.assertEqual(file_id, 'uploaded_file_id')

    @patch('googleapiclient.discovery.Resource')
    def test_delete_file_success(self, mock_service):
        # Given: 삭제하려는 파일 ID가 있을 때
        service = GoogleDriveService(mock_service)
        file_id = 'fake_file_id'

        # When: 파일을 삭제 요청하면
        service.delete_file(file_id)

        # Then: 파일이 성공적으로 삭제되어야 함
        mock_service.files().delete.assert_called_once_with(fileId=file_id)
