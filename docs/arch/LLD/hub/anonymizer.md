# Anonymizer Service — 상세 설계

**컴포넌트**: PARA Hub
**관련 요구사항**: FR-3.1
**날짜**: 2026-03-01
**상태**: Draft (사용자 합의 전)

---

## 1. 책임

사용자 프로젝트 파일에서 PII(개인식별정보)를 제거하고, 차등 프라이버시를 적용하여 Agent 전용 포맷으로 변환하기 전의 익명화 콘텐츠를 생성한다.

---

## 2. 인터페이스

```python
@dataclass
class AnonymizationResult:
    anonymized_content: str
    pii_removed_count:  int
    confidence:         float   # 0.0 ~ 1.0
    preservation_score: float   # 의미 보존율

class AnonymizerService:
    async def anonymize(
        self,
        content: str,
        epsilon: float = 0.5    # 차등 프라이버시 강도
    ) -> AnonymizationResult
```

---

## 3. 파이프라인 (5단계)

```
입력 텍스트
  │
  ▼ Step 1: Named Entity Recognition
    spaCy en_core_web_trf 모델로 PII 엔티티 감지
    → PERSON, GPE, DATE, PHONE, EMAIL, ORG, MONEY
  │
  ▼ Step 2: 문맥 익명화
    감지된 엔티티를 범주형 플레이스홀더로 대체
    → "Alice" → [PERSON_1]
    → "오키나와" → [ISLAND_DESTINATION]
    → "2026-03-15" → [SPRING_DATE]
  │
  ▼ Step 3: 차등 프라이버시 (수치 데이터)
    금액, 기간 등에 Laplace 노이즈 추가 (ε = 0.1 ~ 1.0)
  │
  ▼ Step 4: 의미론적 보존 확인
    익명화 전후 임베딩 코사인 유사도로 보존율 계산
    → 보존율 < 0.7 시 경고
  │
  ▼ Step 5: 신뢰도 계산
    pii_count, preservation_score 기반
    → ≥ 0.95: 자동 공유 가능
    → 0.80 ~ 0.95: 사용자 경고 후 확인
    → < 0.80: 공유 차단
```

---

## 4. 엔티티 매핑 테이블

| NER 태그 | 대체 패턴 | 예시 |
|----------|-----------|------|
| PERSON | [PERSON_N] | Alice → [PERSON_1] |
| GPE (지명) | [LOCATION_TYPE] | 오키나와 → [ISLAND_DESTINATION] |
| DATE (특정일) | [DATE_RANGE] | 2026-03-15 → [SPRING_DATE] |
| PHONE | [CONTACT_INFO] | — |
| EMAIL | [EMAIL_ADDRESS] | — |
| ORG | [ORGANIZATION] | — |
| MONEY (정확값) | 노이즈 추가 | ¥15,000 → ¥14,300 |

---

## 5. 차등 프라이버시 구현

```python
def _apply_differential_privacy(self, content: str, epsilon: float) -> str:
    """수치 데이터에 Laplace 메커니즘 적용"""
    import re
    from numpy.random import laplace

    def add_noise(match: re.Match) -> str:
        raw = match.group().replace(',', '')
        value = float(re.sub(r'[¥$€£]', '', raw))
        sensitivity = abs(value) * 0.1      # 민감도: 값의 10%
        noise = laplace(0, sensitivity / epsilon)
        noisy = round(value + noise, -2)    # 100 단위 반올림
        return f"¥{int(noisy):,}"

    content = re.sub(r'[¥$€£]\s*[\d,]+', add_noise, content)
    return content
```

**ε 가이드라인**:

| ε | 프라이버시 | 유용성 |
|---|-----------|--------|
| 0.1 | 매우 강함 | 낮음 |
| 0.5 (기본) | 강함 | 중간 |
| 1.0 | 중간 | 높음 |

---

## 6. 신뢰도 계산

```python
def _calculate_confidence(
    self,
    pii_count:          int,
    preservation_score: float
) -> float:
    pii_penalty = min(0.1, pii_count * 0.01)
    base = 1.0 - pii_penalty
    return round(base * preservation_score, 3)
```

---

## 7. 테스트 계획

| 테스트 | 목표 |
|--------|------|
| 합성 PII 100개 문서 감지율 | > 99.5% |
| 익명화 후 의미 보존 (인간 평가 50개) | > 90% |
| 신뢰도 임계값 차단 동작 | 100% |
| ε 파라미터별 노이즈 범위 | 단위 |
