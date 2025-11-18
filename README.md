# 📚 Velog Backup

> Velog 블로그 포스트를 Google Drive에 자동으로 백업하는 무료 웹 서비스

[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

## ✨ 주요 기능

- 🔐 **안전한 인증**: Google 계정으로 간편 로그인
- 📝 **자동 백업**: Velog 포스트를 Markdown 형식으로 자동 백업
- ☁️ **Google Drive 저장**: 본인의 Google Drive에 안전하게 보관
- 🔄 **실시간 동기화**: 포스트 수정 시 자동으로 업데이트
- 📊 **백업 현황 확인**: 대시보드에서 백업 통계 확인
- 🆓 **완전 무료**: 모든 기능 무료 제공

## 🚀 사용 방법

### 1. 회원가입
1. [velog-backup.vercel.app](https://velog-backup.vercel.app) 접속
2. "Google로 시작하기" 클릭
3. Google 계정으로 로그인

### 2. Velog 계정 연동
1. 대시보드에서 "Velog 연동" 클릭
2. Velog 사용자명 입력 (예: `@username`)
3. "확인" 버튼 클릭

### 3. Google Drive 연동
1. "Google Drive 연동" 버튼 클릭
2. Google Drive 권한 승인
3. 자동으로 "Velog Backup" 폴더 생성됨

### 4. 백업 시작
- **자동 백업**: 매일 자동으로 백업됨
- **수동 백업**: "지금 백업하기" 버튼으로 즉시 백업

## 📂 백업된 파일 구조

```
Google Drive/
└── Velog Backup/
    ├── 2024-01-15_first-post.md
    ├── 2024-01-20_react-hooks.md
    └── 2024-02-01_typescript-tips.md
```

각 Markdown 파일에는 다음 정보가 포함됩니다:
- 제목, 작성일, 태그
- 전체 포스트 내용
- 썸네일 이미지 URL

## 🔒 보안 및 프라이버시

- ✅ Google OAuth 2.0 공식 인증 사용
- ✅ 비밀번호 저장 안 함 (Google 계정만 사용)
- ✅ Google Drive 접근 권한: 앱이 생성한 파일만 접근
- ✅ 모든 데이터는 HTTPS로 암호화 전송
- ✅ 언제든지 연동 해제 가능

## 💡 자주 묻는 질문 (FAQ)

<details>
<summary><strong>Q: 비용이 드나요?</strong></summary>
A: 완전 무료입니다! 모든 기능을 무료로 사용할 수 있습니다.
</details>

<details>
<summary><strong>Q: Google Drive 용량을 얼마나 사용하나요?</strong></summary>
A: Markdown 텍스트 파일은 매우 작습니다. 100개 포스트도 1MB 미만입니다.
</details>

<details>
<summary><strong>Q: 이미지도 백업되나요?</strong></summary>
A: 현재는 이미지 URL만 저장됩니다. 이미지 파일 백업은 곧 추가될 예정입니다.
</details>

<details>
<summary><strong>Q: 백업 주기를 변경할 수 있나요?</strong></summary>
A: 기본은 하루 1회이며, 설정에서 변경 가능합니다.
</details>

<details>
<summary><strong>Q: 개인정보가 안전한가요?</strong></summary>
A: 네! Google OAuth만 사용하며, 비밀번호는 저장하지 않습니다. Google Drive 접근도 최소 권한만 요청합니다.
</details>

<details>
<summary><strong>Q: Velog 포스트가 삭제되면 백업도 삭제되나요?</strong></summary>
A: 아니요. Google Drive의 백업 파일은 그대로 유지됩니다.
</details>

## 🛠️ 기술 스택

### Frontend
- **Next.js 14** - React 프레임워크
- **Tailwind CSS** - 스타일링
- **Vercel** - 무료 호스팅 및 도메인

### Backend
- **FastAPI** - Python 웹 프레임워크
- **Railway** - 무료 서버 호스팅
- **Supabase** - 무료 PostgreSQL 데이터베이스
- **Upstash Redis** - 무료 Redis (작업 큐)

## 🌟 로드맵

- [x] Google 로그인
- [x] Velog 포스트 크롤링
- [x] Google Drive 백업
- [x] 자동 백업 스케줄러
- [ ] GitHub 백업 추가
- [ ] 이미지 파일 백업
- [ ] 이메일 알림
- [ ] 백업 히스토리 관리

## 🤝 기여하기

이슈와 PR은 언제나 환영합니다!

## 📄 라이선스

MIT License - 자유롭게 사용하세요!

## 📧 문의

- 이슈: [GitHub Issues](https://github.com/dbwls99706/Velog_Backup/issues)
- 이메일: support@velog-backup.com

---

Made with ❤️ for Velog users
