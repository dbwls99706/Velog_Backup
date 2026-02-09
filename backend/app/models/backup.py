from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class BackupStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"


class BackupLog(Base):
    """백업 작업 로그"""
    __tablename__ = "backup_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Backup Info
    status = Column(Enum(BackupStatus), default=BackupStatus.IN_PROGRESS, index=True)
    posts_total = Column(Integer, default=0)
    posts_new = Column(Integer, default=0)
    posts_updated = Column(Integer, default=0)
    posts_skipped = Column(Integer, default=0)
    posts_failed = Column(Integer, default=0)

    # Details
    message = Column(Text, nullable=True)
    error_details = Column(Text, nullable=True)

    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="backups")

    def __repr__(self):
        return f"<BackupLog {self.id} - {self.status}>"
