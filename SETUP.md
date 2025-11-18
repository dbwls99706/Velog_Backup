# Velog Backup - 개발 환경 설정 가이드

## 🚀 빠른 시작 (Docker 사용)

### 1. 사전 요구사항
- Docker 및 Docker Compose 설치
- Git

### 2. 프로젝트 클론
```bash
git clone <repository-url>
cd Velog_Backup
```

### 3. 환경 변수 설정

#### Backend 환경 변수
```bash
cp backend/.env.example backend/.env
```

`backend/.env` 파일을 열어서 필요한 값을 설정하세요:
- `SECRET_KEY`: 강력한 시크릿 키로 변경
- Google OAuth (선택): `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- GitHub OAuth (선택): `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`

#### Frontend 환경 변수
```bash
cp frontend/.env.example frontend/.env.local
```

기본 설정으로 사용 가능합니다.

### 4. 전체 서비스 실행
```bash
docker-compose up -d
```

서비스가 시작되면:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 5. 데이터베이스 마이그레이션 (최초 1회)
```bash
docker-compose exec backend alembic upgrade head
```

### 6. 서비스 중지
```bash
docker-compose down
```

### 7. 로그 확인
```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery_worker
```

---

## 🛠️ 로컬 개발 (Docker 없이)

### 사전 요구사항
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### Backend 설정

```bash
cd backend

# 가상 환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 DATABASE_URL 등을 설정

# 데이터베이스 마이그레이션
alembic upgrade head

# 서버 실행
uvicorn app.main:app --reload
```

### Frontend 설정

```bash
cd frontend

# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env.local

# 개발 서버 실행
npm run dev
```

### Celery Worker 실행

```bash
cd backend
source venv/bin/activate

# Worker 실행
celery -A app.tasks.celery_app worker --loglevel=info

# Beat (스케줄러) 실행 (별도 터미널)
celery -A app.tasks.celery_app beat --loglevel=info
```

---

## 📝 OAuth 설정 (선택)

### Google Drive API 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성
3. "API 및 서비스" > "사용자 인증 정보" 이동
4. "OAuth 2.0 클라이언트 ID" 생성
   - 애플리케이션 유형: 웹 애플리케이션
   - 승인된 리디렉션 URI: `http://localhost:8000/api/v1/integrations/google-drive/callback`
5. 클라이언트 ID와 시크릿을 `backend/.env`에 추가
6. "API 및 서비스" > "라이브러리"에서 "Google Drive API" 활성화

### GitHub OAuth 설정

1. GitHub Settings > Developer settings > OAuth Apps
2. "New OAuth App" 클릭
3. 정보 입력:
   - Application name: Velog Backup
   - Homepage URL: `http://localhost:3000`
   - Authorization callback URL: `http://localhost:8000/api/v1/integrations/github/callback`
4. 클라이언트 ID와 시크릿을 `backend/.env`에 추가

---

## 🧪 테스트

### Backend 테스트
```bash
cd backend
pytest
```

### Frontend 테스트
```bash
cd frontend
npm test
```

---

## 📦 프로덕션 빌드

### Frontend 빌드
```bash
cd frontend
npm run build
npm start
```

### Backend 프로덕션 실행
```bash
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## 🔍 문제 해결

### Docker 관련 이슈

**포트 충돌 오류**
- 다른 서비스가 3000, 8000, 5432, 6379 포트를 사용 중인지 확인
- `docker-compose.yml`에서 포트 변경 가능

**데이터베이스 연결 실패**
```bash
# 데이터베이스 상태 확인
docker-compose ps db

# 로그 확인
docker-compose logs db

# 재시작
docker-compose restart db
```

**Celery worker 작동 안함**
```bash
# Redis 상태 확인
docker-compose ps redis

# Celery 로그 확인
docker-compose logs celery_worker
```

### 로컬 개발 이슈

**PostgreSQL 연결 오류**
- PostgreSQL 서비스가 실행 중인지 확인
- `DATABASE_URL`이 올바른지 확인

**Redis 연결 오류**
- Redis 서비스가 실행 중인지 확인
- `REDIS_URL`이 올바른지 확인

---

## 📚 추가 자료

- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Next.js 문서](https://nextjs.org/docs)
- [Celery 문서](https://docs.celeryproject.org/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)

---

## 💡 개발 팁

### 핫 리로드
- Backend: uvicorn의 `--reload` 옵션 사용 중
- Frontend: Next.js 자동 핫 리로드

### API 테스트
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 데이터베이스 관리
```bash
# psql 접속
docker-compose exec db psql -U velog_user -d velog_backup

# 테이블 확인
\dt

# 데이터 확인
SELECT * FROM users;
```

### Redis 확인
```bash
# Redis CLI 접속
docker-compose exec redis redis-cli

# 키 확인
KEYS *
```
