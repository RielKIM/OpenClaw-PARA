# Intent Classifier — 상세 설계

**컴포넌트**: OpenClaw PARA Memory Plugin
**관련 요구사항**: FR-2.1
**날짜**: 2026-03-01
**상태**: Draft (사용자 합의 전)

---

## 1. 책임

사용자 쿼리를 `project` / `area` / `resource` / `unknown` 4가지 PARA 카테고리로 분류하고, 엔티티(의도 유형, 키워드 등)를 추출한다.

---

## 2. 인터페이스

```typescript
interface ClassificationResult {
  intent:      'project' | 'area' | 'resource' | 'unknown';
  confidence:  number;          // 0.0 ~ 1.0
  entities: {
    type?:     string;          // travel | parenting | tech | finance | ...
    target?:   string;          // 주요 대상 ("오키나와", "6개월 아기")
    keywords:  string[];
  };
  fallbackUsed: boolean;        // LLM 폴백 사용 여부
}

class IntentClassifier {
  async classify(query: string): Promise<ClassificationResult>
}
```

---

## 3. 분류 파이프라인

```
사용자 쿼리
  │
  ▼
1. 임베딩 생성 (text-embedding-3-large)
   └── 캐시 확인 → 캐시 히트 시 API 호출 스킵
  │
  ▼
2. 카테고리 프로토타입 벡터와 코사인 유사도 계산
  │
  ├── 최고 유사도 ≥ 0.7 → 해당 카테고리 반환
  │
  └── 최고 유사도 < 0.7 → LLM 폴백
        │
        ▼
      시스템 프롬프트로 4개 카테고리 분류 요청
      구조화된 JSON 응답 파싱
```

---

## 4. 카테고리 프로토타입

오프라인 사전 계산 후 번들에 포함 (API 호출 없음):

```typescript
const CATEGORY_PROTOTYPES: Record<string, string[]> = {
  project: [
    'travel plan', 'development project', 'event planning',
    'goal achievement', 'build something', 'launch product',
    'trip preparation', 'create app',
  ],
  area: [
    'health management', 'parenting advice', 'financial planning',
    'career development', 'ongoing responsibility', 'daily routine',
    'baby crying', 'exercise habit',
  ],
  resource: [
    'documentation', 'tutorial', 'reference material',
    'how to guide', 'technical spec', 'learning resource',
    'cheatsheet', 'api docs',
  ],
};
```

---

## 5. LLM 폴백 프롬프트

```
System:
  아래 쿼리를 다음 중 하나로 분류하라.
  - project: 마감일이 있는 단기 목표/계획
  - area: 지속적으로 관리하는 책임/영역
  - resource: 참고용 정보/자료
  - unknown: 분류 불가

  JSON만 반환:
  { "intent": "...", "confidence": 0.0~1.0,
    "type": "...", "keywords": [...] }

User: {query}
```

---

## 6. 카테고리별 예시

| 카테고리 | 예시 쿼리 |
|----------|-----------|
| `project` | "오키나와 여행 계획 중", "새 앱 개발 시작하려는데" |
| `area` | "6개월 아기가 계속 울어요", "건강 관리 어떻게 하지" |
| `resource` | "Python async 문서 찾아줘", "Redux 튜토리얼" |
| `unknown` | "안녕", "뭐하지" |

---

## 7. 성능 목표

| 항목 | 목표 |
|------|------|
| 임베딩 기반 분류 | < 200ms (캐시 미스 기준) |
| LLM 폴백 | < 2초 |
| 분류 정확도 | > 95% (테스트셋 100개 기준) |

---

## 8. 테스트 계획

| 테스트 | 방법 |
|--------|------|
| 카테고리별 정확도 | 레이블 100개 테스트셋 |
| 신뢰도 < 0.7 시 폴백 트리거 | 단위 |
| LLM 응답 파싱 실패 처리 | 단위 (응답 목킹) |
| 임베딩 캐시 히트 | 단위 |
