// PARA Hub HTTP 클라이언트 (Phase 2)
// LLD 참조: docs/arch/LLD/hub/hub-api.md
import type { PluginConfig } from '../types.js';

export class HubClient {
  constructor(private readonly config: PluginConfig) {}

  // POST /api/v1/projects/search
  async searchSimilar(metadata: Record<string, unknown>): Promise<unknown[]> {
    // TODO: Phase 2 구현
    throw new Error('Hub not enabled');
  }

  // POST /api/v1/projects/share
  async shareProject(payload: Record<string, unknown>): Promise<unknown> {
    // TODO: Phase 2 구현
    throw new Error('Hub not enabled');
  }

  // GET /api/v1/projects/{id}/content
  async fetchAgentContent(contentId: string): Promise<unknown> {
    // TODO: Phase 2 구현 — 메모리 내 전달, 로컬 저장 금지
    throw new Error('Hub not enabled');
  }

  // GET /api/v1/users/me/reputation
  async getReputation(): Promise<unknown> {
    // TODO: Phase 2 구현
    throw new Error('Hub not enabled');
  }

  async post(path: string, body: unknown): Promise<unknown> {
    // TODO: JWT 인증 헤더 포함
    throw new Error('Hub not enabled');
  }

  async get(path: string): Promise<unknown> {
    // TODO: JWT 인증 헤더 포함
    throw new Error('Hub not enabled');
  }
}
