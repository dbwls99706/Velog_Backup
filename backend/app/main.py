from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy import text
import logging

from app.core.config import settings
from app.core.database import init_db, SessionLocal
from app.api import auth, user, backup

# 로깅 설정
logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 라이프사이클 관리"""
    init_db()
    db = SessionLocal()
    try:
        # V2 마이그레이션: 기존 사용자 이메일 알림 기본 활성화
        db.execute(
            text("UPDATE users SET email_notification_enabled = TRUE WHERE email_notification_enabled IS NULL")
        )
        db.commit()

        # 서버 시작 시 멈춘 백업 자동 복구
        from app.api.backup import recover_stuck_backups
        recovered = recover_stuck_backups(db)
        if recovered:
            logger.info(f"Startup: recovered {recovered} stuck backup(s)")
    except Exception as e:
        logger.warning(f"Startup tasks: {e}")
    finally:
        db.close()
    yield


# FastAPI 앱 생성
app = FastAPI(
    title="Velog Backup API",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url=None
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# 전역 예외 핸들러
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Pydantic 유효성 검사 에러 핸들러"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": "입력값이 올바르지 않습니다", "errors": exc.errors()}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """전역 예외 핸들러"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "서버 오류가 발생했습니다"}
    )


# API 라우터 등록
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(user.router, prefix=f"{settings.API_V1_STR}/user", tags=["user"])
app.include_router(backup.router, prefix=f"{settings.API_V1_STR}/backup", tags=["backup"])


@app.get("/")
def root():
    """루트 엔드포인트"""
    return {
        "name": "Velog Backup API",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """헬스 체크"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
