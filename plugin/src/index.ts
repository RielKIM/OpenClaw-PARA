import type { OpenClawPluginDefinition } from '@openclaw/plugin-sdk';
import type { PluginConfig } from './types.js';
import { MemoryManager }     from './memory/memory-manager.js';
import { CLASTEngine }       from './memory/clast-engine.js';
import { classifyIntentTool }   from './tools/classify-intent.js';
import { searchProjectTool }    from './tools/search-project.js';
import { checkTransitionsTool } from './tools/check-transitions.js';
import { onSessionStart }    from './hooks/session-start.js';

const plugin: OpenClawPluginDefinition = {
  id: 'para-memory',

  configSchema: {
    type: 'object',
    properties: {
      memoryPath:   { type: 'string' },
      hubEnabled:   { type: 'boolean', default: false },
      hubApiUrl:    { type: 'string' },
      openaiApiKey: { type: 'string' },
      flEnabled:    { type: 'boolean', default: false },
    },
  },

  async register(api) {
    const config = api.getConfig<PluginConfig>();
    const memoryManager = new MemoryManager(config.memoryPath);
    const clastEngine   = new CLASTEngine(memoryManager);

    await memoryManager.initialize();

    // FR-1: PARA 폴더 구조 관리 도구
    api.registerTool(checkTransitionsTool(clastEngine));

    // FR-2: Intent 분류 + 프로젝트 검색 도구
    api.registerTool(classifyIntentTool(config));
    api.registerTool(searchProjectTool(memoryManager, config));

    // FR-3: Hub 공유 도구 (Phase 2 — hubEnabled 시 활성화)
    if (config.hubEnabled) {
      const { shareToHubTool } = await import('./tools/share-to-hub.js');
      api.registerTool(shareToHubTool(config));
    }

    // 세션 시작 훅
    api.registerHook(onSessionStart(clastEngine));
  },
};

export default plugin;
