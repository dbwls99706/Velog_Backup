# 📦 Velog Backup - SaaS Platform

Velog 사용자가 자신의 블로그 글을 자동으로 백업하고 Google Drive 또는 GitHub 저장소로 동기화하는 웹 서비스

## 🎯 주요 기능

- 🔐 사용자 인증 시스템 (JWT 기반)
- 📝 Velog 포스트 자동 크롤링
- 📄 Markdown 변환 및 백업
- ☁️ Google Drive 자동 업로드
- 🐙 GitHub Repository 자동 커밋
- ⏰ 정기 자동 백업 (Celery)
- 📊 웹 대시보드 (백업 현황, 로그 확인)

## 🏗️ 기술 스택

### Backend
- **FastAPI** - Python 3.11+
- **PostgreSQL** - 데이터베이스
- **SQLAlchemy** - ORM
- **Celery + Redis** - 백그라운드 작업
- **OAuth 2.0** - Google Drive, GitHub 연동

### Frontend
- **Next.js 14** - React Framework (App Router)
- **TypeScript** - 타입 안전성
- **Tailwind CSS** - 스타일링
- **Zustand** - 상태 관리

### Infrastructure
- **Docker Compose** - 로컬 개발 환경
- **Redis** - 캐시 및 작업 큐
- **Nginx** - 리버스 프록시 (프로덕션)

## 📁 프로젝트 구조

```
.
├── backend/                 # FastAPI 백엔드
│   ├── app/
│   │   ├── api/            # API 라우터
│   │   ├── core/           # 설정, 보안
│   │   ├── models/         # DB 모델
│   │   ├── schemas/        # Pydantic 스키마
│   │   ├── services/       # 비즈니스 로직
│   │   └── tasks/          # Celery 태스크
│   ├── alembic/            # DB 마이그레이션
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/               # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/           # App Router 페이지
│   │   ├── components/    # 재사용 컴포넌트
│   │   ├── lib/           # 유틸리티
│   │   └── store/         # 상태 관리
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml      # 개발 환경 설정
└── README.md
```

## 🚀 시작하기

### 사전 요구사항

- Docker & Docker Compose
- Node.js 18+ (로컬 개발 시)
- Python 3.11+ (로컬 개발 시)

### 개발 환경 실행

```bash
# 전체 서비스 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down
```

### 접속 정보

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 🔧 개발 모드

### Backend 로컬 실행

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend 로컬 실행

```bash
cd frontend
npm install
npm run dev
```

### Celery Worker 실행

```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

## 📊 DB 마이그레이션

```bash
cd backend

# 마이그레이션 생성
alembic revision --autogenerate -m "description"

# 마이그레이션 적용
alembic upgrade head
```

## 🔑 환경 변수 설정

각 서비스의 `.env` 파일을 생성하세요:

### backend/.env
```env
DATABASE_URL=postgresql://user:password@localhost:5432/velog_backup
SECRET_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379/0

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### frontend/.env.local
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🗺️ 개발 로드맵

### ✅ Phase 1 - MVP (현재)
- [x] 프로젝트 구조 설정
- [ ] 사용자 인증 시스템
- [ ] Velog 크롤러
- [ ] Markdown 변환
- [ ] Google Drive 연동
- [ ] 기본 대시보드 UI

### 📋 Phase 2 - 자동화
- [ ] 백업 스케줄러
- [ ] 업데이트 감지 (hash 비교)
- [ ] GitHub 연동
- [ ] 백업 로그 UI

### 🚀 Phase 3 - 확장
- [ ] 이미지 백업
- [ ] 알림 서비스
- [ ] 유료 플랜 (Stripe)
- [ ] 성능 최적화

### 🌐 Phase 4 - 런칭
- [ ] Landing page
- [ ] SEO 최적화
- [ ] 프로덕션 배포

## 📝 라이선스

MIT License

## 👥 기여

이슈와 PR을 환영합니다!
