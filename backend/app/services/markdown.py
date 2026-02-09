from datetime import datetime
from typing import List, Optional
import re


class MarkdownService:
    """Markdown 변환 서비스"""

    @staticmethod
    def convert_to_markdown(
        title: str,
        content: str,
        tags: List[str] = None,
        published_at: Optional[str] = None,
        thumbnail: Optional[str] = None,
        url_slug: Optional[str] = None
    ) -> str:
        """Velog 포스트를 Markdown 파일로 변환"""

        # Frontmatter 생성
        frontmatter = ["---"]
        frontmatter.append(f'title: "{MarkdownService._escape_yaml(title)}"')

        if published_at:
            try:
                date_obj = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                frontmatter.append(f'date: {date_obj.strftime("%Y-%m-%d %H:%M:%S")}')
            except Exception:
                pass

        if tags:
            tags_str = ", ".join([f'"{tag}"' for tag in tags])
            frontmatter.append(f'tags: [{tags_str}]')

        if thumbnail:
            frontmatter.append(f'thumbnail: {thumbnail}')

        if url_slug:
            frontmatter.append(f'slug: {url_slug}')

        frontmatter.append("source: Velog")
        frontmatter.append("---")
        frontmatter.append("")  # 빈 줄

        # 최종 Markdown
        markdown = "\n".join(frontmatter) + "\n" + content

        return markdown

    @staticmethod
    def generate_filename(slug: str, published_at: Optional[str] = None) -> str:
        """백업 파일명 생성"""
        safe_slug = MarkdownService._sanitize_filename(slug)

        if published_at:
            try:
                date_obj = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                date_prefix = date_obj.strftime('%Y%m%d')
                return f"{date_prefix}_{safe_slug}.md"
            except Exception:
                pass

        return f"{safe_slug}.md"

    @staticmethod
    def generate_folder_name(title: str) -> str:
        """글 제목으로 폴더명 생성"""
        safe_title = MarkdownService._sanitize_folder_name(title)
        if not safe_title:
            safe_title = "untitled"
        return safe_title

    @staticmethod
    def _sanitize_folder_name(name: str) -> str:
        """폴더명에서 사용 불가능한 문자 제거 (제목 기반)"""
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            name = name.replace(char, '')

        # 앞뒤 공백 및 마침표 제거
        name = name.strip().strip('.')

        # 연속 공백 제거
        name = re.sub(r'\s+', ' ', name)

        # 최대 길이 제한
        if len(name) > 100:
            name = name[:100].rstrip()

        return name

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """파일명에서 사용 불가능한 문자 제거"""
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        filename = filename.replace(' ', '-')
        filename = re.sub(r'-+', '-', filename)

        if len(filename) > 200:
            filename = filename[:200]

        return filename.strip('-_')

    @staticmethod
    def _escape_yaml(text: str) -> str:
        """YAML 문자열 이스케이프"""
        if not text:
            return ""
        text = text.replace('"', '\\"')
        return text
