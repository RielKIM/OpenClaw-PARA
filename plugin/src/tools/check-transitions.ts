// LLD 참조: docs/arch/LLD/plugin/clast-engine.md
import type { OpenClawPluginToolFactory } from '@openclaw/plugin-sdk';
import type { CLASTEngine }              from '../memory/clast-engine.js';

export function checkTransitionsTool(clast: CLASTEngine): OpenClawPluginToolFactory {
  return {
    id:          'para_check_transitions',
    name:        'PARA Check Transitions',
    description: '비활성 프로젝트의 상태 전환 권장사항을 확인합니다. 전환은 사용자 확인 후에만 실행됩니다.',
    schema: {
      type: 'object',
      properties: {
        execute: {
          type:        'boolean',
          description: 'true 시 사용자 확인 후 전환 실행, false(기본)는 권장사항만 반환',
          default:     false,
        },
        id: {
          type:        'string',
          description: '전환을 실행할 항목 ID (execute: true 시 필요)',
        },
        transitionType: {
          type:        'string',
          enum:        ['archive', 'archive_or_extend', 'reactivate'],
          description: '실행할 전환 유형',
        },
      },
    },
    execute: async ({ execute, id, transitionType }) => {
      if (execute && id && transitionType) {
        await clast.executeTransition(id, transitionType);
        return { executed: true, id, transitionType };
      }
      const recommendations = await clast.checkAll();
      return { recommendations };
    },
  };
}
