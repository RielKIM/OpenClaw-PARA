# ARCHITECTURE — Hub (PARA Hub)

**버전**: 4.1 | **날짜**: 2026-03-01 | **상태**: Design Phase

> 전체 시스템 아키텍처 개요는 `docs/arch/HLD/README.md` 참조
> Plugin 컴포넌트: `docs/arch/HLD/plugin/ARCHITECTURE.md`

---

## 1. Static View

### 1.1 서비스 컴포넌트 구조

```
┌──────────────────────────── PARA Hub ──────────────────────────────┐
│                                                                      │
│  ┌─────────────────── Gateway Layer ──────────────────────────────┐ │
│  │   Auth (OAuth 2.0 / JWT)  │  Rate Limiter  │  API Gateway      │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                  │                                    │
│  ┌─────────────────── Core Services ──────────────────────────────┐  │
│  │                                                                  │  │
│  │  ┌───────────────────┐    ┌──────────────────────────────────┐  │  │
│  │  │  Matching Engine  │    │       Anonymizer Service         │  │  │
│  │  │  (6차원 유사도)    │    │  (NER → 치환 → DP → 암호화)     │  │  │
│  │  └───────────────────┘    └──────────────────────────────────┘  │  │
│  │                                                                  │  │
│  │  ┌───────────────────┐    ┌──────────────────────────────────┐  │  │
│  │  │ Reputation Service│    │     Access Control Service       │  │  │
│  │  │ (점수 계산/등급)   │    │     (평판 기반 접근 관리)         │  │  │
│  │  └───────────────────┘    └──────────────────────────────────┘  │  │
│  │                                                                  │  │
│  │  ┌───────────────────┐    ┌──────────────────────────────────┐  │  │
│  │  │   Content Store   │    │         FL Service               │  │  │
│  │  │ (암호화 콘텐츠)    │    │    (FedAvg / SMPC 집계)          │  │  │
│  │  └───────────────────┘    └──────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                  │                                    │
│  ┌─────────────────── Data Layer ─────────────────────────────────┐  │
│  │   PostgreSQL (메타데이터)  │  Redis (캐시/세션)  │  S3 (콘텐츠) │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

---

### 1.2 서비스 간 의존성

```
API Gateway
 ├── Anonymizer Service          ← /share 요청 처리
 │    └── (NER 모델 내장, 독립 실행)
 │
 ├── Matching Engine             ← /search 요청 처리
 │    ├── PostgreSQL  (content_metadata 벡터 조회)
 │    └── Redis       (similar:{hash} 캐시, TTL:30m)
 │
 ├── Content Store               ← 암호화 콘텐츠 저장/조회
 │    ├── S3          (암호화 Blob 저장)
 │    └── PostgreSQL  (shared_content 메타데이터)
 │
 ├── Reputation Service          ← 공유/평가/활동 이벤트 처리
 │    ├── PostgreSQL  (users, reputation_events)
 │    └── Redis       (reputation:{user_id} 캐시, TTL:1h)
 │
 ├── Access Control              ← 등급별 콘텐츠 접근 필터링
 │    └── Reputation Service (등급 조회)
 │
 └── FL Service                  ← 연합 학습 그래디언트 수집/집계
      └── PostgreSQL  (fl_updates)
```

---

### 1.3 네트워크 토폴로지

> **Phase 1 (현재): Docker Compose 단일 서버 배포**
> **Phase 2+ (확장): Kubernetes 클러스터로 마이그레이션**

#### Phase 1 — Docker Compose (단일 서버)

```
인터넷 (사용자 디바이스)
    │  TLS 1.3
    ▼
Nginx  (Reverse Proxy + SSL 종료)
    │  HTTP (내부 네트워크)
    ▼
Docker Compose 네트워크 (hub_network)
    │
    ├─ gateway          :8001  ← 외부 트래픽 진입점 (인증, Rate Limit)
    │      │
    │      ▼  (내부 HTTP)
    ├─ matching         :8002  ← /search 처리
    ├─ anonymizer       :8003  ← /share 익명화 파이프라인
    ├─ reputation       :8004  ← 점수 계산 / 등급 관리
    ├─ content-store    :8005  ← 콘텐츠 저장 / 조회
    └─ fl-service       :8006  ← 연합 학습 그래디언트 집계
            │
            ▼  데이터 서비스 (hub_network 내부)
    ┌─────────────────────────────────────────┐
    │  postgres  :5432  (PostgreSQL 15)        │
    │  redis     :6379  (Redis 7)              │
    │  minio     :9000  (S3 호환 오브젝트 저장) │
    └─────────────────────────────────────────┘
```

#### Phase 2+ — Kubernetes (확장 시)

```
CloudFlare  (CDN + WAF + DDoS Protection)
    │
    ▼
AWS ALB  (SSL 종료, HTTP/2)
    │
    ▼
Kubernetes EKS
    ├─ Gateway Pod ×3+
    ├─ Matching Pod ×5+
    ├─ Anonymizer Pod ×3+
    ├─ Reputation Pod ×2+
    ├─ FL Service Pod ×2+
    └─ Content Store Pod ×2+
            │
            ▼
    RDS PostgreSQL (Multi-AZ) / ElastiCache Redis / S3
```

---

## 2. Dynamic View

### 2.1 프로젝트 공유 흐름

```
 Plugin     API GW    Anonymizer  ContentStore  Reputation   User
   │            │           │           │             │         │
   │ POST /projects/share   │           │             │         │
   │ {projectFiles, jwt}    │           │             │         │
   ├───────────►│           │           │             │         │
   │ JWT 검증   │           │           │             │         │
   │            │ anonymize(files)       │             │         │
   │            ├──────────►│           │             │         │
   │            │  1. NER 엔티티 감지    │             │         │
   │            │  2. 문맥 치환          │             │         │
   │            │  3. 차등 프라이버시     │             │         │
   │            │  4. 지식 그래프 변환    │             │         │
   │            │  5. RSA-4096 암호화    │             │         │
   │            │◄──────────┤           │             │         │
   │            │ {encrypted, confidence}│             │         │
   │            │           │           │             │         │
   │            │ (confidence < 0.95)    │             │         │
   │◄───────────┤           │ ──── 경고 응답, 공유 중단 ─────────►│
   │            │           │           │             │         │
   │            │           │ store()   │             │         │
   │            ├───────────────────────►│             │         │
   │            │           │  S3 업로드 │             │         │
   │            │           │  DB insert │             │         │
   │            │◄───────────────────────┤             │         │
   │            │           │            │ addEvent(+100)        │
   │            ├────────────────────────────────────►│         │
   │            │◄────────────────────────────────────┤         │
   │◄───────────┤ 201 {contentId, newReputation}                 │
```

---

### 2.2 유사 프로젝트 검색 흐름

```
 Plugin     API GW   AccessCtrl  Matching    ContentStore
   │            │          │          │             │
   │ POST /projects/search │          │             │
   │ {intent, type, jwt}   │          │             │
   ├───────────►│          │          │             │
   │            │ checkAccess(grade)  │             │
   │            ├──────────►│          │             │
   │            │◄──────────┤          │             │
   │            │ {allowed_min_rep}    │             │
   │            │                      │             │
   │            │ search(intent, filter)             │
   │            ├─────────────────────►│             │
   │            │  벡터 유사도 6차원 계산│             │
   │            │  Redis 캐시 확인      │             │
   │            │◄─────────────────────┤             │
   │            │ [top-K contentIds]    │             │
   │            │                                    │
   │            │ getContent(ids, agentKey)           │
   │            ├────────────────────────────────────►│
   │            │  RSA 복호화 (Hub 개인키)             │
   │            │◄────────────────────────────────────┤
   │            │ [decrypted_for_agent]               │
   │◄───────────┤ 200 {projects: [...]}               │
   │ (Agent 메모리에서만 사용, 로컬 저장 금지)
```

---

### 2.3 연합 학습 라운드 흐름

```
 FL Client    API GW     FL Service    Aggregator   GlobalModel
 (Plugin)        │             │             │            │
    │ (배치 스케줄 — 로컬 데이터로 그래디언트 계산 완료)
    │            │             │             │            │
    │ POST /fl/gradients       │             │            │
    │ {encrypted_gradient, model_version}    │            │
    ├───────────►│             │             │            │
    │            │ store + 검증│             │            │
    │            ├────────────►│             │            │
    │◄───────────┤ 202 Accepted│             │            │
    │            │             │             │            │
    │            │ (n ≥ 최소 기여자 수 충족 시 집계 트리거)
    │            │             │ aggregate() │            │
    │            │             ├────────────►│            │
    │            │             │  SMPC 또는 동형암호 집계 │
    │            │             │◄────────────┤            │
    │            │             │ updateModel │            │
    │            │             ├─────────────────────────►│
    │            │             │◄─────────────────────────┤
    │            │             │ {new_model_version}       │
    │◄───────────┤ 모델 업데이트 알림 (WebSocket)          │
    │ 개선된 글로벌 모델 수신    │             │            │
```

---

### 2.4 평판 업데이트 흐름

```
 Event Source  Reputation Svc   PostgreSQL      Redis      WebSocket
  (공유/평가)        │               │              │            │
      │               │               │              │            │
      │ addEvent(userId, type, points) │              │            │
      ├──────────────►│               │              │            │
      │               │ INSERT reputation_events      │            │
      │               ├──────────────►│              │            │
      │               │◄──────────────┤              │            │
      │               │               │              │            │
      │               │ 점수 재계산 + 등급 확인        │            │
      │               │               │              │            │
      │               │ UPDATE users SET              │            │
      │               │  reputation_score, grade      │            │
      │               ├──────────────►│              │            │
      │               │◄──────────────┤              │            │
      │               │               │              │            │
      │               │ DEL reputation:{userId}  캐시 무효화       │
      │               ├────────────────────────────►│            │
      │               │◄────────────────────────────┤            │
      │               │               │              │            │
      │               │ (등급 변경 시 실시간 알림)                  │
      │               ├────────────────────────────────────────►  │
      │◄──────────────┤  {event:"grade_up", newGrade:"Trusted"}   │
```

---

## 3. 컴포넌트 상세

### Matching Engine

| 항목 | 내용 |
|------|------|
| 역할 | 유사 공유 프로젝트/영역 검색 |
| 입력 | 새 프로젝트 메타데이터, 사용자 의도 |
| 출력 | 유사도 점수가 있는 상위-K 유사 프로젝트 |
| 유사도 차원 | 의도, 도메인, 구조, 시간, 리소스, 패턴 (6차원) |

### Anonymizer Service

PII 제거 파이프라인 (5단계):

```
1. Named Entity Recognition (NER)
   → 이름, 주소, 전화, 이메일, 날짜, 조직, 위치 감지

2. 문맥 익명화 (Contextual Anonymization)
   → [PERSON_1], [LOCATION_TYPE], [DATE_RANGE] 등으로 대체

3. 차등 프라이버시 (Differential Privacy)
   → 수치 데이터에 보정된 노이즈 추가 (ε = 0.1 ~ 1.0)

4. 의미론적 보존 (Semantic Preservation)
   → 실행 가능한 지식(무엇, 언제, 어떻게), 패턴, 워크플로우 유지

5. Agent 전용 포맷팅
   → 구조화된 지식 그래프 JSON 변환
   → Hub 공개키(RSA-4096)로 암호화
```

### Reputation Service

평판 점수 계산식:

```
평판 = Σ (구성요소 × 가중치)

• 콘텐츠 품질 (40%): average_rating × total_shares
• 콘텐츠 수량 (25%): log(1 + shared_projects_count) × 100
• 커뮤니티 참여 (20%): (helpful_votes + comments) × 0.5
• 일관성 (10%): max(0, min(30, current_streak)) × 3.33
• 도움 (5%): (resolved_issues + accepted_reports) × 5
```

### Federated Learning Service

```
각 사용자 디바이스 (로컬)
  → 로컬 모델 훈련 (원본 데이터 유지)
  → 암호화된 그래디언트만 Hub로 전송

Hub Aggregator
  → SMPC 또는 동형암호로 집계
  → 글로벌 모델 업데이트
  → 원본 데이터 노출 없음

개선된 글로벌 모델 배포
  → 모든 사용자에게 집계 통찰 제공
```

### Content Store

| 항목 | 내용 |
|------|------|
| 저장 형식 | 암호화된 지식 그래프 JSON |
| 암호화 | RSA-4096 + AES-256 |
| 접근 | Hub만 복호화 가능, Agent는 메모리 내 콘텐츠 수신 후 즉시 폐기 |
| 감사 | 모든 접근 로그: agentId, contentId, timestamp |
| 삭제 | 90일 미활동 자동 삭제, 사용자 요청 시 7일 내 삭제 |

### Access Control Service

| 항목 | 내용 |
|------|------|
| 역할 | 평판 기반 접근 관리 |
| 처리 순서 | 사용자 평판 등급 확인 → 요청 콘텐츠 매칭 → 등급에 따른 필터링 |
| 기록 | 모든 접근 시도 감사 로그 |

---

## 4. Hub API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/v1/projects/search` | 유사 프로젝트 검색 |
| POST | `/api/v1/projects/share` | 익명화된 프로젝트 업로드 |
| GET | `/api/v1/projects/{id}/content` | Agent 전용 콘텐츠 조회 |
| GET | `/api/v1/users/reputation` | 평판 점수 조회 |
| POST | `/api/v1/ratings` | 공유 콘텐츠 평가 |
| POST | `/api/v1/fl/gradients` | 연합 학습 그래디언트 전송 |
| GET | `/api/v1/fl/insights/{category}` | 집계 통찰 조회 (n ≥ 10) |

**인증**: OAuth 2.0 (OpenClaw 계정) + JWT 토큰
