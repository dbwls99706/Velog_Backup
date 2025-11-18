from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "velog_backup",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# 주기적 작업 스케줄
celery_app.conf.beat_schedule = {
    'auto-backup-daily': {
        'task': 'app.tasks.backup_tasks.auto_backup_all_users',
        'schedule': crontab(hour=2, minute=0),  # 매일 오전 2시
    },
}
