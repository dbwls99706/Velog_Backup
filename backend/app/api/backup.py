from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Any, List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.integration import UserIntegration
from app.models.post import PostCache
from app.models.backup import BackupLog, BackupStatus
from app.schemas.backup import BackupTrigger, BackupLogResponse, BackupStats
from app.services.velog_scraper import VelogScraper
from app.services.markdown_converter import MarkdownConverter
from app.services.google_drive import GoogleDriveService
from app.services.github_service import GitHubService

router = APIRouter()


def perform_backup(
    user_id: int,
    destination: str,
    force: bool,
    db: Session
):
    """백업 수행 (백그라운드 작업)"""
    from app.models.backup import BackupDestination

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.velog_username:
        return

    integration = db.query(UserIntegration).filter(
        UserIntegration.user_id == user_id
    ).first()

    # 백업 로그 생성
    backup_log = BackupLog(
        user_id=user_id,
        destination=destination,
        status=BackupStatus.IN_PROGRESS
    )
    db.add(backup_log)
    db.commit()
    db.refresh(backup_log)

    try:
        # Velog 포스트 가져오기
        scraper = VelogScraper()
        posts = scraper.get_user_posts(user.velog_username)

        backup_log.posts_total = len(posts)
        db.commit()

        posts_backed_up = 0
        posts_failed = 0
        posts_skipped = 0

        for post_info in posts:
            try:
                # 전체 포스트 내용 가져오기
                post_data = scraper.get_post_content(
                    user.velog_username,
                    post_info['url_slug']
                )

                if not post_data:
                    posts_failed += 1
                    continue

                formatted_post = scraper.format_post_for_backup(post_data)

                # 변경 감지
                existing_post = db.query(PostCache).filter(
                    PostCache.user_id == user_id,
                    PostCache.slug == formatted_post['slug']
                ).first()

                if not force and existing_post:
                    if existing_post.content_hash == formatted_post['content_hash']:
                        posts_skipped += 1
                        continue

                # Markdown 변환
                markdown_content = MarkdownConverter.convert_post_to_markdown(
                    title=formatted_post['title'],
                    content=formatted_post['content'],
                    tags=formatted_post['tags'],
                    published_at=formatted_post.get('published_at'),
                    thumbnail=formatted_post.get('thumbnail')
                )

                filename = MarkdownConverter.generate_filename(
                    formatted_post['slug'],
                    formatted_post.get('published_at')
                )

                # 백업 수행
                backup_success = False

                # Google Drive 백업
                if (destination in [BackupDestination.GOOGLE_DRIVE, BackupDestination.BOTH] and
                    integration.google_drive_enabled and
                    integration.google_access_token):

                    try:
                        drive_service = GoogleDriveService(
                            integration.google_access_token,
                            integration.google_refresh_token
                        )
                        drive_service.upload_file(
                            filename,
                            markdown_content,
                            integration.google_folder_id
                        )
                        backup_success = True
                    except Exception as e:
                        print(f"Google Drive backup failed: {e}")

                # GitHub 백업
                if (destination in [BackupDestination.GITHUB, BackupDestination.BOTH] and
                    integration.github_enabled and
                    integration.github_access_token):

                    try:
                        github_service = GitHubService(integration.github_access_token)
                        github_service.upload_or_update_file(
                            integration.github_repo_name,
                            f"posts/{filename}",
                            markdown_content,
                            f"Backup: {formatted_post['title']}"
                        )
                        backup_success = True
                    except Exception as e:
                        print(f"GitHub backup failed: {e}")

                if backup_success:
                    # 포스트 캐시 업데이트
                    if existing_post:
                        existing_post.content_hash = formatted_post['content_hash']
                        existing_post.last_backed_up = datetime.utcnow()
                        existing_post.title = formatted_post['title']
                    else:
                        new_post = PostCache(
                            user_id=user_id,
                            slug=formatted_post['slug'],
                            title=formatted_post['title'],
                            content_hash=formatted_post['content_hash'],
                            thumbnail=formatted_post.get('thumbnail'),
                            tags=str(formatted_post['tags']),
                            published_at=formatted_post.get('published_at'),
                            last_backed_up=datetime.utcnow()
                        )
                        db.add(new_post)

                    posts_backed_up += 1
                else:
                    posts_failed += 1

            except Exception as e:
                print(f"Error backing up post {post_info.get('url_slug')}: {e}")
                posts_failed += 1

        # 백업 로그 완료
        backup_log.posts_backed_up = posts_backed_up
        backup_log.posts_failed = posts_failed
        backup_log.posts_skipped = posts_skipped
        backup_log.status = BackupStatus.SUCCESS if posts_failed == 0 else BackupStatus.PARTIAL
        backup_log.completed_at = datetime.utcnow()
        backup_log.message = f"Backed up {posts_backed_up}/{len(posts)} posts"

        db.commit()

    except Exception as e:
        backup_log.status = BackupStatus.FAILED
        backup_log.error_details = str(e)
        backup_log.completed_at = datetime.utcnow()
        db.commit()


@router.post("/trigger", status_code=status.HTTP_202_ACCEPTED)
def trigger_backup(
    backup_data: BackupTrigger,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """수동 백업 트리거"""
    if not current_user.velog_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Velog username not set"
        )

    integration = db.query(UserIntegration).filter(
        UserIntegration.user_id == current_user.id
    ).first()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration settings not found"
        )

    # 연동 확인
    from app.models.backup import BackupDestination

    if backup_data.destination in [BackupDestination.GOOGLE_DRIVE, BackupDestination.BOTH]:
        if not integration.google_drive_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google Drive not connected"
            )

    if backup_data.destination in [BackupDestination.GITHUB, BackupDestination.BOTH]:
        if not integration.github_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub not connected"
            )

    # 백그라운드 작업으로 백업 수행
    background_tasks.add_task(
        perform_backup,
        current_user.id,
        backup_data.destination,
        backup_data.force,
        db
    )

    return {"message": "Backup started"}


@router.get("/logs", response_model=List[BackupLogResponse])
def get_backup_logs(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """백업 로그 조회"""
    logs = db.query(BackupLog).filter(
        BackupLog.user_id == current_user.id
    ).order_by(BackupLog.started_at.desc()).limit(limit).all()

    return logs


@router.get("/stats", response_model=BackupStats)
def get_backup_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """백업 통계 조회"""
    integration = db.query(UserIntegration).filter(
        UserIntegration.user_id == current_user.id
    ).first()

    total_posts = db.query(PostCache).filter(
        PostCache.user_id == current_user.id
    ).count()

    last_backup_log = db.query(BackupLog).filter(
        BackupLog.user_id == current_user.id,
        BackupLog.status == BackupStatus.SUCCESS
    ).order_by(BackupLog.completed_at.desc()).first()

    recent_logs = db.query(BackupLog).filter(
        BackupLog.user_id == current_user.id
    ).order_by(BackupLog.started_at.desc()).limit(5).all()

    return {
        "total_posts": total_posts,
        "last_backup": last_backup_log.completed_at if last_backup_log else None,
        "google_drive_connected": integration.google_drive_enabled if integration else False,
        "github_connected": integration.github_enabled if integration else False,
        "recent_logs": recent_logs
    }
