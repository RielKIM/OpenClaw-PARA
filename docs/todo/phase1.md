# Phase 1 구현 TODO

> 작업 시작·완료 시마다 업데이트
> `dev-progress.md` 는 기능 단위 추적 / 이 파일은 실제 코드 작업 단위 추적

**마지막 업데이트**: 2026-03-01

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

- [x] `store.py` — `save_tree`, `load_meta`, `load_tree`, `delete_tree`, `list_docs`
- [x] `indexer.py` — `index_file`, `reindex_item`
- [x] `searcher.py` — `_build_tree_summary`, `_extract_nodes`, `search`
- [x] `server.py` — `POST /index`, `DELETE /index`, `POST /reindex`, `POST /search`

---

## 2. plugin — MemoryManager (TypeScript)

- [ ] `initialize()` — SQLite-vec 주석 제거, PageIndex 서버 health check 위임 구조로 정리
- [ ] `createProject` — `projects/{id}/index.md` + 첫 일일 로그 생성
- [ ] `createArea` — `areas/{id}/index.md` 생성
- [ ] `createResource` — `resources/{id}/index.md` 생성
- [ ] `archive` — `projects/{id}` → `archive/{id}` 이동 + PageIndex 인덱스 삭제
- [ ] `restore` — `archive/{id}` → `projects/{id}` 복원 + PageIndex 재인덱싱
- [ ] `readMetadata` — `index.md` frontmatter 파싱
- [ ] `readAllFiles` — 항목 디렉터리 내 모든 `.md` 읽기
- [ ] `listByCategory` — 카테고리별 항목 목록 반환
- [ ] `updateIndex` — PageIndex 서버 `indexFile` 위임

---

## 3. plugin — PageIndexSearchEngine (TypeScript)

- [ ] `checkHealth` — `GET /health` (타임아웃 2s, healthy 캐싱)
- [ ] `searchInProject` — `POST /search` (project_id 지정, 저점수 시 searchAll 폴백)
- [ ] `searchAll` — `POST /search` (전체 / 카테고리 필터)
- [ ] `indexFile` — `POST /index`
- [ ] `reindexItem` — `POST /reindex`
- [ ] `deleteIndex` — `DELETE /index`

---

## 4. plugin — IntentClassifier (TypeScript)

- [ ] 카테고리 프로토타입 임베딩 벡터 정의
- [ ] `embedText` — `text-embedding-3-large` 호출
- [ ] 코사인 유사도 계산 + 최고값 ≥ 0.7 시 반환
- [ ] LLM 폴백 (`gpt-4o-mini`, 신뢰도 < 0.7 시)
- [ ] `classify` 메서드 완성

---

## 5. plugin — CLASTEngine (TypeScript)

- [ ] 전환 규칙 상수 정의 (30일 미활동 → archive, 마감 초과 등)
- [ ] `check` — 단일 항목에 전환 규칙 적용
- [ ] `checkAll` — 전체 projects + areas 순회
- [ ] `executeTransition` — `archive_or_extend` 케이스 처리

---

## 6. plugin — Tools & Hook

- [ ] `tools/classify-intent.ts` — execute 구현
- [ ] `tools/check-transitions.ts` — execute 구현
- [ ] `hooks/session-start.ts` — 확인 (이미 완성)

---

## 7. 검증

- [ ] `pageindex-server`: `docker compose up` → `/health`, `/index`, `/search` E2E
- [ ] plugin: 로컬 PARA 폴더 생성 → 인덱싱 → 검색 흐름 확인
- [ ] CLAST: 30일 미활동 항목 → 아카이브 권장 표시 확인
