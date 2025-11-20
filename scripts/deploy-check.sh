#!/bin/bash

# Velog Backup 프로덕션 배포 체크리스트

echo "🔍 프로덕션 배포 전 체크리스트"
echo "================================"

# 색상
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

checks_passed=0
checks_failed=0

check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
        ((checks_passed++))
    else
        echo -e "${RED}❌ $1${NC}"
        ((checks_failed++))
    fi
}

# Backend 체크
echo -e "\n${YELLOW}Backend 체크:${NC}"

if [ -f "backend/.env" ]; then
    if grep -q "your-super-secret-key-change-this" backend/.env; then
        echo -e "${RED}❌ SECRET_KEY가 변경되지 않았습니다${NC}"
        ((checks_failed++))
    else
        echo -e "${GREEN}✅ SECRET_KEY 설정됨${NC}"
        ((checks_passed++))
    fi
else
    echo -e "${RED}❌ backend/.env 파일이 없습니다${NC}"
    ((checks_failed++))
fi

if grep -q "GOOGLE_CLIENT_ID" backend/.env 2>/dev/null; then
    echo -e "${GREEN}✅ Google OAuth 설정 확인됨${NC}"
    ((checks_passed++))
else
    echo -e "${RED}❌ Google OAuth 설정 필요${NC}"
    ((checks_failed++))
fi

# Frontend 체크
echo -e "\n${YELLOW}Frontend 체크:${NC}"

if [ -f "frontend/.env.local" ]; then
    echo -e "${GREEN}✅ frontend/.env.local 존재${NC}"
    ((checks_passed++))
else
    echo -e "${RED}❌ frontend/.env.local 파일이 없습니다${NC}"
    ((checks_failed++))
fi

# 문서 체크
echo -e "\n${YELLOW}문서 체크:${NC}"

[ -f "README.md" ] && check "README.md 존재" || check "README.md 없음"
[ -f "DEPLOYMENT.md" ] && check "DEPLOYMENT.md 존재" || check "DEPLOYMENT.md 없음"
[ -f "LICENSE" ] && check "LICENSE 존재" || check "LICENSE 없음"
[ -f "SECURITY.md" ] && check "SECURITY.md 존재" || check "SECURITY.md 없음"

# 결과
echo -e "\n================================"
echo -e "통과: ${GREEN}${checks_passed}${NC}"
echo -e "실패: ${RED}${checks_failed}${NC}"

if [ $checks_failed -eq 0 ]; then
    echo -e "\n${GREEN}🎉 모든 체크 통과! 배포 준비 완료!${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  일부 체크가 실패했습니다. 위 내용을 확인해주세요.${NC}"
    exit 1
fi
