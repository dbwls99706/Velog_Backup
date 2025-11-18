from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class BackupStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    IN_PROGRESS = "in_progress"


class BackupDestination(str, enum.Enum):
    GOOGLE_DRIVE = "google_drive"
    GITHUB = "github"
    BOTH = "both"


class BackupLog(Base):
    """백업 작업 로그"""
    __tablename__ = "backup_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Backup Info
    status = Column(Enum(BackupStatus), default=BackupStatus.IN_PROGRESS)
    destination = Column(Enum(BackupDestination), nullable=False)
    posts_total = Column(Integer, default=0)
    posts_backed_up = Column(Integer, default=0)
    posts_failed = Column(Integer, default=0)
    posts_skipped = Column(Integer, default=0)  # Already up-to-date

    # Details
    message = Column(Text, nullable=True)
    error_details = Column(Text, nullable=True)
    task_id = Column(String, nullable=True)  # Celery task ID

    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="backup_logs")

    def __repr__(self):
        return f"<BackupLog {self.id} - {self.status}>"
