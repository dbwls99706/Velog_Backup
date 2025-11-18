from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import verify_google_token, create_access_token
from app.models.user import User

router = APIRouter()


class GoogleLoginRequest(BaseModel):
    token: str  # Google ID Token


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/google", response_model=TokenResponse)
async def google_login(request: GoogleLoginRequest, db: Session = Depends(get_db)):
    """Google OAuth 로그인"""
    # Google 토큰 검증
    user_info = verify_google_token(request.token)

    # 사용자 조회 또는 생성
    user = db.query(User).filter(User.google_id == user_info["google_id"]).first()

    if not user:
        # 새 사용자 생성
        user = User(
            email=user_info["email"],
            google_id=user_info["google_id"],
            name=user_info.get("name"),
            picture=user_info.get("picture")
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # JWT 토큰 생성
    access_token = create_access_token(data={"sub": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
