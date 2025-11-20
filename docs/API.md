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
  "velog_username": "username",
  "has_google_drive": true
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

## Google Drive

### GET /google/auth-url

Google Drive OAuth URL 생성

**Response:**
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/auth?...",
  "state": "random_state"
}
```

### POST /google/connect

Google Drive 연동

**Request Body:**
```json
{
  "code": "oauth_authorization_code"
}
```

**Response:**
```json
{
  "message": "Google Drive가 연동되었습니다",
  "folder_id": "drive_folder_id"
}
```

### DELETE /google/disconnect

Google Drive 연동 해제

**Response:**
```json
{
  "message": "Google Drive 연동이 해제되었습니다"
}
```

---

## 백업 (Backup)

### POST /backup/trigger

수동 백업 시작

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
  "google_drive_connected": true,
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
  "detail": "리소스를 찾을 수 없습니다"
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

현재 Rate Limiting은 적용되지 않았습니다. 향후 추가될 예정입니다.

## Webhooks

현재 Webhook은 지원하지 않습니다. 향후 추가될 예정입니다.

---

## Interactive API 문서

FastAPI는 자동으로 Interactive API 문서를 생성합니다:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

프로덕션 환경에서는 보안을 위해 비활성화됩니다.
