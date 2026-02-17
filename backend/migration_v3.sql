-- Velog Backup V3 Migration Script
-- GitHub App 전환: installation_id 컬럼 추가

-- GitHub App installation ID
ALTER TABLE users ADD COLUMN IF NOT EXISTS github_installation_id INTEGER;
