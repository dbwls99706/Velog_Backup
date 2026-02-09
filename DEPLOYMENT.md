# 배포 가이드

무료 서비스로 Velog Backup을 배포하는 방법입니다.

## 사전 준비

1. **GitHub 계정** (OAuth 및 코드 호스팅)
2. **Supabase 계정** (무료 PostgreSQL)
3. **Railway 계정** (백엔드 호스팅)
4. **Vercel 계정** (프론트엔드 호스팅)
5. **Resend 계정** (이메일 알림, 선택)

---

## 1. GitHub OAuth 설정

### GitHub OAuth App 생성

1. [GitHub Developer Settings](https://github.com/settings/developers) 접속
2. **OAuth Apps > New OAuth App** 클릭
3. 앱 정보 입력:
   - Application name: `Velog Backup`
   - Homepage URL: `https://your-app.vercel.app`
   - Authorization callback URL: `https://your-app.vercel.app/auth/callback`
4. **Register application** 클릭
5. **Client ID** 복사
6. **Generate a new client secret** 클릭하여 **Client Secret** 복사

> 개발 환경에서는 callback URL을 `http://localhost:3000/auth/callback`으로 설정하세요.

---

## 2. Supabase (Database) 설정

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

## 3. Railway (Backend) 배포

1. [Railway](https://railway.app/) 접속 및 GitHub로 로그인
2. **New Project > Deploy from GitHub repo** 클릭
3. 저장소 선택: `Velog_Backup`
4. **Add variables** 클릭하여 환경 변수 설정:

```env
DATABASE_URL=postgresql://postgres:password@host:5432/postgres
SECRET_KEY=your-super-secret-key-min-32-characters-long
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
FRONTEND_URL=https://your-app.vercel.app
ENVIRONMENT=production
RESEND_API_KEY=re_your_resend_api_key  # 선택: 이메일 알림용
```

5. **Settings > Environment**에서 Root Directory 설정:
   - Root Directory: `backend`

6. 배포 완료 후 도메인 복사:
   ```
   https://your-backend.up.railway.app
   ```

---

## 4. Vercel (Frontend) 배포

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
```

6. **Deploy** 클릭
7. 배포 완료 후 도메인 확인:
   ```
   https://your-app.vercel.app
   ```

---

## 5. GitHub OAuth Callback URL 업데이트

1. [GitHub Developer Settings](https://github.com/settings/developers)로 돌아가기
2. 생성한 OAuth App 클릭
3. **Authorization callback URL**을 Vercel 도메인으로 업데이트:
   ```
   https://your-app.vercel.app/auth/callback
   ```
4. **Update application** 클릭

---

## 배포 완료!

이제 다음 URL로 접속할 수 있습니다:

- **프론트엔드**: https://your-app.vercel.app
- **백엔드 API**: https://your-backend.up.railway.app/docs

---

## 문제 해결

### 500 Error (Backend)
- Railway 로그 확인: `Settings > Deployments > Logs`
- 환경 변수가 올바른지 확인

### CORS Error
- Backend `FRONTEND_URL`이 정확한지 확인
- 추가 도메인이 필요하면 `CORS_ORIGINS` 환경 변수에 쉼표로 구분하여 추가

### Database Connection Error
- Supabase DATABASE_URL 확인
- Supabase 프로젝트가 활성 상태인지 확인

### GitHub 로그인 실패
- `GITHUB_CLIENT_ID`와 `GITHUB_CLIENT_SECRET`이 올바른지 확인
- Authorization callback URL이 정확한지 확인

---

## 비용 (무료 플랜 제한)

| 서비스 | 무료 플랜 제한 |
|--------|---------------|
| Supabase | 500MB DB, 2GB 트래픽/월 |
| Railway | $5 무료 크레딧/월, 500시간 |
| Vercel | 100GB 대역폭/월, 무제한 배포 |
| Resend | 3,000 이메일/월 |

**참고**: 개인 사용 기준으로 충분합니다!
