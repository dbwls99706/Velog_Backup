from pydantic_settings import BaseSettings
from typing import Optional


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

    # GitHub OAuth
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str

    # Resend (Email notifications)
    RESEND_API_KEY: Optional[str] = None

    # CORS
    FRONTEND_URL: str = "https://velog-backup.vercel.app"
    CORS_ORIGINS: str = ""

    @property
    def GITHUB_REDIRECT_URI(self) -> str:
        """GitHub OAuth 리다이렉트 URI"""
        if self.ENVIRONMENT == "development":
            return "http://localhost:3000/auth/callback"
        return f"{self.FRONTEND_URL}/auth/callback"

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
