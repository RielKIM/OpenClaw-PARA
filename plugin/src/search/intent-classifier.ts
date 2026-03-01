// LLD 참조: docs/arch/LLD/plugin/intent-classifier.md
import type { ClassificationResult, PluginConfig } from '../types.js';

export class IntentClassifier {
  constructor(private readonly config: PluginConfig) {}

  /**
   * FR-2.1: 사용자 쿼리를 project/area/resource/unknown 으로 분류
   * 1차: 임베딩 기반 코사인 유사도 (≥0.7 시 반환)
   * 폴백: LLM 분류 (<0.7 시)
   */
  async classify(query: string): Promise<ClassificationResult> {
    // TODO: 구현
    //   1. embedText(query) → text-embedding-3-large
    //   2. CATEGORY_PROTOTYPES와 코사인 유사도 계산
    //   3. 최고 유사도 ≥ 0.7 → 반환
    //   4. < 0.7 → LLM 폴백
    throw new Error('Not implemented');
  }
}
