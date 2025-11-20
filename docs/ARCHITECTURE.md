# 아키텍처

Velog Backup의 시스템 아키텍처 문서입니다.

## 시스템 구성도

```
┌─────────────┐
│   사용자    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│     Frontend (Next.js / Vercel)     │
│  - Google OAuth Login               │
│  - Dashboard UI                     │
│  - Backup Management                │
└────────────┬────────────────────────┘
             │ HTTP/REST API
             ▼
┌─────────────────────────────────────┐
│    Backend (FastAPI / Railway)      │
│  ┌─────────────────────────────┐   │
│  │  API Layer                  │   │
│  │  - auth, user, google, backup│  │
│  └───────┬─────────────────────┘   │
│          ▼                          │
│  ┌─────────────────────────────┐   │
│  │  Services Layer             │   │
│  │  - Velog Scraper            │   │
│  │  - Google Drive Service     │   │
│  │  - Markdown Converter       │   │
│  └───────┬─────────────────────┘   │
│          ▼                          │
│  ┌─────────────────────────────┐   │
│  │  Data Layer                 │   │
│  │  - SQLAlchemy Models        │   │
│  │  - Database Operations      │   │
│  └───────┬─────────────────────┘   │
└──────────┼─────────────────────────┘
           │
           ├──────────────┬─────────────┐
           ▼              ▼             ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │PostgreSQL│  │  Redis   │  │ Google   │
    │(Supabase)│  │(Upstash) │  │ APIs     │
    └──────────┘  └──────────┘  └──────────┘
                                      │
                                      ├─ OAuth 2.0
                                      └─ Drive API
```

## 컴포넌트 설명

### 1. Frontend (Next.js)

**기술 스택:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- React OAuth Google

**주요 기능:**
- 사용자 인터페이스
- Google OAuth 로그인 플로우
- 백업 통계 시각화
- Velog/Drive 연동 관리

**배포:** Vercel (자동 CI/CD)

---

### 2. Backend (FastAPI)

**기술 스택:**
- FastAPI (Python 3.11+)
- SQLAlchemy (ORM)
- Pydantic (Validation)
- Google API Client

**레이어 구조:**

#### API Layer (`/api`)
- 엔드포인트 라우팅
- 요청/응답 처리
- JWT 인증 검증

#### Service Layer (`/services`)
- **VelogScraper**: GraphQL API로 포스트 크롤링
- **MarkdownConverter**: Markdown 변환 (frontmatter)
- **GoogleDriveService**: Drive API 연동

#### Data Layer (`/models`)
- **User**: 사용자 정보
- **PostCache**: 포스트 캐시 (변경 감지)
- **BackupLog**: 백업 작업 로그

**배포:** Railway (자동 배포)

---

### 3. Database (PostgreSQL)

**제공자:** Supabase (무료 플랜)

**스키마:**

```sql
-- 사용자
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    google_id VARCHAR UNIQUE NOT NULL,
    name VARCHAR,
    velog_username VARCHAR,
    google_access_token TEXT,
    google_refresh_token TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 포스트 캐시
CREATE TABLE post_cache (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    slug VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    content_hash VARCHAR NOT NULL,
    velog_published_at TIMESTAMP,
    last_backed_up TIMESTAMP
);

-- 백업 로그
CREATE TABLE backup_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    status VARCHAR,
    posts_total INTEGER,
    posts_new INTEGER,
    posts_updated INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

---

### 4. Redis (Upstash)

**용도:**
- 세션 관리 (향후)
- 작업 큐 (Celery, 향후)
- 캐싱 (향후)

---

### 5. 외부 API

#### Google OAuth 2.0
- 사용자 인증
- Google Drive 접근 권한

#### Google Drive API
- 파일 업로드/업데이트
- 폴더 관리

#### Velog GraphQL API
```
https://v2.velog.io/graphql
```
- 포스트 목록 조회
- 포스트 내용 조회

---

## 데이터 흐름

### 1. 로그인 플로우

```
1. 사용자 → Frontend: "Google로 로그인" 클릭
2. Frontend → Google: OAuth 요청
3. Google → Frontend: ID Token 반환
4. Frontend → Backend: ID Token 전송
5. Backend: Token 검증, User 생성/조회
6. Backend → Frontend: JWT Access Token
7. Frontend: 토큰 저장, Dashboard 이동
```

### 2. 백업 플로우

```
1. 사용자 → Frontend: "백업 시작" 클릭
2. Frontend → Backend: POST /backup/trigger
3. Backend: 백그라운드 작업 시작
4. Backend → Velog API: 포스트 목록 요청
5. Velog API → Backend: 포스트 목록 반환
6. Backend: 각 포스트 처리
   a. Velog API에서 전체 내용 가져오기
   b. MD5 해시로 변경 감지
   c. Markdown 변환
   d. Google Drive 업로드
   e. DB 캐시 업데이트
7. Backend: 백업 로그 저장
8. Frontend: 통계 업데이트
```

### 3. 변경 감지 메커니즘

```python
# 1. 포스트 내용 가져오기
post_content = await velog.get_post_content(username, slug)

# 2. MD5 해시 생성
new_hash = hashlib.md5(post_content.encode()).hexdigest()

# 3. DB에서 기존 해시 조회
cached_post = db.query(PostCache).filter_by(slug=slug).first()

# 4. 비교
if cached_post and cached_post.content_hash == new_hash:
    # 변경 없음 - 스킵
    continue
else:
    # 변경 있음 - 백업 수행
    backup_to_drive(post_content)
    update_cache(slug, new_hash)
```

---

## 보안

### 1. 인증/인가
- Google OAuth 2.0 (비밀번호 저장 안 함)
- JWT Bearer Token
- HTTPS 강제

### 2. 데이터 보호
- 환경 변수로 민감 정보 관리
- Database 연결 암호화 (SSL)
- Google Drive: 최소 권한 (생성 파일만 접근)

### 3. API 보안
- CORS 설정
- Input Validation (Pydantic)
- SQL Injection 방지 (SQLAlchemy ORM)

---

## 확장성

### 수평 확장
- Frontend: Vercel Edge Network
- Backend: Railway Auto-scaling
- Database: Supabase Connection Pooling

### 성능 최적화
- Redis 캐싱 (향후)
- CDN (Vercel)
- Database Indexing
- 비동기 I/O (FastAPI async)

---

## 모니터링

현재는 기본 로깅만 구현되어 있습니다.

**향후 추가 예정:**
- Sentry (에러 추적)
- Google Analytics (사용자 분석)
- Uptime Robot (서비스 모니터링)

---

## 배포 파이프라인

### Frontend (Vercel)
```
GitHub Push → Vercel Auto Deploy → Preview/Production
```

### Backend (Railway)
```
GitHub Push → Railway Auto Deploy → Production
```

**Environment Variables:**
- Vercel: `NEXT_PUBLIC_*`
- Railway: 모든 환경 변수

---

## 비용 분석

| 서비스 | 무료 플랜 | 예상 비용 |
|--------|-----------|----------|
| Vercel | 100GB 대역폭/월 | $0 |
| Railway | $5 크레딧/월 | $0 (개인 사용) |
| Supabase | 500MB DB | $0 |
| Upstash | 10K 명령/일 | $0 |
| **합계** | | **$0** |

사용자 1,000명 기준으로도 무료 플랜 내에서 운영 가능합니다.
