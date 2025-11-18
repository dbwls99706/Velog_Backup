# 🚀 배포 가이드

무료 서비스로 Velog Backup을 배포하는 방법입니다.

## 📋 사전 준비

1. **GitHub 계정**
2. **Google Cloud Platform 계정** (OAuth용)
3. **Supabase 계정** (무료 PostgreSQL)
4. **Upstash 계정** (무료 Redis)
5. **Railway 계정** (백엔드 호스팅)
6. **Vercel 계정** (프론트엔드 호스팅)

---

## 1️⃣ Google OAuth 설정

### Google Cloud Console 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성: "Velog Backup"

### OAuth 2.0 클라이언트 ID 생성

1. **API 및 서비스 > 사용자 인증 정보**로 이동
2. **+ 사용자 인증 정보 만들기 > OAuth 클라이언트 ID** 클릭
3. **OAuth 동의 화면 구성** (최초 1회)
   - 사용자 유형: 외부
   - 앱 이름: Velog Backup
   - 사용자 지원 이메일: 본인 이메일
   - 범위 추가: `userinfo.email`, `userinfo.profile`
   - 테스트 사용자 추가 (본인 이메일)

4. **OAuth 클라이언트 ID 생성**
   - 애플리케이션 유형: **웹 애플리케이션**
   - 이름: Velog Backup Web Client
   - **승인된 리디렉션 URI** 추가:
     ```
     http://localhost:3000/dashboard
     https://your-app.vercel.app/dashboard
     ```

5. **클라이언트 ID**와 **클라이언트 보안 비밀** 복사 → 나중에 사용

### Google Drive API 활성화

1. **API 및 서비스 > 라이브러리**로 이동
2. "Google Drive API" 검색
3. **사용** 버튼 클릭

---

## 2️⃣ Supabase (Database) 설정

1. [Supabase](https://supabase.com/) 접속 및 회원가입
2. **New Project** 클릭
3. 프로젝트 정보 입력:
   - Name: velog-backup
   - Database Password: 강력한 비밀번호 생성
   - Region: Northeast Asia (Seoul)
4. 프로젝트 생성 완료 (1-2분 소요)
5. **Settings > Database**에서 Connection String 복사:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@[HOST]:5432/postgres
   ```

---

## 3️⃣ Upstash (Redis) 설정

1. [Upstash](https://upstash.com/) 접속 및 회원가입
2. **Create Database** 클릭
3. 설정:
   - Name: velog-backup-redis
   - Type: Regional
   - Region: ap-northeast-1 (Tokyo)
   - TLS: Enabled
4. **REST API** 탭에서 `UPSTASH_REDIS_REST_URL` 복사
5. 또는 **Details** 탭에서 Redis URL 복사:
   ```
   redis://default:[PASSWORD]@[HOST]:6379
   ```

---

## 4️⃣ Railway (Backend) 배포

1. [Railway](https://railway.app/) 접속 및 GitHub로 로그인
2. **New Project > Deploy from GitHub repo** 클릭
3. 저장소 선택: `Velog_Backup`
4. **Add variables** 클릭하여 환경 변수 설정:

```env
DATABASE_URL=postgresql://postgres:password@host:5432/postgres
REDIS_URL=redis://default:password@host:6379
SECRET_KEY=your-super-secret-key-min-32-characters-long
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
FRONTEND_URL=https://your-app.vercel.app
ENVIRONMENT=production
```

5. **Settings > Environment**에서 Root Directory 설정:
   - Root Directory: `backend`

6. 배포 완료 후 도메인 복사:
   ```
   https://your-backend.up.railway.app
   ```

---

## 5️⃣ Vercel (Frontend) 배포

1. [Vercel](https://vercel.com/) 접속 및 GitHub로 로그인
2. **Add New > Project** 클릭
3. GitHub 저장소 선택: `Velog_Backup`
4. **Configure Project**:
   - Framework Preset: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

5. **Environment Variables** 추가:

```env
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

6. **Deploy** 클릭
7. 배포 완료 후 도메인 확인:
   ```
   https://your-app.vercel.app
   ```

---

## 6️⃣ Google OAuth 리다이렉션 URI 업데이트

1. Google Cloud Console로 돌아가기
2. **API 및 서비스 > 사용자 인증 정보**
3. OAuth 2.0 클라이언트 ID 편집
4. **승인된 리디렉션 URI**에 Vercel 도메인 추가:
   ```
   https://your-app.vercel.app/dashboard
   ```
5. **저장**

---

## ✅ 배포 완료!

이제 다음 URL로 접속할 수 있습니다:

- **프론트엔드**: https://your-app.vercel.app
- **백엔드 API**: https://your-backend.up.railway.app/docs

---

## 🔍 문제 해결

### 500 Error (Backend)
- Railway 로그 확인: `Settings > Deployments > Logs`
- 환경 변수가 올바른지 확인

### CORS Error
- Backend `FRONTEND_URL`이 정확한지 확인
- Google OAuth 리다이렉션 URI 확인

### Database Connection Error
- Supabase DATABASE_URL 확인
- Supabase 프로젝트가 활성 상태인지 확인

### Google Login 실패
- `GOOGLE_CLIENT_ID`가 프론트엔드 환경 변수에 있는지 확인
- Google Cloud Console에서 OAuth 동의 화면이 게시되었는지 확인

---

## 💰 비용 (무료 플랜 제한)

| 서비스 | 무료 플랜 제한 |
|--------|---------------|
| Supabase | 500MB DB, 2GB 트래픽/월 |
| Upstash | 10,000 명령/일 |
| Railway | $5 무료 크레딧/월, 500시간 |
| Vercel | 100GB 대역폭/월, 무제한 배포 |

**참고**: 개인 사용 기준으로 충분합니다!

---

## 🎉 축하합니다!

Velog Backup 서비스가 완전히 무료로 배포되었습니다!
