// LLD 참조: docs/arch/LLD/plugin/clast-engine.md
import type { MemoryManager }             from './memory-manager.js';
import type { TransitionRecommendation }  from '../types.js';

export class CLASTEngine {
  constructor(private readonly memoryManager: MemoryManager) {}

  /**
   * FR-1.3: 모든 활성 항목 상태 점검
   * 세션 시작 훅에서 자동 호출
   */
  async checkAll(): Promise<TransitionRecommendation[]> {
    // TODO: 구현
    //   1. listByCategory('projects') + listByCategory('areas')
    //   2. 각 항목에 TRANSITION_RULES 적용
    //   3. 해당하는 TransitionRecommendation 반환
    return [];
  }

  async check(id: string): Promise<TransitionRecommendation | null> {
    // TODO: 구현
    return null;
  }

  /** 사용자 확인 후 전환 실행 — 자동 실행 금지 */
  async executeTransition(
    id:   string,
    type: TransitionRecommendation['type'],
  ): Promise<void> {
    switch (type) {
      case 'archive':
        await this.memoryManager.archive(id, 'projects');
        break;
      case 'reactivate':
        await this.memoryManager.restore(id);
        break;
      case 'archive_or_extend':
        // TODO: 사용자가 선택한 액션 처리
        break;
    }
  }
}
