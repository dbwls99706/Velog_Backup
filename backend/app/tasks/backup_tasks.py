from celery import shared_task
from app.core.database import SessionLocal
from app.models.user import User
from app.models.integration import UserIntegration
from app.models.backup import BackupDestination
from app.api.backup import perform_backup


@shared_task
def auto_backup_all_users():
    """모든 활성 사용자 자동 백업"""
    db = SessionLocal()
    try:
        # 자동 백업이 활성화된 사용자 조회
        integrations = db.query(UserIntegration).filter(
            UserIntegration.auto_backup_enabled == True
        ).all()

        for integration in integrations:
            user = db.query(User).filter(
                User.id == integration.user_id,
                User.is_active == True,
                User.velog_username.isnot(None)
            ).first()

            if not user:
                continue

            # 연동된 서비스 확인
            destination = None
            if integration.google_drive_enabled and integration.github_enabled:
                destination = BackupDestination.BOTH
            elif integration.google_drive_enabled:
                destination = BackupDestination.GOOGLE_DRIVE
            elif integration.github_enabled:
                destination = BackupDestination.GITHUB

            if destination:
                # 백업 수행
                perform_backup(
                    user_id=user.id,
                    destination=destination,
                    force=False,
                    db=db
                )

    finally:
        db.close()


@shared_task
def backup_single_user(user_id: int, destination: str, force: bool = False):
    """단일 사용자 백업 (Celery 태스크)"""
    db = SessionLocal()
    try:
        perform_backup(
            user_id=user_id,
            destination=destination,
            force=force,
            db=db
        )
    finally:
        db.close()
