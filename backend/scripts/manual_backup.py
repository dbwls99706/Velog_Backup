"""
특정 사용자의 백업을 강제로 실행하는 관리자 스크립트
"""
import asyncio
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.api.backup import perform_backup_task


async def manual_backup(velog_username: str, force: bool = True):
    """특정 Velog 사용자의 백업을 강제 실행"""
    db: Session = SessionLocal()

    try:
        # 사용자 조회
        user = db.query(User).filter(User.velog_username == velog_username).first()

        if not user:
            print(f"❌ 사용자를 찾을 수 없습니다: {velog_username}")
            return

        print(f"✅ 사용자 발견: {user.email} (velog: {user.velog_username})")
        print(f"🔄 백업 시작... (force={force})")

        # 백업 실행
        await perform_backup_task(user.id, force, db)

        print(f"✅ 백업 완료!")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python scripts/manual_backup.py <velog_username>")
        print("예시: python scripts/manual_backup.py soheelog")
        sys.exit(1)

    velog_username = sys.argv[1]
    asyncio.run(manual_backup(velog_username))
