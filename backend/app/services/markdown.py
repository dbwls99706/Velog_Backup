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
            except:
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
        # 안전한 파일명으로 변환
        safe_slug = MarkdownService._sanitize_filename(slug)

        # 날짜 prefix 추가
        if published_at:
            try:
                date_obj = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                date_prefix = date_obj.strftime('%Y%m%d')
                return f"{date_prefix}_{safe_slug}.md"
            except:
                pass

        return f"{safe_slug}.md"

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """파일명에서 사용 불가능한 문자 제거"""
        # 사용 불가능한 문자 제거
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # 공백을 하이픈으로
        filename = filename.replace(' ', '-')

        # 연속된 하이픈 제거
        filename = re.sub(r'-+', '-', filename)

        # 최대 길이 제한
        if len(filename) > 200:
            filename = filename[:200]

        return filename.strip('-_')

    @staticmethod
    def _escape_yaml(text: str) -> str:
        """YAML 문자열 이스케이프"""
        if not text:
            return ""
        # 따옴표 이스케이프
        text = text.replace('"', '\\"')
        return text
