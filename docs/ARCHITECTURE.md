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
│  - GitHub OAuth Login               │
│  - Dashboard UI                     │
│  - Backup Management                │
│  - 다크 모드 지원                    │
└────────────┬────────────────────────┘
             │ HTTP/REST API
             ▼
┌─────────────────────────────────────┐
│    Backend (FastAPI / Railway)      │
│  ┌─────────────────────────────┐   │
│  │  API Layer                  │   │
│  │  - auth, user, backup       │   │
│  └───────┬─────────────────────┘   │
│          ▼                          │
│  ┌─────────────────────────────┐   │
│  │  Services Layer             │   │
│  │  - Velog Scraper            │   │
│  │  - GitHub Sync Service      │   │
│  │  - Email Service (Resend)   │   │
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
    │PostgreSQL│  │  GitHub   │  │  Resend  │
    │(Supabase)│  │  API      │  │  (Email) │
    └──────────┘  └──────────┘  └──────────┘
                        │
                        ├─ OAuth 2.0
                        └─ Repository Sync
```

## 컴포넌트 설명

### 1. Frontend (Next.js)

**기술 스택:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS (다크 모드 지원)
- Axios

**주요 기능:**
- 사용자 인터페이스
- GitHub OAuth 로그인 플로우
- 백업 통계 시각화
- Velog/GitHub 연동 관리
- 다크 모드 (설정에서 토글)

**배포:** Vercel (자동 CI/CD)

---

### 2. Backend (FastAPI)

**기술 스택:**
- FastAPI (Python 3.11+)
- SQLAlchemy (ORM)
- Pydantic (Validation)
- httpx (비동기 HTTP)

**레이어 구조:**

#### API Layer (`/api`)
- 엔드포인트 라우팅
- 요청/응답 처리
- JWT 인증 검증

#### Service Layer (`/services`)
- **VelogScraper**: GraphQL API로 포스트 크롤링
- **MarkdownConverter**: Markdown 변환 (frontmatter)
- **GitHubSyncService**: GitHub Repository 동기화
- **EmailService**: Resend API로 백업 알림 이메일

#### Data Layer (`/models`)
- **User**: 사용자 정보 (GitHub OAuth)
- **PostCache**: 포스트 백업 저장소 (서버 DB에 직접 저장)
- **BackupLog**: 백업 작업 로그

**배포:** Railway (자동 배포)

---

### 3. Database (PostgreSQL)

**제공자:** Supabase (무료 플랜)

**주요 테이블:**
- `users`: 사용자 정보, GitHub 토큰, 설정
- `post_cache`: 백업된 포스트 내용 (마크다운 전체 저장)
- `backup_logs`: 백업 작업 이력

---

### 4. 외부 API

#### GitHub OAuth 2.0
- 사용자 인증
- Repository 접근 권한 (repo scope)

#### GitHub Repository API
- Private Repository 자동 생성
- 포스트를 단일 커밋으로 동기화
- README.md 자동 생성

#### Velog GraphQL API
```
https://v2.velog.io/graphql
```
- 포스트 목록 조회
- 포스트 내용 조회

#### Resend API
- 백업 완료/실패 알림 이메일
- 관련 링크 포함 (GitHub repo, Velog, Dashboard)

---

## 데이터 흐름

### 1. 로그인 플로우

```
1. 사용자 → Frontend: "GitHub로 시작하기" 클릭
2. Frontend → GitHub: OAuth 인증 요청
3. GitHub → Frontend: Authorization code 반환 (/auth/callback)
4. Frontend → Backend: code + state 전송
5. Backend → GitHub: code로 access_token 교환
6. Backend: User 생성/조회, JWT 발급
7. Backend → Frontend: JWT Access Token
8. Frontend: 토큰 저장, Dashboard 이동
```

### 2. 백업 플로우

```
1. 사용자 → Frontend: "지금 백업하기" 클릭
2. Frontend → Backend: POST /backup/trigger
3. Backend: 백그라운드 작업 시작
4. Backend → Velog API: 포스트 목록 요청
5. Velog API → Backend: 포스트 목록 반환
6. Backend: 각 포스트 병렬 처리 (최대 10개 동시)
   a. Velog API에서 전체 내용 가져오기
   b. MD5 해시로 변경 감지
   c. Markdown 변환 (frontmatter 포함)
   d. 서버 DB에 저장
7. Backend → GitHub: Repository에 단일 커밋으로 동기화 (활성화 시)
8. Backend → Resend: 이메일 알림 발송 (활성화 시)
9. Frontend: 통계 자동 업데이트 (폴링)
```

### 3. 변경 감지 메커니즘

```python
# 1. 포스트 내용 가져오기
post_content = await velog.get_post_content(username, slug)

# 2. MD5 해시 생성
new_hash = hashlib.md5(post_content.encode()).hexdigest()

# 3. DB에서 기존 해시 조회
cached_post = db.query(PostCache).filter_by(user_id=user_id, slug=slug).first()

# 4. 비교
if cached_post and cached_post.content_hash == new_hash:
    # 변경 없음 - 스킵
else:
    # 변경 있음 - 백업 수행 (DB에 직접 저장)
```

---

## 보안

### 1. 인증/인가
- GitHub OAuth 2.0 (비밀번호 저장 안 함)
- JWT Bearer Token (7일 유효)
- HTTPS 강제

### 2. 데이터 보호
- 환경 변수로 민감 정보 관리
- Database 연결 암호화 (SSL)
- GitHub Repository: Private으로 자동 생성

### 3. API 보안
- CORS 설정 (허용 도메인 제한)
- Input Validation (Pydantic)
- SQL Injection 방지 (SQLAlchemy ORM)
- 이메일 에러 메시지 HTML 이스케이프 (XSS 방지)

---

## 확장성

### 수평 확장
- Frontend: Vercel Edge Network
- Backend: Railway Auto-scaling
- Database: Supabase Connection Pooling

### 성능 최적화
- Database Indexing (user_id, slug)
- CDN (Vercel)
- 비동기 I/O (FastAPI async)
- 병렬 포스트 처리 (asyncio.Semaphore)

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
- Vercel: `NEXT_PUBLIC_API_URL`
- Railway: `DATABASE_URL`, `SECRET_KEY`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `FRONTEND_URL`, `RESEND_API_KEY`

---

## 비용 분석

| 서비스 | 무료 플랜 | 예상 비용 |
|--------|-----------|----------|
| Vercel | 100GB 대역폭/월 | $0 |
| Railway | $5 크레딧/월 | $0 (개인 사용) |
| Supabase | 500MB DB | $0 |
| Resend | 3,000 이메일/월 | $0 |
| **합계** | | **$0** |

사용자 1,000명 기준으로도 무료 플랜 내에서 운영 가능합니다.
