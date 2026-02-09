import re
import httpx
import hashlib
import logging
from typing import List, Tuple
from urllib.parse import urlparse, unquote
import os

logger = logging.getLogger(__name__)

# Velog 이미지 URL 패턴
IMAGE_PATTERN = re.compile(
    r'!\[([^\]]*)\]\((https?://[^\s\)]+\.(?:png|jpg|jpeg|gif|webp|svg|bmp|ico)(?:\?[^\s\)]*)?)\)',
    re.IGNORECASE
)

# HTML img 태그 패턴
HTML_IMG_PATTERN = re.compile(
    r'<img\s+[^>]*src=["\']([^"\']+)["\'][^>]*/?>',
    re.IGNORECASE
)


class ImageService:
    """이미지 다운로드 및 마크다운 내 URL 치환 서비스"""

    @staticmethod
    def extract_image_urls(content: str) -> List[Tuple[str, str, str]]:
        """마크다운 콘텐츠에서 이미지 URL 추출
        Returns: [(원본_전체_매치, alt_text, url), ...]
        """
        images = []

        # 마크다운 이미지: ![alt](url)
        for match in IMAGE_PATTERN.finditer(content):
            full_match = match.group(0)
            alt_text = match.group(1)
            url = match.group(2)
            images.append((full_match, alt_text, url))

        # HTML img 태그: <img src="url" />
        for match in HTML_IMG_PATTERN.finditer(content):
            url = match.group(1)
            if any(url.lower().endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp')):
                full_match = match.group(0)
                images.append((full_match, '', url))

        return images

    @staticmethod
    def get_image_filename(url: str, index: int) -> str:
        """URL에서 이미지 파일명 생성"""
        parsed = urlparse(url)
        path = unquote(parsed.path)
        original_name = os.path.basename(path)

        # 확장자 추출
        _, ext = os.path.splitext(original_name)
        if not ext:
            ext = '.png'

        # 파일명이 너무 길거나 특수문자가 많으면 해시 사용
        safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', original_name)
        if len(safe_name) > 50:
            name_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            safe_name = f"{name_hash}{ext}"

        return f"{index}_{safe_name}"

    @staticmethod
    async def download_image(url: str, timeout: float = 30.0) -> bytes | None:
        """이미지 URL에서 바이너리 다운로드"""
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url, timeout=timeout)
                response.raise_for_status()
                return response.content
        except Exception as e:
            logger.warning(f"Failed to download image {url}: {e}")
            return None

    @staticmethod
    async def process_images(content: str) -> Tuple[str, List[Tuple[str, bytes]]]:
        """마크다운 콘텐츠의 이미지를 다운로드하고 경로를 치환

        Returns:
            (치환된_마크다운, [(파일명, 바이너리), ...])
        """
        images = ImageService.extract_image_urls(content)
        if not images:
            return content, []

        downloaded_images = []
        processed_content = content

        for index, (full_match, alt_text, url) in enumerate(images, 1):
            image_data = await ImageService.download_image(url)
            if image_data is None:
                # 다운로드 실패 시 원본 URL 유지
                logger.warning(f"Keeping original URL for image {index}: {url}")
                continue

            filename = ImageService.get_image_filename(url, index)
            relative_path = f"./images/{filename}"

            # 마크다운 이미지 경로 치환
            if full_match.startswith('!['):
                new_ref = f"![{alt_text}]({relative_path})"
                processed_content = processed_content.replace(full_match, new_ref, 1)
            elif full_match.startswith('<img'):
                new_ref = full_match.replace(url, relative_path)
                processed_content = processed_content.replace(full_match, new_ref, 1)

            downloaded_images.append((filename, image_data))

        return processed_content, downloaded_images
