import httpx
import hashlib
import logging
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)


class VelogService:
    """Velog GraphQL API 서비스"""

    GRAPHQL_ENDPOINT = "https://v2.velog.io/graphql"

    @staticmethod
    async def get_user_posts(username: str) -> List[Dict]:
        """사용자의 모든 포스트 목록 가져오기 (페이지네이션)"""
        all_posts = []
        cursor = None

        query = """
        query GetPosts($username: String!, $cursor: ID) {
            posts(username: $username, cursor: $cursor, limit: 100) {
                id
                title
                short_description
                thumbnail
                url_slug
                released_at
                updated_at
                tags
                is_private
            }
        }
        """

        async with httpx.AsyncClient(timeout=30.0) as client:
            page = 0
            while True:
                page += 1
                response = await client.post(
                    VelogService.GRAPHQL_ENDPOINT,
                    json={"query": query, "variables": {"username": username, "cursor": cursor}},
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                data = response.json()

                if "data" in data and "posts" in data["data"]:
                    posts = data["data"]["posts"]
                    logger.info(f"Velog API page {page}: received {len(posts)} posts, cursor={cursor}")

                    # 더 이상 포스트가 없으면 종료
                    if not posts or len(posts) == 0:
                        logger.info(f"No more posts. Total collected: {len(all_posts)}")
                        break

                    # 비공개 포스트 제외하고 추가
                    public_posts = [p for p in posts if not p.get("is_private")]
                    all_posts.extend(public_posts)
                    logger.info(f"Public posts in this page: {len(public_posts)}, Total so far: {len(all_posts)}")

                    # 다음 페이지를 위한 커서 설정
                    cursor = posts[-1]["id"]
                else:
                    logger.warning(f"Unexpected response format: {data}")
                    break

            logger.info(f"Finished fetching posts for {username}. Total: {len(all_posts)}")
            return all_posts

    @staticmethod
    async def get_post_content(username: str, slug: str) -> Optional[Dict]:
        """특정 포스트의 전체 내용 가져오기"""
        query = """
        query ReadPost($username: String!, $url_slug: String!) {
            post(username: $username, url_slug: $url_slug) {
                id
                title
                released_at
                updated_at
                body
                short_description
                thumbnail
                tags
                is_private
                url_slug
            }
        }
        """

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                VelogService.GRAPHQL_ENDPOINT,
                json={
                    "query": query,
                    "variables": {"username": username, "url_slug": slug}
                },
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()

            if "data" in data and "post" in data["data"]:
                post = data["data"]["post"]
                if not post.get("is_private"):
                    return post
            return None

    @staticmethod
    def compute_content_hash(content: str) -> str:
        """컨텐츠 해시 생성 (변경 감지용)"""
        return hashlib.md5(content.encode()).hexdigest()

    @staticmethod
    async def verify_username(username: str) -> bool:
        """Velog 사용자명 유효성 확인"""
        query = """
        query GetPosts($username: String!) {
            posts(username: $username, limit: 1) {
                id
            }
        }
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    VelogService.GRAPHQL_ENDPOINT,
                    json={"query": query, "variables": {"username": username}},
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                data = response.json()
                return "data" in data and "posts" in data["data"]
        except Exception:
            return False
