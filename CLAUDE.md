# OpenClaw-PARA — Claude Code 운영 규칙

이 파일은 Claude Code가 세션 시작 시 자동으로 읽는 프로젝트 규칙입니다.
아래 규칙은 사용자와 합의된 사항이며 변경 시 반드시 사용자 승인이 필요합니다.

---

## 0. claude-mem 사용 가능 여부

### 확인 방법

세션 시작 시 아래 명령으로 상태를 확인한다:

```bash
$(find ~/.claude/plugins/cache/thedotmack/claude-mem -name "claude-mem" -type f | sort -V | tail -1) status
# "Worker is running" → 사용 가능 (AVAILABLE)
# "Worker is not running" → 사용 불가 (UNAVAILABLE)
```

서버가 꺼져 있으면 아래 명령으로 시작한다:

```bash
$(find ~/.claude/plugins/cache/thedotmack/claude-mem -name "claude-mem" -type f | sort -V | tail -1) start
```

### 현재 상태

> **`AVAILABLE`** — claude-mem 서버 실행 중 (localhost:37777)
>
> 이 상태는 매 세션마다 직접 확인하여 갱신한다.
> 상태가 바뀌었으면 위 값을 `UNAVAILABLE` 또는 `AVAILABLE` 로 수정한다.

### 상태별 행동 규칙

| 상태 | 행동 |
|------|------|
| `AVAILABLE` | 파이프라인의 `🧠 AVAILABLE` 단계를 실행한다 |
| `UNAVAILABLE` | `🧠 AVAILABLE` 단계를 건너뛰고 `📁 UNAVAILABLE` 대안을 실행한다 |

> `UNAVAILABLE` 상태에서 claude-mem 도구를 호출하면 오류가 발생한다.

---

## 1. 문서 관리 규칙 (최우선)

### docs/arch/ — 설계 문서

#### docs/arch/HLD/ — 고수준 설계 (동결)

> ⛔ **이 폴더의 파일은 사용자와 명시적으로 합의하지 않으면 절대 수정할 수 없습니다.**

- 내용을 읽는 것은 허용
- 수정·삭제·생성은 사용자 요청 + 합의 후에만 가능
- 합의 없이 "현재 구현에 맞게 업데이트"하는 것도 금지
- 코드와 설계 문서가 충돌하면: **수정하지 말고 사용자에게 보고**할 것 (코드 기준으로 구현하되 문서는 건드리지 않음)

```
docs/arch/HLD/
├── README.md          ← 전체 아키텍처 다이어그램 + 문서 인덱스
├── CONTEXT.md         ← 시스템 전체 컨텍스트 (공통)
├── DECISIONS.md       ← ADR-001~007 (공통)
├── CURRENT_STATE.md   ← 현재 구현 상태 (공통)
├── plugin/            ← OpenClaw PARA Memory Plugin
│   ├── ARCHITECTURE.md  (컴포넌트, 데이터 흐름, memory-core 공존)
│   ├── DATA_MODEL.md    (PARA 파일 구조, PageIndex 서버 인덱스)
│   ├── REQUIREMENTS.md  (FR-1, FR-2)
│   └── OPERATIONS.md    (플러그인 설치, PageIndex 서버 실행)
└── hub/               ← PARA Hub (Cloud)
    ├── ARCHITECTURE.md  (Hub 컴포넌트, 흐름, Hub API)
    ├── DATA_MODEL.md    (PostgreSQL 스키마, Redis, 보존 정책)
    ├── REQUIREMENTS.md  (FR-3, FR-4, FR-5, NFR)
    └── OPERATIONS.md    (Kubernetes 배포, 보안, 모니터링, 백업)
```

#### docs/arch/LLD/ — 상세 설계 (합의 완료 후 동결)

- 기존 파일 (plugin): `plugin/memory-manager.md`, `plugin/clast-engine.md`, `plugin/intent-classifier.md`, `plugin/pageindex-search.md`, `plugin/fl-client.md`
- 기존 파일 (hub): `hub/anonymizer.md`, `hub/content-store.md`, `hub/matching-engine.md`, `hub/reputation-service.md`, `hub/access-control.md`, `hub/fl-aggregator.md`, `hub/hub-api.md`, `hub/pageindex-server.md`
- Step 3 Brainstorming 단계에서 신규 파일 초안 작성 후 사용자와 반복 합의
- **합의 완료 후에는 HLD와 동일하게 수정 금지**
- 신규 파일 위치: `plugin/` 또는 `hub/` 하위, 파일명은 컴포넌트명 (예: `plugin/new-component.md`)
- 코드와 충돌 시: 수정하지 말고 사용자에게 보고

### docs/dev-progress.md — 전체 프로젝트 진행 현황판 (단일 파일)

- `docs/arch/` 설계 문서(SRS 등) 기준으로 작성된 **전체 기능/비기능 목록**
- 각 항목에 구현 우선순위와 상태 표시: `예정` / `구현중` / `완료`
- 구현 시작·완료 시마다 반드시 업데이트
- Claude가 자유롭게 수정 가능 (단, 기능 목록 자체를 추가/삭제 할 때는 사용자 합의 필요)

### docs/todo/ — 상세 설계 문서 및 TODO

- 기능별 상세 설계 문서와 구현 TODO 파일 관리
- Claude가 자유롭게 생성·수정 가능
- 파일명 형식: `YYYY-MM-DD-{feature}-todo.md`

### docs/memory-docs/ — 로컬 메모리 + 에러 이력

claude-mem `UNAVAILABLE` 시 각 단계의 기억을 대체 저장/조회하는 폴더. 에러 이력도 통합 관리.
Claude가 자유롭게 생성·수정 가능.

```
docs/memory-docs/
├── session_세션컨텍스트/   ← 세션 시작 시 컨텍스트 복원용 메모
├── step1_현황파악/          ← 현황 파악 이력
├── step2_설계확인/          ← 유사 설계 결정 메모
├── step3_설계결정/          ← 확정된 설계 결정 + 근거
├── step6_구현패턴/          ← 구현 중 발견한 패턴 / 트레이드오프
├── step9_완료회고/          ← 기능 완료 회고 + 다음 작업 주의점
└── bugs/                    ← 에러 해결 이력 (§4 연동)
```

파일명 형식: `YYYY-MM-DD-{기능명 또는 주제}.md`

---

## 1-1. 작업 실행 규칙 (최우선)

> ⛔ **구현 범위의 자의적 확장을 절대 금지한다. 명시적 구현 명령 없이 코드를 작성하지 않는다.**
> 스킬은 `Skill` 도구로 호출하며, 1%라도 해당 스킬이 적용될 가능성이 있으면 반드시 호출한다.
> 스킬 이름을 언급만 하고 실제로 `Skill` 도구를 호출하지 않는 것은 **규칙 위반**이다.

### 구현 파이프라인 (순서 엄수)

```
[세션 시작 시 — 자동]
        └─ SessionStart hook이 claude-mem 컨텍스트 자동 로드
        └─ 이전 세션의 작업 이력, 결정사항, 패턴 복원
        🧠 AVAILABLE : claude-mem search → timeline → get_observations (3-layer)
        📁 UNAVAILABLE: docs/memory-docs/session_세션컨텍스트/ 최근 파일 읽기

Step 1. 현황 파악
        └─ docs/dev-progress.md 확인
        └─ 구현 우선순위 기준으로 다음 작업할 기능 파악
        └─ 해당 기능에 대한 과거 작업 이력 검색
        🧠 AVAILABLE : Skill claude-mem:mem-search ("기능명 past work")
        📁 UNAVAILABLE: docs/memory-docs/step1_현황파악/ 에서 기능명 관련 파일 읽기

Step 2. 설계 문서 확인
        └─ docs/arch/ 에서 해당 기능 관련 문서 읽기
        └─ 과거 유사 설계 결정 검색
        🧠 AVAILABLE : Skill claude-mem:mem-search ("기능명 design decision")
        📁 UNAVAILABLE: docs/memory-docs/step2_설계확인/ 에서 기능명 관련 파일 읽기

Step 3. Brainstorming + 상세 설계 문서 작성  ← 반복 구간 시작
        └─ docs/arch/LLD/{Requirement ID}_detail_arch.md 초안 작성
        └─ 사용자에게 제시 → 피드백 반영 → 재작성
        └─ 사용자가 상세 설계 문서 확정할 때까지 반복   ← 반복 구간 끝
        └─ 확정 후 핵심 설계 결정 저장 (LLD 파일이 공식 설계 문서가 됨)
        🔧 Skill: superpowers:brainstorming
        🧠 AVAILABLE : save_observation (확정된 설계 결정 + 근거)
        📁 UNAVAILABLE: docs/memory-docs/step3_설계결정/{date}-{feature}.md 에 저장

Step 4. TODO 작성
        └─ 확정된 상세 설계 기반으로 docs/todo/{date}-{feature}-todo.md 작성
        └─ 사용자에게 제시 → 합의
        🔧 Skill: superpowers:writing-plans

Step 5. 명시적 구현 명령 대기
        └─ "구현 시작해" 또는 이에 준하는 명령이 있을 때만 코드 작성 시작

Step 6. 구현 실행
        └─ ⚠️ 코드 작성 전 반드시 테스트 먼저 작성 (TDD 기본값, 예외 없음)
        └─ TODO 항목을 순서대로 구현
        └─ 독립 태스크가 2개 이상이면 병렬 처리
        └─ 구현 중 발견한 중요 패턴/해결책 즉시 저장
        🔧 Skill (필수): superpowers:test-driven-development
        🔧 Skill (필수): superpowers:executing-plans
        🔧 Skill (병렬 시): superpowers:dispatching-parallel-agents
        🧠 AVAILABLE : save_observation (중요 구현 패턴, 트레이드오프)
        📁 UNAVAILABLE: docs/memory-docs/step6_구현패턴/{date}-{feature}.md 에 저장

Step 7. 완료 검증
        └─ "완료됐다"고 말하기 전 반드시 검증 실행
        🔧 Skill: superpowers:verification-before-completion

Step 8. 코드 리뷰
        └─ 주요 기능 완성 후 리뷰 요청
        🔧 Skill: superpowers:requesting-code-review
        🔧 Skill (리뷰 수신 시): superpowers:receiving-code-review

Step 9. dev-progress.md 업데이트 + 브랜치 완료
        └─ 해당 기능 상태를 "구현중" → "완료" 로 변경
        └─ 기능 완료 회고 저장
        🔧 Skill: superpowers:finishing-a-development-branch
        🧠 AVAILABLE : save_observation (완료 기능 요약, 다음 작업 시 주의점)
        📁 UNAVAILABLE: docs/memory-docs/step9_완료회고/{date}-{feature}.md 에 저장
```

**버그/오류 발생 시 (언제든)**
```
        └─ 과거 유사 에러 먼저 검색
        🧠 AVAILABLE : Skill claude-mem:mem-search ("에러 키워드")
        📁 UNAVAILABLE: docs/memory-docs/bugs/ 에서 유사 파일 읽기
        🔧 Skill: superpowers:systematic-debugging
        └─ 수정 완료 후 docs/memory-docs/bugs/ 에 문서화 (§4 참조)
        🧠 AVAILABLE : save_observation (에러 패턴 + 해결책 요약)
        📁 UNAVAILABLE: docs/memory-docs/bugs/{date}-{error-keyword}.md 에 저장
```

> Step 5의 명시적 명령 없이 코드를 작성하는 것은 **규칙 위반**이다.

### 금지 행동

- TODO에 없는 파일을 수정·생성·삭제하는 것
- "더 나을 것 같아서" 구현 범위를 넘어 추가하는 것
- 설계 문서에 없는 기능을 자체 판단으로 구현하는 것
- 요청받지 않은 리팩토링, 주석 추가, 코드 정리를 하는 것
- 합의·명령 없이 스스로 다음 단계로 진행하는 것

### 상태 값 (dev-progress.md 공통)

| 상태 | 의미 |
|------|------|
| `예정` | 미착수 |
| `구현중` | Step 3~5 진행 중 또는 코딩 중 |
| `완료` | 코드 작성 및 검증 완료 |

---

## 2. 현재 구현 상태 (Design Phase)

> 상세 내용은 `docs/arch/HLD/CURRENT_STATE.md` 참조 (전체 컨텍스트: `docs/arch/HLD/CONTEXT.md`)

- **현재 단계**: Design Phase — 코드 구현 미시작
- **Plugin 런타임**: Node.js >=22 / TypeScript (OpenClaw 플러그인)
- **Plugin 저장소**: Markdown 파일 + LanceDB (로컬, `~/.openclaw/workspace/memory/`)
- **Hub 백엔드**: Python 3.11+ / FastAPI (Phase 2 예정)
- **Hub DB**: PostgreSQL 15 + Redis 7 + S3 (Phase 2 예정)
- **임베딩**: OpenAI text-embedding-3-large
- **암호화**: RSA-4096 + AES-256-GCM (Agent 전용 콘텐츠)
- **PARA 폴더**: 복수형 `projects/`, `areas/`, `resources/`, `archive/`
- **FL 프레임워크**: 미확정 (TensorFlow Federated 또는 PySyft 검토 중, Phase 3)

---

## 3. 에러 수정 — 문서화 필수

에러 수정 요청을 받았을 때 **수정 + 문서화를 한 세트**로 처리한다.

> §1-1 예외: `docs/memory-docs/bugs/` 파일 생성은 TODO 선행 없이 허용한다.
> 단, 에러 수정 범위를 넘는 코드 변경은 여전히 TODO 선행 + 구현 명령 필요.

### 처리 순서
1. `docs/todo/` 에 에러 수정 항목을 간단히 TODO로 등록
2. 에러 수정 (코드 변경)
3. `docs/memory-docs/bugs/YYYY-MM-DD-{에러-키워드}.md` 에 저장

### 문서 템플릿
```markdown
# {에러 제목}

**날짜**: YYYY-MM-DD
**관련 파일**: `파일경로`

## 증상
## 원인
## 해결 방법
## 예방 (선택)
```

---

## 4. 코드 작업 원칙

- 파일 수정 전 반드시 Read 도구로 먼저 읽을 것

### Plugin (Node.js / TypeScript)

- 테스트: `pnpm test` (vitest)
- 타입체크: `pnpm typecheck` (tsc --noEmit)
- 빌드: `pnpm build` (tsdown src/index.ts)
- 개발 감시: `pnpm dev` (tsdown --watch)
- 로컬 설치: `pnpm install:local` → `openclaw plugin install . --mode install`
- 재설치: `pnpm reinstall` → uninstall 후 재설치 (플러그인 ID: `para-memory`)
- SDK 타입 참조: `openclaw/openclaw/` 에 소스 위치 (`openclaw/README.md` 참고)
- 새 도구 추가 시: 도구 구현 → `openclaw.plugin.json` 등록 순서로 작업
- 로컬 저장소 접근은 반드시 `MemoryManager` 통해서만 (직접 `fs` 호출 금지)
- Hub API 호출은 반드시 `HubClient` 래퍼를 통해서만 (직접 `fetch` 금지)
- Agent 전용 콘텐츠는 메모리 내에서만 사용, 로컬 파일 저장 절대 금지

### Hub (Python / FastAPI)

- 테스트: `pytest` (hub/ 디렉토리에서 실행)
- 개발 서버: `uvicorn src.main:app --reload` (PYTHONPATH=hub 설정 필요)
- 의존성 설치: `pip install -r requirements.txt` 또는 `pip install -e ".[dev]"`
- DB 마이그레이션 생성: `alembic revision --autogenerate -m "설명"`
- DB 마이그레이션 적용: `alembic upgrade head`
- 새 엔드포인트 추가 시: 라우터 → 서비스 → 스키마(Pydantic) 순서로 작업
- DB 스키마 변경 시: Alembic 마이그레이션 파일 반드시 생성
- PII가 포함될 수 있는 데이터는 반드시 `AnonymizerService` 통해서만 처리
- 평판 점수 변경은 반드시 `ReputationService.process_event()` 통해서만 (직접 DB 업데이트 금지)

---

## 5. claude-mem 메모리 관리 규칙

### 조회 순서 (AVAILABLE 시 항상 이 순서)

```
1. search(query)           → ID 목록 획득
2. timeline(anchor=ID)     → 해당 ID 주변 컨텍스트 파악
3. get_observations([IDs]) → 필요한 것만 전체 내용 조회
```

> `get_observations`를 search 없이 바로 호출하지 않는다.

### 저장 기준 (save_observation)

**저장한다:**
- 확정된 설계 결정과 근거 (Step 3)
- 구현 중 발견한 중요 패턴 또는 트레이드오프 (Step 6)
- 에러 패턴 + 해결책 (§3 완료 시)
- 기능 완료 회고 및 다음 작업 시 주의점 (Step 9)
- 여러 세션에서 반복 확인된 사용자 선호 패턴

**저장하지 않는다:**
- 현재 세션의 일시적 작업 상태
- 미완성이거나 검증되지 않은 정보
- `docs/arch/`에 이미 문서화된 내용
- 단순 반복 작업 (파일 읽기, 편집 등)

---

## 6. 이 파일 수정 규칙

- 이 파일(`CLAUDE.md`) 자체도 사용자 승인 없이 수정 금지
- 새 규칙 추가 시 사용자에게 먼저 제안하고 승인 후 작성
