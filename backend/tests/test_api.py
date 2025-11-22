import pytest
from fastapi import status


class TestHealthCheck:
    """헬스 체크 엔드포인트 테스트"""

    def test_health_check(self, client):
        """헬스 체크 정상 응답"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}

    def test_root_endpoint(self, client):
        """루트 엔드포인트 정상 응답"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Velog Backup API"
        assert data["status"] == "running"


class TestAuthEndpoints:
    """인증 엔드포인트 테스트"""

    def test_get_github_auth_url(self, client):
        """GitHub 인증 URL 반환"""
        response = client.get("/api/v1/auth/github/url")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "auth_url" in data
        assert "github.com/login/oauth/authorize" in data["auth_url"]

    def test_github_callback_without_code(self, client):
        """코드 없이 콜백 요청 시 에러"""
        response = client.post("/api/v1/auth/github/callback", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_github_callback_with_invalid_code(self, client):
        """잘못된 코드로 콜백 요청 시 에러"""
        response = client.post("/api/v1/auth/github/callback", json={"code": "invalid"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestProtectedEndpoints:
    """인증 필요 엔드포인트 테스트"""

    def test_get_user_without_auth(self, client):
        """인증 없이 사용자 정보 요청 시 에러"""
        response = client.get("/api/v1/user/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_backup_stats_without_auth(self, client):
        """인증 없이 백업 통계 요청 시 에러"""
        response = client.get("/api/v1/backup/stats")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_backup_trigger_without_auth(self, client):
        """인증 없이 백업 트리거 요청 시 에러"""
        response = client.post("/api/v1/backup/trigger", json={})
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestInputValidation:
    """입력 유효성 검사 테스트"""

    def test_backup_logs_invalid_limit(self, client):
        """잘못된 limit 파라미터"""
        response = client.get("/api/v1/backup/logs?limit=0")
        assert response.status_code == status.HTTP_403_FORBIDDEN  # 인증 필요

    def test_backup_posts_invalid_page(self, client):
        """잘못된 page 파라미터"""
        response = client.get("/api/v1/backup/posts?page=0")
        assert response.status_code == status.HTTP_403_FORBIDDEN  # 인증 필요
