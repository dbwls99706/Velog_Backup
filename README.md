# Velog Backup

> Velog 블로그 포스트를 서버에 무료로 백업하는 웹 서비스

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![License](https://img.shields.io/badge/License-MIT-green)

[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

## 주요 기능

- **안전한 인증**: Google 계정으로 간편 로그인
- **서버 저장소**: 포스트가 서버 DB에 직접 저장 (Google Drive 연동 불필요)
- **영구 보존**: Velog에서 포스트를 삭제해도 백업은 유지
- **개인정보 보호**: 각 사용자는 자신의 포스트만 열람 가능
- **마크다운 다운로드**: 언제든지 .md 파일로 다운로드
- **완전 무료**: 모든 기능 무료 제공

## 사용 방법

### 1. 회원가입
1. [velog-backup.vercel.app](https://velog-backup.vercel.app) 접속
2. "Google로 시작하기" 클릭
3. Google 계정으로 로그인

### 2. Velog 계정 연동
1. 대시보드에서 "Velog 연동" 섹션 확인
2. Velog 사용자명 입력 (예: `username`)
3. "확인" 버튼 클릭

### 3. 백업 시작
- "지금 백업하기" 버튼으로 즉시 백업
- 모든 포스트가 서버에 저장됨

### 4. 포스트 확인 및 다운로드
1. 대시보드에서 "포스트 보기" 클릭
2. 백업된 포스트 목록 확인
3. 개별 포스트 클릭하여 내용 확인
4. 마크다운 파일로 다운로드 가능

## 저장 방식

모든 포스트는 서버 데이터베이스에 마크다운 형식으로 저장됩니다:

- 제목, 작성일, 태그
- 전체 포스트 내용 (frontmatter 포함)
- 썸네일 이미지 URL

Velog에서 원본 포스트를 삭제해도 백업된 내용은 서버에 그대로 유지됩니다.

## 보안 및 프라이버시

- Google OAuth 2.0 공식 인증 사용
- 비밀번호 저장 안 함 (Google 계정만 사용)
- 각 사용자는 자신의 백업 포스트만 접근 가능
- 모든 데이터는 HTTPS로 암호화 전송
- 언제든지 데이터 삭제 가능

## 자주 묻는 질문 (FAQ)

### Q: 비용이 드나요?
A: 완전 무료입니다! 모든 기능을 무료로 사용할 수 있습니다.

### Q: 저장 용량 제한이 있나요?
A: Supabase 무료 플랜(500MB)을 사용합니다. 텍스트 위주의 마크다운 파일은 용량이 매우 작아 일반적인 사용에 충분합니다.

### Q: 이미지도 백업되나요?
A: 현재는 이미지 URL만 저장됩니다. 이미지 파일은 Velog 서버에서 제공됩니다.

### Q: Velog 포스트가 삭제되면 백업도 삭제되나요?
A: 아니요. 서버에 저장된 백업은 그대로 유지됩니다. 이것이 이 서비스의 핵심 기능입니다.

### Q: 다른 사람이 내 백업을 볼 수 있나요?
A: 아니요. 각 사용자는 자신의 백업 포스트만 볼 수 있습니다.

### Q: 백업 파일을 내 컴퓨터에 저장할 수 있나요?
A: 네! 각 포스트를 마크다운(.md) 파일로 다운로드할 수 있습니다.

## 기술 스택

### Frontend
- **Next.js 14** - React 프레임워크
- **Tailwind CSS** - 스타일링
- **Vercel** - 무료 호스팅 및 도메인

### Backend
- **FastAPI** - Python 웹 프레임워크
- **Railway** - 무료 서버 호스팅
- **Supabase** - 무료 PostgreSQL 데이터베이스

## 기여하기

이슈와 PR은 언제나 환영합니다!

## 라이선스

MIT License - 자유롭게 사용하세요!

## 문의

- 이슈: [GitHub Issues](https://github.com/dbwls99706/Velog_Backup/issues)

---

Made with love for Velog users
