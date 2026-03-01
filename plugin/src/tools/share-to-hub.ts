// Phase 2 — hubEnabled: true 시 동적 로드
// LLD 참조: docs/arch/LLD/hub/anonymizer.md, docs/arch/LLD/hub/content-store.md
import type { OpenClawPluginToolFactory } from '@openclaw/plugin-sdk';
import type { PluginConfig }             from '../types.js';

export function shareToHubTool(config: PluginConfig): OpenClawPluginToolFactory {
  return {
    id:          'para_share_to_hub',
    name:        'PARA Share to Hub',
    description: '프로젝트를 익명화하여 PARA Hub에 공유합니다. PII가 제거된 후 Agent 전용 암호화 포맷으로 업로드됩니다.',
    schema: {
      type: 'object',
      required: ['projectId'],
      properties: {
        projectId: {
          type:        'string',
          description: '공유할 프로젝트 ID',
        },
        accessLevel: {
          type:        'string',
          enum:        ['public', 'reputation_gated'],
          default:     'public',
          description: '접근 레벨',
        },
      },
    },
    execute: async ({ projectId, accessLevel }) => {
      // TODO: Phase 2 구현
      //   1. MemoryManager.readAllFiles(projectId)
      //   2. HubClient.anonymize(files) → 신뢰도 확인
      //   3. HubClient.shareProject({ anonymized, metadata, accessLevel })
      //   4. 평판 업데이트 결과 반환
      throw new Error('Phase 2 미구현');
    },
  };
}
