# Matching Engine — 상세 설계

**컴포넌트**: PARA Hub
**관련 요구사항**: FR-3.3
**날짜**: 2026-03-01
**상태**: Draft (사용자 합의 전)

---

## 1. 책임

새 프로젝트 메타데이터와 사용자 의도를 받아, Hub에 저장된 익명화 콘텐츠 중 유사한 항목을 검색하여 반환한다. 사용자 평판 등급에 따라 접근 가능한 결과만 필터링한다.

---

## 2. 인터페이스

```python
@dataclass
class SimilarProject:
    content_id:       str
    similarity_score: float
    intent_type:      str
    domain:           str
    rating:           float
    use_count:        int
    access_allowed:   bool

class MatchingEngine:
    async def find_similar(
        self,
        query_metadata:   ProjectMetadata,
        user_reputation:  int,
        top_k:            int = 5
    ) -> list[SimilarProject]
```

---

## 3. 다차원 유사도 계산

| 차원 | 가중치 | 계산 방법 |
|------|--------|-----------|
| intent | 0.30 | 의도 유형 정확 매칭 (0 or 1) |
| domain | 0.25 | 도메인 태그 Jaccard 유사도 |
| structure | 0.20 | 복잡도 레벨 차이 (simple/moderate/complex) |
| resources | 0.15 | 리소스 레벨 차이 (low/medium/high) |
| temporal | 0.10 | 기간(일) 차이 정규화 |

```python
def _calculate_multidimensional_score(
    self,
    query: ProjectMetadata,
    candidate: ContentMetadata
) -> float:
    scores = {
        'intent':    1.0 if query.intent_type == candidate.intent_type else 0.0,
        'domain':    jaccard(query.domain_tags, candidate.domain_tags),
        'structure': 1.0 - abs(LEVEL_MAP[query.complexity] -
                               LEVEL_MAP[candidate.complexity]) / 2,
        'resources': 1.0 - abs(LEVEL_MAP[query.resource_level] -
                               LEVEL_MAP[candidate.resource_level]) / 2,
        'temporal':  1.0 - min(1.0, abs(query.duration_days -
                               candidate.duration_days) / 30),
    }
    weights = {'intent':0.30, 'domain':0.25, 'structure':0.20,
               'resources':0.15, 'temporal':0.10}
    return sum(scores[k] * weights[k] for k in scores)
```

---

## 4. 검색 파이프라인

```
입력: query_metadata, user_reputation
  │
  ▼
1. 시맨틱 후보 추출 (pgvector KNN)
   → similarity_embedding 기준 상위 top_k × 3 후보
  │
  ▼
2. 다차원 유사도 재계산 (6차원)
  │
  ▼
3. 접근 권한 필터링
   → content.min_reputation > user_reputation → 제외
  │
  ▼
4. 상위 top_k 반환 (유사도 내림차순)
```

---

## 5. DB 스키마 (관련 부분)

```sql
-- pgvector 확장 필요
ALTER TABLE content_metadata
  ADD COLUMN similarity_embedding vector(1536);

CREATE INDEX ON content_metadata
  USING ivfflat (similarity_embedding vector_cosine_ops)
  WITH (lists = 100);
```

---

## 6. API 엔드포인트

**POST `/api/v1/projects/search`**

```
Request:
{
  "intent":        "travel",
  "domain_tags":   ["okinawa", "family", "1week"],
  "complexity":    "moderate",
  "resource_level":"medium",
  "duration_days": 7
}

Response:
{
  "matches": [
    {
      "content_id":       "uuid",
      "similarity_score": 0.92,
      "intent_type":      "travel",
      "domain":           "asia/japan",
      "access_allowed":   true,
      "rating":           4.8,
      "use_count":        23
    }
  ]
}
```

---

## 7. 테스트 계획

| 테스트 | 목표 |
|--------|------|
| 다차원 유사도 계산 정확도 | 단위 (고정 입력) |
| 접근 권한 필터링 | 단위 (등급별 시나리오) |
| KNN 검색 응답 시간 | < 3초 (10만 건 기준) |
| 매칭 관련성 | > 85% (레이블 테스트셋) |
