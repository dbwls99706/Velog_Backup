from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class IntegrationBase(BaseModel):
    google_drive_enabled: bool = False
    github_enabled: bool = False
    backup_frequency: str = "daily"
    auto_backup_enabled: bool = True
    include_images: bool = False


class IntegrationUpdate(BaseModel):
    google_drive_enabled: Optional[bool] = None
    github_enabled: Optional[bool] = None
    backup_frequency: Optional[str] = None
    auto_backup_enabled: Optional[bool] = None
    include_images: Optional[bool] = None


class IntegrationResponse(IntegrationBase):
    id: int
    user_id: int
    google_folder_id: Optional[str] = None
    github_repo_name: Optional[str] = None
    github_repo_url: Optional[str] = None
    github_username: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GoogleDriveConnect(BaseModel):
    code: str  # OAuth authorization code


class GitHubConnect(BaseModel):
    code: str  # OAuth authorization code
    repo_name: Optional[str] = "velog-backup"
