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

    # Redis (Optional - Upstash)
    REDIS_URL: Optional[str] = None

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    # CORS
    FRONTEND_URL: str = "https://velog-backup.vercel.app"
    CORS_ORIGINS: str = ""

    @property
    def GOOGLE_REDIRECT_URI(self) -> str:
        """동적으로 리다이렉트 URI 생성"""
        if self.ENVIRONMENT == "development":
            return "http://localhost:3000/api/auth/google/callback"
        return f"{self.FRONTEND_URL}/api/auth/google/callback"

    @property
    def ALLOWED_ORIGINS(self) -> list:
        """CORS 허용 도메인"""
        origins = [self.FRONTEND_URL]
        if self.CORS_ORIGINS:
            origins.extend([o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()])
        if self.ENVIRONMENT == "development":
            origins.extend([
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ])
        return origins

    # Celery (Optional)
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

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
