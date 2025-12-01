import httpx
import hashlib
from typing import List, Optional, Dict


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

        async with httpx.AsyncClient() as client:
            while True:
                response = await client.post(
                    VelogService.GRAPHQL_ENDPOINT,
                    json={"query": query, "variables": {"username": username, "cursor": cursor}},
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                data = response.json()

                if "data" in data and "posts" in data["data"]:
                    posts = data["data"]["posts"]
                    if not posts:
                        break

                    # 비공개 포스트 제외하고 추가
                    all_posts.extend([p for p in posts if not p.get("is_private")])

                    # 100개 미만이면 마지막 페이지
                    if len(posts) < 100:
                        break

                    # 다음 페이지를 위한 커서 설정
                    cursor = posts[-1]["id"]
                else:
                    break

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

        async with httpx.AsyncClient() as client:
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
        try:
            posts = await VelogService.get_user_posts(username)
            return True  # 빈 블로그도 유효
        except:
            return False
