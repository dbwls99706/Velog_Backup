"""
데이터베이스 초기 마이그레이션 스크립트
Docker 컨테이너 시작 시 자동으로 실행됩니다.
"""
from app.core.database import Base, engine
from app.models import User, UserIntegration, PostCache, BackupLog

def init_db():
    """데이터베이스 테이블 생성"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
