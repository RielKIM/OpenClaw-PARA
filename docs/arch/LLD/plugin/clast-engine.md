# CLAST Engine — 상세 설계

**컴포넌트**: OpenClaw PARA Memory Plugin
**관련 요구사항**: FR-1.3
**날짜**: 2026-03-01
**상태**: Draft (사용자 합의 전)

---

## 1. 책임

CLAST(Cognitive Load Aware State Transition) Engine은 프로젝트 수명주기를 자동으로 감시하고, 상태 전환이 필요한 시점을 사용자에게 알린다.

> **중요**: 자동 실행 금지. 전환은 반드시 사용자 확인 후에만 실행한다.

---

## 2. 인터페이스

```typescript
class CLASTEngine {
  constructor(private memoryManager: MemoryManager) {}

  // 모든 활성 항목 점검 (세션 시작 시 자동 호출)
  async checkAll(): Promise<TransitionRecommendation[]>

  // 단일 항목 점검
  async check(id: string): Promise<TransitionRecommendation | null>

  // 사용자 확인 후 전환 실행
  async executeTransition(id: string, type: TransitionType): Promise<void>
}

interface TransitionRecommendation {
  id:      string;
  title:   string;
  type:    TransitionType;
  reason:  string;   // 사용자에게 보여줄 메시지
  daysSince?: number;
}

type TransitionType = 'archive' | 'archive_or_extend' | 'reactivate';
```

---

## 3. 전환 규칙

```typescript
const TRANSITION_RULES: Array<{
  condition: (meta: ItemMetadata) => boolean;
  type:      TransitionType;
  reason:    (meta: ItemMetadata) => string;
}> = [
  {
    condition: (m) => daysSince(m.last_accessed) >= 30,
    type:      'archive',
    reason:    (m) => `${daysSince(m.last_accessed)}일간 접근 없음`,
  },
  {
    condition: (m) => !!m.deadline && daysSince(m.deadline) > 0,
    type:      'archive_or_extend',
    reason:    (m) => `마감일(${m.deadline}) 경과`,
  },
];
```

아카이브에서 항목에 접근하면 `reactivate` 권장을 별도 트리거.

---

## 4. 실행 흐름

```
세션 시작
  │
  ▼
CLASTEngine.checkAll()
  │
  ├── 권장 없음 → 종료
  │
  └── 권장 있음
        │
        ▼
      사용자에게 알림 (요약)
      예: "2개 프로젝트가 아카이브 권장 상태입니다"
        │
        ▼
      사용자 확인 (항목별)
        ├── 수락 → executeTransition()
        └── 거절 → 다음 세션까지 스킵
```

---

## 5. executeTransition 상세

```typescript
async executeTransition(id: string, type: TransitionType): Promise<void> {
  switch (type) {
    case 'archive':
      await this.memoryManager.archive(id, 'projects');
      break;

    case 'archive_or_extend':
      // UI에서 사용자가 선택 (아카이브 or 새 마감일 입력)
      break;

    case 'reactivate':
      await this.memoryManager.restore(id);
      break;
  }
}
```

---

## 6. 호출 시점

| 시점 | 동작 |
|------|------|
| 세션 시작 | `checkAll()` 자동 실행, 권장 항목 있으면 알림 |
| 아카이브 항목 접근 | `reactivate` 권장 트리거 |
| `/check-transitions` 명령 | 수동 실행 |

---

## 7. 테스트 계획

| 테스트 | 방법 |
|--------|------|
| 30일 미활동 감지 | 단위 (날짜 목킹) |
| 마감일 경과 감지 | 단위 (날짜 목킹) |
| 사용자 거절 시 재알림 안 함 | 단위 |
| 아카이브 → 복원 전환 | 통합 |
