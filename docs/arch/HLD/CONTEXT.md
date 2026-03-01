# CONTEXT — OpenClaw-PARA

**버전**: 3.0 | **날짜**: 2026-03-01 | **상태**: Design Phase

---

## 1. 프로젝트 개요

**OpenClaw-PARA**는 OpenClaw의 메모리 구조를 PARA 방법론으로 변환하는 플러그인과, 익명화된 프로젝트 템플릿 및 지식 공유를 위한 프라이버시 보존 네트워크(PARA Hub)로 구성된 시스템입니다.

### 핵심 목표

- 사용자의 프로젝트 기반 메모리를 PARA 방법론으로 조직화
- 유사한 과거 프로젝트의 공유 지식을 활용하여 **사전 예방적 프로젝트 생성** 가능
- **Agent 전용 콘텐츠 접근**을 통해 완전한 프라이버시 유지

---

## 2. 범위

### 포함 범위

- PARA Memory System과의 사용자 상호작용
- PARA Hub를 통한 지식 공유 워크플로우
- Reputation 기반 인센티브 메커니즘
- Agent 전용 콘텐츠 접근 패턴
- 프라이버시 보존 데이터 흐름

### 제외 범위

- OpenClaw 코어 엔진 수정
- 개인 식별 정보(PII) 공유
- 금전적 거래/토큰 시스템

---

## 3. 시스템 액터

| 액터 | 설명 |
|------|------|
| **End User** | OpenClaw를 사용하여 프로젝트/영역 생성, Agent와 상호작용, Hub에 콘텐츠 공유, 평판 구축 |
| **OpenClaw Agent** | 사용자 의도 분류, Hub에서 유사 콘텐츠 검색, 사전 예방적 프로젝트 구조 생성, Agent 전용 암호화 콘텐츠 접근 |
| **PARA Hub System** | 익명화된 콘텐츠 저장, 유사 프로젝트 매칭, 평판 점수 관리, 프라이버시 정책 시행 |
| **Anonymizer Service** | PII 제거, 차등 프라이버시 적용, Agent 전용 포맷 변환, 콘텐츠 암호화 |

---

## 4. 핵심 혁신

### 4.1 사전 예방적 프로젝트 생성

사용자가 새 프로젝트 의도를 표현하면, Agent가 PARA Hub에서 유사한 익명화 프로젝트를 검색하고, 집합적 지식(체크리스트, 타임라인, 예산, 주의사항)을 미리 채운 프로젝트 구조를 자동 생성합니다.

### 4.2 Agent 전용 콘텐츠

공유 콘텐츠는 Hub의 RSA-4096 공개키로 암호화되어 AI Agent만 접근 가능합니다. 인간 사용자는 절대 원본 암호화 콘텐츠를 볼 수 없으며, Agent는 추론 후 즉시 콘텐츠를 폐기합니다.

### 4.3 평판 기반 인센티브

금전 거래 없이 기여(콘텐츠 공유, 커뮤니티 참여)를 통해 평판을 쌓고, 평판 등급에 따라 프리미엄 콘텐츠 접근 권한을 획득합니다.

---

## 5. 기술 스택

### 클라이언트 (PARA Memory Plugin)

| 영역 | 기술 |
|------|------|
| 런타임 | Node.js 18+ |
| 언어 | TypeScript |
| 저장소 | Markdown 파일 + LanceDB |
| AI/ML | OpenAI API (text-embedding-3-large), spaCy (NER) |
| 인덱싱 | LanceDB (벡터 + FTS), JSON |

### 서버 (PARA Hub)

| 영역 | 기술 |
|------|------|
| 런타임 | Python 3.11+ |
| 프레임워크 | FastAPI, Pydantic, AsyncIO |
| AI/ML | PyTorch, Transformers, spaCy, scikit-learn, TensorFlow Federated |
| 데이터베이스 | PostgreSQL 15, Redis 7 |
| ORM | SQLAlchemy, Alembic |
| 저장소 | AWS S3 / MinIO |
| 보안 | RSA-4096, AES-256, Google DP, PySyft, HashiCorp Vault |

### 인프라

| 영역 | 기술 |
|------|------|
| 오케스트레이션 | Kubernetes (EKS), Docker, Helm |
| CI/CD | GitHub Actions, ArgoCD |
| 모니터링 | Prometheus, Grafana, ELK Stack, Jaeger |
| 클라우드 | AWS, CloudFlare |

---

## 6. PARA 메모리 구조

```
memory/
├── projects/    ← 활성 프로젝트 (마감일 있음, 단기 목표)
├── areas/       ← 진행 중 책임 영역 (지속적 관리)
├── resources/   ← 참고 자료 (토픽별 정보)
└── archive/     ← 완료/비활성 프로젝트
```

### 프로젝트 폴더 구조 예시

```
memory/projects/okinawa-trip-2026/
├── index.md           ← 메타데이터 (생성일, 키워드, 상태)
├── 2026-03-01.md      ← 첫 번째 일일 로그
├── checklist.md       ← Hub에서 가져온 체크리스트
├── budget.md          ← 예산 분석
└── itinerary.md       ← 추천 일정
```

---

## 7. 제약사항

| 제약 | 내용 |
|------|------|
| 프라이버시 | 공유 시 PII 제거율 > 99.5% 보장 |
| 보안 | Agent 전용 콘텐츠는 인간 사용자에게 절대 노출 금지 |
| 규제 | GDPR, 개인정보보호법 준수 |
| 기술 | OpenClaw 플러그인 API 제약 준수 |
| 연합학습 | n>10 소스에서만 집계 통찰 제공 |
