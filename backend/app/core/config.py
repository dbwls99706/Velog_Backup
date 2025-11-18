from pydantic_settings import BaseSettings
from typing import Optional
import secrets


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Velog Backup"
    ENVIRONMENT: str = "production"
    API_V1_STR: str = "/api/v1"

    # Database (Supabase PostgreSQL)
    DATABASE_URL: str

    # Redis (Upstash)
    REDIS_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    @property
    def GOOGLE_REDIRECT_URI(self) -> str:
        """동적으로 리다이렉트 URI 생성"""
        if self.ENVIRONMENT == "development":
            return "http://localhost:3000/api/auth/google/callback"
        return f"{self.FRONTEND_URL}/api/auth/google/callback"

    # CORS
    FRONTEND_URL: str

    @property
    def ALLOWED_ORIGINS(self) -> list:
        """CORS 허용 도메인"""
        origins = [self.FRONTEND_URL]
        if self.ENVIRONMENT == "development":
            origins.extend([
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ])
        return origins

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Celery URL을 Redis URL로 기본 설정
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = self.REDIS_URL
        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = self.REDIS_URL

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


# 싱글톤 인스턴스
settings = Settings()

# 보안 검증
if settings.ENVIRONMENT == "production":
    if len(settings.SECRET_KEY) < 32:
        raise ValueError("SECRET_KEY must be at least 32 characters long in production")
    if not settings.DATABASE_URL.startswith("postgresql"):
        raise ValueError("Invalid DATABASE_URL format")
    if not settings.REDIS_URL.startswith("redis"):
        raise ValueError("Invalid REDIS_URL format")
