# DATA_MODEL — Plugin (OpenClaw PARA Memory Plugin)

**버전**: 4.0 | **날짜**: 2026-03-01 | **상태**: Design Phase

> Hub 데이터 모델: `docs/arch/HLD/hub/DATA_MODEL.md`

---

## 1. 로컬 PARA 파일 구조

### 1.1 Project

```
memory/projects/{project-id}/
├── index.md        ← 프로젝트 메타데이터
├── YYYY-MM-DD.md   ← 일일 로그
└── ...             ← 추가 컨텍스트 파일
```

**index.md 구조**:

```markdown
---
id: {uuid}
title: {제목}
category: project
status: active | archived
created_at: YYYY-MM-DD
deadline: YYYY-MM-DD
last_accessed: YYYY-MM-DD
keywords: [키워드1, 키워드2]
hub_content_ids: [hub-id-1, hub-id-2]
---
```

### 1.2 Area

```
memory/areas/{area-id}/
├── index.md
└── ...
```

**index.md 구조**:

```markdown
---
id: {uuid}
title: {영역명}
category: area
created_at: YYYY-MM-DD
last_reviewed: YYYY-MM-DD
keywords: [키워드]
---
```

### 1.3 Resource

```
memory/resources/{resource-id}/
├── index.md
└── content.md
```

### 1.4 Archive

```
memory/archive/{original-category}/{item-id}/
├── index.md       ← status: archived
└── ...
```

---

## 2. PageIndex 서버 인덱스 구조

섹션 단위 검색 인덱스는 플러그인 내부에 저장하지 않는다.
인덱스는 로컬 PageIndex 서버(`localhost:37779`)가 전담하며, 플러그인은 HTTP 클라이언트로만 동작한다.

```
~/.openclaw/workspace/.pageindex/
└── {project-id}/
    └── *.json    ← 헤더 트리 JSON (PageIndex 서버 관리)
```

> 자세한 인덱스 구조: `docs/arch/LLD/hub/pageindex-server.md`
