from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import asyncio

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.post import PostCache
from app.models.backup import BackupLog, BackupStatus
from app.services.velog import VelogService
from app.services.markdown import MarkdownService

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
    async with semaphore:  # 동시 요청 수 제한
        try:
            # 전체 포스트 내용 가져오기
            post_data = await velog.get_post_content(username, post_info['url_slug'])
            if not post_data:
                return {'status': 'failed', 'slug': post_info['url_slug']}

            # 변경 감지
            content_hash = velog.compute_content_hash(post_data['body'])
            existing_post = db.query(PostCache).filter(
                PostCache.user_id == user_id,
                PostCache.slug == post_data['url_slug']
            ).first()

            if not force and existing_post and existing_post.content_hash == content_hash:
                return {'status': 'skipped', 'slug': post_info['url_slug']}

            # Markdown 변환
            markdown_content = MarkdownService.convert_to_markdown(
                title=post_data['title'],
                content=post_data['body'],
                tags=post_data.get('tags', []),
                published_at=post_data.get('released_at'),
                thumbnail=post_data.get('thumbnail'),
                url_slug=post_data.get('url_slug')
            )

            # DB에 직접 저장 (개별 커밋 제거, 배치로 처리)
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

        # 병렬 처리 (동시 10개씩)
        semaphore = asyncio.Semaphore(10)
        tasks = [
            process_single_post(semaphore, velog, user.velog_username, post_info, user_id, force, db)
            for post_info in posts
        ]

        # 모든 포스트를 병렬로 처리
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 결과 집계
        posts_new = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'new')
        posts_updated = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'updated')
        posts_skipped = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'skipped')
        posts_failed = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'failed')

        # 배치 커밋 (한 번에)
        db.commit()

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
    """수동 백업 트리거 - 서버 DB에 저장"""
    if not current_user.velog_username:
        raise HTTPException(status_code=400, detail="Velog 계정을 먼저 연동해주세요")

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
    """백업된 포스트 목록 조회 (각 사용자는 자신의 포스트만 볼 수 있음)"""
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
    """백업된 특정 포스트 조회 (자신의 포스트만 조회 가능)"""
    post = db.query(PostCache).filter(
        PostCache.id == post_id,
        PostCache.user_id == current_user.id  # 자신의 포스트만
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
    """백업된 포스트 삭제 (자신의 포스트만 삭제 가능)"""
    post = db.query(PostCache).filter(
        PostCache.id == post_id,
        PostCache.user_id == current_user.id
    ).first()

    if not post:
        raise HTTPException(status_code=404, detail="포스트를 찾을 수 없습니다")

    db.delete(post)
    db.commit()

    return {"message": "포스트가 삭제되었습니다"}
