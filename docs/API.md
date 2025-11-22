# API 문서

Velog Backup API 엔드포인트 문서입니다.

## Base URL

```
Production: https://your-backend.up.railway.app/api/v1
Development: http://localhost:8000/api/v1
```

## 인증

모든 보호된 엔드포인트는 JWT Bearer 토큰이 필요합니다.

```http
Authorization: Bearer <access_token>
```

---

## 인증 (Authentication)

### POST /auth/google

Google OAuth로 로그인

**Request Body:**
```json
{
  "token": "google_id_token"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

---

## 사용자 (User)

### GET /user/me

현재 로그인한 사용자 정보 조회

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "홍길동",
  "velog_username": "username"
}
```

### POST /user/velog/verify

Velog 사용자명 검증 및 연동

**Request Body:**
```json
{
  "username": "username"
}
```

**Response:**
```json
{
  "message": "Velog 계정이 연동되었습니다",
  "username": "username"
}
```

---

## 백업 (Backup)

### POST /backup/trigger

수동 백업 시작 - 포스트를 서버 DB에 저장

**Request Body:**
```json
{
  "force": false
}
```

**Response:**
```json
{
  "message": "백업이 시작되었습니다"
}
```

### GET /backup/stats

백업 통계 조회

**Response:**
```json
{
  "total_posts": 10,
  "last_backup": "2024-11-20T10:30:00Z",
  "velog_connected": true,
  "recent_logs": [
    {
      "id": 1,
      "status": "success",
      "posts_total": 10,
      "posts_new": 2,
      "posts_updated": 3,
      "posts_skipped": 5,
      "message": "새 포스트 2개, 업데이트 3개",
      "started_at": "2024-11-20T10:30:00Z",
      "completed_at": "2024-11-20T10:31:00Z"
    }
  ]
}
```

### GET /backup/logs?limit=20

백업 로그 목록 조회

**Query Parameters:**
- `limit`: 조회할 로그 수 (기본값: 20)

**Response:**
```json
[
  {
    "id": 1,
    "status": "success",
    "posts_total": 10,
    "posts_new": 2,
    "posts_updated": 3,
    "posts_skipped": 5,
    "message": "새 포스트 2개, 업데이트 3개",
    "started_at": "2024-11-20T10:30:00Z",
    "completed_at": "2024-11-20T10:31:00Z"
  }
]
```

---

## 포스트 (Posts)

### GET /backup/posts?page=1&limit=20

백업된 포스트 목록 조회 (자신의 포스트만)

**Query Parameters:**
- `page`: 페이지 번호 (기본값: 1)
- `limit`: 페이지당 포스트 수 (기본값: 20)

**Response:**
```json
{
  "posts": [
    {
      "id": 1,
      "slug": "my-first-post",
      "title": "나의 첫 번째 포스트",
      "content": "---\ntitle: ...",
      "thumbnail": "https://...",
      "tags": "[\"React\", \"JavaScript\"]",
      "velog_published_at": "2024-01-15T10:00:00Z",
      "last_backed_up": "2024-11-20T10:30:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "limit": 20
}
```

### GET /backup/posts/{post_id}

백업된 특정 포스트 조회 (자신의 포스트만)

**Response:**
```json
{
  "id": 1,
  "slug": "my-first-post",
  "title": "나의 첫 번째 포스트",
  "content": "---\ntitle: 나의 첫 번째 포스트\ndate: 2024-01-15\ntags:\n  - React\n  - JavaScript\n---\n\n# 서론\n...",
  "thumbnail": "https://...",
  "tags": "[\"React\", \"JavaScript\"]",
  "velog_published_at": "2024-01-15T10:00:00Z",
  "last_backed_up": "2024-11-20T10:30:00Z"
}
```

### DELETE /backup/posts/{post_id}

백업된 포스트 삭제 (자신의 포스트만)

**Response:**
```json
{
  "message": "포스트가 삭제되었습니다"
}
```

---

## 에러 응답

### 400 Bad Request
```json
{
  "detail": "잘못된 요청입니다"
}
```

### 401 Unauthorized
```json
{
  "detail": "인증이 필요합니다"
}
```

### 404 Not Found
```json
{
  "detail": "포스트를 찾을 수 없습니다"
}
```

### 500 Internal Server Error
```json
{
  "detail": "서버 오류가 발생했습니다"
}
```

---

## Rate Limiting

현재 Rate Limiting은 적용되지 않았습니다.

---

## Interactive API 문서

FastAPI는 자동으로 Interactive API 문서를 생성합니다:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
