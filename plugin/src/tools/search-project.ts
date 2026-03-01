// LLD 참조: docs/arch/LLD/plugin/pageindex-search.md
import type { OpenClawPluginToolFactory } from '@openclaw/plugin-sdk';
import { PageIndexSearchEngine }         from '../search/pageindex-search.js';
import type { MemoryManager }            from '../memory/memory-manager.js';
import type { PluginConfig }             from '../types.js';

export function searchProjectTool(
  memoryManager: MemoryManager,
  config:        PluginConfig,
): OpenClawPluginToolFactory {
  const engine = new PageIndexSearchEngine(memoryManager, config);

  return {
    id:          'para_search_project',
    name:        'PARA Project Search',
    description: 'PARA 메모리에서 관련 섹션을 검색합니다. projectId 미지정 시 전체 메모리를 검색합니다.',
    schema: {
      type: 'object',
      required: ['query'],
      properties: {
        query: {
          type:        'string',
          description: '검색 쿼리',
        },
        projectId: {
          type:        'string',
          description: '특정 항목 내 검색 시 해당 항목 ID (옵션)',
        },
        limit: {
          type:        'number',
          description: '반환할 최대 결과 수 (기본 5)',
          default:     5,
        },
      },
    },
    execute: async ({ query, projectId, limit }) => {
      if (projectId) {
        return engine.searchInProject(projectId, query, limit);
      }
      return engine.searchAll(query, undefined, limit);
    },
  };
}
