from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request as GoogleRequest

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.google_drive import GoogleDriveService

router = APIRouter()


class GoogleAuthRequest(BaseModel):
    code: str


@router.get("/auth-url")
async def get_google_auth_url():
    """Google OAuth URL 생성"""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
            }
        },
        scopes=GoogleDriveService.SCOPES
    )

    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    return {"auth_url": authorization_url, "state": state}


@router.post("/connect")
async def connect_google_drive(
    request: GoogleAuthRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Google Drive 연동"""
    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
                }
            },
            scopes=GoogleDriveService.SCOPES
        )

        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

        # 인증 코드로 토큰 교환
        flow.fetch_token(code=request.code)

        credentials = flow.credentials

        # 사용자 정보 업데이트
        current_user.google_access_token = credentials.token
        current_user.google_refresh_token = credentials.refresh_token
        db.commit()

        # 백업 폴더 생성
        drive = GoogleDriveService(credentials.token, credentials.refresh_token)
        folder_id = drive.get_or_create_backup_folder()

        return {
            "message": "Google Drive가 연동되었습니다",
            "folder_id": folder_id
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google Drive 연동 실패: {str(e)}")


@router.delete("/disconnect")
async def disconnect_google_drive(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Google Drive 연동 해제"""
    current_user.google_access_token = None
    current_user.google_refresh_token = None
    db.commit()

    return {"message": "Google Drive 연동이 해제되었습니다"}
