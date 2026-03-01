# OpenClaw-PARA — 전체 프로젝트 진행 현황판

> 이 파일은 `docs/arch/HLD/` 설계 문서 기준으로 작성된 전체 기능/비기능 목록입니다.
> 구현 시작·완료 시마다 반드시 업데이트합니다.
> 기능 목록 자체를 추가/삭제할 때는 사용자 합의 필요.

**마지막 업데이트**: 2026-03-01

---

## 상태 범례

| 상태 | 의미 |
|------|------|
| `예정` | 미착수 |
| `구현중` | Step 3~5 진행 중 또는 코딩 중 |
| `완료` | 코드 작성 및 검증 완료 |

---

## Phase 0 — 스켈레톤 / 설계 기반

| 항목 | 상태 |
|------|------|
| HLD 전체 문서 작성 | `완료` |
| LLD plugin/ 전체 (5개) | `완료` |
| LLD hub/ 전체 (8개) | `완료` |
| plugin/ 소스 스켈레톤 | `완료` |
| hub/ 소스 스켈레톤 | `완료` |
| pageindex-server/ 스켈레톤 | `완료` |
| ADR-002 개정 — 인덱싱 아키텍처 v3 확정 (PageIndex 서버) | `완료` |
| ADR-007 신규 — para-memory × memory-core 공존 설계 | `완료` |
| HLD plugin/ hub/ 디렉터리 분리 (B안) | `완료` |
| ADR-008 신규 — Hub 1차 배포 Docker Compose 확정 | `완료` |

---

## Phase 1 — Plugin MVP

### FR-1: PARA 메모리 조직화

| ID | 기능 | 우선순위 | 상태 |
|----|------|----------|------|
| FR-1.1 | PARA 폴더 구조 초기화 (projects/areas/resources/archive) | P0 | `예정` |
| FR-1.2 | 프로젝트 메타데이터 생성 (index.md, 일일 로그) | P0 | `예정` |
| FR-1.3 | CLAST 자동 상태 전환 (30일 미활동 → 아카이브) | P1 | `예정` |
| FR-1.3 | CLAST 마감일 경과 처리 | P1 | `예정` |
| FR-1.3 | CLAST 아카이브 재활성화 | P2 | `예정` |

### FR-2: Intent 기반 검색

| ID | 기능 | 우선순위 | 상태 |
|----|------|----------|------|
| FR-2.1 | Intent Classifier (임베딩 기반 1차 분류) | P0 | `예정` |
| FR-2.1 | Intent Classifier LLM 폴백 (신뢰도 < 0.7) | P1 | `예정` |
| FR-2.2 | PageIndex Search (LLM 추론 기반, PageIndex 서버 연동) | P0 | `예정` |
| FR-2.3 | 전체 메모리 폴백 검색 | P1 | `예정` |

### 슬래시 명령

| 명령 | 우선순위 | 상태 |
|------|----------|------|
| `/new-project {title}` | P0 | `예정` |
| `/new-area {title}` | P0 | `예정` |
| `/search {query}` | P0 | `예정` |
| `/archive {id}` | P1 | `예정` |
| `/restore {id}` | P1 | `예정` |
| `/classify {query}` (디버그) | P2 | `예정` |

### PageIndex 로컬 서버 (`pageindex-server/`)

> LLD: `docs/arch/LLD/hub/pageindex-server.md`
> Python 직접 실행 또는 Docker 컨테이너 실행 지원

| 기능 | 우선순위 | 상태 |
|------|----------|------|
| FastAPI 서버 + `/health` 엔드포인트 | P0 | `예정` |
| `store.py` — 트리 JSON 저장/조회 | P0 | `예정` |
| `indexer.py` — pageindex `md_to_tree()` 연동 | P0 | `예정` |
| `searcher.py` — LLM 추론 검색 (gpt-4o-mini) | P0 | `예정` |
| `/index` 엔드포인트 구현 | P0 | `예정` |
| `/search` 엔드포인트 구현 | P0 | `예정` |
| `/reindex` 엔드포인트 구현 | P1 | `예정` |
| `/index` DELETE 엔드포인트 구현 | P1 | `예정` |
| Dockerfile + docker-compose.yml 검증 | P1 | `예정` |

---

## Phase 2 — Hub 연동

### FR-3: PARA Hub 지식 공유

| ID | 기능 | 우선순위 | 상태 |
|----|------|----------|------|
| FR-3.1 | NER 기반 PII 감지 및 제거 | P0 | `예정` |
| FR-3.1 | 차등 프라이버시 적용 (ε = 0.5 기본) | P0 | `예정` |
| FR-3.1 | 익명화 신뢰도 점수 + 사용자 경고 | P0 | `예정` |
| FR-3.2 | Agent 전용 지식 그래프 JSON 변환 | P0 | `예정` |
| FR-3.2 | RSA-4096 + AES-256 콘텐츠 암호화 | P0 | `예정` |
| FR-3.2 | Agent 전용 접근 (메모리 내, 로컬 저장 금지) | P0 | `예정` |
| FR-3.3 | 다차원 유사도 매칭 엔진 (6차원) | P1 | `예정` |
| FR-3.4 | `/share-to-hub {name}` 명령 | P0 | `예정` |
| FR-3.4 | 익명화 미리보기 | P1 | `예정` |
| FR-3.4 | `/no-hub-suggestions` 명령 | P1 | `예정` |

### FR-4: 평판 시스템

| ID | 기능 | 우선순위 | 상태 |
|----|------|----------|------|
| FR-4.1 | 평판 점수 계산 (5개 구성요소) | P0 | `예정` |
| FR-4.2 | 등급 결정 (Newbie ~ Master) | P0 | `예정` |
| FR-4.3 | 이벤트 처리 (공유, 평가 수신 등) | P0 | `예정` |
| FR-4.4 | 미활동 패널티 배치 처리 | P1 | `예정` |
| FR-4.5 | 배지 시스템 (6종) | P2 | `예정` |
| - | WebSocket 실시간 평판 알림 | P1 | `예정` |

### Hub API

| 엔드포인트 | 우선순위 | 상태 |
|-----------|----------|------|
| POST `/api/v1/projects/search` | P0 | `예정` |
| POST `/api/v1/projects/share` | P0 | `예정` |
| GET `/api/v1/projects/{id}/content` | P0 | `예정` |
| GET `/api/v1/users/reputation` | P0 | `예정` |
| POST `/api/v1/ratings` | P1 | `예정` |

### Hub 인프라

| 기능 | 우선순위 | 상태 |
|------|----------|------|
| docker-compose.yml 작성 (전체 서비스 + MinIO) | P0 | `예정` |
| Nginx Reverse Proxy 설정 (SSL 종료) | P0 | `예정` |
| OAuth 2.0 인증 (OpenClaw 계정 연동) | P0 | `예정` |
| JWT 토큰 발급 및 검증 | P0 | `예정` |
| API Rate Limiting | P0 | `예정` |
| PostgreSQL 스키마 생성 | P0 | `예정` |
| Redis 캐시 설정 | P0 | `예정` |
| MinIO 오브젝트 저장소 설정 (S3 호환) | P0 | `예정` |
| docker-compose.monitoring.yml (Prometheus + Grafana + Loki) | P1 | `예정` |
| Kubernetes 배포 설정 (Phase 2+ 마이그레이션) | P2 | `예정` |

---

## Phase 3 — 고급 기능

### FR-5: 연합 학습

| ID | 기능 | 우선순위 | 상태 |
|----|------|----------|------|
| FR-5 | 로컬 FL 클라이언트 (그래디언트 계산) | P2 | `예정` |
| FR-5 | 암호화된 그래디언트 전송 | P2 | `예정` |
| FR-5 | Hub FL Aggregator (FedAvg) | P2 | `예정` |
| FR-5 | SMPC 기반 안전 집계 | P3 | `예정` |
| FR-5 | 집계 통찰 API (`/api/v1/fl/insights/{category}`) | P2 | `예정` |
| FR-5 | n < 10 시 통찰 제공 거부 | P2 | `예정` |

### 기타 고급 기능

| 기능 | 우선순위 | 상태 |
|------|----------|------|
| 커스텀 템플릿 요청 (Trusted+ 등급) | P2 | `예정` |
| 커뮤니티 소개 (Expert+ 등급) | P3 | `예정` |
| 전문가 프로필 페이지 (Master 등급) | P3 | `예정` |
| 플러그인 핫 리로드 | P2 | `예정` |

---

## 비기능 요구사항 달성 현황

| NFR | 목표 | 상태 |
|-----|------|------|
| PageIndex 검색 응답 | < 2s (LLM API latency 포함) | `예정` |
| 프로젝트 생성 | < 2초 | `예정` |
| Hub 쿼리 응답 | < 3초 | `예정` |
| PII 감지율 | > 99.5% | `예정` |
| Hub 가용성 | > 99.9% | `예정` |
| 차등 프라이버시 | ε = 0.1~1.0 | `예정` |
| Intent 분류 정확도 | > 95% | `예정` |
