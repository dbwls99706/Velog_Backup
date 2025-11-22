from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import httpx

from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User

router = APIRouter()


class GitHubCallbackRequest(BaseModel):
    code: str  # GitHub authorization code


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.get("/github/url")
async def get_github_auth_url():
    """GitHub OAuth 인증 URL 반환"""
    auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
        f"&scope=user:email"
    )
    return {"auth_url": auth_url}


@router.post("/github/callback", response_model=TokenResponse)
async def github_callback(request: GitHubCallbackRequest, db: Session = Depends(get_db)):
    """GitHub OAuth 콜백 처리"""
    # GitHub에서 access token 교환
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": request.code,
                "redirect_uri": settings.GITHUB_REDIRECT_URI,
            },
            headers={"Accept": "application/json"}
        )

        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="GitHub 인증 실패")

        token_data = token_response.json()

        if "error" in token_data:
            raise HTTPException(status_code=400, detail=token_data.get("error_description", "GitHub 인증 실패"))

        github_access_token = token_data.get("access_token")

        if not github_access_token:
            raise HTTPException(status_code=400, detail="GitHub 액세스 토큰을 받지 못했습니다")

        # GitHub 사용자 정보 가져오기
        user_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {github_access_token}",
                "Accept": "application/json"
            }
        )

        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="GitHub 사용자 정보를 가져올 수 없습니다")

        github_user = user_response.json()

        # 이메일 가져오기 (private email인 경우)
        email = github_user.get("email")
        if not email:
            email_response = await client.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {github_access_token}",
                    "Accept": "application/json"
                }
            )
            if email_response.status_code == 200:
                emails = email_response.json()
                primary_email = next((e for e in emails if e.get("primary")), None)
                if primary_email:
                    email = primary_email.get("email")

        if not email:
            email = f"{github_user['login']}@github.local"

    github_id = str(github_user["id"])

    # 사용자 조회 또는 생성
    user = db.query(User).filter(User.github_id == github_id).first()

    if not user:
        # 이메일로도 검색 (기존 사용자 연결)
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.github_id = github_id
            user.name = github_user.get("name") or github_user.get("login")
            user.picture = github_user.get("avatar_url")
        else:
            # 새 사용자 생성
            user = User(
                email=email,
                github_id=github_id,
                name=github_user.get("name") or github_user.get("login"),
                picture=github_user.get("avatar_url")
            )
            db.add(user)

        db.commit()
        db.refresh(user)

    # JWT 토큰 생성
    access_token = create_access_token(data={"sub": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
