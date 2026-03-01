// OpenClaw session_start 훅
// LLD 참조: docs/arch/LLD/plugin/clast-engine.md § 6
import type { CLASTEngine } from '../memory/clast-engine.js';

export function onSessionStart(clast: CLASTEngine) {
  return {
    type:     'session_start' as const,
    handler:  async () => {
      const recommendations = await clast.checkAll();
      if (recommendations.length === 0) return;

      // OpenClaw 에이전트에 CLAST 권장사항 주입
      // Agent가 대화 시작 시 사용자에게 알림
      return {
        systemPromptAddition: [
          '## PARA 상태 점검 결과',
          ...recommendations.map(r =>
            `- **${r.title}**: ${r.reason} → ${r.type} 권장`,
          ),
          '',
          '필요 시 사용자에게 위 항목 처리를 제안하세요.',
        ].join('\n'),
      };
    },
  };
}
