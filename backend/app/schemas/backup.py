from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.backup import BackupStatus, BackupDestination


class BackupTrigger(BaseModel):
    destination: BackupDestination = BackupDestination.BOTH
    force: bool = False  # Force backup even if no changes


class BackupLogResponse(BaseModel):
    id: int
    user_id: int
    status: BackupStatus
    destination: BackupDestination
    posts_total: int
    posts_backed_up: int
    posts_failed: int
    posts_skipped: int
    message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VelogPost(BaseModel):
    slug: str
    title: str
    content: str
    thumbnail: Optional[str] = None
    tags: List[str] = []
    published_at: Optional[datetime] = None


class BackupStats(BaseModel):
    total_posts: int
    last_backup: Optional[datetime] = None
    google_drive_connected: bool
    github_connected: bool
    recent_logs: List[BackupLogResponse]
