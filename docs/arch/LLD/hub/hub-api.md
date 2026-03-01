# Hub API — 상세 설계

**컴포넌트**: PARA Hub
**관련 요구사항**: FR-3.4, FR-4, FR-5
**날짜**: 2026-03-01
**상태**: Draft (사용자 합의 전)

---

## 1. 개요

PARA Hub의 FastAPI 기반 REST API 전체 엔드포인트 명세. 인증, 에러 처리, Rate Limiting 공통 정책 포함.

---

## 2. 공통 정책

### 인증

- **OAuth 2.0**: OpenClaw 계정 연동
- **JWT Access Token**: 만료 1시간
- **Refresh Token**: 만료 30일 (Secure HttpOnly Cookie)
- **API Key**: Agent 전용 접근 (헤더 `X-Agent-Id`)

모든 엔드포인트는 `Authorization: Bearer {jwt}` 필수 (공개 엔드포인트 제외).

### Rate Limiting

| 대상 | 제한 |
|------|------|
| 일반 사용자 | 100 req/min |
| Trusted 이상 | 300 req/min |
| Agent 전용 콘텐츠 조회 | 50 req/min |

### 공통 에러 응답

```json
{
  "error":   "REPUTATION_INSUFFICIENT",
  "message": "평판 300점 필요 (현재 250점)",
  "hint":    "프로젝트 공유(+100점)로 평판을 올려보세요."
}
```

| HTTP 코드 | 에러 코드 | 설명 |
|-----------|-----------|------|
| 400 | `VALIDATION_ERROR` | 요청 형식 오류 |
| 401 | `UNAUTHORIZED` | 인증 토큰 없음/만료 |
| 403 | `REPUTATION_INSUFFICIENT` | 평판 부족 |
| 403 | `ACCESS_DENIED` | 등급 부족 |
| 404 | `CONTENT_NOT_FOUND` | 콘텐츠 없음 |
| 429 | `RATE_LIMIT_EXCEEDED` | 요청 한도 초과 |

---

## 3. 프로젝트 API

### POST `/api/v1/projects/search`

유사 프로젝트 검색.

**Request**:
```json
{
  "intent":         "travel",
  "domain_tags":    ["okinawa", "family", "1week"],
  "complexity":     "moderate",
  "resource_level": "medium",
  "duration_days":  7
}
```

**Response 200**:
```json
{
  "matches": [
    {
      "content_id":       "uuid",
      "similarity_score": 0.92,
      "intent_type":      "travel",
      "domain":           "asia/japan",
      "access_allowed":   true,
      "rating":           4.8,
      "use_count":        23
    }
  ]
}
```

---

### POST `/api/v1/projects/share`

익명화된 프로젝트 업로드.

**Request**:
```json
{
  "project_id":          "okinawa-trip-2026",
  "anonymized_content":  "<base64 encrypted>",
  "metadata": {
    "intent_type":    "travel",
    "domain_tags":    ["okinawa", "family"],
    "complexity":     "moderate",
    "duration_days":  7,
    "resource_level": "medium"
  },
  "access_level": "public"
}
```

**Response 201**:
```json
{
  "content_id":       "uuid",
  "reputation_delta": 100,
  "new_score":        350,
  "new_grade":        "Trusted",
  "new_badges":       ["🌱 Seedling"]
}
```

---

### GET `/api/v1/projects/{content_id}/content`

Agent 전용 암호화 콘텐츠 조회.

**Headers**: `X-Agent-Id: {agent_id}`

**Response 200**:
```json
{
  "encrypted_content": "<base64>",
  "encrypted_key":     "<base64>",
  "nonce":             "<base64>"
}
```

> 응답은 메모리 내에서만 사용, 로컬 저장 금지. `Cache-Control: no-store` 헤더 포함.

---

### POST `/api/v1/ratings`

공유 콘텐츠 평가.

**Request**:
```json
{
  "content_id": "uuid",
  "rating":     4,
  "comment":    "오키나와 여행에 실제 도움됐어요"
}
```

**Response 200**:
```json
{
  "accepted":          true,
  "reputation_delta":  0,
  "owner_delta":       100
}
```

---

## 4. 사용자 / 평판 API

### GET `/api/v1/users/me/reputation`

내 평판 점수 및 등급 조회.

**Response 200**:
```json
{
  "score":    350,
  "grade":    "Trusted",
  "badges":   ["🌱 Seedling"],
  "breakdown": {
    "quality":     80,
    "quantity":    120,
    "engagement":  90,
    "consistency": 40,
    "helpfulness": 20
  },
  "permissions": [
    "premium_content",
    "custom_template_requests"
  ]
}
```

---

## 5. 연합 학습 API

### POST `/api/v1/fl/gradients`

암호화된 그래디언트 제출.

**Request**:
```json
{
  "model_version":       "v1.2.3",
  "encrypted_gradients": "<base64>",
  "sample_size":         5
}
```

**Response 202** (비동기 처리):
```json
{ "accepted": true, "batch_id": "uuid" }
```

---

### GET `/api/v1/fl/model/latest`

최신 글로벌 모델 조회.

**Response 200**:
```json
{
  "version":  "v1.2.3",
  "patterns": [...]
}
```

---

### GET `/api/v1/fl/insights/{category}/{subcategory}`

집계 통찰 조회.

**Response 200**:
```json
{
  "available":   true,
  "patterns":    [...],
  "warnings":    [...],
  "disclaimer":  "156개의 익명화된 경험 기반. 전문 조언 아님."
}
```

**Response 200 (데이터 부족)**:
```json
{
  "available": false,
  "reason":    "데이터 부족 (7/10)"
}
```

---

## 6. WebSocket

**연결**: `wss://hub.para.app/ws?token={jwt}`

**서버 → 클라이언트 이벤트**:

```json
// 평판 업데이트
{ "event": "reputation_update", "data": { "delta": 100, "new_score": 350, "new_grade": "Trusted" } }

// 배지 수여
{ "event": "badge_awarded", "data": { "badge": "🌱 Seedling" } }

// 콘텐츠 사용 알림
{ "event": "content_used", "data": { "content_id": "uuid", "use_count": 11 } }
```
