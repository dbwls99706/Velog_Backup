from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from typing import Optional
import re

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


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """현재 로그인한 사용자 정보"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "picture": current_user.picture,
        "velog_username": current_user.velog_username,
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
