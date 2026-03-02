# Phase 1 구현 TODO

> 작업 시작·완료 시마다 업데이트
> `dev-progress.md` 는 기능 단위 추적 / 이 파일은 실제 코드 작업 단위 추적

**마지막 업데이트**: 2026-03-02

---

## 범례

| 기호 | 의미 |
|------|------|
| `[ ]` | 미착수 |
| `[~]` | 진행 중 |
| `[x]` | 완료 |

---

## 0. 사전 수정

- [x] `search-project.ts` 버그: `new PageIndexSearchEngine(memoryManager, config)` → 생성자는 `config`만 받음
- [ ] `memory-manager.ts` → `initialize()` 내 SQLite-vec 주석 제거

---

## 1. pageindex-server (Python)

### 코드 구현
- [x] `store.py` — `save_tree`, `load_meta`, `load_tree`, `delete_tree`, `list_docs`
- [x] `indexer.py` — `index_file`, `reindex_item`
- [x] `searcher.py` — `_build_tree_summary`, `_extract_nodes`, `search`
- [x] `server.py` — `POST /index`, `DELETE /index`, `POST /reindex`, `POST /search`

### Docker 인프라
- [x] `Dockerfile` — python:3.11-slim, requirements 설치, uvicorn 실행
- [x] `docker-compose.yml` — 포트 바인딩, 볼륨 마운트, healthcheck
- [x] `.dockerignore` — `__pycache__`, `.env`, `.git` 제외
- [x] `.env.example` — `OPENAI_API_KEY`, `PAGEINDEX_DATA_DIR`, `PAGEINDEX_PORT`

### 수정 사항 (pageindex 라이브러리 이슈)
- [x] `pageindex` 라이브러리가 VectifyAI 클라우드 API(PDF 전용)임을 확인 → `md_to_tree` 미제공
- [x] `indexer.py`: 자체 마크다운 헤딩 기반 파서 구현 (`_parse_md_tree`)
- [x] `requirements.txt`: `pageindex` 의존성 제거
- [x] `docker-compose.yml`: 볼륨 마운트를 `${HOME}/.openclaw/workspace` 전체로 확장
- [x] `Dockerfile`: 하드코딩 경로 제거

### 검증
- [x] `docker compose up --build` 빌드 성공 확인
- [x] `GET /health` → `{"status":"ok","version":"0.1.0"}` 확인
- [x] `POST /index` → `doc_id`, `node_count: 8`, `.tree.json` + `.meta.json` 생성 확인
- [x] `POST /search` → LLM 추론으로 "예산 계획"(1.2), "3일차 스노클링"(1.3.3) 정확 반환 확인
- [x] 컨테이너 재시작 후 인덱스 유지 확인 (볼륨 퍼시스턴스)

---

## 2. plugin — MemoryManager (TypeScript)

### 코드 구현
- [ ] `initialize()` — SQLite-vec 주석 제거, 디렉터리 초기화만 수행
- [ ] `createProject` — `projects/{id}/index.md` + 첫 일일 로그 생성
- [ ] `createArea` — `areas/{id}/index.md` 생성
- [ ] `createResource` — `resources/{id}/index.md` 생성
- [ ] `archive` — `projects/{id}` → `archive/{id}` 이동
- [ ] `restore` — `archive/{id}` → 원래 카테고리 복원
- [ ] `readMetadata` — `index.md` frontmatter 파싱
- [ ] `readAllFiles` — 항목 디렉터리 내 모든 `.md` 읽기
- [ ] `listByCategory` — 카테고리별 항목 목록 반환
- [ ] `updateIndex` — PageIndex 서버 `indexFile` 위임

### 검증
- [ ] `initialize()` 호출 후 `projects/areas/resources/archive` 폴더 생성 확인
- [ ] `createProject("테스트")` → `projects/{id}/index.md` 파일 생성 및 frontmatter 확인
- [ ] `listByCategory("projects")` → 생성된 항목 반환 확인
- [ ] `archive(id)` → `archive/` 이동 확인
- [ ] `restore(id)` → 원래 카테고리 복원 확인

---

## 3. plugin — PageIndexSearchEngine (TypeScript)

### 코드 구현
- [ ] `checkHealth` — `GET /health` (타임아웃 2s, healthy 상태 캐싱)
- [ ] `searchInProject` — `POST /search` (project_id 지정, 저점수 시 searchAll 폴백)
- [ ] `searchAll` — `POST /search` (전체 / 카테고리 필터)
- [ ] `indexFile` — `POST /index`
- [ ] `reindexItem` — `POST /reindex`
- [ ] `deleteIndex` — `DELETE /index`

### 검증
- [ ] 서버 실행 중 `checkHealth()` → `true` 반환 확인
- [ ] 서버 미실행 시 `checkHealth()` → `false`, 이후 `searchInProject()` → 빈 배열 반환 확인 (graceful degradation)
- [ ] `indexFile()` 호출 후 pageindex-server에 `.tree.json` 생성 확인
- [ ] `searchInProject("test-okinawa", "예산")` → 예산 섹션 반환 확인
- [ ] `relevanceScore < 0.3` 시 `searchAll` 폴백 동작 확인

---

## 4. plugin — IntentClassifier (TypeScript)

### 코드 구현
- [ ] 카테고리 프로토타입 임베딩 벡터 정의
- [ ] `embedText` — `text-embedding-3-large` 호출
- [ ] 코사인 유사도 계산 + 최고값 ≥ 0.7 시 반환
- [ ] LLM 폴백 (`gpt-4o-mini`, 신뢰도 < 0.7 시)
- [ ] `classify` 메서드 완성

### 검증
- [ ] `classify("오키나와 여행 계획")` → `intent: "project"`, `confidence ≥ 0.7` 확인
- [ ] `classify("건강 관리")` → `intent: "area"` 확인
- [ ] `classify("React 튜토리얼")` → `intent: "resource"` 확인
- [ ] 모호한 쿼리 → `fallbackUsed: true`, LLM 폴백 동작 확인

---

## 5. plugin — CLASTEngine (TypeScript)

### 코드 구현
- [ ] 전환 규칙 상수 정의 (30일 미활동 → archive, 마감 초과 등)
- [ ] `check` — 단일 항목에 전환 규칙 적용
- [ ] `checkAll` — 전체 projects + areas 순회
- [ ] `executeTransition` — `archive_or_extend` 케이스 처리

### 검증
- [ ] `last_accessed` 31일 이전인 항목 → `check()` 가 `type: "archive"` 반환 확인
- [ ] `deadline` 초과 항목 → `type: "archive_or_extend"` 반환 확인
- [ ] `checkAll()` → 여러 항목 일괄 점검 결과 반환 확인
- [ ] `executeTransition(id, "archive")` → `archive/` 이동 확인

---

## 6. plugin — Tools & Hook

### 코드 구현
- [ ] `tools/classify-intent.ts` — execute 구현
- [ ] `tools/check-transitions.ts` — execute 구현
- [ ] `hooks/session-start.ts` — 확인 (이미 완성)

### 검증
- [ ] `classify_intent` 도구 호출 → `ClassificationResult` 형식 응답 확인
- [ ] `check_transitions` 도구 호출 → `TransitionRecommendation[]` 형식 응답 확인
- [ ] `session_start` 훅 → CLAST 결과가 있을 때 `systemPromptAddition` 반환 확인

---

## 7. E2E 통합 검증

- [ ] pageindex-server 실행 → MemoryManager로 프로젝트 생성 → 자동 인덱싱 → PageIndexSearchEngine으로 검색 흐름 확인
- [ ] CLAST: 30일 미활동 항목 → session_start 훅에서 아카이브 권장 메시지 출력 확인
- [ ] graceful degradation: pageindex-server 미실행 상태에서 플러그인 정상 로드 확인 (검색만 불가)
