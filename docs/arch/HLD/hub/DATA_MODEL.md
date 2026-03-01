# DATA_MODEL — Hub (PARA Hub)

**버전**: 3.0 | **날짜**: 2026-03-01 | **상태**: Design Phase

> Plugin 데이터 모델: `docs/arch/HLD/plugin/DATA_MODEL.md`

---

## 1. Hub 데이터 모델 (PostgreSQL)

### 1.1 SharedContent

```sql
CREATE TABLE shared_content (
    id              UUID PRIMARY KEY,
    owner_user_id   UUID NOT NULL REFERENCES users(id),
    category        TEXT NOT NULL,  -- project | area | resource
    encrypted_data  BYTEA NOT NULL, -- RSA-4096 + AES-256 암호화
    pii_removed_at  TIMESTAMP,
    pii_confidence  FLOAT,          -- 익명화 신뢰도 (0.0 ~ 1.0)
    access_level    TEXT,           -- public | reputation_gated
    min_reputation  INTEGER DEFAULT 0,
    use_count       INTEGER DEFAULT 0,
    avg_rating      FLOAT,
    created_at      TIMESTAMP DEFAULT NOW(),
    last_accessed   TIMESTAMP,
    expires_at      TIMESTAMP       -- 90일 미활동 시 삭제
);
```

### 1.2 ContentMetadata

```sql
CREATE TABLE content_metadata (
    id              UUID PRIMARY KEY,
    content_id      UUID REFERENCES shared_content(id),
    intent_type     TEXT,           -- travel | parenting | finance | ...
    domain_tags     TEXT[],         -- 도메인 태그 배열
    complexity      TEXT,           -- simple | moderate | complex
    duration_days   INTEGER,
    resource_level  TEXT,           -- low | medium | high
    similarity_embedding VECTOR(1536)  -- 매칭용 벡터
);
```

### 1.3 User (Hub 사용자 프로필)

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY,
    openclaw_user_id TEXT UNIQUE NOT NULL,
    reputation_score INTEGER DEFAULT 0,
    reputation_grade TEXT DEFAULT 'Newbie',  -- Newbie | Contributor | Trusted | Expert | Master
    shared_count    INTEGER DEFAULT 0,
    streak_days     INTEGER DEFAULT 0,
    last_share_date DATE,
    badges          TEXT[],
    created_at      TIMESTAMP DEFAULT NOW(),
    last_active     TIMESTAMP
);
```

### 1.4 ReputationEvent

```sql
CREATE TABLE reputation_events (
    id          UUID PRIMARY KEY,
    user_id     UUID REFERENCES users(id),
    event_type  TEXT NOT NULL,  -- share | use | rate | bug_report | ...
    points      INTEGER NOT NULL,
    content_id  UUID REFERENCES shared_content(id),
    occurred_at TIMESTAMP DEFAULT NOW()
);
```

### 1.5 AccessLog

```sql
CREATE TABLE access_logs (
    id          UUID PRIMARY KEY,
    agent_id    TEXT NOT NULL,
    content_id  UUID REFERENCES shared_content(id),
    user_id     UUID REFERENCES users(id),
    access_type TEXT,   -- view | download | federated
    accessed_at TIMESTAMP DEFAULT NOW()
);
```

### 1.6 FederatedLearningUpdate

```sql
CREATE TABLE fl_updates (
    id              UUID PRIMARY KEY,
    user_id         UUID REFERENCES users(id),
    model_version   TEXT NOT NULL,
    gradient_hash   TEXT NOT NULL,   -- 무결성 검증
    contributed_at  TIMESTAMP DEFAULT NOW()
);
```

---

## 2. Redis 캐시 구조

```
session:{user_id}                → 세션 정보 (TTL: 24h)
reputation:{user_id}             → 평판 점수 캐시 (TTL: 1h)
similar:{intent_hash}            → 유사 프로젝트 검색 결과 캐시 (TTL: 30m)
ratelimit:{user_id}:{endpoint}   → API 요청 제한 카운터 (TTL: 1m)
```

---

## 3. 데이터 볼륨 추정

| 항목 | 추정 |
|------|------|
| 활성 사용자 | 1,000만+ |
| 공유 콘텐츠 | 사용자당 평균 5개 = 5,000만+ |
| 암호화 콘텐츠 평균 크기 | ~50KB |
| S3 총 저장소 | ~2.5TB |
| PostgreSQL 크기 | ~500GB (메타데이터) |
| Redis 메모리 | ~50GB (핫 캐시) |

---

## 4. 데이터 보존 정책

| 데이터 | 보존 기간 | 삭제 조건 |
|--------|-----------|-----------|
| 공유 콘텐츠 | 최대 90일 미활동 | 미활동 90일 또는 사용자 요청 (7일 지연) |
| 접근 로그 | 90일 | 롤링 삭제 |
| 평판 이력 | 영구 | 사용자 계정 삭제 시 익명화 |
| FL 그래디언트 | 집계 완료 후 즉시 삭제 | - |
| 세션 데이터 | 24시간 | TTL 만료 |
