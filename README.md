# Velog Backup V2

> Velog 블로그 포스트를 이미지 포함하여 안전하게 백업하는 무료 웹 서비스

## 주요 기능

- **이미지 포함 백업**: 포스트 내 이미지를 실제 파일로 다운로드하여 함께 보관
- **글 제목별 폴더 정리**: ZIP 다운로드 시 각 글이 제목 폴더로 깔끔하게 정리
- **GitHub Repository 동기화**: 백업된 포스트를 GitHub repo에 자동 커밋
- **이메일 알림**: 백업 완료/실패 시 이메일로 알림 수신
- **서버 저장**: 포스트가 서버 DB에 안전하게 저장됨
- **영구 보존**: Velog에서 삭제해도 백업은 유지
- **완전 무료**: 모든 기능 무료 제공

## 사용 방법

### 1. 회원가입
1. [velog-backup.vercel.app](https://velog-backup.vercel.app) 접속
2. "GitHub로 시작하기" 클릭
3. GitHub 계정으로 로그인 (repo 권한 포함)

### 2. Velog 계정 연동
1. 설정 페이지에서 Velog 사용자명 입력 (예: `username`)
2. "확인" 버튼 클릭

### 3. 백업 시작
- 대시보드에서 "지금 백업하기" 버튼으로 즉시 백업
- 모든 공개 포스트가 서버에 저장됨

### 4. 포스트 확인 및 다운로드
- **포스트 보기**: 백업된 포스트 목록 확인, 개별 마크다운 다운로드
- **전체 다운로드 (ZIP)**: 모든 포스트를 이미지 포함 ZIP으로 다운로드

### 5. GitHub 동기화 (선택)
1. 설정 페이지에서 Repository 이름 입력
2. "자동 동기화" 토글 활성화
3. 이후 백업 시 자동으로 GitHub repo에 커밋

### 6. 이메일 알림 (선택)
- 설정 페이지에서 "백업 알림" 토글 활성화
- 백업 완료/실패 시 등록된 이메일로 알림 수신

## ZIP 다운로드 구조

```
velog_backup_username_20260209.zip
├── 나의 첫 번째 블로그 글/
│   ├── index.md
│   └── images/
│       ├── 1_cover.png
│       └── 2_diagram.png
├── React 성능 최적화 가이드/
│   ├── index.md
│   └── images/
│       └── 1_thumbnail.png
└── Docker 입문하기/
    └── index.md
```

## 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | Next.js 14, React 18, Tailwind CSS, TypeScript |
| Backend | FastAPI, SQLAlchemy, Python 3.11 |
| Database | PostgreSQL (Supabase) |
| Auth | GitHub OAuth, JWT |
| Deploy | Vercel (Frontend), Railway (Backend) |

## 자주 묻는 질문

**Q: 비용이 드나요?**
A: 완전 무료입니다.

**Q: 이미지도 백업되나요?**
A: 네. ZIP 다운로드 및 GitHub 동기화 시 이미지 파일이 함께 저장됩니다.

**Q: GitHub 동기화는 어떻게 작동하나요?**
A: 로그인 시 부여된 GitHub 권한으로 지정한 repo에 포스트를 자동 커밋합니다. repo가 없으면 자동 생성됩니다.

**Q: Velog 포스트가 삭제되면 백업도 삭제되나요?**
A: 아니요. 서버에 저장된 백업은 그대로 유지됩니다.

**Q: 다른 사람이 내 백업을 볼 수 있나요?**
A: 아니요. 각 사용자는 자신의 백업만 볼 수 있습니다.

**Q: 기존 사용자인데 GitHub 동기화가 안 돼요.**
A: 로그아웃 후 다시 로그인하면 repo 권한이 부여됩니다.

## 환경변수 설정

### Backend (Railway)

```env
# 필수
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key-min-32-chars
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
FRONTEND_URL=https://your-app.vercel.app

# 선택 (이메일 알림)
RESEND_API_KEY=re_your_resend_api_key
```

### Frontend (Vercel)

```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

## 보안

- GitHub OAuth 공식 인증 사용
- 비밀번호 저장 없음
- HTTPS 암호화 전송
- JWT 토큰 기반 인증 (7일 만료)
- 사용자별 데이터 격리
- 언제든지 데이터 삭제 가능

## 문의

버그 제보 및 문의: [GitHub Issues](https://github.com/dbwls99706/Velog_Backup/issues)

---

MIT License
