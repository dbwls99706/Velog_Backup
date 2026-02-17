import time
import base64
import logging

import httpx
from jose import jwt

from app.core.config import settings

logger = logging.getLogger(__name__)


class GitHubAppService:
    """GitHub App 인증 서비스 (installation access token 발급)"""

    API_BASE = "https://api.github.com"

    @staticmethod
    def _get_private_key() -> str:
        """환경변수에서 PEM 개인키를 가져온다 (base64 인코딩 지원)."""
        raw = settings.GITHUB_APP_PRIVATE_KEY or ""
        if raw.startswith("-----BEGIN"):
            return raw
        return base64.b64decode(raw).decode("utf-8")

    @staticmethod
    def _create_app_jwt() -> str:
        """GitHub App JWT 생성 (RS256, 유효기간 10분)."""
        now = int(time.time())
        payload = {
            "iat": now - 60,
            "exp": now + 600,
            "iss": settings.GITHUB_APP_ID,
        }
        private_key = GitHubAppService._get_private_key()
        return jwt.encode(payload, private_key, algorithm="RS256")

    @staticmethod
    async def get_installation_token(installation_id: int) -> str:
        """installation_id로 단기 access token을 발급받는다."""
        app_jwt = GitHubAppService._create_app_jwt()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GitHubAppService.API_BASE}/app/installations/{installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {app_jwt}",
                    "Accept": "application/vnd.github.v3+json",
                },
                timeout=10.0,
            )
            resp.raise_for_status()
            return resp.json()["token"]

    @staticmethod
    async def list_installation_repos(installation_id: int) -> list[dict]:
        """설치된 App이 접근 가능한 레포지토리 목록 반환."""
        token = await GitHubAppService.get_installation_token(installation_id)
        repos = []
        page = 1
        async with httpx.AsyncClient() as client:
            while True:
                resp = await client.get(
                    f"{GitHubAppService.API_BASE}/installation/repositories?per_page=100&page={page}",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/vnd.github.v3+json",
                    },
                    timeout=10.0,
                )
                resp.raise_for_status()
                data = resp.json()
                for r in data["repositories"]:
                    repos.append({
                        "name": r["name"],
                        "full_name": r["full_name"],
                        "private": r["private"],
                        "description": r.get("description", ""),
                    })
                if len(repos) >= data["total_count"]:
                    break
                page += 1
        return repos

    @staticmethod
    async def get_user_installation(github_id: str) -> int | None:
        """App JWT로 설치 목록을 조회하고 사용자의 GitHub ID와 매칭한다."""
        app_jwt = GitHubAppService._create_app_jwt()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GitHubAppService.API_BASE}/app/installations",
                headers={
                    "Authorization": f"Bearer {app_jwt}",
                    "Accept": "application/vnd.github.v3+json",
                },
                timeout=10.0,
            )
            if resp.status_code != 200:
                logger.warning(
                    "GitHub /app/installations returned %d: %s",
                    resp.status_code,
                    resp.text[:500],
                )
                return None
            installations = resp.json()
            for inst in installations:
                account = inst.get("account", {})
                if str(account.get("id")) == github_id:
                    return inst["id"]
            logger.info(
                "No installation matched github_id=%s among %d installations",
                github_id,
                len(installations),
            )
        return None

    @staticmethod
    def is_configured() -> bool:
        """GitHub App 설정이 완료되었는지 확인."""
        return bool(
            settings.GITHUB_APP_ID
            and settings.GITHUB_APP_PRIVATE_KEY
            and settings.GITHUB_APP_NAME
        )
