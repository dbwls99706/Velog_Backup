import httpx
import base64
import logging
from typing import List, Optional
from datetime import datetime, timezone

from app.services.markdown import MarkdownService
from app.services.image import ImageService

logger = logging.getLogger(__name__)


class GitHubSyncService:
    """GitHub Repository 동기화 서비스 (Git Tree API - 단일 커밋)"""

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
            resp = await client.get(
                f"{self.API_BASE}/repos/{owner}/{repo_name}",
                headers=self.headers
            )
            if resp.status_code == 200:
                return True

            resp = await client.post(
                f"{self.API_BASE}/user/repos",
                headers=self.headers,
                json={
                    "name": repo_name,
                    "description": "Velog Backup - 자동 백업된 블로그 포스트",
                    "private": True,
                    "auto_init": True,
                }
            )
            resp.raise_for_status()
            return True

    async def _get_default_branch_sha(self, owner: str, repo: str) -> Optional[str]:
        """기본 브랜치의 최신 커밋 SHA 조회"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.API_BASE}/repos/{owner}/{repo}/git/ref/heads/main",
                headers=self.headers
            )
            if resp.status_code == 200:
                return resp.json()["object"]["sha"]

            # main이 없으면 master 시도
            resp = await client.get(
                f"{self.API_BASE}/repos/{owner}/{repo}/git/ref/heads/master",
                headers=self.headers
            )
            if resp.status_code == 200:
                return resp.json()["object"]["sha"]

            return None

    async def _create_blob(self, client: httpx.AsyncClient, owner: str, repo: str, content: bytes, encoding: str = "base64") -> str:
        """Blob 생성 후 SHA 반환"""
        resp = await client.post(
            f"{self.API_BASE}/repos/{owner}/{repo}/git/blobs",
            headers=self.headers,
            json={
                "content": base64.b64encode(content).decode("utf-8"),
                "encoding": encoding,
            },
            timeout=30.0
        )
        resp.raise_for_status()
        return resp.json()["sha"]

    async def _create_tree(self, client: httpx.AsyncClient, owner: str, repo: str, base_tree_sha: str, tree_items: list) -> str:
        """Git Tree 생성 후 SHA 반환"""
        resp = await client.post(
            f"{self.API_BASE}/repos/{owner}/{repo}/git/trees",
            headers=self.headers,
            json={
                "base_tree": base_tree_sha,
                "tree": tree_items,
            },
            timeout=60.0
        )
        resp.raise_for_status()
        return resp.json()["sha"]

    async def _create_commit(self, client: httpx.AsyncClient, owner: str, repo: str, tree_sha: str, parent_sha: str, message: str) -> str:
        """커밋 생성 후 SHA 반환"""
        resp = await client.post(
            f"{self.API_BASE}/repos/{owner}/{repo}/git/commits",
            headers=self.headers,
            json={
                "message": message,
                "tree": tree_sha,
                "parents": [parent_sha],
            },
            timeout=30.0
        )
        resp.raise_for_status()
        return resp.json()["sha"]

    async def _update_ref(self, client: httpx.AsyncClient, owner: str, repo: str, commit_sha: str):
        """main 브랜치 ref를 새 커밋으로 업데이트"""
        resp = await client.patch(
            f"{self.API_BASE}/repos/{owner}/{repo}/git/refs/heads/main",
            headers=self.headers,
            json={"sha": commit_sha},
            timeout=30.0
        )
        resp.raise_for_status()

    async def sync_posts(self, repo_name: str, posts: List, velog_username: str) -> str:
        """모든 포스트를 GitHub Repository에 단일 커밋으로 동기화. GitHub 사용자명을 반환."""
        owner = await self._get_authenticated_user()
        await self._ensure_repo_exists(repo_name, owner)

        # 최신 커밋 SHA 조회
        base_sha = await self._get_default_branch_sha(owner, repo_name)
        if not base_sha:
            raise RuntimeError(f"Could not get base SHA for {owner}/{repo_name}")

        # 중복 폴더명 처리
        folder_names = {}
        tree_items = []
        synced = 0

        async with httpx.AsyncClient() as client:
            # 1. 모든 파일의 Blob을 생성
            for post in posts:
                try:
                    folder_name = MarkdownService.generate_folder_name(post.title)

                    if folder_name in folder_names:
                        folder_names[folder_name] += 1
                        folder_name = f"{folder_name} ({folder_names[folder_name]})"
                    else:
                        folder_names[folder_name] = 1

                    content = post.content or ""

                    # 이미지 처리: URL 추출 → Blob 생성 → 경로 치환
                    images = ImageService.extract_image_urls(content)
                    processed_content = content

                    for index, (full_match, alt_text, url) in enumerate(images, 1):
                        try:
                            img_data = await ImageService.download_image(url)
                            if img_data:
                                img_filename = ImageService.get_image_filename(url, index)
                                img_path = f"posts/{folder_name}/images/{img_filename}"

                                img_blob_sha = await self._create_blob(client, owner, repo_name, img_data)
                                tree_items.append({
                                    "path": img_path,
                                    "mode": "100644",
                                    "type": "blob",
                                    "sha": img_blob_sha,
                                })

                                # 마크다운 내 이미지 경로 치환
                                relative_path = f"./images/{img_filename}"
                                if full_match.startswith('!['):
                                    new_ref = f"![{alt_text}]({relative_path})"
                                    processed_content = processed_content.replace(full_match, new_ref, 1)
                                elif full_match.startswith('<img'):
                                    new_ref = full_match.replace(url, relative_path)
                                    processed_content = processed_content.replace(full_match, new_ref, 1)
                        except Exception as e:
                            logger.warning(f"Failed to process image for {post.title}: {e}")

                    # 마크다운 Blob 생성
                    md_blob_sha = await self._create_blob(client, owner, repo_name, processed_content.encode("utf-8"))
                    tree_items.append({
                        "path": f"posts/{folder_name}/index.md",
                        "mode": "100644",
                        "type": "blob",
                        "sha": md_blob_sha,
                    })

                    synced += 1

                except Exception as e:
                    logger.error(f"Failed to prepare post {post.title}: {e}")

            # README Blob 생성
            readme_content = self._generate_readme(posts, velog_username, synced)
            readme_blob_sha = await self._create_blob(client, owner, repo_name, readme_content.encode("utf-8"))
            tree_items.append({
                "path": "README.md",
                "mode": "100644",
                "type": "blob",
                "sha": readme_blob_sha,
            })

            # 2. Tree 생성 (단일)
            new_tree_sha = await self._create_tree(client, owner, repo_name, base_sha, tree_items)

            # 3. 커밋 생성 (단일)
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            commit_message = f"backup: {synced}개 포스트 동기화 ({now})"
            new_commit_sha = await self._create_commit(client, owner, repo_name, new_tree_sha, base_sha, commit_message)

            # 4. ref 업데이트 → 끝
            await self._update_ref(client, owner, repo_name, new_commit_sha)

        logger.info(f"GitHub sync complete: {synced}/{len(posts)} posts in single commit to {owner}/{repo_name}")

        return owner

    def _generate_readme(self, posts: List, velog_username: str, synced: int) -> str:
        """README.md 내용 생성"""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

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

        for post in sorted(posts, key=lambda p: p.velog_published_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True):
            folder_name = MarkdownService.generate_folder_name(post.title)
            date_str = ""
            if post.velog_published_at:
                date_str = f" ({post.velog_published_at.strftime('%Y-%m-%d')})"
            lines.append(f"- [{post.title}](posts/{folder_name}/index.md){date_str}")

        return "\n".join(lines) + "\n"
