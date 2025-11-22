#!/bin/bash

# Velog Backup 로컬 개발 환경 설정 스크립트

set -e

echo "🚀 Velog Backup 개발 환경 설정을 시작합니다..."

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Backend 설정
echo -e "\n${YELLOW}📦 Backend 설정 중...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo "Python 가상 환경 생성 중..."
    python3 -m venv venv
fi

echo "가상 환경 활성화..."
source venv/bin/activate

echo "의존성 설치 중..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
    echo ".env 파일 생성 중..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  backend/.env 파일을 편집하여 환경 변수를 설정하세요!${NC}"
fi

cd ..

# Frontend 설정
echo -e "\n${YELLOW}📦 Frontend 설정 중...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo "npm 의존성 설치 중..."
    npm install
fi

if [ ! -f ".env.local" ]; then
    echo ".env.local 파일 생성 중..."
    cp .env.example .env.local
    echo -e "${YELLOW}⚠️  frontend/.env.local 파일을 편집하여 환경 변수를 설정하세요!${NC}"
fi

cd ..

echo -e "\n${GREEN}✅ 개발 환경 설정 완료!${NC}"
echo -e "\n다음 단계:"
echo "1. backend/.env 파일 편집 (데이터베이스, Google OAuth 설정)"
echo "2. frontend/.env.local 파일 편집 (API URL, Google OAuth 설정)"
echo ""
echo "Backend 실행:"
echo "  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "Frontend 실행:"
echo "  cd frontend && npm run dev"
