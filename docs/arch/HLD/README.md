# OpenClaw-PARA — HLD (High Level Design)

> ⛔ 이 폴더의 파일은 사용자와 명시적으로 합의하지 않으면 절대 수정할 수 없습니다.
> 코드와 설계 문서가 충돌하면 수정하지 말고 사용자에게 보고할 것.

---

## 문서 구조

### 공통 (시스템 전체)

| 파일 | 설명 |
|------|------|
| `CONTEXT.md` | 프로젝트 전체 컨텍스트 (목적, 범위, 핵심 혁신, 기술 스택) |
| `DECISIONS.md` | 핵심 설계 결정 이력 및 근거 (ADR-001~ADR-007) |
| `CURRENT_STATE.md` | 현재 구현 상태 및 다음 단계 |

### plugin/ — OpenClaw PARA Memory Plugin

| 파일 | 설명 |
|------|------|
| `plugin/ARCHITECTURE.md` | 플러그인 컴포넌트, 데이터 흐름, 메모리 공존 구조 |
| `plugin/DATA_MODEL.md` | 로컬 PARA 파일 구조 및 PageIndex 서버 인덱스 |
| `plugin/REQUIREMENTS.md` | FR-1 (PARA 조직화), FR-2 (Intent 검색) |
| `plugin/OPERATIONS.md` | 플러그인 설치/배포, PageIndex 서버 실행 |

### hub/ — PARA Hub

| 파일 | 설명 |
|------|------|
| `hub/ARCHITECTURE.md` | Hub 컴포넌트, 데이터 흐름, Hub API |
| `hub/DATA_MODEL.md` | Hub DB 스키마 (PostgreSQL), Redis 캐시, 데이터 보존 |
| `hub/REQUIREMENTS.md` | FR-3 (지식 공유), FR-4 (평판), FR-5 (FL), NFR |
| `hub/OPERATIONS.md` | Hub 배포 인프라, 보안, 모니터링, 백업 |

---

## 전체 시스템 아키텍처

```
┌──────────────────────────────────────────────────────┐
│                사용자 디바이스 (Local)                 │
│                                                        │
│  ┌───────────────────────────────────────────────┐   │
│  │              OpenClaw Agent (Plugin)           │   │
│  │  ┌────────────┐  ┌──────────────┐  ┌────────┐ │   │
│  │  │  Intent    │  │  PageIndex   │  │ CLAST  │ │   │
│  │  │ Classifier │  │Search Client │  │ Engine │ │   │
│  │  └────────────┘  └──────┬───────┘  └────────┘ │   │
│  │  ┌──────────────────────│──────────────────┐   │   │
│  │  │      Memory Manager  │                  │   │   │
│  │  └──────────────────────│──────────────────┘   │   │
│  └─────────────────────────│──────────────────────┘   │
│                     HTTP localhost:37779               │
│  ┌──────────────────────────────────────────────┐    │
│  │   PageIndex Local Server (Python / Docker)   │    │
│  │   VectifyAI pageindex 라이브러리 래핑         │    │
│  │   - Markdown → 헤더 트리 파싱                │    │
│  │   - LLM 추론 기반 관련 노드 검색             │    │
│  │   저장소: ~/.openclaw/workspace/.pageindex/   │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  ┌───────────────────────────────────────────────┐   │
│  │          PARA Memory (Local Storage)           │   │
│  │  memory/                                       │   │
│  │  ├─ projects/   (활성 프로젝트)               │   │
│  │  ├─ areas/      (진행 중 책임)                │   │
│  │  ├─ resources/  (참고 자료)                   │   │
│  │  └─ archive/    (완료 프로젝트)               │   │
│  │  저장소: Markdown                              │   │
│  └───────────────────────────────────────────────┘   │
└─────────────────────┬────────────────────────────────┘
                      │ HTTPS / WSS (암호화)
                      ▼
┌──────────────────────────────────────────┐
│           PARA Hub (Cloud Service)        │
│                                           │
│  ┌── Gateway Layer ──────────────────┐   │
│  │  Auth  │  Rate Limit  │  API GW   │   │
│  └────────────────────────────────────┘  │
│                                           │
│  ┌── Core Services ──────────────────┐   │
│  │  Matching Engine  │  Anonymizer   │   │
│  │  Reputation Svc   │  FL Service   │   │
│  │  Content Store    │  Access Ctrl  │   │
│  └────────────────────────────────────┘  │
│                                           │
│  ┌── Data Layer ─────────────────────┐   │
│  │  PostgreSQL  │  Redis  │  S3/Blob │   │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

---

## 시스템 요약

**OpenClaw-PARA**는 두 개의 주요 컴포넌트로 구성됩니다.

1. **OpenClaw PARA Memory Plugin** — 사용자 디바이스에서 실행되는 로컬 플러그인
   - PARA 방법론(Projects / Areas / Resources / Archive)으로 OpenClaw 메모리 조직화
   - Intent 분류, 계층적 문서 검색(PageIndex 서버), 프로젝트 수명주기 자동 관리
   - `memory-core`와 공존 (메모리 슬롯 비경쟁, ADR-007)

2. **PARA Hub** — 익명화된 지식 공유 클라우드 서비스
   - PII 제거 후 Agent 전용 암호화 콘텐츠 저장 및 공유
   - 평판 기반 접근 제어 (금전 거래 없음)
   - 연합 학습(Federated Learning)으로 집계 통찰 제공

## 핵심 원칙

| 원칙 | 설명 |
|------|------|
| Privacy-First | 공유 콘텐츠는 완전 익명화, AI Agent 전용 암호화 접근 |
| Local-First | 원본 데이터는 디바이스에 보관, 패턴만 공유 |
| Reputation-Driven | 기여 기반 접근 제어, 크레딧/토큰 없음 |
| Proactive | 유사 프로젝트 지식으로 사전 예방적 프로젝트 생성 |

---
**버전**: 4.0 | **날짜**: 2026-03-01 | **상태**: Design Phase
