from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any
from authlib.integrations.requests_client import OAuth2Session

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.integration import UserIntegration
from app.schemas.integration import (
    IntegrationResponse,
    IntegrationUpdate,
    GoogleDriveConnect,
    GitHubConnect
)
from app.services.google_drive import GoogleDriveService
from app.services.github_service import GitHubService

router = APIRouter()


@router.get("/", response_model=IntegrationResponse)
def get_integrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """사용자 연동 정보 조회"""
    integration = db.query(UserIntegration).filter(
        UserIntegration.user_id == current_user.id
    ).first()

    if not integration:
        # 연동 정보가 없으면 생성
        integration = UserIntegration(user_id=current_user.id)
        db.add(integration)
        db.commit()
        db.refresh(integration)

    return integration


@router.patch("/", response_model=IntegrationResponse)
def update_integrations(
    integration_data: IntegrationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """연동 설정 업데이트"""
    integration = db.query(UserIntegration).filter(
        UserIntegration.user_id == current_user.id
    ).first()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration settings not found"
        )

    # 업데이트
    update_data = integration_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(integration, field, value)

    db.commit()
    db.refresh(integration)

    return integration


@router.get("/google-drive/auth-url")
def get_google_drive_auth_url(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Google Drive OAuth URL 생성"""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )

    oauth = OAuth2Session(
        settings.GOOGLE_CLIENT_ID,
        settings.GOOGLE_CLIENT_SECRET,
        scope=GoogleDriveService.SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )

    authorization_url, state = oauth.create_authorization_url(
        'https://accounts.google.com/o/oauth2/auth',
        access_type='offline',
        prompt='consent'
    )

    return {"auth_url": authorization_url, "state": state}


@router.post("/google-drive/connect")
def connect_google_drive(
    connect_data: GoogleDriveConnect,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Google Drive 연동"""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )

    try:
        # OAuth 토큰 교환
        oauth = OAuth2Session(
            settings.GOOGLE_CLIENT_ID,
            settings.GOOGLE_CLIENT_SECRET,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )

        token = oauth.fetch_token(
            'https://oauth2.googleapis.com/token',
            code=connect_data.code
        )

        # 연동 정보 저장
        integration = db.query(UserIntegration).filter(
            UserIntegration.user_id == current_user.id
        ).first()

        if not integration:
            integration = UserIntegration(user_id=current_user.id)
            db.add(integration)

        integration.google_access_token = token['access_token']
        integration.google_refresh_token = token.get('refresh_token')
        integration.google_drive_enabled = True

        # 백업 폴더 생성
        drive_service = GoogleDriveService(
            token['access_token'],
            token.get('refresh_token')
        )
        folder_id = drive_service.get_or_create_folder("Velog Backup")
        integration.google_folder_id = folder_id

        db.commit()

        return {"message": "Google Drive connected successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect Google Drive: {str(e)}"
        )


@router.delete("/google-drive/disconnect")
def disconnect_google_drive(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Google Drive 연동 해제"""
    integration = db.query(UserIntegration).filter(
        UserIntegration.user_id == current_user.id
    ).first()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )

    integration.google_drive_enabled = False
    integration.google_access_token = None
    integration.google_refresh_token = None
    integration.google_folder_id = None

    db.commit()

    return {"message": "Google Drive disconnected"}


@router.get("/github/auth-url")
def get_github_auth_url(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """GitHub OAuth URL 생성"""
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth not configured"
        )

    auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
        f"&scope=repo"
    )

    return {"auth_url": auth_url}


@router.post("/github/connect")
def connect_github(
    connect_data: GitHubConnect,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """GitHub 연동"""
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth not configured"
        )

    try:
        # OAuth 토큰 교환
        import requests
        response = requests.post(
            'https://github.com/login/oauth/access_token',
            headers={'Accept': 'application/json'},
            data={
                'client_id': settings.GITHUB_CLIENT_ID,
                'client_secret': settings.GITHUB_CLIENT_SECRET,
                'code': connect_data.code
            }
        )

        token_data = response.json()
        access_token = token_data.get('access_token')

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get access token"
            )

        # GitHub 서비스 초기화
        github_service = GitHubService(access_token)
        user_info = github_service.get_user_info()

        # 저장소 생성
        repo_info = github_service.create_or_get_repo(connect_data.repo_name)

        # README 생성
        github_service.create_readme(connect_data.repo_name)

        # 연동 정보 저장
        integration = db.query(UserIntegration).filter(
            UserIntegration.user_id == current_user.id
        ).first()

        if not integration:
            integration = UserIntegration(user_id=current_user.id)
            db.add(integration)

        integration.github_access_token = access_token
        integration.github_enabled = True
        integration.github_repo_name = repo_info['name']
        integration.github_repo_url = repo_info['url']
        integration.github_username = user_info['username']

        db.commit()

        return {
            "message": "GitHub connected successfully",
            "repo_url": repo_info['url']
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect GitHub: {str(e)}"
        )


@router.delete("/github/disconnect")
def disconnect_github(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """GitHub 연동 해제"""
    integration = db.query(UserIntegration).filter(
        UserIntegration.user_id == current_user.id
    ).first()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )

    integration.github_enabled = False
    integration.github_access_token = None
    integration.github_repo_name = None
    integration.github_repo_url = None
    integration.github_username = None

    db.commit()

    return {"message": "GitHub disconnected"}
