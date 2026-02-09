from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from typing import Optional
import re
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.post import PostCache
from app.models.backup import BackupLog
from app.services.velog import VelogService

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
    email_notification_enabled: bool

    class Config:
        from_attributes = True


class UserSettingsUpdate(BaseModel):
    github_repo: Optional[str] = None
    github_sync_enabled: Optional[bool] = None
    email_notification_enabled: Optional[bool] = None


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """현재 로그인한 사용자 정보"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "username": current_user.github_login,
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
        "email_notification_enabled": current_user.email_notification_enabled or False,
    }


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
