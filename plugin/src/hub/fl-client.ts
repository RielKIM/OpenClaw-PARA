// Federated Learning 클라이언트 (Phase 3)
// LLD 참조: docs/arch/LLD/plugin/fl-client.md
import type { HubClient }     from './hub-client.js';
import type { PluginConfig }  from '../types.js';

export class FederatedLearningClient {
  constructor(
    private readonly hubClient: HubClient,
    private readonly config: PluginConfig,
  ) {}

  /**
   * FR-5: 로컬 훈련 + 암호화 그래디언트 전송
   * 원본 데이터는 절대 전송하지 않음
   */
  async runLocalTraining(category: string): Promise<{ skipped: boolean; reason?: string }> {
    // TODO: Phase 3 구현
    return { skipped: true, reason: 'Phase 3 미구현' };
  }

  async syncGlobalModel(): Promise<void> {
    // TODO: Phase 3 구현
  }
}
