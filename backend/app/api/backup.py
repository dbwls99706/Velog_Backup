from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import asyncio
import zipfile
import io

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.post import PostCache
from app.models.backup import BackupLog, BackupStatus
from app.services.velog import VelogService
from app.services.markdown import MarkdownService
from app.services.image import ImageService

router = APIRouter()


class BackupTriggerRequest(BaseModel):
    force: bool = False  # 강제 전체 백업


class BackupLogResponse(BaseModel):
    id: int
    status: str
    posts_total: int
    posts_new: int
    posts_updated: int
    posts_skipped: int
    message: str | None
    started_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True


class BackupStatsResponse(BaseModel):
    total_posts: int
    last_backup: datetime | None
    velog_connected: bool
    recent_logs: List[BackupLogResponse]


class PostResponse(BaseModel):
    id: int
    slug: str
    title: str
    content: Optional[str]
    thumbnail: Optional[str]
    tags: Optional[str]
    velog_published_at: Optional[datetime]
    last_backed_up: Optional[datetime]

    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    posts: List[PostResponse]
    total: int
    page: int
    limit: int


async def process_single_post(
    semaphore: asyncio.Semaphore,
    velog: VelogService,
    username: str,
    post_info: dict,
    user_id: int,
    force: bool,
    db: Session
):
    """단일 포스트 처리 (병렬 처리용)"""
    async with semaphore:
        try:
            post_data = await velog.get_post_content(username, post_info['url_slug'])
            if not post_data:
                return {'status': 'failed', 'slug': post_info['url_slug']}

            content_hash = velog.compute_content_hash(post_data['body'])
            existing_post = db.query(PostCache).filter(
                PostCache.user_id == user_id,
                PostCache.slug == post_data['url_slug']
            ).first()

            if not force and existing_post and existing_post.content_hash == content_hash:
                return {'status': 'skipped', 'slug': post_info['url_slug']}

            markdown_content = MarkdownService.convert_to_markdown(
                title=post_data['title'],
                content=post_data['body'],
                tags=post_data.get('tags', []),
                published_at=post_data.get('released_at'),
                thumbnail=post_data.get('thumbnail'),
                url_slug=post_data.get('url_slug')
            )

            if existing_post:
                existing_post.content = markdown_content
                existing_post.content_hash = content_hash
                existing_post.title = post_data['title']
                existing_post.thumbnail = post_data.get('thumbnail')
                existing_post.tags = json.dumps(post_data.get('tags', []))
                existing_post.last_backed_up = datetime.utcnow()
                return {'status': 'updated', 'slug': post_info['url_slug']}
            else:
                new_post = PostCache(
                    user_id=user_id,
                    slug=post_data['url_slug'],
                    title=post_data['title'],
                    content=markdown_content,
                    content_hash=content_hash,
                    thumbnail=post_data.get('thumbnail'),
                    tags=json.dumps(post_data.get('tags', [])),
                    velog_published_at=post_data.get('released_at'),
                    last_backed_up=datetime.utcnow()
                )
                db.add(new_post)
                return {'status': 'new', 'slug': post_info['url_slug']}

        except Exception as e:
            print(f"Error backing up post {post_info.get('url_slug')}: {e}")
            return {'status': 'failed', 'slug': post_info['url_slug'], 'error': str(e)}


async def perform_backup_task(user_id: int, force: bool, db: Session):
    """백업 작업 수행 (백그라운드) - 서버 DB에 직접 저장 (병렬 처리)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.velog_username:
        return

    backup_log = BackupLog(user_id=user_id, status=BackupStatus.IN_PROGRESS)
    db.add(backup_log)
    db.commit()
    db.refresh(backup_log)

    try:
        velog = VelogService()
        posts = await velog.get_user_posts(user.velog_username)

        backup_log.posts_total = len(posts)
        db.commit()

        semaphore = asyncio.Semaphore(10)
        tasks = [
            process_single_post(semaphore, velog, user.velog_username, post_info, user_id, force, db)
            for post_info in posts
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        posts_new = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'new')
        posts_updated = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'updated')
        posts_skipped = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'skipped')
        posts_failed = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'failed')

        db.commit()

        backup_log.status = BackupStatus.SUCCESS
        backup_log.posts_new = posts_new
        backup_log.posts_updated = posts_updated
        backup_log.posts_skipped = posts_skipped
        backup_log.posts_failed = posts_failed
        backup_log.completed_at = datetime.utcnow()
        backup_log.message = f"새 포스트 {posts_new}개, 업데이트 {posts_updated}개"

        db.commit()

        # GitHub 동기화 (활성화된 경우)
        if user.github_sync_enabled and user.github_repo and user.github_access_token:
            try:
                from app.services.github_sync import GitHubSyncService
                github_sync = GitHubSyncService(user.github_access_token)
                all_posts = db.query(PostCache).filter(PostCache.user_id == user_id).all()
                await github_sync.sync_posts(user.github_repo, all_posts, user.velog_username)
                backup_log.message += " | GitHub 동기화 완료"
                db.commit()
            except Exception as e:
                backup_log.message += f" | GitHub 동기화 실패: {str(e)[:100]}"
                db.commit()

        # 이메일 알림 (활성화된 경우)
        if user.email_notification_enabled:
            try:
                from app.services.email import EmailService
                EmailService.send_backup_notification(
                    to_email=user.email,
                    username=user.velog_username,
                    posts_new=posts_new,
                    posts_updated=posts_updated,
                    posts_failed=posts_failed,
                    total_posts=len(posts),
                    status="success"
                )
            except Exception as e:
                print(f"Failed to send email notification: {e}")

    except Exception as e:
        backup_log.status = BackupStatus.FAILED
        backup_log.error_details = str(e)
        backup_log.completed_at = datetime.utcnow()
        db.commit()

        # 실패 알림
        if user.email_notification_enabled:
            try:
                from app.services.email import EmailService
                EmailService.send_backup_notification(
                    to_email=user.email,
                    username=user.velog_username,
                    posts_new=0,
                    posts_updated=0,
                    posts_failed=0,
                    total_posts=0,
                    status="failed",
                    error_message=str(e)
                )
            except Exception:
                pass


@router.post("/trigger")
async def trigger_backup(
    request: BackupTriggerRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """수동 백업 트리거 - 서버 DB에 저장"""
    if not current_user.velog_username:
        raise HTTPException(status_code=400, detail="Velog 계정을 먼저 연동해주세요")

    background_tasks.add_task(perform_backup_task, current_user.id, request.force, db)

    return {"message": "백업이 시작되었습니다"}


@router.get("/stats", response_model=BackupStatsResponse)
async def get_backup_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """백업 통계"""
    total_posts = db.query(PostCache).filter(PostCache.user_id == current_user.id).count()

    last_backup_log = db.query(BackupLog).filter(
        BackupLog.user_id == current_user.id,
        BackupLog.status == BackupStatus.SUCCESS
    ).order_by(BackupLog.completed_at.desc()).first()

    recent_logs = db.query(BackupLog).filter(
        BackupLog.user_id == current_user.id
    ).order_by(BackupLog.started_at.desc()).limit(10).all()

    return {
        "total_posts": total_posts,
        "last_backup": last_backup_log.completed_at if last_backup_log else None,
        "velog_connected": bool(current_user.velog_username),
        "recent_logs": recent_logs
    }


@router.get("/logs", response_model=List[BackupLogResponse])
async def get_backup_logs(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """백업 로그 조회"""
    logs = db.query(BackupLog).filter(
        BackupLog.user_id == current_user.id
    ).order_by(BackupLog.started_at.desc()).limit(limit).all()

    return logs


@router.get("/posts", response_model=PostListResponse)
async def get_backed_up_posts(
    page: int = Query(default=1, ge=1, le=1000),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """백업된 포스트 목록 조회"""
    offset = (page - 1) * limit

    total = db.query(PostCache).filter(PostCache.user_id == current_user.id).count()

    posts = db.query(PostCache).filter(
        PostCache.user_id == current_user.id
    ).order_by(PostCache.velog_published_at.desc()).offset(offset).limit(limit).all()

    return {
        "posts": posts,
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_backed_up_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """백업된 특정 포스트 조회"""
    post = db.query(PostCache).filter(
        PostCache.id == post_id,
        PostCache.user_id == current_user.id
    ).first()

    if not post:
        raise HTTPException(status_code=404, detail="포스트를 찾을 수 없습니다")

    return post


@router.delete("/posts/{post_id}")
async def delete_backed_up_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """백업된 포스트 삭제"""
    post = db.query(PostCache).filter(
        PostCache.id == post_id,
        PostCache.user_id == current_user.id
    ).first()

    if not post:
        raise HTTPException(status_code=404, detail="포스트를 찾을 수 없습니다")

    db.delete(post)
    db.commit()

    return {"message": "포스트가 삭제되었습니다"}


@router.get("/download-zip")
async def download_all_posts_as_zip(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """백업된 모든 포스트를 ZIP 파일로 다운로드 (글 제목별 폴더 + 이미지 포함)"""
    posts = db.query(PostCache).filter(
        PostCache.user_id == current_user.id
    ).order_by(PostCache.velog_published_at.desc()).all()

    if not posts or len(posts) == 0:
        raise HTTPException(status_code=404, detail="백업된 포스트가 없습니다")

    zip_buffer = io.BytesIO()

    # 중복 폴더명 처리용
    folder_names = {}

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for post in posts:
            # 글 제목으로 폴더명 생성
            folder_name = MarkdownService.generate_folder_name(post.title)

            # 중복 제목 처리
            if folder_name in folder_names:
                folder_names[folder_name] += 1
                folder_name = f"{folder_name} ({folder_names[folder_name]})"
            else:
                folder_names[folder_name] = 1

            # 마크다운 콘텐츠에서 이미지 URL 추출 및 다운로드
            content = post.content or ""
            images = ImageService.extract_image_urls(content)

            if images:
                # 이미지가 있는 경우: 이미지 URL을 상대 경로로 치환
                processed_content = content
                for index, (full_match, alt_text, url) in enumerate(images, 1):
                    filename = ImageService.get_image_filename(url, index)
                    relative_path = f"./images/{filename}"

                    if full_match.startswith('!['):
                        new_ref = f"![{alt_text}]({relative_path})"
                        processed_content = processed_content.replace(full_match, new_ref, 1)
                    elif full_match.startswith('<img'):
                        new_ref = full_match.replace(url, relative_path)
                        processed_content = processed_content.replace(full_match, new_ref, 1)

                # index.md 작성
                zip_file.writestr(f"{folder_name}/index.md", processed_content)

                # 이미지 다운로드 및 추가 (동기적으로 - ZIP 생성 시)
                import httpx
                for index, (full_match, alt_text, url) in enumerate(images, 1):
                    try:
                        with httpx.Client(follow_redirects=True) as client:
                            resp = client.get(url, timeout=15.0)
                            if resp.status_code == 200:
                                img_filename = ImageService.get_image_filename(url, index)
                                zip_file.writestr(
                                    f"{folder_name}/images/{img_filename}",
                                    resp.content
                                )
                    except Exception:
                        pass  # 다운로드 실패 시 건너뜀
            else:
                # 이미지 없는 경우: index.md만 저장
                zip_file.writestr(f"{folder_name}/index.md", content)

    zip_buffer.seek(0)

    username = current_user.velog_username or current_user.email.split('@')[0]
    today = datetime.utcnow().strftime('%Y%m%d')
    zip_filename = f"velog_backup_{username}_{today}.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={zip_filename}"
        }
    )
