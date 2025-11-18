import requests
from bs4 import BeautifulSoup
from typing import List, Optional
import hashlib
import json
from datetime import datetime


class VelogScraper:
    """Velog 포스트 크롤러"""

    BASE_URL = "https://v2.velog.io/graphql"
    USER_URL = "https://velog.io/@{username}"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        })

    def get_user_posts(self, username: str, limit: int = 100) -> List[dict]:
        """사용자의 모든 포스트 목록 가져오기"""
        query = """
        query Posts($username: String!, $limit: Int!) {
            posts(username: $username, limit: $limit) {
                id
                title
                short_description
                thumbnail
                user {
                    username
                }
                url_slug
                released_at
                updated_at
                tags
                is_private
            }
        }
        """

        variables = {
            "username": username,
            "limit": limit
        }

        try:
            response = self.session.post(
                self.BASE_URL,
                json={"query": query, "variables": variables}
            )
            response.raise_for_status()
            data = response.json()

            if "data" in data and "posts" in data["data"]:
                return data["data"]["posts"]
            return []

        except Exception as e:
            print(f"Error fetching posts for {username}: {e}")
            return []

    def get_post_content(self, username: str, slug: str) -> Optional[dict]:
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
                user {
                    username
                }
            }
        }
        """

        variables = {
            "username": username,
            "url_slug": slug
        }

        try:
            response = self.session.post(
                self.BASE_URL,
                json={"query": query, "variables": variables}
            )
            response.raise_for_status()
            data = response.json()

            if "data" in data and "post" in data["data"]:
                return data["data"]["post"]
            return None

        except Exception as e:
            print(f"Error fetching post {slug}: {e}")
            return None

    def compute_content_hash(self, content: str) -> str:
        """컨텐츠 해시 생성 (변경 감지용)"""
        return hashlib.md5(content.encode()).hexdigest()

    def verify_username(self, username: str) -> bool:
        """Velog 사용자 이름 검증"""
        try:
            posts = self.get_user_posts(username, limit=1)
            return len(posts) >= 0  # 빈 블로그도 유효
        except:
            return False

    def format_post_for_backup(self, post_data: dict) -> dict:
        """백업용 포스트 데이터 포맷팅"""
        return {
            "slug": post_data.get("url_slug", ""),
            "title": post_data.get("title", ""),
            "content": post_data.get("body", ""),
            "thumbnail": post_data.get("thumbnail"),
            "tags": post_data.get("tags", []),
            "published_at": post_data.get("released_at"),
            "updated_at": post_data.get("updated_at"),
            "is_private": post_data.get("is_private", False),
            "content_hash": self.compute_content_hash(post_data.get("body", ""))
        }
