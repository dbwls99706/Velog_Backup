-- Velog Backup V2 Migration Script
-- 기존 users 테이블에 새 컬럼 추가 (이미 있으면 무시)

-- GitHub API 토큰 (repo 동기화용)
ALTER TABLE users ADD COLUMN IF NOT EXISTS github_access_token TEXT;

-- GitHub repo 설정
ALTER TABLE users ADD COLUMN IF NOT EXISTS github_repo VARCHAR;

-- GitHub 동기화 활성화 여부
ALTER TABLE users ADD COLUMN IF NOT EXISTS github_sync_enabled BOOLEAN DEFAULT FALSE;

-- 이메일 알림 활성화 여부
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_notification_enabled BOOLEAN DEFAULT TRUE;

-- 기존 사용자 이메일 알림 기본 활성화
UPDATE users SET email_notification_enabled = TRUE WHERE email_notification_enabled = FALSE;

-- post_cache 중복 방지 유니크 제약조건
-- 먼저 기존 중복 데이터 제거 (최신 것만 유지)
DELETE FROM post_cache a USING post_cache b
WHERE a.id < b.id AND a.user_id = b.user_id AND a.slug = b.slug;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_post_cache_user_slug') THEN
        ALTER TABLE post_cache ADD CONSTRAINT uq_post_cache_user_slug UNIQUE (user_id, slug);
    END IF;
END $$;
