// LLD 참조: docs/arch/LLD/plugin/pageindex-search.md (v4)
// PageIndex 로컬 서버 HTTP 클라이언트
//
// 서버: pageindex-server/ (Python/Docker, localhost:37779)
// 서버 LLD: docs/arch/LLD/hub/pageindex-server.md

import type { SearchResult, PARACategory, PluginConfig } from '../types.js';

const DEFAULT_SERVER_URL = 'http://localhost:37779';

export class PageIndexSearchEngine {
  private readonly serverUrl: string;
  private healthy = false;

  constructor(config: PluginConfig) {
    this.serverUrl = config.pageIndexServerUrl ?? DEFAULT_SERVER_URL;
  }

  /**
   * 세션 시작 시 1회 호출 — 서버 상태 캐시
   * UNHEALTHY 시 search*()는 빈 배열 반환, indexFile()은 무시
   */
  async checkHealth(): Promise<boolean> {
    // TODO: GET {serverUrl}/health
    // TODO: 응답 { status: 'ok' } 이면 this.healthy = true
    // TODO: 타임아웃(2s) 또는 오류 시 this.healthy = false
    void this.serverUrl;
    void this.healthy;
    throw new Error('Not implemented');
  }

  /**
   * FR-2.2: 특정 항목 내 LLM 추론 검색
   * POST {serverUrl}/search { query, project_id, limit }
   */
  async searchInProject(
    _projectId: string,
    _query:     string,
    _limit      = 5,
  ): Promise<SearchResult[]> {
    // TODO: !this.healthy → 빈 배열 반환
    // TODO: POST {serverUrl}/search { query, project_id: projectId, limit }
    // TODO: 응답 data.results → SearchResult[] 변환 (snake_case → camelCase)
    // TODO: 결과 0개 또는 최상위 relevanceScore < 0.3 → searchAll() 폴백
    throw new Error('Not implemented');
  }

  /**
   * FR-2.3: 전체 메모리 폴백 검색 (archive 제외)
   * POST {serverUrl}/search { query, category, limit }
   */
  async searchAll(
    _query:     string,
    _category?: PARACategory,
    _limit      = 5,
  ): Promise<SearchResult[]> {
    // TODO: !this.healthy → 빈 배열 반환
    // TODO: POST {serverUrl}/search { query, category: category ?? null, limit }
    // TODO: 응답 data.results → SearchResult[] 변환
    throw new Error('Not implemented');
  }

  /**
   * 파일 저장/수정 시 MemoryManager에서 호출
   * POST {serverUrl}/index { file_path, project_id, category }
   */
  async indexFile(
    _filePath:  string,
    _projectId: string,
    _category:  PARACategory,
  ): Promise<void> {
    // TODO: !this.healthy → 조용히 리턴 (인덱싱 실패는 검색 불가일 뿐, 파일 저장 정상)
    // TODO: POST {serverUrl}/index { file_path, project_id, category }
    throw new Error('Not implemented');
  }

  /**
   * 항목 전체 재인덱싱
   * POST {serverUrl}/reindex { item_path }
   */
  async reindexItem(_itemPath: string): Promise<void> {
    // TODO: !this.healthy → 조용히 리턴
    // TODO: POST {serverUrl}/reindex { item_path }
    throw new Error('Not implemented');
  }

  /**
   * 아카이브/삭제 시 인덱스 제거
   * DELETE {serverUrl}/index { file_path }
   */
  async deleteIndex(_filePath: string): Promise<void> {
    // TODO: !this.healthy → 조용히 리턴
    // TODO: DELETE {serverUrl}/index { file_path }
    throw new Error('Not implemented');
  }
}
