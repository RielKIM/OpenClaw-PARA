# REQUIREMENTS — Plugin (OpenClaw PARA Memory Plugin)

**버전**: 4.0 | **날짜**: 2026-03-01 | **상태**: Design Phase

> Hub 요구사항 (FR-3~FR-5, NFR): `docs/arch/HLD/hub/REQUIREMENTS.md`

---

## FR-1: PARA 메모리 조직화

### FR-1.1: PARA 폴더 구조

- `memory/projects/`, `memory/areas/`, `memory/resources/`, `memory/archive/` 4개 폴더 자동 생성
- 각 카테고리에 맞는 폴더 구조와 메타데이터 파일 초기화
- 기존 `memory/` 폴더와 하위 호환 유지

### FR-1.2: 프로젝트 메타데이터

- 각 프로젝트 폴더에 `index.md` 자동 생성
  - 포함 필드: 생성일, 마감일, 상태(active/archived), 키워드, 카테고리, Hub 링크
- 일일 로그 파일 자동 초기화: `YYYY-MM-DD.md`

### FR-1.3: 자동 상태 전환 (CLAST Engine)

- 30일 미활동 → 아카이브 권장 알림
- 마감일 경과 → 자동 아카이브 또는 연장 확인
- 아카이브에서 접근 시 → 재활성화 제안
- 전환 시 사용자 확인 필요 (자동 실행 금지)

---

## FR-2: Intent 기반 검색

### FR-2.1: Intent 분류

- 사용자 쿼리를 4가지 카테고리로 분류: `Project` / `Area` / `Resource` / `Unknown`
- 분류 신뢰도 점수 제공 (0.0 ~ 1.0)
- 신뢰도 < 0.7 시 LLM 폴백 분류 수행
- 분류 정확도 목표: 95% 이상

### FR-2.2: PageIndex 검색

- 프로젝트 내 계층적 문서 검색 (Markdown → 헤더 트리 파싱)
- LLM 추론 기반 관련 노드 선택 (VectifyAI PageIndex, 벡터 없음)
- 관련 섹션 순위 목록 반환 (상위 5개)
- 검색 응답 시간: < 2s (LLM API latency 포함)
- PageIndex 로컬 서버(`localhost:37779`) 연동 — 서버 미실행 시 빈 결과 반환

### FR-2.3: 전체 메모리 폴백 검색

- PageIndex 결과 없거나 최상위 관련도 < 0.3 시 전체 메모리 검색으로 폴백
- archive 카테고리 제외
