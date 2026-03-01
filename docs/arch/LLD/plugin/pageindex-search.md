# PageIndex Search Engine — 상세 설계

**컴포넌트**: OpenClaw PARA Memory Plugin (클라이언트 측)
**관련 요구사항**: FR-2.2, FR-2.3
**날짜**: 2026-03-01
**상태**: Draft (사용자 합의 전)

---

## 1. 설계 결정 이력

| 버전 | 결정 | 사유 |
|------|------|------|
| v1 | `better-sqlite3` + `sqlite-vec` + FTS5 | 초기 설계 |
| v2 | `@lancedb/lancedb` 하이브리드 검색 | OpenClaw 플러그인 native addon 불가 (Jiti 로더) |
| v3 | PageIndex 알고리즘 TypeScript 재구현 | 검토 후 기각 |
| **v4** | **PageIndex 로컬 서버 HTTP 클라이언트** | OpenClaw MCP 미지원 → HTTP 직접 호출. 서버는 Python 또는 Docker로 별도 실행. 서버 LLD: `hub/pageindex-server.md` |

**v4 핵심 변경:**
- 플러그인은 순수 HTTP 클라이언트 역할만 담당
- 실제 트리 파싱 + LLM 추론은 PageIndex 로컬 서버가 처리
- `@lancedb/lancedb` 검색용 제거 (item-level 인덱스도 서버에 위임)
- 의존성: 표준 `fetch` API만 사용

---

## 2. 책임

- PageIndex 로컬 서버의 HTTP 클라이언트 역할
- 파일 저장/수정 시 서버에 인덱싱 요청
- 검색 쿼리를 서버에 전달하고 결과 수신
- 서버 미실행 시 graceful degradation (검색 비활성화, 사용자 알림)

---

## 3. 인터페이스

```typescript
interface SearchResult {
  projectId:      string;
  projectTitle:   string;
  filePath:       string;
  nodeId:         string;       // 트리 노드 ID ("1.2.3")
  section:        string;       // 섹션 제목
  content:        string;       // 해당 노드 텍스트
  relevanceScore: number;       // 0.0 ~ 1.0
  reasoning:      string;       // LLM 선택 근거
}

class PageIndexSearchEngine {
  private serverUrl: string;    // 기본값: http://localhost:37779
  private healthy:   boolean;   // 서버 상태 캐시

  // 서버 상태 확인 (세션 시작 시 1회 호출)
  async checkHealth(): Promise<boolean>

  // 파일 인덱싱 요청 (MemoryManager에서 호출)
  async indexFile(filePath: string, projectId: string, category: PARACategory): Promise<void>

  // 항목 전체 재인덱싱
  async reindexItem(itemPath: string): Promise<void>

  // 인덱스 삭제 (아카이브/삭제 시)
  async deleteIndex(filePath: string): Promise<void>

  // 특정 프로젝트 내 검색
  async searchInProject(projectId: string, query: string, limit?: number): Promise<SearchResult[]>

  // 전체 메모리 검색 (폴백)
  async searchAll(query: string, category?: PARACategory, limit?: number): Promise<SearchResult[]>
}
```

---

## 4. 서버 통신 (HTTP API)

서버 API 명세는 `docs/arch/LLD/hub/pageindex-server.md` 참조.

### 인덱싱 요청

```typescript
// POST http://localhost:37779/index
async indexFile(filePath: string, projectId: string, category: PARACategory) {
  if (!this.healthy) return; // 서버 없으면 조용히 스킵

  await fetch(`${this.serverUrl}/index`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file_path: filePath, project_id: projectId, category }),
  });
}
```

### 검색 요청

```typescript
// POST http://localhost:37779/search
async searchInProject(projectId: string, query: string, limit = 5) {
  if (!this.healthy) return [];

  const res = await fetch(`${this.serverUrl}/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, project_id: projectId, limit }),
  });

  const data = await res.json();
  return data.results as SearchResult[];
}
```

---

## 5. 서버 미실행 시 동작 (Graceful Degradation)

```
세션 시작 시 checkHealth() 실행
  │
  ├─ HEALTHY → 정상 인덱싱/검색
  │
  └─ UNHEALTHY
       └─ indexFile() → 무시 (파일 저장은 정상 진행)
       └─ search*()   → [] 반환
       └─ session_start hook → systemPromptAddition에 경고 메시지 추가:
          "⚠️ PageIndex 서버가 실행 중이 아닙니다. 문서 검색 기능이 비활성화되어 있습니다.
           실행 방법: docs/arch/LLD/hub/pageindex-server.md 참조"
```

---

## 6. 폴백 조건 (FR-2.3)

| 조건 | 폴백 동작 |
|------|-----------|
| `searchInProject` 결과 0개 | `searchAll()` 실행 |
| 최상위 결과 relevanceScore < 0.3 | `searchAll()` 실행 |
| projectId 미지정 | 바로 `searchAll()` 실행 |
| 서버 UNHEALTHY | 빈 배열 반환 + 경고 |

---

## 7. 설정 (PluginConfig 추가 항목)

```typescript
interface PluginConfig {
  // 기존 항목 ...
  pageIndexServerUrl?: string;   // 기본값: "http://localhost:37779"
  pageIndexEnabled?:  boolean;   // 기본값: true (서버 실행 중이면 자동 활성화)
}
```

---

## 8. 슬래시 명령

| 명령 | 동작 |
|------|------|
| `/search {query}` | 전체 메모리 검색 |
| `/search-in {id} {query}` | 특정 항목 내 검색 |

---

## 9. 테스트 계획

| 테스트 | 방법 |
|--------|------|
| 서버 HEALTHY 시 인덱싱 요청 전달 | 단위 (mock fetch) |
| 서버 UNHEALTHY 시 graceful 처리 | 단위 |
| 검색 결과 파싱 | 단위 |
| 폴백 조건 트리거 | 단위 |
| 전체 흐름 (서버 실행 포함) | 통합 |
