from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from typing import Optional
import re
import logging

import httpx

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.post import PostCache
from app.models.backup import BackupLog
from app.services.velog import VelogService
from app.services.github_app import GitHubAppService

logger = logging.getLogger(__name__)

router = APIRouter()


class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    username: Optional[str]
    picture: Optional[str]
    velog_username: Optional[str]
    github_repo: Optional[str]

    class Config:
        from_attributes = True


class VelogUsernameRequest(BaseModel):
    username: str

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip().lstrip('@')
        if not v:
            raise ValueError('사용자명을 입력해주세요')
        if len(v) > 50:
            raise ValueError('사용자명이 너무 깁니다')
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('사용자명은 영문, 숫자, _, -만 사용할 수 있습니다')
        return v


class UserSettingsResponse(BaseModel):
    github_repo: Optional[str]
    github_sync_enabled: bool
    github_installed: bool = False
    email_notification_enabled: bool

    class Config:
        from_attributes = True


class UserSettingsUpdate(BaseModel):
    github_repo: Optional[str] = None
    github_sync_enabled: Optional[bool] = None
    email_notification_enabled: Optional[bool] = None

    @field_validator('github_repo')
    @classmethod
    def validate_github_repo(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            return v
        if len(v) > 100:
            raise ValueError('Repository 이름이 너무 깁니다')
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError('Repository 이름은 영문, 숫자, ., -, _만 사용할 수 있습니다')
        return v


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """현재 로그인한 사용자 정보"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "username": current_user.name,
        "picture": current_user.picture,
        "velog_username": current_user.velog_username,
        "github_repo": current_user.github_repo,
    }


@router.get("/settings", response_model=UserSettingsResponse)
async def get_user_settings(current_user: User = Depends(get_current_active_user)):
    """사용자 설정 조회"""
    return {
        "github_repo": current_user.github_repo,
        "github_sync_enabled": current_user.github_sync_enabled or False,
        "github_installed": bool(current_user.github_installation_id),
        "email_notification_enabled": current_user.email_notification_enabled or False,
    }


@router.put("/settings", response_model=UserSettingsResponse)
async def update_user_settings(
    settings: UserSettingsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """사용자 설정 업데이트"""
    if settings.github_repo is not None:
        current_user.github_repo = settings.github_repo.strip() or None

    if settings.github_sync_enabled is not None:
        current_user.github_sync_enabled = settings.github_sync_enabled

    if settings.email_notification_enabled is not None:
        current_user.email_notification_enabled = settings.email_notification_enabled

    db.commit()
    db.refresh(current_user)

    return {
        "github_repo": current_user.github_repo,
        "github_sync_enabled": current_user.github_sync_enabled or False,
        "github_installed": bool(current_user.github_installation_id),
        "email_notification_enabled": current_user.email_notification_enabled or False,
    }


@router.get("/github/repo/check")
async def check_github_repo(
    name: str,
    current_user: User = Depends(get_current_active_user),
):
    """GitHub Repository 존재 여부 확인"""
    if not current_user.github_access_token:
        raise HTTPException(status_code=400, detail="GitHub 연동이 필요합니다")

    if not name.strip():
        return {"exists": False}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            owner_resp = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {current_user.github_access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            owner_resp.raise_for_status()
            owner = owner_resp.json()["login"]

            repo_resp = await client.get(
                f"https://api.github.com/repos/{owner}/{name.strip()}",
                headers={
                    "Authorization": f"Bearer {current_user.github_access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            if repo_resp.status_code == 200:
                repo_data = repo_resp.json()
                return {
                    "exists": True,
                    "description": repo_data.get("description", ""),
                    "private": repo_data.get("private", False),
                }
            return {"exists": False}
    except Exception as e:
        logger.warning(f"GitHub repo check failed: {e}")
        return {"exists": False}


@router.post("/velog/verify")
async def verify_velog(
    request: VelogUsernameRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Velog 사용자명 확인 및 저장 (수정 가능)"""
    username = request.username.lstrip('@')

    is_valid = await VelogService.verify_username(username)

    if not is_valid:
        raise HTTPException(
            status_code=404,
            detail="Velog 사용자를 찾을 수 없습니다"
        )

    is_update = current_user.velog_username and current_user.velog_username != username

    if is_update:
        deleted_posts = db.query(PostCache).filter(
            PostCache.user_id == current_user.id
        ).count()

        db.query(PostCache).filter(
            PostCache.user_id == current_user.id
        ).delete()

        db.query(BackupLog).filter(
            BackupLog.user_id == current_user.id
        ).delete()

        logger.info(f"User {current_user.id} changed username from '{current_user.velog_username}' to '{username}'. Deleted {deleted_posts} posts.")

    current_user.velog_username = username
    db.commit()

    message = "Velog 계정이 수정되었습니다" if is_update else "Velog 계정이 연동되었습니다"
    return {"message": message, "username": username}


# ── GitHub App 엔드포인트 ──


@router.get("/github/app/install-url")
async def get_github_app_install_url(current_user: User = Depends(get_current_active_user)):
    """GitHub App 설치 URL 반환"""
    if not GitHubAppService.is_configured():
        raise HTTPException(status_code=501, detail="GitHub App이 설정되지 않았습니다")
    url = f"https://github.com/apps/{settings.GITHUB_APP_NAME}/installations/new"
    return {"install_url": url}


@router.post("/github/app/connect")
async def connect_github_app(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """사용자의 GitHub App 설치를 자동 감지하여 연결"""
    if not GitHubAppService.is_configured():
        raise HTTPException(status_code=501, detail="GitHub App이 설정되지 않았습니다")
    if not current_user.github_id:
        raise HTTPException(status_code=400, detail="GitHub 로그인이 필요합니다")

    installation_id = await GitHubAppService.get_user_installation(
        current_user.github_id
    )
    if not installation_id:
        raise HTTPException(
            status_code=404,
            detail="GitHub App 설치를 찾을 수 없습니다. 먼저 App을 설치해주세요.",
        )

    current_user.github_installation_id = installation_id
    db.commit()
    return {"installation_id": installation_id}


@router.get("/github/app/repos")
async def list_github_app_repos(current_user: User = Depends(get_current_active_user)):
    """GitHub App이 접근 가능한 레포지토리 목록"""
    if not current_user.github_installation_id:
        raise HTTPException(status_code=400, detail="GitHub App이 연결되지 않았습니다")
    try:
        repos = await GitHubAppService.list_installation_repos(
            current_user.github_installation_id
        )
        return {"repos": repos}
    except Exception as e:
        logger.warning(f"Failed to list repos: {e}")
        raise HTTPException(status_code=502, detail="레포지토리 목록을 가져올 수 없습니다")


@router.delete("/github/app/disconnect")
async def disconnect_github_app(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """GitHub App 연결 해제"""
    current_user.github_installation_id = None
    current_user.github_sync_enabled = False
    db.commit()
    return {"message": "GitHub App 연결이 해제되었습니다"}
