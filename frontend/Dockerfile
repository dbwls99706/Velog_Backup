FROM node:18-alpine

WORKDIR /app

# 의존성 파일 복사
COPY package*.json ./

# 의존성 설치
RUN npm install

# 앱 코드 복사
COPY . .

# 포트 노출
EXPOSE 3000

# 개발 모드 실행
CMD ["npm", "run", "dev"]
