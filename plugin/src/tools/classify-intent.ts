// LLD 참조: docs/arch/LLD/plugin/intent-classifier.md
import type { OpenClawPluginToolFactory } from '@openclaw/plugin-sdk';
import { IntentClassifier }              from '../search/intent-classifier.js';
import type { PluginConfig }             from '../types.js';

export function classifyIntentTool(config: PluginConfig): OpenClawPluginToolFactory {
  const classifier = new IntentClassifier(config);

  return {
    id:          'para_classify_intent',
    name:        'PARA Intent Classifier',
    description: '사용자 쿼리를 PARA 카테고리(project/area/resource/unknown)로 분류합니다.',
    schema: {
      type: 'object',
      required: ['query'],
      properties: {
        query: {
          type:        'string',
          description: '분류할 사용자 쿼리',
        },
      },
    },
    execute: async ({ query }) => {
      return classifier.classify(query);
    },
  };
}
