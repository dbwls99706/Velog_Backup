from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from typing import Optional


class GoogleDriveService:
    """Google Drive API 서비스"""

    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
    ]

    def __init__(self, access_token: str, refresh_token: Optional[str] = None):
        """Google Drive 서비스 초기화"""
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            scopes=self.SCOPES
        )
        self.service = build('drive', 'v3', credentials=self.credentials)

    def get_or_create_backup_folder(self) -> str:
        """백업 폴더 가져오기 또는 생성"""
        folder_name = "Velog Backup"

        # 기존 폴더 검색
        query = (
            f"name='{folder_name}' and "
            f"mimeType='application/vnd.google-apps.folder' and "
            f"trashed=false"
        )

        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()

        folders = results.get('files', [])

        if folders:
            return folders[0]['id']

        # 폴더 생성
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        folder = self.service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()

        return folder['id']

    def upload_or_update_file(
        self,
        filename: str,
        content: str,
        folder_id: str
    ) -> str:
        """파일 업로드 또는 업데이트"""
        # 같은 이름의 파일 검색
        query = (
            f"name='{filename}' and "
            f"'{folder_id}' in parents and "
            f"trashed=false"
        )

        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()

        files = results.get('files', [])

        # Media 생성
        media = MediaInMemoryUpload(
            content.encode('utf-8'),
            mimetype='text/markdown',
            resumable=True
        )

        if files:
            # 기존 파일 업데이트
            file_id = files[0]['id']
            self.service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            return file_id
        else:
            # 새 파일 생성
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            return file['id']

    def list_backup_files(self, folder_id: str) -> list:
        """백업 폴더의 파일 목록 조회"""
        query = f"'{folder_id}' in parents and trashed=false"

        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, createdTime, modifiedTime, size)',
            orderBy='name'
        ).execute()

        return results.get('files', [])
