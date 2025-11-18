from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.post import PostCache
from app.models.backup import BackupLog, BackupStatus
from app.services.velog import VelogService
from app.services.markdown import MarkdownService
from app.services.google_drive import GoogleDriveService

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
    google_drive_connected: bool
    velog_connected: bool
    recent_logs: List[BackupLogResponse]


async def perform_backup_task(user_id: int, force: bool, db: Session):
    """백업 작업 수행 (백그라운드)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.velog_username or not user.google_access_token:
        return

    # 백업 로그 시작
    backup_log = BackupLog(user_id=user_id, status=BackupStatus.IN_PROGRESS)
    db.add(backup_log)
    db.commit()
    db.refresh(backup_log)

    try:
        # Velog 포스트 가져오기
        velog = VelogService()
        posts = await velog.get_user_posts(user.velog_username)

        backup_log.posts_total = len(posts)
        db.commit()

        # Google Drive 서비스
        drive = GoogleDriveService(user.google_access_token, user.google_refresh_token)
        folder_id = drive.get_or_create_backup_folder()

        posts_new = 0
        posts_updated = 0
        posts_skipped = 0
        posts_failed = 0

        for post_info in posts:
            try:
                # 전체 포스트 내용 가져오기
                post_data = await velog.get_post_content(user.velog_username, post_info['url_slug'])
                if not post_data:
                    posts_failed += 1
                    continue

                # 변경 감지
                content_hash = velog.compute_content_hash(post_data['body'])
                existing_post = db.query(PostCache).filter(
                    PostCache.user_id == user_id,
                    PostCache.slug == post_data['url_slug']
                ).first()

                if not force and existing_post and existing_post.content_hash == content_hash:
                    posts_skipped += 1
                    continue

                # Markdown 변환
                markdown_content = MarkdownService.convert_to_markdown(
                    title=post_data['title'],
                    content=post_data['body'],
                    tags=post_data.get('tags', []),
                    published_at=post_data.get('released_at'),
                    thumbnail=post_data.get('thumbnail'),
                    url_slug=post_data.get('url_slug')
                )

                filename = MarkdownService.generate_filename(
                    post_data['url_slug'],
                    post_data.get('released_at')
                )

                # Google Drive 업로드
                drive.upload_or_update_file(filename, markdown_content, folder_id)

                # 캐시 업데이트
                if existing_post:
                    existing_post.content_hash = content_hash
                    existing_post.title = post_data['title']
                    existing_post.last_backed_up = datetime.utcnow()
                    posts_updated += 1
                else:
                    new_post = PostCache(
                        user_id=user_id,
                        slug=post_data['url_slug'],
                        title=post_data['title'],
                        content_hash=content_hash,
                        thumbnail=post_data.get('thumbnail'),
                        tags=str(post_data.get('tags', [])),
                        velog_published_at=post_data.get('released_at'),
                        last_backed_up=datetime.utcnow()
                    )
                    db.add(new_post)
                    posts_new += 1

                db.commit()

            except Exception as e:
                print(f"Error backing up post {post_info.get('url_slug')}: {e}")
                posts_failed += 1

        # 백업 로그 완료
        backup_log.status = BackupStatus.SUCCESS
        backup_log.posts_new = posts_new
        backup_log.posts_updated = posts_updated
        backup_log.posts_skipped = posts_skipped
        backup_log.posts_failed = posts_failed
        backup_log.completed_at = datetime.utcnow()
        backup_log.message = f"새 포스트 {posts_new}개, 업데이트 {posts_updated}개"

        db.commit()

    except Exception as e:
        backup_log.status = BackupStatus.FAILED
        backup_log.error_details = str(e)
        backup_log.completed_at = datetime.utcnow()
        db.commit()


@router.post("/trigger")
async def trigger_backup(
    request: BackupTriggerRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """수동 백업 트리거"""
    if not current_user.velog_username:
        raise HTTPException(status_code=400, detail="Velog 계정을 먼저 연동해주세요")

    if not current_user.google_access_token:
        raise HTTPException(status_code=400, detail="Google Drive를 먼저 연동해주세요")

    # 백그라운드 작업 추가
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
        "google_drive_connected": bool(current_user.google_access_token),
        "velog_connected": bool(current_user.velog_username),
        "recent_logs": recent_logs
    }


@router.get("/logs", response_model=List[BackupLogResponse])
async def get_backup_logs(
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """백업 로그 조회"""
    logs = db.query(BackupLog).filter(
        BackupLog.user_id == current_user.id
    ).order_by(BackupLog.started_at.desc()).limit(limit).all()

    return logs
