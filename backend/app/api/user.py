from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.velog import VelogService

router = APIRouter()


class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    picture: Optional[str]
    velog_username: Optional[str]
    has_google_drive: bool

    class Config:
        from_attributes = True


class VelogUsernameRequest(BaseModel):
    username: str


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """현재 로그인한 사용자 정보"""
    return {
        **current_user.__dict__,
        "has_google_drive": bool(current_user.google_access_token)
    }


@router.post("/velog/verify")
async def verify_velog(
    request: VelogUsernameRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Velog 사용자명 확인 및 저장"""
    # @ 제거
    username = request.username.lstrip('@')

    # Velog 사용자명 검증
    is_valid = await VelogService.verify_username(username)

    if not is_valid:
        raise HTTPException(
            status_code=404,
            detail="Velog 사용자를 찾을 수 없습니다"
        )

    # 사용자 정보 업데이트
    current_user.velog_username = username
    db.commit()

    return {"message": "Velog 계정이 연동되었습니다", "username": username}
