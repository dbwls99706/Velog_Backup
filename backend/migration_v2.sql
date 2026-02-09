-- Velog Backup V2 Migration Script
-- 기존 users 테이블에 새 컬럼 추가 (이미 있으면 무시)

-- GitHub 사용자 로그인 ID
ALTER TABLE users ADD COLUMN IF NOT EXISTS github_login VARCHAR;

-- GitHub API 토큰 (repo 동기화용)
ALTER TABLE users ADD COLUMN IF NOT EXISTS github_access_token TEXT;

-- GitHub repo 설정
ALTER TABLE users ADD COLUMN IF NOT EXISTS github_repo VARCHAR;

-- GitHub 동기화 활성화 여부
ALTER TABLE users ADD COLUMN IF NOT EXISTS github_sync_enabled BOOLEAN DEFAULT FALSE;

-- 이메일 알림 활성화 여부
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_notification_enabled BOOLEAN DEFAULT FALSE;
