from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from typing import Optional
import io


class GoogleDriveService:
    """Google Drive API 서비스"""

    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.appdata'
    ]

    def __init__(self, access_token: str, refresh_token: str):
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            scopes=self.SCOPES
        )
        self.service = build('drive', 'v3', credentials=self.credentials)

    def create_backup_folder(self, folder_name: str = "Velog Backup") -> str:
        """백업용 폴더 생성"""
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        try:
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()

            return folder.get('id')

        except Exception as e:
            print(f"Error creating folder: {e}")
            raise

    def get_or_create_folder(self, folder_name: str = "Velog Backup") -> str:
        """폴더가 존재하면 가져오고, 없으면 생성"""
        try:
            # 폴더 검색
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()

            folders = results.get('files', [])

            if folders:
                return folders[0]['id']
            else:
                return self.create_backup_folder(folder_name)

        except Exception as e:
            print(f"Error getting/creating folder: {e}")
            raise

    def upload_file(
        self,
        filename: str,
        content: str,
        folder_id: Optional[str] = None,
        mime_type: str = 'text/markdown'
    ) -> str:
        """파일 업로드"""
        file_metadata = {'name': filename}

        if folder_id:
            file_metadata['parents'] = [folder_id]

        # 같은 이름의 파일이 있는지 확인
        existing_file_id = self.find_file(filename, folder_id)

        try:
            media = MediaInMemoryUpload(
                content.encode('utf-8'),
                mimetype=mime_type,
                resumable=True
            )

            if existing_file_id:
                # 파일 업데이트
                file = self.service.files().update(
                    fileId=existing_file_id,
                    media_body=media
                ).execute()
            else:
                # 새 파일 생성
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()

            return file.get('id')

        except Exception as e:
            print(f"Error uploading file {filename}: {e}")
            raise

    def find_file(self, filename: str, folder_id: Optional[str] = None) -> Optional[str]:
        """파일 검색"""
        try:
            query = f"name='{filename}' and trashed=false"
            if folder_id:
                query += f" and '{folder_id}' in parents"

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()

            files = results.get('files', [])
            return files[0]['id'] if files else None

        except Exception as e:
            print(f"Error finding file: {e}")
            return None

    def delete_file(self, file_id: str):
        """파일 삭제"""
        try:
            self.service.files().delete(fileId=file_id).execute()
        except Exception as e:
            print(f"Error deleting file: {e}")
            raise

    def list_files(self, folder_id: Optional[str] = None) -> list:
        """폴더 내 파일 목록 조회"""
        try:
            query = "trashed=false"
            if folder_id:
                query += f" and '{folder_id}' in parents"

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, createdTime, modifiedTime)'
            ).execute()

            return results.get('files', [])

        except Exception as e:
            print(f"Error listing files: {e}")
            return []
