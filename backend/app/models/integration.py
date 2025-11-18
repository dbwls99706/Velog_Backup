from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UserIntegration(Base):
    __tablename__ = "user_integrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Google Drive Integration
    google_drive_enabled = Column(Boolean, default=False)
    google_access_token = Column(Text, nullable=True)
    google_refresh_token = Column(Text, nullable=True)
    google_folder_id = Column(String, nullable=True)  # Drive folder for backups

    # GitHub Integration
    github_enabled = Column(Boolean, default=False)
    github_access_token = Column(Text, nullable=True)
    github_repo_name = Column(String, nullable=True)
    github_repo_url = Column(String, nullable=True)
    github_username = Column(String, nullable=True)

    # Backup Settings
    backup_frequency = Column(String, default="daily")  # daily, hourly, manual
    auto_backup_enabled = Column(Boolean, default=True)
    include_images = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="integrations")

    def __repr__(self):
        return f"<UserIntegration user_id={self.user_id}>"
