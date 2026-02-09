import httpx
import base64
import json
import logging
from typing import List, Optional
from datetime import datetime

from app.services.markdown import MarkdownService
from app.services.image import ImageService

logger = logging.getLogger(__name__)


class GitHubSyncService:
    """GitHub Repository 동기화 서비스"""

    API_BASE = "https://api.github.com"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def _get_authenticated_user(self) -> str:
        """인증된 GitHub 사용자명 반환"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.API_BASE}/user", headers=self.headers)
            resp.raise_for_status()
            return resp.json()["login"]

    async def _ensure_repo_exists(self, repo_name: str, owner: str) -> bool:
        """Repository가 존재하는지 확인하고, 없으면 생성"""
        async with httpx.AsyncClient() as client:
            # 존재 확인
            resp = await client.get(
                f"{self.API_BASE}/repos/{owner}/{repo_name}",
                headers=self.headers
            )

            if resp.status_code == 200:
                return True

            # 생성
            resp = await client.post(
                f"{self.API_BASE}/user/repos",
                headers=self.headers,
                json={
                    "name": repo_name,
                    "description": "Velog Backup - 자동 백업된 블로그 포스트",
                    "private": False,
                    "auto_init": True,
                }
            )
            resp.raise_for_status()
            return True

    async def _get_file_sha(self, owner: str, repo: str, path: str) -> Optional[str]:
        """기존 파일의 SHA 조회 (업데이트 시 필요)"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.API_BASE}/repos/{owner}/{repo}/contents/{path}",
                headers=self.headers
            )
            if resp.status_code == 200:
                return resp.json().get("sha")
            return None

    async def _create_or_update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: bytes,
        message: str,
        sha: Optional[str] = None
    ):
        """파일 생성 또는 업데이트"""
        data = {
            "message": message,
            "content": base64.b64encode(content).decode("utf-8"),
        }
        if sha:
            data["sha"] = sha

        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"{self.API_BASE}/repos/{owner}/{repo}/contents/{path}",
                headers=self.headers,
                json=data,
                timeout=30.0
            )
            resp.raise_for_status()

    async def sync_posts(self, repo_name: str, posts: List, velog_username: str):
        """모든 포스트를 GitHub Repository에 동기화"""
        owner = await self._get_authenticated_user()
        await self._ensure_repo_exists(repo_name, owner)

        # 중복 폴더명 처리
        folder_names = {}
        synced = 0

        for post in posts:
            try:
                folder_name = MarkdownService.generate_folder_name(post.title)

                if folder_name in folder_names:
                    folder_names[folder_name] += 1
                    folder_name = f"{folder_name} ({folder_names[folder_name]})"
                else:
                    folder_names[folder_name] = 1

                content = post.content or ""
                file_path = f"posts/{folder_name}/index.md"

                # 기존 파일 SHA 확인
                sha = await self._get_file_sha(owner, repo_name, file_path)

                # 마크다운 업로드
                await self._create_or_update_file(
                    owner=owner,
                    repo=repo_name,
                    path=file_path,
                    content=content.encode("utf-8"),
                    message=f"backup: {post.title}",
                    sha=sha
                )

                # 이미지 업로드
                images = ImageService.extract_image_urls(content)
                for index, (full_match, alt_text, url) in enumerate(images, 1):
                    try:
                        img_data = await ImageService.download_image(url)
                        if img_data:
                            img_filename = ImageService.get_image_filename(url, index)
                            img_path = f"posts/{folder_name}/images/{img_filename}"
                            img_sha = await self._get_file_sha(owner, repo_name, img_path)
                            await self._create_or_update_file(
                                owner=owner,
                                repo=repo_name,
                                path=img_path,
                                content=img_data,
                                message=f"backup: image for {post.title}",
                                sha=img_sha
                            )
                    except Exception as e:
                        logger.warning(f"Failed to sync image for {post.title}: {e}")

                synced += 1

            except Exception as e:
                logger.error(f"Failed to sync post {post.title}: {e}")

        # README 업데이트
        await self._update_readme(owner, repo_name, posts, velog_username, synced)

        logger.info(f"GitHub sync complete: {synced}/{len(posts)} posts synced to {owner}/{repo_name}")

    async def _update_readme(self, owner: str, repo: str, posts: List, velog_username: str, synced: int):
        """README.md 자동 생성/업데이트"""
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        lines = [
            f"# Velog Backup - @{velog_username}",
            "",
            f"> 자동 백업 by [Velog Backup](https://velog-backup.vercel.app)",
            f"> 마지막 동기화: {now}",
            f"> 총 {len(posts)}개 포스트 | {synced}개 동기화",
            "",
            "## 포스트 목록",
            "",
        ]

        for post in sorted(posts, key=lambda p: p.velog_published_at or datetime.min, reverse=True):
            folder_name = MarkdownService.generate_folder_name(post.title)
            date_str = ""
            if post.velog_published_at:
                date_str = f" ({post.velog_published_at.strftime('%Y-%m-%d')})"
            lines.append(f"- [{post.title}](posts/{folder_name}/index.md){date_str}")

        readme_content = "\n".join(lines) + "\n"

        sha = await self._get_file_sha(owner, repo, "README.md")
        await self._create_or_update_file(
            owner=owner,
            repo=repo,
            path="README.md",
            content=readme_content.encode("utf-8"),
            message=f"backup: update README ({now})",
            sha=sha
        )
