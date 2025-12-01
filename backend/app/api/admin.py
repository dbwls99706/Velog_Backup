from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.api.backup import perform_backup_task

router = APIRouter()

# 관리자 이메일 목록
ADMIN_EMAILS = [
    "yujinhong3@gmail.com"
]


def is_admin(user: User) -> bool:
    """관리자 권한 확인"""
    return user.email in ADMIN_EMAILS


class AdminBackupRequest(BaseModel):
    velog_username: str
    force: bool = True


@router.post("/backup/{velog_username}")
async def admin_trigger_backup(
    velog_username: str,
    force: bool = True,
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """관리자 전용: 특정 사용자의 백업 강제 실행"""
    # 관리자 권한 확인
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다")

    # 대상 사용자 조회
    target_user = db.query(User).filter(User.velog_username == velog_username).first()

    if not target_user:
        raise HTTPException(
            status_code=404,
            detail=f"Velog 사용자를 찾을 수 없습니다: {velog_username}"
        )

    # 백업 실행
    background_tasks.add_task(perform_backup_task, target_user.id, force, db)

    return {
        "message": f"{velog_username} 사용자의 백업이 시작되었습니다",
        "user_email": target_user.email,
        "force": force
    }


@router.get("/users")
async def admin_list_users(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """관리자 전용: 모든 사용자 목록 조회"""
    # 관리자 권한 확인
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다")

    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "velog_username": user.velog_username,
            "is_active": user.is_active
        }
        for user in users
    ]
