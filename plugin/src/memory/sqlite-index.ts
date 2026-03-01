// LLD 참조: docs/arch/LLD/plugin/pageindex-search.md
//
// ── 아키텍처 변경 이력 ──────────────────────────────────────
// v1: better-sqlite3 + sqlite-vec (native addon → Jiti 로더 불가)
// v2: @lancedb/lancedb (async 임베디드 DB → OpenClaw MCP 미지원으로 방향 전환)
// v3: PageIndex 로컬 서버 HTTP 클라이언트 (현재)
//
// 인덱싱/검색은 pageindex-server/ (Python/Docker) 가 전담.
// 플러그인은 HTTP 클라이언트 역할만 수행.
// 클라이언트 구현 위치: src/search/pageindex-search.ts
// 서버 LLD: docs/arch/LLD/hub/pageindex-server.md
// ────────────────────────────────────────────────────────────

// 이 파일은 더 이상 로컬 인덱스를 관리하지 않음.
// 하위 호환을 위해 파일을 유지하되 내용은 비워둠.
// 실제 인덱싱 요청은 MemoryManager → PageIndexSearchEngine.indexFile() 경로로 처리.
