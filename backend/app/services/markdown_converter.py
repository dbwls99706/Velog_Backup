from datetime import datetime
from typing import List, Optional


class MarkdownConverter:
    """Velog 포스트를 Markdown 파일로 변환"""

    @staticmethod
    def convert_post_to_markdown(
        title: str,
        content: str,
        tags: List[str] = None,
        published_at: Optional[datetime] = None,
        thumbnail: Optional[str] = None
    ) -> str:
        """포스트를 Markdown 형식으로 변환"""

        frontmatter_parts = [
            "---",
            f"title: \"{title}\"",
        ]

        if published_at:
            frontmatter_parts.append(f"date: {published_at.strftime('%Y-%m-%d %H:%M:%S')}")

        if tags:
            tags_str = ", ".join(tags)
            frontmatter_parts.append(f"tags: [{tags_str}]")

        if thumbnail:
            frontmatter_parts.append(f"thumbnail: {thumbnail}")

        frontmatter_parts.append("---")
        frontmatter_parts.append("")  # Empty line after frontmatter

        frontmatter = "\n".join(frontmatter_parts)

        # 포스트 본문 (이미 Markdown 형식이므로 그대로 사용)
        markdown_content = f"{frontmatter}\n{content}"

        return markdown_content

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """파일명에서 사용 불가능한 문자 제거"""
        # Windows와 Unix에서 사용 불가능한 문자 제거
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # 공백을 하이픈으로 변경
        filename = filename.replace(' ', '-')

        # 최대 길이 제한 (200자)
        if len(filename) > 200:
            filename = filename[:200]

        return filename

    @staticmethod
    def generate_filename(slug: str, published_at: Optional[datetime] = None) -> str:
        """백업 파일명 생성"""
        # 날짜 prefix 추가 (선택적)
        if published_at:
            date_prefix = published_at.strftime('%Y%m%d')
            filename = f"{date_prefix}_{slug}.md"
        else:
            filename = f"{slug}.md"

        return MarkdownConverter.sanitize_filename(filename)
