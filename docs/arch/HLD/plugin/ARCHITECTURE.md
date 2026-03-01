# ARCHITECTURE — Plugin (OpenClaw PARA Memory Plugin)

**버전**: 5.0 | **날짜**: 2026-03-01 | **상태**: Design Phase

> 전체 시스템 아키텍처 개요는 `docs/arch/HLD/README.md` 참조
> Hub 컴포넌트: `docs/arch/HLD/hub/ARCHITECTURE.md`

---

## 1. Static View

### 1.1 컴포넌트 구조

```
┌──────────────────────────────────────────────────────────┐
│                   para-memory Plugin                      │
│                                                           │
│  ┌───────────────────────────────────────────────────┐   │
│  │                   index.ts                        │   │
│  │          (진입점 / 도구·명령 오케스트레이터)         │   │
│  └──────────┬──────────────┬────────────┬────────────┘   │
│             │              │            │                  │
│  ┌──────────▼────┐  ┌──────▼───┐  ┌────▼──────────────┐ │
│  │    Intent     │  │  CLAST   │  │   Memory Manager  │ │
│  │  Classifier   │  │  Engine  │  │                   │ │
│  └──────────┬────┘  └──────────┘  └────┬──────────────┘ │
│             │                           │                  │
│             │                  ┌────────▼──────────────┐  │
│             │                  │ PageIndex Search Engine│  │
│             │                  │    (HTTP 클라이언트)    │  │
│             │                  └────────┬──────────────┘  │
└─────────────│──────────────────────────│──────────────────┘
              │                          │ HTTP localhost:37779
              ▼                          ▼
         OpenAI API               PageIndex Server
    (text-embedding-3-large       (Python / Docker)
      + LLM 폴백)
```

---

### 1.2 소스 파일 구조

```
plugin/src/
├── index.ts                    ← 진입점: onLoad(), 도구·슬래시 명령 등록
├── types.ts                    ← 공유 타입 (PARACategory, SearchResult, PluginConfig, ...)
├── memory/
│   ├── memory-manager.ts       ← PARA 폴더/파일 CRUD, PageIndex 인덱싱 위임
│   └── sqlite-index.ts         ← 아키텍처 변천 기록 (현재 미사용)
├── search/
│   └── pageindex-search.ts     ← PageIndex 서버 HTTP 클라이언트
├── intent/
│   └── intent-classifier.ts    ← OpenAI 임베딩 기반 의도 분류
└── clast/
    └── clast-engine.ts         ← 프로젝트 수명주기 상태 전환 엔진
```

---

### 1.3 의존성

```
index.ts
 ├── IntentClassifier
 │    ├── OpenAI text-embedding-3-large   ← 임베딩 유사도 분류 (1차)
 │    └── OpenAI LLM (gpt-4o-mini)        ← 신뢰도 < 0.7 시 폴백
 │
 ├── MemoryManager
 │    └── PageIndexSearchEngine
 │         └── PageIndex Server           ← HTTP → localhost:37779
 │                                          (미실행 시 graceful degradation)
 └── CLASTEngine
      └── MemoryManager.readMetadata()    ← 항목 메타데이터 직접 참조

외부 의존성 요약:
  - OpenAI API        필수  (Intent Classifier)
  - PageIndex Server  선택  (검색 기능, 미실행 시 검색 불가)
  - PARA Hub API      선택  (Phase 2, 미연결 시 로컬 전용 동작)
```

---

### 1.4 배포 컨텍스트

```
사용자 디바이스
 │
 ├─ OpenClaw Agent  (Node.js, Jiti 런타임 transpile)
 │   └─ para-memory plugin
 │       ├─ 파일시스템  :  ~/.openclaw/workspace/memory/
 │       └─ 설정 파일   :  openclaw.plugin.json
 │
 └─ PageIndex Server  (별도 프로세스)
     ├─ 실행 옵션 A  :  uvicorn server:app --host 127.0.0.1 --port 37779
     ├─ 실행 옵션 B  :  docker-compose up -d
     └─ 인덱스 저장  :  ~/.openclaw/workspace/.pageindex/
```

---

## 2. Dynamic View

### 2.1 플러그인 초기화 흐름

```
OpenClaw            para-memory         PageIndex
  Agent              onLoad()             Server
    │                    │                   │
    │   플러그인 로드     │                   │
    ├───────────────────►│                   │
    │                    │  GET /health      │
    │                    ├──────────────────►│
    │                    │  (timeout: 2s)    │
    │                    │◄── {status:"ok"} ─┤  healthy = true
    │                    │  (실패 시) ────────┤  healthy = false
    │                    │                   │
    │                    │ 도구 등록:
    │                    │   classify_intent
    │                    │   search_project
    │                    │   check_transition
    │                    │
    │                    │ 슬래시 명령 등록:
    │                    │   /new-project
    │                    │   /new-area
    │                    │   /search
    │                    │   /archive  /restore
    │                    │
    │                    │ 시스템 프롬프트 주입 (메모리 라우팅 가이드)
    │◄───────────────────┤
    │   onLoad 완료       │
```

---

### 2.2 `/new-project {title}` 명령 흐름

```
 User    Handler    IntentClassifier  MemoryManager  PageIndexSvr   Hub
   │        │               │               │               │         │
   │ /new-project "오키나와 여행"            │               │         │
   ├───────►│               │               │               │         │
   │        │ classify()    │               │               │         │
   │        ├──────────────►│               │               │         │
   │        │◄──────────────┤               │               │         │
   │        │ {intent:"project",            │               │         │
   │        │  confidence:0.92}             │               │         │
   │        │               │               │               │         │
   │        │  (hubEnabled) Hub 유사 프로젝트 쿼리           │         │
   │        ├──────────────────────────────────────────────────────►  │
   │        │◄────────────────────────────────────────────────────── │
   │        │  [similar_projects]           │               │         │
   │        │               │               │               │         │
   │        │  createProject({title, hubContentIds})        │         │
   │        ├──────────────────────────────►│               │         │
   │        │               │ mkdir + index.md 생성         │         │
   │        │               │ YYYY-MM-DD.md 생성            │         │
   │        │               │               │               │         │
   │        │               │ updateIndex() │               │         │
   │        │               ├──────────────────────────────►│         │
   │        │               │◄──────────────────────────────┤         │
   │        │◄──────────────────────────────┤               │         │
   │        │ {project}     │               │               │         │
   │◄───────┤ 프로젝트 생성 완료 + Hub 제안 표시             │         │
```

---

### 2.3 `/search {query}` 명령 흐름

```
 User    Handler   IntentClassifier  PageIndexEngine  PageIndexSvr
   │        │               │                │               │
   │ /search "여행 예산 계획" │                │               │
   ├───────►│               │                │               │
   │        │ classify()    │                │               │
   │        ├──────────────►│                │               │
   │        │◄──────────────┤                │               │
   │        │ {intent:"project",             │               │
   │        │  confidence:0.85,              │               │
   │        │  target:"여행"}                │               │
   │        │               │                │               │
   │        │  searchInProject(projectId, query)             │
   │        ├───────────────────────────────►│               │
   │        │                                │ POST /search  │
   │        │                                │ {query, project_id, limit:5}
   │        │                                ├──────────────►│
   │        │                                │  LLM 추론 중  │
   │        │                                │◄──────────────┤
   │        │                                │ {results}     │
   │        │◄───────────────────────────────┤               │
   │        │                                │               │
   │        │  (결과 없음 또는 top score < 0.3 → fallback)
   │        │                                │               │
   │        │  searchAll(query, category)    │               │
   │        ├───────────────────────────────►│               │
   │        │                                │ POST /search  │
   │        │                                │ {query, category:null}
   │        │                                ├──────────────►│
   │        │                                │◄──────────────┤
   │        │◄───────────────────────────────┤               │
   │◄───────┤ 검색 결과 표시 (최대 5개)       │               │
```

---

### 2.4 CLAST 상태 전환 체크 흐름

```
OpenClaw     CLASTEngine       MemoryManager
  Agent           │                  │
    │ (세션 시작 또는 명시적 호출)
    │  checkTransitions()             │
    ├──────────────►│                 │
    │               │ listByCategory('projects')
    │               ├────────────────►│
    │               │◄────────────────┤
    │               │ [projectMeta[]] │
    │               │                 │
    │               │  각 항목 평가:   │
    │               │ ┌───────────────────────────────────────┐
    │               │ │ last_accessed + 30일 < today          │
    │               │ │   → {type:"archive", reason:"30일 미활동"}
    │               │ │                                       │
    │               │ │ deadline < today                      │
    │               │ │   → {type:"archive_or_extend"}        │
    │               │ │                                       │
    │               │ │ status == "archived" && 접근 감지     │
    │               │ │   → {type:"reactivate"}               │
    │               │ └───────────────────────────────────────┘
    │◄──────────────┤
    │ [TransitionRecommendation[]]
    │
    │ (권장 목록이 있으면 사용자에게 알림 제시)
```

---

## 3. 컴포넌트 상세

### Intent Classifier

| 항목 | 내용 |
|------|------|
| 역할 | 사용자 쿼리를 Project / Area / Resource / Unknown으로 분류 |
| 입력 | 사용자 쿼리 텍스트 |
| 출력 | 의도 유형, 대상 엔티티, 신뢰도 점수 |
| 알고리즘 | 임베딩 기반 유사성 매칭 (text-embedding-3-large) + LLM 폴백 |
| 신뢰도 임계 | < 0.7 시 LLM 폴백 |

### PageIndex Search Engine

| 항목 | 내용 |
|------|------|
| 역할 | 프로젝트 내 계층적 문서 검색 (HTTP 클라이언트) |
| 입력 | 프로젝트명, 검색 쿼리 |
| 출력 | 관련 섹션 순위 목록 (상위 5개) |
| 알고리즘 | Markdown → 헤더 트리 파싱 + LLM 추론 기반 노드 선택 (VectifyAI PageIndex) |
| 성능 목표 | < 2s (LLM API latency 포함) |

### CLAST Engine

| 항목 | 내용 |
|------|------|
| 역할 | 프로젝트 수명주기 자동 관리 |
| 입력 | 프로젝트 메타데이터 (마지막 접근일, 마감일) |
| 출력 | 상태 전환 권장사항 |
| 전환 규칙 | 30일 미활동 → 아카이브 권장 / 마감일 경과 → 아카이브 또는 연장 확인 / 아카이브 접근 → 재활성화 제안 |

### Memory Manager

| 항목 | 내용 |
|------|------|
| 역할 | PARA 폴더 구조 생성 및 유지보수 |
| 작업 | Create, Read, Update, Move, Archive |
| 저장소 | Markdown 파일 (인덱싱: PageIndex 서버 HTTP 호출) |

---

## 4. 플러그인 통합

### 도구 등록

```
api.registerTool('classify_intent', definition)
api.registerTool('search_project', definition)
api.registerTool('check_transition', definition)
```

### 슬래시 명령

| 명령 | 설명 |
|------|------|
| `/new-project {title}` | PARA 프로젝트 생성 |
| `/new-area {title}` | 영역 생성 |
| `/search {query}` | 프로젝트·영역·리소스 검색 |
| `/archive {id}` | 수동 아카이브 |
| `/restore {id}` | 아카이브 복원 |
| `/share-to-hub {name}` | Hub에 프로젝트 공유 (Phase 2) |
| `/no-hub-suggestions` | Hub 제안 비활성화 |

### 플러그인 위치

```
~/.openclaw/workspace/skills/project-centric-context-engineering/
```

---

## 5. 메모리 공존 구조 (memory-core + para-memory)

### OpenClaw 메모리 슬롯 시스템

OpenClaw는 단일 메모리 플러그인 슬롯을 사용한다. `"kind": "memory"`를 선언한 플러그인만 슬롯에 등록되며, 동시에 하나만 활성화된다 (`resolveMemorySlotDecision()` in `config-state.ts`).

```
# openclaw config 예시
plugins.slots.memory: "memory-core"     ← 기본값 (파일 기반 대화 메모리)
plugins.slots.memory: "memory-lancedb"  ← 벡터 메모리로 교체 시 (선택)
plugins.slots.memory: "para-memory"     ← ❌ para-memory는 슬롯 비경쟁 (ADR-007)
```

`para-memory`는 `"kind": "memory"`를 선언하지 않으므로 슬롯을 점령하지 않고 `memory-core`와 **공존**한다.

---

### 공존 구조

```
OpenClaw Agent
 │
 ├─ memory-core  [슬롯 점유 — kind: "memory"]
 │   ├─ MEMORY.md          ← 대화 컨텍스트 + 세션 간 핵심 기억
 │   ├─ memory/*.md        ← 주제별 기억 파일
 │   └─ 제공 도구: memory_search, memory_get
 │
 └─ para-memory  [슬롯 비경쟁 — kind 없음]
     ├─ memory/projects/   ← PARA 프로젝트 (마감 있는 목표)
     ├─ memory/areas/      ← 진행 중 책임 영역
     ├─ memory/resources/  ← 참고 자료
     ├─ memory/archive/    ← 완료/비활성 항목
     └─ 제공 도구: classify_intent, search_project, check_transition
```

두 플러그인은 각자의 메모리 경로를 사용하며 충돌하지 않는다.

---

### 도구 호출 라우팅

| 상황 | 호출 도구 | 플러그인 |
|------|----------|----------|
| 이전 대화 내용 / 일반 기억 검색 | `memory_search` | memory-core |
| 세션 간 기억 조회 | `memory_get` | memory-core |
| PARA 카테고리 분류 | `classify_intent` | para-memory |
| 프로젝트·영역·리소스 검색 | `search_project` | para-memory |
| 상태 전환 확인 (아카이브 권장 등) | `check_transition` | para-memory |
| 슬래시 명령 (`/new-project` 등) | 슬래시 핸들러 | para-memory |

---

### 시스템 프롬프트 주입

플러그인 초기화(`onLoad`) 시 다음 가이드를 시스템 프롬프트에 추가하여 Agent가 두 메모리 시스템을 올바르게 구분하도록 한다.

```
일반 대화 기억 검색은 memory_search / memory_get 을 사용하세요.
프로젝트·영역·리소스 탐색은 search_project 와 /search {query} 를 사용하세요.
새 프로젝트/영역 생성은 /new-project, /new-area 를 사용하세요.
```
