from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    github_id = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, nullable=True)
    picture = Column(String, nullable=True)
    velog_username = Column(String, index=True, nullable=True)

    # GitHub API (repo sync)
    github_access_token = Column(Text, nullable=True)
    github_repo = Column(String, nullable=True)
    github_sync_enabled = Column(Boolean, default=False)

    # Notification
    email_notification_enabled = Column(Boolean, default=False)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    posts = relationship("PostCache", back_populates="user", cascade="all, delete-orphan")
    backups = relationship("BackupLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"
